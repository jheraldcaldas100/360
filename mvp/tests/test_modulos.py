"""Pruebas del registro de alertas, Telegram (simulado), evaluación y experimento."""

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from almacen import Almacen, segundos_entre  # noqa: E402
from analizador import fusionar  # noqa: E402
from evaluar import AlertaVideo, Evento, emparejar, leer_etiquetas, resumir, tabla_markdown  # noqa: E402
from experimento import calcular_resultado, resumir as resumir_experimento  # noqa: E402
from notificador import Telegram, botones_para  # noqa: E402
from reglas import Deteccion, Motor  # noqa: E402

# ------------------------------------------------------------------ almacén


def test_flujo_de_estados(tmp_path):
    db = Almacen(tmp_path / "a.db")
    i = db.guardar("Cam", "aglomeracion", "msg", None, duracion_s=5.2, latencia_ms=80)
    fila = db.obtener(i)
    assert fila["estado"] == "nueva" and fila["duracion_s"] == 5.2 and fila["inicio_situacion"]
    assert not db.cambiar_estado(i, "atendida")  # no se puede atender sin confirmar
    assert db.cambiar_estado(i, "confirmada", por="Ana")
    assert not db.cambiar_estado(i, "descartada")  # ya fue revisada
    assert db.cambiar_estado(i, "atendida", por="Luis")
    fila = db.obtener(i)
    assert fila["estado"] == "atendida" and fila["revisado_por"] == "Ana"
    assert fila["atendido_por"] == "Luis" and fila["atendida"]
    assert db.contar_por_estado()["atendida"] == 1


def test_migra_una_base_antigua(tmp_path):
    ruta = tmp_path / "vieja.db"
    con = sqlite3.connect(ruta)
    con.execute("CREATE TABLE alertas (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL,"
                " camara TEXT NOT NULL, tipo TEXT NOT NULL, mensaje TEXT NOT NULL, imagen TEXT,"
                " estado TEXT NOT NULL DEFAULT 'nueva', revisada TEXT)")
    con.execute("INSERT INTO alertas (fecha, camara, tipo, mensaje) VALUES ('2026-01-01T10:00:00', 'c', 't', 'm')")
    con.commit()
    con.close()
    db = Almacen(ruta)
    assert db.cambiar_estado(1, "confirmada")
    assert db.obtener(1)["revisado_por"] == "dashboard"


def test_segundos_entre_tolera_valores_vacios():
    assert segundos_entre("2026-01-01T10:00:00.000", "2026-01-01T10:00:04.500") == 4.5
    assert segundos_entre("2026-01-01T10:00:00", None) is None
    assert segundos_entre("2026-01-01T10:00:00", float("nan")) is None


# ---------------------------------------------------------- ajustes en vivo


def test_ajustar_parametros_conserva_el_conteo():
    motor = Motor.desde_config({"aglomeracion": {"personas_min": 3, "segundos": 10}})
    gente = [Deteccion("person", 0.9, (100 * i, 0, 100 * i + 50, 200)) for i in range(4)]
    for k in range(30):  # 6 s
        motor.evaluar(gente, 1280, 720, k * 0.2)
    regla = motor.reglas[0]
    motor.aplicar_config({"aglomeracion": {"personas_min": 3, "segundos": 5}})
    assert motor.reglas[0] is regla  # misma instancia: no perdió los 6 s acumulados
    alertas, _ = motor.evaluar(gente, 1280, 720, 6.2)
    assert len(alertas) == 1 and alertas[0].duracion >= 5


def test_activar_y_desactivar_reglas():
    motor = Motor.desde_config({"aglomeracion": {}, "zona_restringida": {"activa": False}})
    assert [r.tipo for r in motor.reglas] == ["aglomeracion"]
    motor.aplicar_config({"aglomeracion": {"activa": False}, "zona_restringida": {"activa": True}})
    assert [r.tipo for r in motor.reglas] == ["zona_restringida"]


def test_fusionar_config():
    base = {"confianza": 0.4, "reglas": {"aglomeracion": {"personas_min": 3, "segundos": 5}}}
    r = fusionar(base, {"reglas": {"aglomeracion": {"segundos": 9}}})
    assert r["reglas"]["aglomeracion"] == {"personas_min": 3, "segundos": 9}
    assert base["reglas"]["aglomeracion"]["segundos"] == 5  # no modifica el original


# ---------------------------------------------------------------- telegram


class SesionFalsa:
    def __init__(self):
        self.llamadas = []

    def post(self, url, data=None, files=None, timeout=None):
        self.llamadas.append((url.rsplit("/", 1)[-1], data))

        class R:
            ok = True

            def raise_for_status(self):
                pass

        return R()


def _boton(data, chat=123):
    return {"id": "cb1", "data": data, "from": {"first_name": "Ana"},
            "message": {"message_id": 7, "chat": {"id": chat}, "caption": "🚨 Alerta"}}


def test_telegram_confirmar_y_atender(tmp_path):
    db = Almacen(tmp_path / "a.db")
    i = db.guardar("Cam", "persona_en_suelo", "msg", None)
    sesion = SesionFalsa()
    tg = Telegram("TOKEN", "123", db, sesion=sesion)

    assert "Confirmada por Ana" in tg.procesar_boton(_boton(f"ok:{i}"))
    assert db.obtener(i)["estado"] == "confirmada"
    assert db.obtener(i)["revisado_por"] == "Telegram: Ana"
    edicion = next(d for m, d in sesion.llamadas if m == "editMessageCaption")
    assert json.loads(edicion["reply_markup"]) == botones_para("confirmada", i)

    assert "Atendida" in tg.procesar_boton(_boton(f"at:{i}"))
    assert db.obtener(i)["estado"] == "atendida"


def test_telegram_ignora_otros_chats_y_alertas_ya_revisadas(tmp_path):
    db = Almacen(tmp_path / "a.db")
    i = db.guardar("Cam", "aglomeracion", "msg", None)
    tg = Telegram("TOKEN", "123", db, sesion=SesionFalsa())
    assert tg.procesar_boton(_boton(f"ok:{i}", chat=999)) == "Chat no autorizado"
    assert db.obtener(i)["estado"] == "nueva"
    db.cambiar_estado(i, "descartada")
    assert "ya está descartada" in tg.procesar_boton(_boton(f"ok:{i}"))


def test_telegram_envia_foto_con_botones(tmp_path):
    db = Almacen(tmp_path / "a.db")
    foto = tmp_path / "f.jpg"
    foto.write_bytes(b"jpg")
    sesion = SesionFalsa()
    Telegram("TOKEN", "123", db, sesion=sesion).enviar_ahora(5, "aglomeracion", "msg", "Cam", str(foto))
    metodo, datos = sesion.llamadas[0]
    assert metodo == "sendPhoto" and datos["chat_id"] == "123"
    assert json.loads(datos["reply_markup"]) == botones_para("nueva", 5)


# ---------------------------------------------------------------- evaluación


def test_leer_etiquetas_y_emparejar(tmp_path):
    csv_ = tmp_path / "e.csv"
    csv_.write_text("video,tipo,inicio_s,fin_s\nv1.mp4,aglomeracion,2,10\n"
                    "v1.mp4,persona_en_suelo,20,30\nv2.mp4,,,\n", encoding="utf-8")
    videos, eventos = leer_etiquetas(csv_)
    assert videos == ["v1.mp4", "v2.mp4"] and len(eventos) == 2
    alertas = [
        AlertaVideo("v1.mp4", "aglomeracion", 7.0),   # acierto
        AlertaVideo("v1.mp4", "aglomeracion", 8.0),   # duplicada: falsa alarma
        AlertaVideo("v2.mp4", "persona_en_suelo", 3), # en un video sin eventos: falsa alarma
        AlertaVideo("v1.mp4", "persona_en_suelo", 40),  # demasiado tarde (fin 30 + tolerancia 5)
    ]
    emparejar(eventos, alertas, tolerancia=5)
    filas = {f["situacion"]: f for f in resumir(eventos, alertas, 3600, {"aglomeracion": 5})}
    assert filas["Aglomeración"]["detectados"] == 1
    assert filas["Aglomeración"]["tiempo_medio_alerta_s"] == 5.0
    assert filas["Aglomeración"]["falsas_alarmas"] == 1
    assert filas["Persona en el suelo"]["omitidos"] == 1
    assert filas["Persona en el suelo"]["falsas_alarmas"] == 2
    assert "| Aglomeración | 1 | 1 | 0 | 100 % | 1 | 5.0 s | 5 s |" in tabla_markdown(list(filas.values()))


# --------------------------------------------------------------- experimento


def test_resultado_de_un_participante():
    assert calcular_resultado([3.0, 26.5, 30], evento=25) == {
        "detecto": True, "reaccion_s": 1.5, "avisos_falsos": 1}
    assert calcular_resultado([], evento=25)["detecto"] is False


def test_resumen_del_experimento(tmp_path):
    ruta = tmp_path / "r.csv"
    ruta.write_text("participante,video,evento_s,detecto,reaccion_s,avisos_falsos\n"
                    "Ana,m.mp4,25,si,12.0,0\nLuis,m.mp4,25,si,30.0,1\nEva,m.mp4,25,no,,0\n",
                    encoding="utf-8")
    texto = resumir_experimento(ruta, sistema=20.0)
    assert "No la detectaron: 1 de 3" in texto
    assert "más rápido que 1 de las 2" in texto
