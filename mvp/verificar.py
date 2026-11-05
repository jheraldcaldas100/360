"""Chequeo previo a la demo: revisa que todo esté listo y dice qué falta.

Uso:
    python verificar.py
    python verificar.py --fuente http://192.168.1.20:8080/video
"""

from __future__ import annotations

import argparse
import importlib
import shutil
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
OK, FALLA, AVISO = "✅", "❌", "⚠️ "


def linea(estado: str, texto: str) -> bool:
    print(f"{estado} {texto}")
    return estado != FALLA


def revisar_dependencias() -> bool:
    bien = True
    for modulo in ("cv2", "ultralytics", "streamlit", "yaml", "requests", "pandas", "PIL"):
        try:
            importlib.import_module(modulo)
        except ImportError:
            bien = linea(FALLA, f"Falta la librería {modulo}: ejecuta pip install -r requirements.txt")
    return linea(OK, "Librerías instaladas") if bien else False


def revisar_camara(fuente) -> bool:
    import cv2

    from detector import abrir_fuente

    src, _ = abrir_fuente(fuente)
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        return linea(FALLA, f"No se pudo abrir la cámara «{fuente}». Revisa la URL, el wifi o el número.")
    n, t0, frame = 0, time.time(), None
    while time.time() - t0 < 3:
        ok, f = cap.read()
        if ok:
            n, frame = n + 1, f
    cap.release()
    if frame is None:
        return linea(FALLA, f"La cámara «{fuente}» abrió pero no entrega imagen.")
    alto, ancho = frame.shape[:2]
    brillo = float(frame.mean())
    linea(OK, f"Cámara «{fuente}»: {ancho}x{alto}, unos {n / 3:.0f} fps")
    if brillo < 50:
        linea(AVISO, "La imagen se ve muy oscura: busca más luz.")
    return True


def revisar_modelo(cfg: dict, fuente) -> bool:
    import cv2
    import numpy as np

    from analizador import Analizador

    try:
        analizador = Analizador(cfg)
    except Exception as e:
        return linea(FALLA, f"No se pudo cargar el modelo {cfg.get('modelo')}: {e}")
    imagen = np.zeros((720, 1280, 3), np.uint8)
    analizador.detectar(imagen)  # la primera inferencia siempre es más lenta
    t0 = time.time()
    for _ in range(5):
        analizador.detectar(imagen)
    fps = 5 / (time.time() - t0)
    estado = OK if fps >= 5 else AVISO
    linea(estado, f"Modelo {cfg.get('modelo')}: unos {fps:.1f} fps en esta computadora")
    if fps < 5:
        linea(AVISO, "Va lento: baja tamano_imagen a 480 o 320 en config.yaml.")
    return True


def revisar_telegram(cfg: dict) -> bool:
    import requests

    from notificador import credenciales

    token, chat_id = credenciales(cfg)
    if not token or not chat_id:
        return linea(AVISO, "Telegram sin configurar (opcional, pero recomendado para la demo).")
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if not r.ok:
            return linea(FALLA, f"Telegram rechazó el token (HTTP {r.status_code}).")
        r = requests.get(f"https://api.telegram.org/bot{token}/getChat",
                         params={"chat_id": chat_id}, timeout=10)
        if not r.ok:
            return linea(FALLA, "El bot no encuentra el chat: revisa TELEGRAM_CHAT_ID y que el bot esté en el grupo.")
        nombre = r.json()["result"].get("title") or r.json()["result"].get("first_name")
        return linea(OK, f"Telegram listo: el bot puede escribir en «{nombre}»")
    except requests.RequestException as e:
        return linea(FALLA, f"No hay conexión con Telegram: {e}")


def revisar_ia(cfg: dict) -> bool:
    from ia import configuracion_ia

    clave, modelo_o_motivo = configuracion_ia(cfg)
    if not clave:
        return linea(AVISO, f"Descripción con IA: {modelo_o_motivo} (opcional).")
    return linea(OK, f"Descripción con IA configurada ({modelo_o_motivo}).")


def revisar_disco() -> bool:
    libre = shutil.disk_usage(AQUI).free / 1e9
    if libre < 1:
        return linea(FALLA, f"Queda poco disco ({libre:.1f} GB).")
    return linea(OK, f"Disco libre: {libre:.0f} GB")


def main():
    parser = argparse.ArgumentParser(description="Chequeo previo a la demo")
    parser.add_argument("--config", default=str(AQUI / "config.yaml"))
    parser.add_argument("--fuente")
    args = parser.parse_args()

    print("Revisando Tres60 SafeCampus...\n")
    if not revisar_dependencias():
        raise SystemExit(1)
    from analizador import cargar_yaml

    cfg = cargar_yaml(args.config)
    fuente = args.fuente if args.fuente is not None else cfg["fuente"]
    resultados = [
        revisar_camara(fuente),
        revisar_modelo(cfg, fuente),
        revisar_telegram(cfg),
        revisar_ia(cfg),
        revisar_disco(),
    ]
    print()
    if all(resultados):
        print("Todo listo para la demo. Ejecuta: python iniciar_demo.py")
    else:
        print("Corrige los puntos marcados con ❌ antes de la demo.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
