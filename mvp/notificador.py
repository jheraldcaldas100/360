"""Alertas al celular del guardia por Telegram, con foto y botones.

El guardia puede confirmar, descartar y marcar como atendida cada alerta desde
el chat; el cambio se guarda en la misma base que usa el dashboard.

Configuración (variables de entorno o sección `telegram` de config.yaml):
    TELEGRAM_TOKEN    token del bot que entrega @BotFather
    TELEGRAM_CHAT_ID  chat o grupo donde llegan las alertas
"""

from __future__ import annotations

import json
import os
import queue
import threading
import time

import requests

from almacen import Almacen

NOMBRES = {
    "aglomeracion": "👥 Aglomeración",
    "objeto_desatendido": "🎒 Objeto desatendido",
    "persona_en_suelo": "🚑 Persona en el suelo",
    "zona_restringida": "⛔ Zona restringida",
}

# acción del botón -> (estado nuevo, texto que se agrega al mensaje)
ACCIONES = {
    "ok": ("confirmada", "✅ Confirmada"),
    "no": ("descartada", "⚪ Descartada"),
    "at": ("atendida", "🚓 Atendida"),
}


def botones_para(estado: str, alerta_id: int) -> dict:
    if estado == "nueva":
        return {"inline_keyboard": [[
            {"text": "✅ Confirmar", "callback_data": f"ok:{alerta_id}"},
            {"text": "❌ Descartar", "callback_data": f"no:{alerta_id}"},
        ]]}
    if estado == "confirmada":
        return {"inline_keyboard": [[
            {"text": "🚓 Marcar atendida", "callback_data": f"at:{alerta_id}"},
        ]]}
    return {"inline_keyboard": []}


def credenciales(cfg: dict) -> tuple[str | None, str | None]:
    tg = cfg.get("telegram") or {}
    token = os.environ.get("TELEGRAM_TOKEN") or tg.get("token") or None
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or tg.get("chat_id") or None
    return token, (str(chat_id) if chat_id else None)


class Telegram:
    def __init__(self, token: str, chat_id: str, almacen: Almacen,
                 api: str = "https://api.telegram.org", sesion=None):
        self.url = f"{api}/bot{token}"
        self.chat_id = str(chat_id)
        self.almacen = almacen
        self.http = sesion or requests.Session()
        self._cola: queue.Queue = queue.Queue()
        self._offset = 0
        self._activo = False

    # --------------------------------------------------------------- envío

    def iniciar(self) -> None:
        self._activo = True
        threading.Thread(target=self._enviar_pendientes, daemon=True).start()
        threading.Thread(target=self._escuchar, daemon=True).start()

    def detener(self) -> None:
        self._activo = False

    def enviar_alerta(self, alerta_id: int, tipo: str, mensaje: str, camara: str,
                      imagen: str | None) -> None:
        """Encola el envío para no frenar el análisis del video si la red está lenta."""
        self._cola.put((alerta_id, tipo, mensaje, camara, imagen))

    def _enviar_pendientes(self) -> None:
        while self._activo:
            try:
                alerta = self._cola.get(timeout=1)
            except queue.Empty:
                continue
            for intento in range(3):
                try:
                    self.enviar_ahora(*alerta)
                    break
                except requests.RequestException as e:
                    print(f"[Telegram] Error al enviar (intento {intento + 1}): {e}")
                    time.sleep(2)

    def enviar_ahora(self, alerta_id, tipo, mensaje, camara, imagen) -> None:
        texto = f"🚨 *{NOMBRES.get(tipo, tipo)}*\n{camara} · Alerta #{alerta_id}\n{mensaje}"
        datos = {
            "chat_id": self.chat_id,
            "caption": texto,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(botones_para("nueva", alerta_id)),
        }
        if imagen and os.path.exists(imagen):
            with open(imagen, "rb") as f:
                r = self.http.post(f"{self.url}/sendPhoto", data=datos, files={"photo": f}, timeout=15)
        else:
            datos["text"] = datos.pop("caption")
            r = self.http.post(f"{self.url}/sendMessage", data=datos, timeout=15)
        r.raise_for_status()

    # ------------------------------------------------------------ botones

    def _escuchar(self) -> None:
        while self._activo:
            try:
                r = self.http.get(
                    f"{self.url}/getUpdates",
                    params={"timeout": 20, "offset": self._offset,
                            "allowed_updates": json.dumps(["callback_query"])},
                    timeout=30,
                )
                r.raise_for_status()
                for update in r.json().get("result", []):
                    self._offset = update["update_id"] + 1
                    if "callback_query" in update:
                        self.procesar_boton(update["callback_query"])
            except requests.RequestException as e:
                print(f"[Telegram] Error al recibir respuestas: {e}")
                time.sleep(3)

    def procesar_boton(self, cq: dict) -> str:
        """Aplica la acción de un botón. Devuelve el texto de respuesta para el guardia."""
        mensaje = cq.get("message") or {}
        if str((mensaje.get("chat") or {}).get("id")) != self.chat_id:
            respuesta = "Chat no autorizado"  # solo el chat configurado puede cambiar alertas
        else:
            try:
                accion, alerta_id = cq.get("data", "").split(":")
                estado, etiqueta = ACCIONES[accion]
                alerta_id = int(alerta_id)
            except (ValueError, KeyError):
                accion, respuesta = None, "Acción no reconocida"
            else:
                quien = (cq.get("from") or {}).get("first_name", "guardia")
                if self.almacen.cambiar_estado(alerta_id, estado, por=f"Telegram: {quien}"):
                    respuesta = f"{etiqueta} por {quien}"
                    texto = (mensaje.get("caption") or mensaje.get("text") or "")
                    texto += f"\n{respuesta} a las {time.strftime('%H:%M:%S')}"
                    metodo = "editMessageCaption" if "caption" in mensaje else "editMessageText"
                    campo = "caption" if "caption" in mensaje else "text"
                    self._post(metodo, {
                        "chat_id": self.chat_id,
                        "message_id": mensaje.get("message_id"),
                        campo: texto,
                        "reply_markup": json.dumps(botones_para(estado, alerta_id)),
                    })
                else:
                    fila = self.almacen.obtener(alerta_id)
                    actual = fila["estado"] if fila else "inexistente"
                    respuesta = f"La alerta ya está {actual} (revisada en otro lugar)"
        self._post("answerCallbackQuery", {"callback_query_id": cq.get("id"), "text": respuesta})
        return respuesta

    def _post(self, metodo: str, datos: dict) -> None:
        try:
            self.http.post(f"{self.url}/{metodo}", data=datos, timeout=10)
        except requests.RequestException as e:
            print(f"[Telegram] Error en {metodo}: {e}")


def probar_conexion(token: str, chat_id: str) -> None:
    """Envía un mensaje de prueba. Uso: python notificador.py"""
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": "✅ Tres60 SafeCampus conectado. Aquí llegarán las alertas."},
        timeout=15,
    )
    print("Mensaje enviado." if r.ok else f"Error {r.status_code}: {r.text}")


if __name__ == "__main__":
    from pathlib import Path

    import yaml

    cfg = yaml.safe_load((Path(__file__).parent / "config.yaml").read_text(encoding="utf-8"))
    token, chat_id = credenciales(cfg)
    if not token or not chat_id:
        raise SystemExit("Falta TELEGRAM_TOKEN o TELEGRAM_CHAT_ID (ver README, sección Telegram).")
    probar_conexion(token, chat_id)
