"""Datos de ejemplo para la demo pública del dashboard.

Nada de este módulo viene de una cámara ni de una medición: las alertas y sus
tiempos son inventados para mostrar la interfaz, y las imágenes son dibujos, sin
personas reales. Cada visitante recibe su propia base en memoria, así que lo que
toca no le cambia nada a los demás.
"""

from __future__ import annotations

import tempfile
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw

from almacen import Almacen
from mapa import _fuente

ANCHO, ALTO = 960, 540
AMARILLO, ROJO, GRIS = (250, 190, 40), (248, 80, 80), (148, 163, 184)
RUTULO = "IMAGEN ILUSTRATIVA: NO ES UNA CÁMARA REAL"

MAPA = {
    "imagen": "",
    "camaras": {
        "Ingreso principal": [0.47, 0.84],
        "Patio central": [0.48, 0.52],
        "Biblioteca": [0.19, 0.24],
        "Comedor": [0.17, 0.78],
    },
}

# Reglas de ejemplo: minutos atrás, cámara, tipo, mensaje, segundos hasta la alerta,
# milisegundos de proceso, estado, segundos hasta revisar y hasta atender.
SEMILLA = [
    (312, "Comedor", "aglomeracion", "Aglomeración: 6 personas durante 5 s (umbral: 3 personas, 5 s)",
     5.2, 110, "descartada", 48, None),
    (268, "Biblioteca", "objeto_desatendido", "Objeto #3 sin persona cerca durante 00:20 (umbral: 00:20)",
     20.1, 95, "atendida", 35, 240),
    (225, "Ingreso principal", "persona_en_suelo", "Persona #7 en el suelo durante 5 s (umbral: 5 s)",
     5.4, 130, "atendida", 18, 150),
    (170, "Patio central", "aglomeracion", "Aglomeración: 4 personas durante 5 s (umbral: 3 personas, 5 s)",
     5.1, 105, "descartada", 62, None),
    (96, "Biblioteca", "zona_restringida", "Persona #2 en zona restringida durante 2 s",
     2.3, 90, "atendida", 26, 310),
    (41, "Comedor", "objeto_desatendido", "Objeto #5 sin persona cerca durante 00:20 (umbral: 00:20)",
     20.3, 120, "confirmada", 44, None),
    (12, "Patio central", "aglomeracion", "Aglomeración: 5 personas durante 6 s (umbral: 3 personas, 5 s)",
     5.8, 100, "nueva", None, None),
    (3, "Ingreso principal", "persona_en_suelo", "Persona #9 en el suelo durante 5 s (umbral: 5 s)",
     5.2, 125, "nueva", None, None),
]

SIMULADAS = [
    ("Patio central", "persona_en_suelo", "Persona #12 en el suelo durante 5 s (umbral: 5 s)", 5.3, 115),
    ("Biblioteca", "objeto_desatendido", "Objeto #8 sin persona cerca durante 00:20 (umbral: 00:20)", 20.2, 98),
    ("Comedor", "aglomeracion", "Aglomeración: 7 personas durante 5 s (umbral: 3 personas, 5 s)", 5.1, 104),
]


def _persona(d: ImageDraw.ImageDraw, x: int, y: int, alto: int = 170) -> tuple[int, int, int, int]:
    """Silueta de pie, sin rasgos. Devuelve su caja."""
    r = alto // 8
    d.ellipse((x - r, y, x + r, y + 2 * r), fill=GRIS)
    d.rounded_rectangle((x - r, y + 2 * r + 4, x + r, y + alto), radius=r // 2, fill=GRIS)
    return x - r - 8, y - 8, x + r + 8, y + alto + 8


def _caja(d: ImageDraw.ImageDraw, caja: tuple[int, int, int, int], color=AMARILLO) -> None:
    d.rectangle(caja, outline=color, width=4)


def escena(tipo: str = "") -> Image.Image:
    """Dibujo esquemático de la situación, con su rótulo."""
    img = Image.new("RGB", (ANCHO, ALTO), (24, 33, 48))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 250, ANCHO, ALTO), fill=(38, 50, 69))
    for x in range(-600, ANCHO + 600, 150):  # líneas del piso, en perspectiva
        d.line((ANCHO / 2 + (x - ANCHO / 2) * 0.35, 250, x, ALTO), fill=(52, 66, 88), width=1)
    for y in (290, 345, 420):
        d.line((0, y, ANCHO, y), fill=(52, 66, 88), width=1)
    if tipo == "aglomeracion":
        for x in (300, 400, 490, 590, 680):
            _caja(d, _persona(d, x, 200), ROJO)
    elif tipo == "objeto_desatendido":
        caja = (440, 340, 540, 450)
        d.rounded_rectangle(caja, radius=18, fill=(96, 125, 175))
        _caja(d, (428, 328, 552, 462), ROJO)
        _persona(d, 840, 180)
    elif tipo == "persona_en_suelo":
        d.ellipse((270, 345, 320, 395), fill=GRIS)
        d.rounded_rectangle((325, 345, 660, 395), radius=20, fill=GRIS)
        _caja(d, (255, 330, 675, 410), ROJO)
    elif tipo == "zona_restringida":
        d.rectangle((560, 90, ANCHO - 30, ALTO - 40), outline=ROJO, width=4)
        d.text((575, 100), "Zona restringida", fill=ROJO, font=_fuente(22))
        _caja(d, _persona(d, 730, 210), ROJO)
    else:
        for x in (220, 520):
            _caja(d, _persona(d, x, 200))
    d.rectangle((0, ALTO - 34, ANCHO, ALTO), fill=(10, 15, 25))
    d.text((12, ALTO - 28), RUTULO, fill="white", font=_fuente(18))
    return img


@lru_cache(maxsize=1)
def _imagenes() -> dict[str, str]:
    """Guarda los dibujos una vez por proceso, en una carpeta temporal fuera del repositorio."""
    carpeta = Path(tempfile.mkdtemp(prefix="safecampus_demo_"))
    rutas = {}
    for tipo in ("aglomeracion", "objeto_desatendido", "persona_en_suelo", "zona_restringida"):
        rutas[tipo] = str(carpeta / f"{tipo}.png")
        escena(tipo).save(rutas[tipo])
    return rutas


def _iso(fecha: datetime | None) -> str | None:
    return fecha.isoformat(timespec="milliseconds") if fecha else None


def crear_almacen(ahora: datetime | None = None) -> Almacen:
    """Base en memoria, solo para un visitante, con las alertas de ejemplo."""
    ahora = ahora or datetime.now()
    db = Almacen(":memory:")
    imagenes = _imagenes()
    for minutos, camara, tipo, mensaje, duracion, latencia, estado, revisar, atender in SEMILLA:
        fecha = ahora - timedelta(minutes=minutos)
        revisada = fecha + timedelta(seconds=revisar) if revisar is not None else None
        atendida = fecha + timedelta(seconds=atender) if atender is not None else None
        db.conn.execute(
            "INSERT INTO alertas (fecha, camara, tipo, mensaje, imagen, estado, inicio_situacion,"
            " duracion_s, latencia_ms, revisada, revisado_por, atendida, atendido_por)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                _iso(fecha), camara, tipo, mensaje, imagenes[tipo], estado,
                _iso(fecha - timedelta(seconds=duracion)), duracion, latencia,
                _iso(revisada), "ejemplo" if revisada else None,
                _iso(atendida), "ejemplo" if atendida else None,
            ),
        )
    db.conn.commit()
    return db


def simular_alerta(db: Almacen) -> int:
    """Agrega una alerta nueva de ejemplo, rotando entre los tipos."""
    total = len(db.listar(None))
    camara, tipo, mensaje, duracion, latencia = SIMULADAS[total % len(SIMULADAS)]
    return db.guardar(camara, tipo, mensaje, _imagenes()[tipo], duracion, latencia)
