"""Detector en vivo de Tres60 SafeCampus (MVP).

Lee la cámara (webcam, celular o archivo de video), detecta personas y
objetos con YOLO, aplica las reglas de reglas.py, guarda las alertas en
SQLite con una foto de evidencia, las envía por Telegram (si está
configurado) y publica el último fotograma para el dashboard.

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

from almacen import Almacen
from analizador import Analizador, cargar_yaml, fusionar
from ia import DescriptorIA, configuracion_ia
from notificador import Telegram, credenciales

AQUI = Path(__file__).resolve().parent
DATOS = AQUI / "data"
EVIDENCIAS = DATOS / "evidencias"
EN_VIVO = DATOS / "en_vivo.jpg"
AJUSTES = DATOS / "ajustes.yaml"  # lo escribe el dashboard al mover los deslizadores
CONFIG_ACTIVA = DATOS / "config_activa.yaml"  # configuración en uso, para el dashboard

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

    def __init__(self, fuente, resolucion=None):
        self.fuente = fuente
        self.resolucion = resolucion
        self.cap = self._abrir()
        self.frame = None
        self.t_captura = 0.0
        self.ok = self.cap.isOpened()
        self._lock = threading.Lock()
        self._activo = True
        threading.Thread(target=self._leer, daemon=True).start()

    def _abrir(self):
        cap = cv2.VideoCapture(self.fuente)
        if self.resolucion:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolucion[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolucion[1])
        return cap

    def _leer(self):
        while self._activo:
            ok, frame = self.cap.read()
            if not ok:
                # Se cortó el stream: reintentar en 1 s.
                time.sleep(1)
                self.cap.release()
                self.cap = self._abrir()
                continue
            with self._lock:
                self.frame, self.t_captura = frame, time.time()

    def leer(self):
        """Devuelve (fotograma, hora de captura) o (None, None) si no hay uno nuevo."""
        with self._lock:
            frame, self.frame = self.frame, None
            return frame, (self.t_captura if frame is not None else None)

    def cerrar(self):
        self._activo = False
        self.cap.release()


def abrir_fuente(fuente):
    """Número = webcam o cámara virtual del celular; texto = URL o archivo."""
    if isinstance(fuente, int) or str(fuente).isdigit():
        return int(fuente), False
    return str(fuente), Path(str(fuente)).exists()


def dibujar(frame, detecciones, estados):
    for d in detecciones:
        x1, y1, x2, y2 = map(int, d.caja)
        color = COLOR.get(d.clase, (200, 200, 200))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{d.clase} {d.confianza:.2f}", (x1, max(15, y1 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    y_panel = 25
    for e in estados:
        color = ROJO if e.alerta else AMARILLO
        if e.caja is None:
            cv2.putText(frame, e.texto, (10, y_panel), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_panel += 28
        else:
            x1, y1, x2, y2 = map(int, e.caja)
            if e.texto == "Zona restringida":
                cv2.rectangle(frame, (x1, y1), (x2, y2), ROJO, 2)
                cv2.putText(frame, e.texto, (x1 + 5, y1 + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ROJO, 2)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3 if e.alerta else 2)
                cv2.putText(frame, e.texto, (x1, min(frame.shape[0] - 8, y2 + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return frame


def reemplazar(tmp: Path, destino: Path, intentos: int = 10, espera: float = 0.02) -> bool:
    """os.replace con reintentos. En Windows falla si otro proceso (el dashboard) está
    leyendo el destino; eso no debe tumbar la demo. Devuelve False si sigue ocupado."""
    for i in range(intentos):
        try:
            os.replace(tmp, destino)
            return True
        except PermissionError:
            if i < intentos - 1:
                time.sleep(espera)
    return False


def guardar_jpg(ruta: Path, frame) -> bool:
    """Escribe el JPG de forma atómica para que el dashboard nunca lea uno a medias."""
    tmp = ruta.with_suffix(".tmp.jpg")
    cv2.imwrite(str(tmp), frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return reemplazar(tmp, ruta)


def guardar_config_activa(cfg: dict) -> None:
    tmp = CONFIG_ACTIVA.with_suffix(".tmp")
    tmp.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    if not reemplazar(tmp, CONFIG_ACTIVA):
        print("[Ajustes] No se pudo publicar la configuración activa para el dashboard.")


class Recargador:
    """Detecta cambios en data/ajustes.yaml (hechos desde el dashboard) y los aplica en vivo."""

    def __init__(self, base: dict):
        self.base = base
        self.mtime = None
        self.revisado = 0.0

    def revisar(self, analizador: Analizador) -> None:
        if time.time() - self.revisado < 1:
            return
        self.revisado = time.time()
        if not AJUSTES.exists():
            return
        mtime = AJUSTES.stat().st_mtime
        if mtime == self.mtime:
            return
        self.mtime = mtime
        try:
            cfg = fusionar(self.base, cargar_yaml(AJUSTES))
            analizador.aplicar_config(cfg)
        except Exception as e:  # un ajuste inválido no debe tumbar la demo
            print(f"[Ajustes] No se pudieron aplicar: {e}")
            return
        guardar_config_activa(cfg)
        print("[Ajustes] Parámetros actualizados desde el dashboard.")


def main():
    parser = argparse.ArgumentParser(description="Detector en vivo de Tres60 SafeCampus")
    parser.add_argument("--config", default=str(AQUI / "config.yaml"))
    parser.add_argument("--fuente", help="Sobrescribe la fuente de video del config")
    parser.add_argument("--sin-ventana", action="store_true", help="No abrir ventana de OpenCV")
    args = parser.parse_args()

    cfg = cargar_yaml(args.config)
    fuente, es_archivo = abrir_fuente(args.fuente if args.fuente is not None else cfg["fuente"])
    camara = cfg.get("nombre_camara", "Cámara 1")
    ventana = cfg.get("mostrar_ventana", True) and not args.sin_ventana

    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    AJUSTES.unlink(missing_ok=True)  # al iniciar manda config.yaml; el dashboard ajusta encima
    guardar_config_activa(cfg)
    almacen = Almacen(DATOS / "alertas.db")
    analizador = Analizador(cfg)
    recargador = Recargador(cfg)

    telegram = None
    token, chat_id = credenciales(cfg)
    if token and chat_id:
        telegram = Telegram(token, chat_id, almacen)
        telegram.iniciar()
        print("Telegram activado: las alertas llegarán al chat configurado.")
    else:
        print("Telegram desactivado (falta TELEGRAM_TOKEN o TELEGRAM_CHAT_ID).")

    descriptor = None
    clave_ia, modelo_ia = configuracion_ia(cfg)
    if clave_ia:
        avisar = (lambda i, texto: telegram.enviar_texto(f"🤖 IA sobre la alerta #{i}: {texto}")) \
            if telegram else None
        descriptor = DescriptorIA(clave_ia, modelo_ia, almacen, al_describir=avisar)
        descriptor.iniciar()
        print(f"Descripción con IA activada ({modelo_ia}).")
    else:
        print(f"Descripción con IA desactivada ({modelo_ia}).")

    if es_archivo:
        cap = cv2.VideoCapture(fuente)
        if not cap.isOpened():
            raise SystemExit(f"No se pudo abrir el video: {fuente}")
    else:
        cam = CamaraEnVivo(fuente, cfg.get("resolucion"))
        if not cam.ok:
            raise SystemExit(
                f"No se pudo abrir la cámara: {fuente}. Revisa la URL o el número de cámara."
            )

    print(f"Analizando {fuente} ({camara}). Reglas activas: "
          f"{', '.join(r.tipo for r in analizador.motor.reglas)}. Presiona q para salir.")
    ultimo_publicado = 0.0
    t_fps, n_fps, fps = time.time(), 0, 0.0
    try:
        while True:
            if es_archivo:
                ok, frame = cap.read()
                if not ok:
                    break
                t_captura = time.time()
                ahora = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # tiempo del video
            else:
                frame, t_captura = cam.leer()
                if frame is None:
                    time.sleep(0.01)
                    continue
                ahora = t_captura

            recargador.revisar(analizador)
            detecciones, alertas, estados = analizador.procesar(frame, ahora)
            dibujar(frame, detecciones, estados)

            n_fps += 1
            if time.time() - t_fps >= 1:
                fps, n_fps, t_fps = n_fps / (time.time() - t_fps), 0, time.time()
            ancho = frame.shape[1]
            cv2.putText(frame, f"{fps:.1f} fps", (ancho - 110, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            for a in alertas:
                foto = frame.copy()
                for x1, y1, x2, y2 in a.cajas:
                    cv2.rectangle(foto, (int(x1), int(y1)), (int(x2), int(y2)), ROJO, 4)
                nombre = f"{time.strftime('%Y%m%d_%H%M%S')}_{a.tipo}_{int(time.time() * 1000) % 1000}.jpg"
                ruta = str(EVIDENCIAS / nombre)
                if not guardar_jpg(EVIDENCIAS / nombre, foto):
                    print(f"[Evidencia] No se pudo guardar la foto {nombre}.")
                latencia_ms = (time.time() - t_captura) * 1000
                alerta_id = almacen.guardar(camara, a.tipo, a.mensaje, ruta,
                                            duracion_s=a.duracion, latencia_ms=latencia_ms)
                print(f"[ALERTA #{alerta_id}] {a.mensaje} (procesada en {latencia_ms:.0f} ms)")
                if telegram:
                    telegram.enviar_alerta(alerta_id, a.tipo, a.mensaje, camara, ruta)
                if descriptor:
                    personas = [d.caja for d in detecciones if d.clase == "person"]
                    descriptor.describir_async(alerta_id, a.mensaje, ruta, personas)

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
        if telegram:
            # Dar unos segundos para que salgan las alertas pendientes.
            for _ in range(10):
                if telegram._cola.empty():
                    break
                time.sleep(0.5)
            telegram.detener()
        if descriptor:
            descriptor.detener()
        if ventana:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
