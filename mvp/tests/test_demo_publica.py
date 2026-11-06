"""Pruebas de la demo pública: datos de ejemplo aislados y dashboard sin cámara."""

import os
import sys
from pathlib import Path

import pytest

MVP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MVP))

pytest.importorskip("PIL")
pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

import datos_demo  # noqa: E402


def test_cada_visitante_tiene_su_propia_base():
    a, b = datos_demo.crear_almacen(), datos_demo.crear_almacen()
    nueva = next(f for f in a.listar(None) if f["estado"] == "nueva")
    assert a.cambiar_estado(nueva["id"], "confirmada")
    assert b.obtener(nueva["id"])["estado"] == "nueva"


def test_los_datos_cubren_todos_los_estados_y_tipos():
    db = datos_demo.crear_almacen()
    assert all(n > 0 for n in db.contar_por_estado().values())
    assert {f["tipo"] for f in db.listar(None)} == {
        "aglomeracion", "objeto_desatendido", "persona_en_suelo", "zona_restringida"}


def test_las_alertas_guardan_tiempos_coherentes():
    for f in datos_demo.crear_almacen().listar(None):
        assert f["inicio_situacion"] < f["fecha"]
        assert f["revisada"] is None or f["fecha"] < f["revisada"]
        assert f["atendida"] is None or f["revisada"] < f["atendida"]


def test_simular_alerta_agrega_una_nueva_con_imagen():
    db = datos_demo.crear_almacen()
    antes = len(db.listar(None))
    alerta = db.obtener(datos_demo.simular_alerta(db))
    assert len(db.listar(None)) == antes + 1
    assert alerta["estado"] == "nueva"
    assert Path(alerta["imagen"]).exists()


def test_las_imagenes_quedan_fuera_del_repositorio():
    for ruta in datos_demo._imagenes().values():
        assert MVP not in Path(ruta).resolve().parents


@pytest.fixture
def app(monkeypatch):
    # app.py define estas variables; monkeypatch las restaura al terminar la prueba.
    monkeypatch.setenv("SAFECAMPUS_DEMO", "1")
    monkeypatch.setenv("TZ", os.environ.get("TZ", "UTC"))
    prueba = AppTest.from_file(str(MVP / "demo_publica" / "app.py"), default_timeout=30).run()
    assert not prueba.exception
    return prueba


def test_la_demo_avisa_que_usa_datos_de_ejemplo(app):
    avisos = " ".join(w.value for w in app.warning)
    assert "datos de ejemplo" in avisos
    assert "Cifras de ejemplo" in avisos


def test_la_demo_no_permite_cambiar_parametros(app):
    assert not any(b.label == "Aplicar cambios" for b in app.button)
    assert len(app.slider) == 0


def test_la_demo_muestra_los_parametros_de_forma_legible(app):
    assert len(app.json) == 0
    textos = " ".join(m.value for m in app.markdown)
    for esperado in ("Aglomeración", "Personas mínimas", "Objeto desatendido", "mochila",
                     "Persona en el suelo", "Zona restringida", "60% a 100%"):
        assert esperado in textos


def test_la_demo_no_escribe_en_la_carpeta_de_datos(app):
    assert app.session_state["almacen_demo"].conn.execute("PRAGMA database_list").fetchone()["file"] == ""


def test_simular_una_alerta_desde_el_panel(app):
    next(b for b in app.button if "Simular" in b.label).click()
    app.run()
    assert not app.exception
    assert app.metric[0].value == "3"
