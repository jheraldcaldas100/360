"""Pruebas del mapa, la descripción con IA (API simulada) y el difuminado de rostros."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from almacen import Almacen  # noqa: E402
from ia import configuracion_ia, extraer_texto  # noqa: E402

PIL = pytest.importorskip("PIL")
from mapa import ROJO, VERDE, dibujar_mapa  # noqa: E402


def test_extraer_texto_de_la_respuesta():
    respuesta = {"output": [
        {"type": "reasoning", "content": []},
        {"type": "message", "content": [{"type": "output_text", "text": "Mochila sola. Coincide: sí"}]},
    ]}
    assert extraer_texto(respuesta) == "Mochila sola. Coincide: sí"
    assert extraer_texto({"output_text": " Hola "}) == "Hola"


def test_configuracion_ia(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert configuracion_ia({}) == (None, "desactivada en config.yaml")
    assert configuracion_ia({"ia": {"activa": True, "modelo": "m"}})[0] is None
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    assert configuracion_ia({"ia": {"activa": True, "modelo": ""}}) == (None, "falta ia.modelo en config.yaml")
    assert configuracion_ia({"ia": {"activa": True, "modelo": "m"}}) == ("k", "m")


def test_mapa_marca_en_rojo_las_camaras_con_pendientes():
    cfg = {"camaras": {"A": [0.25, 0.5], "B": [0.75, 0.5]}}
    img = dibujar_mapa(cfg, {"A": 2})
    assert img.getpixel((int(0.25 * img.width) + 8, int(0.5 * img.height))) == ROJO
    assert img.getpixel((int(0.75 * img.width) + 8, int(0.5 * img.height))) == VERDE


def test_mapa_usa_un_plano_propio(tmp_path):
    from PIL import Image

    Image.new("RGB", (400, 300), (0, 0, 255)).save(tmp_path / "plano.png")
    img = dibujar_mapa({"imagen": "plano.png", "camaras": {}}, {}, tmp_path)
    assert img.size == (400, 300) and img.getpixel((5, 5)) == (0, 0, 255)


cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")


class RespuestaFalsa:
    status_code = 200

    def json(self):
        return {"output": [{"type": "message", "content": [
            {"type": "output_text", "text": "Persona tendida en el piso. Coincide: sí"}]}]}


class SesionFalsa:
    def __init__(self):
        self.cuerpo = None

    def post(self, url, json=None, timeout=None, headers=None):
        self.cuerpo, self.headers = json, headers
        return RespuestaFalsa()


def test_descriptor_envia_imagen_y_guarda_texto(tmp_path):
    from ia import DescriptorIA

    foto = tmp_path / "f.jpg"
    cv2.imwrite(str(foto), np.full((720, 1280, 3), 128, np.uint8))
    db = Almacen(tmp_path / "a.db")
    i = db.guardar("Cam", "persona_en_suelo", "Persona en el suelo 5 s", str(foto))
    sesion, avisos = SesionFalsa(), []
    d = DescriptorIA("clave", "modelo-x", db, al_describir=lambda a, t: avisos.append((a, t)), sesion=sesion)
    texto = d.describir("Persona en el suelo 5 s", str(foto))
    assert texto.endswith("Coincide: sí")
    contenido = sesion.cuerpo["input"][0]["content"]
    assert sesion.cuerpo["model"] == "modelo-x" and sesion.headers["Authorization"] == "Bearer clave"
    assert contenido[1]["image_url"].startswith("data:image/jpeg;base64,")
    assert "No identifiques" in contenido[0]["text"]
    # Lo que hace el hilo de trabajo con cada alerta: describir y guardar.
    db.guardar_descripcion(i, d.describir("msg", str(foto), [(100, 100, 300, 600)]))
    assert db.obtener(i)["descripcion_ia"].startswith("Persona tendida")


def test_difuminar_cabezas_de_personas_detectadas():
    from ia import difuminar_rostros, regiones_de_cabeza

    rng = np.random.default_rng(0)
    img = rng.integers(0, 255, (720, 1280, 3), dtype=np.uint8)
    de_pie, acostada = (100, 100, 300, 600), (500, 400, 1100, 600)
    assert regiones_de_cabeza([de_pie]) == [(100, 100, 300, 225.0)]
    assert len(regiones_de_cabeza([acostada])) == 2  # ambos extremos
    salida = difuminar_rostros(img, [de_pie, acostada])
    cambio = cv2.absdiff(img, salida).sum(axis=2) > 0
    assert cambio[100:225, 100:300].mean() > 0.9  # cabeza de la persona de pie
    assert not cambio[300:600, 100:300].any()  # el cuerpo queda igual
    assert cambio[400:600, 500:650].mean() > 0.9 and cambio[400:600, 950:1100].mean() > 0.9
    assert not cambio[400:600, 700:900].any()  # el centro de la persona acostada queda igual


def test_difuminar_sin_rostros_no_cambia_nada():
    from ia import difuminar_rostros

    img = np.full((200, 300, 3), 90, np.uint8)
    assert (difuminar_rostros(img) == img).all()
