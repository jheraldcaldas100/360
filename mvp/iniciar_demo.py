"""Arranca el detector y el dashboard con un solo comando (Ctrl+C detiene ambos).

Uso:
    python iniciar_demo.py
    python iniciar_demo.py --fuente http://192.168.1.20:8080/video
    python iniciar_demo.py --fuente videos/respaldo.mp4      # plan B con video grabado
    python iniciar_demo.py --limpiar                          # borra alertas anteriores
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Inicia la demo de Tres60 SafeCampus")
    parser.add_argument("--config", default=str(AQUI / "config.yaml"))
    parser.add_argument("--fuente", help="Cámara, URL del celular o archivo de video")
    parser.add_argument("--puerto", type=int, default=8501)
    parser.add_argument("--sin-ventana", action="store_true", help="No abrir la ventana de OpenCV")
    parser.add_argument("--limpiar", action="store_true", help="Borrar alertas y evidencias anteriores")
    args = parser.parse_args()

    if args.limpiar and (AQUI / "data").exists():
        shutil.rmtree(AQUI / "data")
        print("Alertas anteriores borradas.")

    detector = [sys.executable, str(AQUI / "detector.py"), "--config", args.config]
    if args.fuente:
        detector += ["--fuente", args.fuente]
    if args.sin_ventana:
        detector.append("--sin-ventana")
    dashboard = [sys.executable, "-m", "streamlit", "run", str(AQUI / "dashboard.py"),
                 "--server.port", str(args.puerto), "--server.headless", "true"]

    procesos = [subprocess.Popen(dashboard, cwd=AQUI), subprocess.Popen(detector, cwd=AQUI)]
    url = f"http://localhost:{args.puerto}"
    time.sleep(4)
    print(f"\nDashboard: {url}  (Ctrl+C para detener todo)\n")
    webbrowser.open(url)
    try:
        while all(p.poll() is None for p in procesos):
            time.sleep(0.5)
        print("Uno de los procesos terminó; deteniendo la demo.")
    except KeyboardInterrupt:
        pass
    finally:
        for p in procesos:
            if p.poll() is None:
                p.terminate()
        for p in procesos:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


if __name__ == "__main__":
    main()
