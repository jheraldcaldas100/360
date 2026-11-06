"""Mapa del campus con la ubicación de cada cámara y sus alertas pendientes.

Si no hay un plano configurado, se dibuja un plano de ejemplo. Para usar el
plano real basta una captura de Google Maps o un croquis en PNG/JPG, y
ubicar cada cámara con proporciones (x, y) entre 0 y 1 en config.yaml.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ANCHO, ALTO = 900, 560
VERDE, ROJO = (40, 160, 90), (220, 40, 40)


def _fuente(tam: int):
    for nombre in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(nombre, tam)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=tam)  # Pillow 10.1 o superior
    except TypeError:
        return ImageFont.load_default()


def plano_de_ejemplo() -> Image.Image:
    img = Image.new("RGB", (ANCHO, ALTO), (236, 240, 232))
    d = ImageDraw.Draw(img)
    f = _fuente(18)
    edificios = [
        ((40, 40, 300, 200), "Biblioteca"),
        ((340, 40, 860, 160), "Pabellón A (aulas)"),
        ((40, 360, 260, 520), "Comedor"),
        ((620, 300, 860, 520), "Pabellón B (laboratorios)"),
        ((300, 420, 560, 520), "Ingreso principal"),
    ]
    d.rectangle((300, 200, 580, 400), fill=(214, 228, 200), outline=(170, 190, 160))
    d.text((310, 210), "Patio central", fill=(90, 110, 80), font=f)
    for caja, nombre in edificios:
        d.rectangle(caja, fill=(205, 210, 220), outline=(130, 135, 150), width=2)
        d.text((caja[0] + 10, caja[1] + 10), nombre, fill=(60, 65, 80), font=f)
    d.text((10, ALTO - 22), "Plano de ejemplo",
           fill=(120, 120, 120), font=_fuente(12))
    return img


def dibujar_mapa(cfg_mapa: dict | None, pendientes: dict[str, int], base_dir: Path | None = None) -> Image.Image:
    """Dibuja las cámaras sobre el plano: verde sin pendientes, rojo con el número de pendientes."""
    cfg_mapa = cfg_mapa or {}
    img = None
    ruta = cfg_mapa.get("imagen")
    if ruta:
        ruta = Path(ruta)
        if not ruta.is_absolute() and base_dir:
            ruta = base_dir / ruta
        if ruta.exists():
            img = Image.open(ruta).convert("RGB")
            if img.width > 1200:
                img = img.resize((1200, int(img.height * 1200 / img.width)))
    if img is None:
        img = plano_de_ejemplo()

    d = ImageDraw.Draw(img)
    radio = max(14, img.width // 45)
    f_num, f_nom = _fuente(radio), _fuente(max(16, radio))
    for nombre, pos in (cfg_mapa.get("camaras") or {}).items():
        x, y = float(pos[0]) * img.width, float(pos[1]) * img.height
        n = pendientes.get(nombre, 0)
        color = ROJO if n else VERDE
        if n:  # halo para que se note la alerta
            d.ellipse((x - radio * 2, y - radio * 2, x + radio * 2, y + radio * 2),
                      outline=ROJO, width=3)
        d.ellipse((x - radio, y - radio, x + radio, y + radio), fill=color, outline="white", width=3)
        d.text((x, y), str(n) if n else "", fill="white", font=f_num, anchor="mm")
        etiqueta = f"{nombre}" + (f" · {n} pendiente{'s' if n > 1 else ''}" if n else "")
        caja = d.textbbox((x + radio + 6, y), etiqueta, font=f_nom, anchor="lm")
        d.rectangle((caja[0] - 4, caja[1] - 3, caja[2] + 4, caja[3] + 3), fill=(255, 255, 255))
        d.text((x + radio + 6, y), etiqueta, fill=color, font=f_nom, anchor="lm")
    return img
