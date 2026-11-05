"""Detector en vivo de Tres60 SafeCampus (MVP).

Lee la cámara (webcam, celular o archivo de video), detecta personas y
objetos con YOLO, aplica las reglas de reglas.py, guarda las alertas en
SQLite con una foto de evidencia y publica el último fotograma para el
dashboard.

Uso:
    python detector.py                       # usa config.yaml
    python detector.py --fuente http://192.168.1.20:8080/video
    python detector.py --fuente video.mp4 --config config_real.yaml
"""

from __future__ import annotations

import argparse
import os
import threading
import time
from pathlib import Path

import cv2
import yaml
from ultralytics import YOLO

from almacen import Almacen
from reglas import Deteccion, Motor

AQUI = Path(__file__).resolve().parent
DATOS = AQUI / "data"
EVIDENCIAS = DATOS / "evidencias"
EN_VIVO = DATOS / "en_vivo.jpg"

CLASES_DE_INTERES = {"person", "backpack", "handbag", "suitcase"}

COLOR = {
    "person": (80, 200, 80),
    "backpack": (255, 160, 0),
    "handbag": (255, 160, 0),
    "suitcase": (255, 160, 0),
}
ROJO = (0, 0, 255)
AMARILLO = (0, 220, 255)


class CamaraEnVivo:
    """Lee la cámara en un hilo aparte y entrega siempre el fotograma más reciente.

    Así el video no se atrasa cuando el análisis es más lento que la cámara
    (pasa mucho con la cámara del celular por wifi y una laptop sin GPU).
    """

    def __init__(self, fuente):
        self.fuente = fuente
        self.cap = cv2.VideoCapture(fuente)
        self.frame = None
        self.ok = self.cap.isOpened()
        self._lock = threading.Lock()
        self._activo = True
        threading.Thread(target=self._leer, daemon=True).start()

    def _leer(self):
        while self._activo:
            ok, frame = self.cap.read()
            if not ok:
                # Se cortó el stream: reintentar en 1 s.
                time.sleep(1)
                self.cap.release()
                self.cap = cv2.VideoCapture(self.fuente)
                continue
            with self._lock:
                self.frame = frame

    def leer(self):
        with self._lock:
            frame, self.frame = self.frame, None
        return frame

    def cerrar(self):
        self._activo = False
        self.cap.release()


def abrir_fuente(fuente):
    """Número = webcam o cámara virtual del celular; texto = URL o archivo."""
    if isinstance(fuente, int) or str(fuente).isdigit():
        return int(fuente), False
    es_archivo = Path(str(fuente)).exists()
    return str(fuente), es_archivo


def dibujar(frame, detecciones, estados):
    for d in detecciones:
        x1, y1, x2, y2 = map(int, d.caja)
        cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR.get(d.clase, (200, 200, 200)), 2)
        cv2.putText(frame, f"{d.clase} {d.confianza:.2f}", (x1, max(15, y1 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR.get(d.clase, (200, 200, 200)), 1)
    y_panel = 25
    for e in estados:
        color = ROJO if e.alerta else AMARILLO
        if e.caja is None:
            cv2.putText(frame, e.texto, (10, y_panel), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_panel += 28
        else:
            x1, y1, x2, y2 = map(int, e.caja)
            if e.texto == "Zona restringida":
                cv2.rectangle(frame, (x1, y1), (x2, y2), ROJO, 1)
                cv2.putText(frame, e.texto, (x1 + 5, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ROJO, 1)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3 if e.alerta else 2)
                cv2.putText(frame, e.texto, (x1, min(frame.shape[0] - 8, y2 + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return frame


def guardar_jpg(ruta: Path, frame):
    """Escribe el JPG de forma atómica para que el dashboard nunca lea uno a medias."""
    tmp = ruta.with_suffix(".tmp.jpg")
    cv2.imwrite(str(tmp), frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    os.replace(tmp, ruta)


def main():
    parser = argparse.ArgumentParser(description="Detector en vivo de Tres60 SafeCampus")
    parser.add_argument("--config", default=str(AQUI / "config.yaml"))
    parser.add_argument("--fuente", help="Sobrescribe la fuente de video del config")
    parser.add_argument("--sin-ventana", action="store_true", help="No abrir ventana de OpenCV")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    fuente, es_archivo = abrir_fuente(args.fuente if args.fuente is not None else cfg["fuente"])
    camara = cfg.get("nombre_camara", "Cámara 1")
    ventana = cfg.get("mostrar_ventana", True) and not args.sin_ventana

    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    almacen = Almacen(DATOS / "alertas.db")
    motor = Motor.desde_config(cfg["reglas"])
    modelo = YOLO(cfg.get("modelo", "yolo11n.pt"))
    clases = [i for i, n in modelo.names.items() if n in CLASES_DE_INTERES]

    if es_archivo:
        cap = cv2.VideoCapture(fuente)
        if not cap.isOpened():
            raise SystemExit(f"No se pudo abrir el video: {fuente}")
    else:
        cam = CamaraEnVivo(fuente)
        if not cam.ok:
            raise SystemExit(
                f"No se pudo abrir la cámara: {fuente}. Revisa la URL o el número de cámara."
            )

    print(f"Analizando {fuente} ({camara}). Reglas activas: "
          f"{', '.join(r.tipo for r in motor.reglas)}. Presiona q para salir.")
    ultimo_publicado = 0.0
    t_fps, n_fps, fps = time.time(), 0, 0.0
    try:
        while True:
            if es_archivo:
                ok, frame = cap.read()
                if not ok:
                    break
                ahora = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # tiempo del video
            else:
                frame = cam.leer()
                if frame is None:
                    time.sleep(0.01)
                    continue
                ahora = time.time()

            alto, ancho = frame.shape[:2]
            resultado = modelo.predict(
                frame, conf=cfg.get("confianza", 0.4), imgsz=cfg.get("tamano_imagen", 640),
                classes=clases, verbose=False,
            )[0]
            detecciones = [
                Deteccion(modelo.names[int(c)], float(p), tuple(map(float, caja)))
                for caja, c, p in zip(
                    resultado.boxes.xyxy.tolist(), resultado.boxes.cls.tolist(),
                    resultado.boxes.conf.tolist(),
                )
            ]
            alertas, estados = motor.evaluar(detecciones, ancho, alto, ahora)
            dibujar(frame, detecciones, estados)

            n_fps += 1
            if time.time() - t_fps >= 1:
                fps, n_fps, t_fps = n_fps / (time.time() - t_fps), 0, time.time()
            cv2.putText(frame, f"{fps:.1f} fps", (ancho - 110, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            for a in alertas:
                foto = frame.copy()
                for x1, y1, x2, y2 in a.cajas:
                    cv2.rectangle(foto, (int(x1), int(y1)), (int(x2), int(y2)), ROJO, 4)
                nombre = f"{time.strftime('%Y%m%d_%H%M%S')}_{a.tipo}_{int(time.time()*1000)%1000}.jpg"
                guardar_jpg(EVIDENCIAS / nombre, foto)
                alerta_id = almacen.guardar(camara, a.tipo, a.mensaje, str(EVIDENCIAS / nombre))
                print(f"[ALERTA #{alerta_id}] {a.mensaje}")

            if time.time() - ultimo_publicado > 0.3:
                guardar_jpg(EN_VIVO, frame)
                ultimo_publicado = time.time()

            if ventana:
                cv2.imshow("Tres60 SafeCampus", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        if es_archivo:
            cap.release()
        else:
            cam.cerrar()
        if ventana:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
