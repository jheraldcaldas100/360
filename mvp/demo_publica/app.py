"""Entrada de la demo pública: el mismo dashboard, con datos de ejemplo y sin cámara.

Va en su propia carpeta para que Streamlit Community Cloud use el requirements.txt
de aquí, sin YOLO ni PyTorch. Para probarla en la laptop:

    streamlit run demo_publica/app.py
"""

import os
import runpy
import sys
import time
from pathlib import Path

MVP = Path(__file__).resolve().parents[1]
if str(MVP) not in sys.path:
    sys.path.insert(0, str(MVP))

os.environ["SAFECAMPUS_DEMO"] = "1"
if hasattr(time, "tzset"):  # el servidor está en UTC; en Windows no hace falta
    os.environ["TZ"] = "America/Lima"
    time.tzset()

runpy.run_path(str(MVP / "dashboard.py"), run_name="__main__")
