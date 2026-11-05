"""Pruebas de las reglas con detecciones simuladas (no necesitan cámara ni modelo)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reglas import (  # noqa: E402
    Deteccion,
    Motor,
    ReglaAglomeracion,
    ReglaObjetoDesatendido,
    ReglaPersonaEnSuelo,
    ReglaZonaRestringida,
    Temporizador,
)

ANCHO, ALTO = 1280, 720


def persona(x1, y1, x2, y2):
    return Deteccion("person", 0.9, (x1, y1, x2, y2))


def mochila(x1, y1, x2, y2):
    return Deteccion("backpack", 0.8, (x1, y1, x2, y2))


def correr(regla, cuadros, fps=5):
    """`cuadros` = lista de (segundos, personas, objetos). Devuelve las alertas generadas.

    El reloj simulado continúa entre llamadas sucesivas sobre la misma regla.
    """
    alertas, t = [], getattr(regla, "_reloj_prueba", 0.0)
    for segundos, personas, objetos in cuadros:
        for _ in range(round(segundos * fps)):
            a, _ = regla.evaluar(personas, objetos, ANCHO, ALTO, t)
            alertas += a
            t += 1 / fps
    regla._reloj_prueba = t
    return alertas


# --------------------------------------------------------------- temporizador


def test_temporizador_tolera_cortes_breves():
    t = Temporizador(tolerancia_s=1.0)
    t.actualizar(True, 0)
    t.actualizar(True, 5)
    t.actualizar(False, 5.5)  # corte breve: no reinicia
    assert t.actualizar(True, 6) == 6
    t.actualizar(False, 7.5)  # corte largo: reinicia
    assert not t.activo


# ---------------------------------------------------------------- aglomeración


def gente(n):
    return [persona(100 * i, 100, 100 * i + 80, 400) for i in range(n)]


def test_aglomeracion_alerta_tras_el_tiempo():
    regla = ReglaAglomeracion(personas_min=3, segundos=5)
    assert correr(regla, [(4, gente(3), [])]) == []
    alertas = correr(regla, [(2, gente(4), [])])
    assert len(alertas) == 1 and alertas[0].tipo == "aglomeracion"


def test_aglomeracion_no_alerta_con_pocas_personas():
    regla = ReglaAglomeracion(personas_min=3, segundos=5)
    assert correr(regla, [(30, gente(2), [])]) == []


def test_aglomeracion_una_alerta_por_episodio_y_rearma():
    regla = ReglaAglomeracion(personas_min=3, segundos=5)
    alertas = correr(regla, [(20, gente(5), []), (5, gente(1), []), (7, gente(5), [])])
    assert len(alertas) == 2


# ---------------------------------------------------------- objeto desatendido

MOCHILA = mochila(600, 500, 660, 580)
DUENO = persona(560, 250, 700, 600)  # sentado junto a la mochila
LEJOS = persona(50, 100, 150, 400)


def test_objeto_con_dueno_no_alerta():
    regla = ReglaObjetoDesatendido(segundos=20)
    assert correr(regla, [(60, [DUENO], [MOCHILA])]) == []


def test_objeto_sin_nadie_alerta_tras_el_tiempo():
    regla = ReglaObjetoDesatendido(segundos=20)
    alertas = correr(regla, [(5, [DUENO], [MOCHILA]), (19, [LEJOS], [MOCHILA])])
    assert alertas == []
    alertas = correr(regla, [(3, [LEJOS], [MOCHILA])])
    assert len(alertas) == 1 and alertas[0].tipo == "objeto_desatendido"


def test_paso_breve_de_alguien_no_reinicia_el_conteo():
    regla = ReglaObjetoDesatendido(segundos=20, segundos_para_reiniciar=3)
    alertas = correr(
        regla, [(12, [], [MOCHILA]), (1, [DUENO], [MOCHILA]), (10, [], [MOCHILA])]
    )
    assert len(alertas) == 1


def test_si_el_dueno_vuelve_se_reinicia_el_conteo():
    regla = ReglaObjetoDesatendido(segundos=20, segundos_para_reiniciar=3)
    alertas = correr(
        regla, [(15, [], [MOCHILA]), (5, [DUENO], [MOCHILA]), (15, [], [MOCHILA])]
    )
    assert alertas == []


def test_objeto_movido_reinicia_el_conteo():
    regla = ReglaObjetoDesatendido(segundos=20)
    otra_posicion = mochila(640, 500, 700, 580)  # se solapa, pero se movió
    alertas = correr(regla, [(15, [], [MOCHILA]), (15, [], [otra_posicion])])
    assert alertas == []


# -------------------------------------------------------------- persona suelo

DE_PIE = persona(500, 100, 600, 500)
TENDIDA = persona(400, 450, 750, 560)
PRIMER_PLANO = persona(200, 300, 1000, 720)  # muy cerca del celular: toca el borde inferior


def test_persona_tendida_alerta_tras_el_tiempo():
    regla = ReglaPersonaEnSuelo(segundos=5)
    assert correr(regla, [(10, [DE_PIE], [])]) == []
    alertas = correr(regla, [(6, [TENDIDA], [])])
    assert len(alertas) == 1 and alertas[0].tipo == "persona_en_suelo"


def test_persona_que_se_levanta_rapido_no_alerta():
    regla = ReglaPersonaEnSuelo(segundos=5)
    assert correr(regla, [(3, [TENDIDA], []), (5, [DE_PIE], [])]) == []


def test_persona_en_primer_plano_no_cuenta_como_tendida():
    regla = ReglaPersonaEnSuelo(segundos=5)
    assert correr(regla, [(10, [PRIMER_PLANO], [])]) == []


# ------------------------------------------------------------ zona restringida


def test_zona_restringida():
    regla = ReglaZonaRestringida(zona=(0.5, 0, 1, 1), segundos=2)
    afuera = persona(100, 100, 200, 500)
    adentro = persona(900, 100, 1000, 500)
    assert correr(regla, [(10, [afuera], [])]) == []
    assert len(correr(regla, [(3, [adentro], [])])) == 1


# --------------------------------------------------------------------- motor


def test_motor_desde_config_respeta_reglas_inactivas():
    motor = Motor.desde_config(
        {
            "aglomeracion": {"activa": True, "personas_min": 2, "segundos": 1},
            "zona_restringida": {"activa": False},
        }
    )
    assert [r.tipo for r in motor.reglas] == ["aglomeracion"]
    alertas = []
    for i in range(10):
        a, _ = motor.evaluar(gente(3), ANCHO, ALTO, i * 0.2)
        alertas += a
    assert len(alertas) == 1


def test_configs_del_repositorio_son_validas():
    import yaml

    for nombre in ("config.yaml", "config_real.yaml"):
        cfg = yaml.safe_load((Path(__file__).resolve().parents[1] / nombre).read_text("utf-8"))
        Motor.desde_config(cfg["reglas"])
