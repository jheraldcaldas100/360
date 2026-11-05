"""Experimento "¿quién lo ve primero?": personas frente a SafeCampus.

Simula una sala de monitoreo con varias cámaras en mosaico. En una de ellas
ocurre una situación (por ejemplo, alguien deja una mochila y se va). Cada
participante mira el mosaico y presiona ESPACIO cuando nota algo raro. Se
mide su tiempo de reacción y se compara con el tiempo de alerta del sistema.

1) Crear el mosaico con 4 a 9 videos (el primero suele ser el del evento):
    python experimento.py crear --videos evento.mp4 cam2.mp4 cam3.mp4 cam4.mp4 \\
        --salida data/mosaico.mp4 --duracion 90 --posicion-evento 3

2) Medir a cada participante (abre una ventana; ESPACIO = "vi algo", ESC = terminar):
    python experimento.py medir --video data/mosaico.mp4 --evento 25 --participante "Ana"

3) Ver el resumen y compararlo con el tiempo del sistema (sale de evaluar.py):
    python experimento.py resumen --sistema 21.4
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RESULTADOS = AQUI / "data" / "experimento.csv"


# -------------------------------------------------------------------- crear


def crear_mosaico(videos: list[str], salida: str, duracion: float, posicion_evento: int = 1,
                  ancho_celda: int = 640, alto_celda: int = 360, fps: float = 15.0) -> tuple[int, int]:
    """Arma un mosaico (2x2 o 3x3) leyendo cada video según su propio tiempo.
    El primer video se coloca en la celda `posicion_evento` (1 = arriba a la izquierda).
    Los videos cortos se repiten. Devuelve (filas, columnas)."""
    import cv2
    import numpy as np

    if not 2 <= len(videos) <= 9:
        raise SystemExit("Usa entre 2 y 9 videos.")
    lado = math.ceil(math.sqrt(len(videos)))
    filas = math.ceil(len(videos) / lado)
    if not 1 <= posicion_evento <= filas * lado:
        raise SystemExit(f"--posicion-evento debe estar entre 1 y {filas * lado}")
    orden = list(videos[1:])
    orden.insert(posicion_evento - 1, videos[0])

    fuentes = []
    for ruta in orden:
        cap = cv2.VideoCapture(ruta)
        if not cap.isOpened():
            raise SystemExit(f"No se pudo abrir {ruta}")
        fuentes.append({"ruta": ruta, "cap": cap, "fps": cap.get(cv2.CAP_PROP_FPS) or 30.0,
                        "frame": None, "leidos": 0, "desfase": 0.0})

    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    out = cv2.VideoWriter(salida, cv2.VideoWriter_fourcc(*"mp4v"), fps,
                          (ancho_celda * lado, alto_celda * filas))
    negro = np.zeros((alto_celda, ancho_celda, 3), np.uint8)
    for k in range(int(duracion * fps)):
        t = k / fps
        lienzo = np.zeros((alto_celda * filas, ancho_celda * lado, 3), np.uint8)
        for i, f in enumerate(fuentes):
            # Avanzar este video hasta el tiempo t (repitiéndolo si se acaba).
            while f["frame"] is None or f["desfase"] + f["leidos"] / f["fps"] <= t:
                ok, frame = f["cap"].read()
                if not ok:
                    if f["leidos"] == 0:
                        raise SystemExit(f"El video {f['ruta']} está vacío")
                    f["desfase"] += f["leidos"] / f["fps"]
                    f["leidos"] = 0
                    f["cap"].release()
                    f["cap"] = cv2.VideoCapture(f["ruta"])
                    continue
                f["frame"], f["leidos"] = frame, f["leidos"] + 1
            celda = cv2.resize(f["frame"], (ancho_celda, alto_celda)) if f["frame"] is not None else negro
            cv2.putText(celda, f"CAM {i + 1}", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255), 2)
            cv2.putText(celda, time.strftime("%H:%M:%S", time.gmtime(t + 8 * 3600)),
                        (ancho_celda - 130, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y, x = divmod(i, lado)
            lienzo[y * alto_celda:(y + 1) * alto_celda, x * ancho_celda:(x + 1) * ancho_celda] = celda
        out.write(lienzo)
    out.release()
    for f in fuentes:
        f["cap"].release()
    return filas, lado


# -------------------------------------------------------------------- medir


def calcular_resultado(presiones: list[float], evento: float) -> dict:
    """Primera presión después del evento = detección. Las anteriores son avisos falsos."""
    antes = [p for p in presiones if p < evento]
    despues = [p for p in presiones if p >= evento]
    return {
        "detecto": bool(despues),
        "reaccion_s": round(despues[0] - evento, 2) if despues else None,
        "avisos_falsos": len(antes),
    }


def medir(video: str, evento: float, participante: str, resultados: Path = RESULTADOS) -> dict:
    import cv2

    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        raise SystemExit(f"No se pudo abrir {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 15.0
    nombre = "Sala de monitoreo - presiona ESPACIO cuando veas algo raro (ESC termina)"
    cv2.namedWindow(nombre, cv2.WINDOW_NORMAL)
    input(f"{participante}: mira la ventana y presiona ESPACIO cuando notes una situación "
          f"de riesgo. Pulsa Enter para empezar...")
    presiones, n, t0 = [], 0, time.monotonic()
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        n += 1
        cv2.imshow(nombre, frame)
        espera = max(1, int((t0 + n / fps - time.monotonic()) * 1000))  # reproducir en tiempo real
        tecla = cv2.waitKey(espera) & 0xFF
        if tecla == 32:  # espacio
            presiones.append(time.monotonic() - t0)
            print(f"  Aviso a los {presiones[-1]:.1f} s")
        elif tecla == 27:  # ESC
            break
    cap.release()
    cv2.destroyAllWindows()

    r = calcular_resultado(presiones, evento)
    resultados.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not resultados.exists()
    with open(resultados, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["participante", "video", "evento_s", "detecto", "reaccion_s", "avisos_falsos"])
        w.writerow([participante, Path(video).name, evento, "si" if r["detecto"] else "no",
                    r["reaccion_s"] if r["reaccion_s"] is not None else "", r["avisos_falsos"]])
    print(f"Resultado de {participante}: " + (
        f"detectó la situación {r['reaccion_s']} s después de que empezó." if r["detecto"]
        else "no detectó la situación."))
    return r


# ------------------------------------------------------------------ resumen


def resumir(resultados: Path, sistema: float | None = None) -> str:
    with open(resultados, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        return "No hay resultados todavía."
    tiempos = [float(f["reaccion_s"]) for f in filas if f["detecto"] == "si" and f["reaccion_s"]]
    n, detectaron = len(filas), len(tiempos)
    lineas = [
        "# Experimento \"¿quién lo ve primero?\"",
        "",
        f"- Participantes: {n}",
        f"- Detectaron la situación: {detectaron} de {n} ({100 * detectaron / n:.0f} %)",
        f"- **No la detectaron: {n - detectaron} de {n}**",
    ]
    if tiempos:
        lineas += [
            f"- Tiempo de reacción de las personas que la detectaron: promedio "
            f"{statistics.mean(tiempos):.1f} s, mediana {statistics.median(tiempos):.1f} s, "
            f"rango {min(tiempos):.1f} a {max(tiempos):.1f} s",
        ]
    avisos = sum(int(f["avisos_falsos"] or 0) for f in filas)
    lineas.append(f"- Avisos antes de que ocurriera la situación (falsos): {avisos}")
    if sistema is not None:
        lineas += ["", f"**SafeCampus alertó a los {sistema:.1f} s** de iniciada la situación "
                       "(incluye el umbral configurado de la regla)."]
        if tiempos:
            mas_lentas = sum(1 for t in tiempos if t > sistema)
            lineas.append(f"- El sistema fue más rápido que {mas_lentas} de las {detectaron} personas "
                          f"que la detectaron, y además no se le pasó (a {n - detectaron} sí).")
    return "\n".join(lineas)


def main():
    parser = argparse.ArgumentParser(description="Experimento personas frente a SafeCampus")
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("crear", help="Crear el video mosaico")
    p.add_argument("--videos", nargs="+", required=True, help="El primero es el del evento")
    p.add_argument("--salida", default=str(AQUI / "data" / "mosaico.mp4"))
    p.add_argument("--duracion", type=float, default=90)
    p.add_argument("--posicion-evento", type=int, default=1,
                   help="Celda donde va el video del evento (1 = arriba a la izquierda)")

    p = sub.add_parser("medir", help="Medir a un participante")
    p.add_argument("--video", default=str(AQUI / "data" / "mosaico.mp4"))
    p.add_argument("--evento", type=float, required=True,
                   help="Segundo del mosaico en que empieza la situación")
    p.add_argument("--participante", required=True)

    p = sub.add_parser("resumen", help="Resumen de resultados")
    p.add_argument("--sistema", type=float, help="Segundos que tardó SafeCampus en alertar")

    args = parser.parse_args()
    if args.comando == "crear":
        filas, columnas = crear_mosaico(args.videos, args.salida, args.duracion, args.posicion_evento)
        print(f"Mosaico {filas}x{columnas} guardado en {args.salida}. El video del evento está "
              f"en la celda CAM {args.posicion_evento}.")
    elif args.comando == "medir":
        medir(args.video, args.evento, args.participante)
    else:
        texto = resumir(RESULTADOS, args.sistema)
        print(texto)
        (RESULTADOS.parent / "experimento_resumen.md").write_text(texto + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
