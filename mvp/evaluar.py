"""Evalúa el sistema con videos etiquetados y genera una tabla de resultados.

Usa exactamente la misma lógica que la demo en vivo (analizador.py), pero
sobre videos grabados, para medir cuántas situaciones detecta, cuántas se le
escapan, cuántas falsas alarmas genera y en cuánto tiempo alerta.

Formato del archivo de etiquetas (CSV), una fila por situación real:

    video,tipo,inicio_s,fin_s
    clips/aglo1.mp4,aglomeracion,3,15
    clips/mochila1.mp4,objeto_desatendido,5,40
    clips/caida1.mp4,persona_en_suelo,4,12
    clips/normal1.mp4,,,

- `inicio_s`: segundo del video en que empieza la situación (por ejemplo,
  cuando la persona se aleja de la mochila o cae al suelo).
- `fin_s`: segundo en que termina. Una fila sin tipo marca un video sin
  situaciones (sirve para contar falsas alarmas).
- Las rutas de los videos son relativas al CSV.

Uso:
    python evaluar.py etiquetas.csv
    python evaluar.py etiquetas.csv --config config.yaml --tolerancia 5
"""

from __future__ import annotations

import argparse
import csv
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

AQUI = Path(__file__).resolve().parent

NOMBRES = {
    "aglomeracion": "Aglomeración",
    "objeto_desatendido": "Objeto desatendido",
    "persona_en_suelo": "Persona en el suelo",
    "zona_restringida": "Zona restringida",
}


@dataclass
class Evento:
    video: str
    tipo: str
    inicio: float
    fin: float
    detectado_en: float | None = None


@dataclass
class AlertaVideo:
    video: str
    tipo: str
    t: float
    emparejada: bool = False


def leer_etiquetas(ruta: Path) -> tuple[list[str], list[Evento]]:
    videos, eventos = [], []
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            video = (fila.get("video") or "").strip()
            if not video:
                continue
            if video not in videos:
                videos.append(video)
            tipo = (fila.get("tipo") or "").strip()
            if tipo:
                eventos.append(Evento(video, tipo, float(fila["inicio_s"]), float(fila["fin_s"])))
    return videos, eventos


def emparejar(eventos: list[Evento], alertas: list[AlertaVideo], tolerancia: float) -> None:
    """Cada situación real se empareja con la primera alerta del mismo tipo, en el mismo
    video, emitida entre su inicio y su fin + tolerancia. Cada alerta cuenta una sola vez."""
    for ev in sorted(eventos, key=lambda e: (e.video, e.inicio)):
        for al in sorted(alertas, key=lambda a: a.t):
            if (not al.emparejada and al.video == ev.video and al.tipo == ev.tipo
                    and ev.inicio <= al.t <= ev.fin + tolerancia):
                al.emparejada = True
                ev.detectado_en = al.t
                break


def resumir(eventos, alertas, duracion_total_s, umbrales) -> list[dict]:
    tipos = sorted({e.tipo for e in eventos} | {a.tipo for a in alertas})
    filas = []
    for tipo in tipos:
        evs = [e for e in eventos if e.tipo == tipo]
        detectados = [e for e in evs if e.detectado_en is not None]
        falsas = [a for a in alertas if a.tipo == tipo and not a.emparejada]
        tiempos = [e.detectado_en - e.inicio for e in detectados]
        filas.append({
            "situacion": NOMBRES.get(tipo, tipo),
            "eventos": len(evs),
            "detectados": len(detectados),
            "omitidos": len(evs) - len(detectados),
            "sensibilidad": f"{100 * len(detectados) / len(evs):.0f} %" if evs else "—",
            "falsas_alarmas": len(falsas),
            "falsas_por_hora": round(len(falsas) / (duracion_total_s / 3600), 1)
            if duracion_total_s else 0,
            "tiempo_medio_alerta_s": round(sum(tiempos) / len(tiempos), 1) if tiempos else None,
            "umbral_configurado_s": umbrales.get(tipo),
        })
    return filas


def tabla_markdown(filas: list[dict]) -> str:
    cab = ("| Situación | Eventos | Detectados | Omitidos | Sensibilidad | Falsas alarmas "
           "| Tiempo medio hasta la alerta | Umbral configurado |")
    sep = "|---|---|---|---|---|---|---|---|"
    lineas = [cab, sep]
    for f in filas:
        t = f"{f['tiempo_medio_alerta_s']} s" if f["tiempo_medio_alerta_s"] is not None else "—"
        u = f"{f['umbral_configurado_s']:.0f} s" if f["umbral_configurado_s"] is not None else "—"
        lineas.append(
            f"| {f['situacion']} | {f['eventos']} | {f['detectados']} | {f['omitidos']} "
            f"| {f['sensibilidad']} | {f['falsas_alarmas']} | {t} | {u} |"
        )
    return "\n".join(lineas)


def analizar_video(analizador, ruta: Path, cada: int = 1):
    """Corre el análisis sobre un video y devuelve (alertas [(tipo, t)], duración, fps de proceso)."""
    import cv2

    cap = cv2.VideoCapture(str(ruta))
    if not cap.isOpened():
        raise SystemExit(f"No se pudo abrir el video: {ruta}")
    analizador.reiniciar_reglas()
    alertas, n, procesados, t0, t_video = [], 0, 0, time.time(), 0.0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        n += 1
        t_video = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if (n - 1) % cada:
            continue
        procesados += 1
        _, nuevas, _ = analizador.procesar(frame, t_video)
        alertas += [(a.tipo, t_video) for a in nuevas]
    cap.release()
    fps = procesados / max(1e-6, time.time() - t0)
    return alertas, t_video, fps


def main():
    parser = argparse.ArgumentParser(description="Evaluación de Tres60 SafeCampus con videos etiquetados")
    parser.add_argument("etiquetas", help="CSV con columnas video,tipo,inicio_s,fin_s")
    parser.add_argument("--config", default=str(AQUI / "config.yaml"))
    parser.add_argument("--tolerancia", type=float, default=5.0,
                        help="Segundos después del fin de la situación en que una alerta aún cuenta")
    parser.add_argument("--cada", type=int, default=1,
                        help="Analizar 1 de cada N fotogramas (para simular una laptop más lenta)")
    parser.add_argument("--salida", default=str(AQUI / "data" / "evaluacion"))
    args = parser.parse_args()

    from analizador import Analizador, cargar_yaml

    ruta_csv = Path(args.etiquetas).resolve()
    videos, eventos = leer_etiquetas(ruta_csv)
    cfg = cargar_yaml(args.config)
    analizador = Analizador(cfg)
    umbrales = {n: p.get("segundos") for n, p in cfg["reglas"].items() if p}

    alertas, duracion_total, fps_lista = [], 0.0, []
    for video in videos:
        ruta = (ruta_csv.parent / video).resolve()
        encontradas, duracion, fps = analizar_video(analizador, ruta, args.cada)
        duracion_total += duracion
        fps_lista.append(fps)
        alertas += [AlertaVideo(video, tipo, t) for tipo, t in encontradas]
        print(f"  {video}: {len(encontradas)} alerta(s) en {duracion:.0f} s de video ({fps:.1f} fps)")

    emparejar(eventos, alertas, args.tolerancia)
    filas = resumir(eventos, alertas, duracion_total, umbrales)

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    with open(salida / "detalle.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["registro", "video", "tipo", "inicio_s", "fin_s", "alerta_s", "resultado"])
        for e in eventos:
            w.writerow(["situacion", e.video, e.tipo, e.inicio, e.fin,
                        f"{e.detectado_en:.1f}" if e.detectado_en is not None else "",
                        "detectada" if e.detectado_en is not None else "omitida"])
        for a in alertas:
            if not a.emparejada:
                w.writerow(["alerta", a.video, a.tipo, "", "", f"{a.t:.1f}", "falsa alarma"])

    md = tabla_markdown(filas)
    fps_medio = sum(fps_lista) / len(fps_lista) if fps_lista else 0
    resumen = (
        f"# Resultados de la evaluación\n\n"
        f"- Videos: {len(videos)} ({duracion_total / 60:.1f} min en total)\n"
        f"- Situaciones etiquetadas: {len(eventos)}\n"
        f"- Velocidad de análisis: {fps_medio:.1f} fotogramas por segundo\n"
        f"- Configuración: `{Path(args.config).name}`; tolerancia: {args.tolerancia:.0f} s\n\n"
        f"{md}\n\n"
        f"El tiempo hasta la alerta se mide desde el inicio etiquetado de la situación; "
        f"incluye a propósito el umbral configurado de cada regla.\n"
    )
    (salida / "resumen.md").write_text(resumen, encoding="utf-8")
    print("\n" + md)
    print(f"\nVelocidad de análisis: {fps_medio:.1f} fps")
    print(f"Resultados guardados en {salida}/resumen.md y {salida}/detalle.csv")


if __name__ == "__main__":
    main()
