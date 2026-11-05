"""Descripción opcional de cada alerta con un modelo de visión (GPT, por la API de OpenAI).

Después de que la alerta ya se generó y se mostró, se envía la foto de
evidencia (con los rostros difuminados) a un modelo de visión, que responde
con una frase objetiva y si la imagen respalda la alerta. La descripción se
agrega a la alerta en el dashboard y, si está activo, en Telegram.

Reglas de uso responsable:
- La IA **nunca** decide ni retrasa la alerta: solo agrega contexto.
- Se difuminan las caras (zona de la cabeza de cada persona) antes de enviar la imagen.
- Se le pide no identificar personas ni describir rasgos físicos.

Configuración: variable de entorno OPENAI_API_KEY (necesita saldo en
platform.openai.com; ChatGPT Plus no incluye la API) y en config.yaml:
    ia:
      activa: true
      modelo: "<un modelo con visión de https://platform.openai.com/docs/models>"
"""

from __future__ import annotations

import base64
import os
import queue
import threading

import requests

from almacen import Almacen

URL_OPENAI = "https://api.openai.com/v1/responses"

INSTRUCCIONES = (
    "Eres un asistente de un operador de seguridad universitaria. El sistema automático "
    "generó esta alerta: «{mensaje}». Mira la imagen y responde en español, en una sola "
    "frase objetiva de máximo 25 palabras, qué se observa que sea relevante para la alerta. "
    "No identifiques a nadie ni describas rasgos físicos, género, edad, etnia o ropa. "
    "Termina con «Coincide: sí», «Coincide: no» o «Coincide: incierto», según si la "
    "imagen respalda la alerta."
)


def regiones_de_cabeza(cajas_personas) -> list[tuple[float, float, float, float]]:
    """Zona aproximada de la cabeza de cada persona detectada por YOLO.
    De pie: el 25 % superior de la caja. Acostada: ambos extremos (no sabemos de qué lado está)."""
    regiones = []
    for x1, y1, x2, y2 in cajas_personas:
        w, h = x2 - x1, y2 - y1
        if h >= w:
            regiones.append((x1, y1, x2, y1 + 0.25 * h))
        else:
            regiones += [(x1, y1, x1 + 0.25 * w, y2), (x2 - 0.25 * w, y1, x2, y2)]
    return regiones


def difuminar_rostros(imagen_bgr, cajas_personas=()):
    """Devuelve una copia con las caras difuminadas antes de enviarla a la IA.

    Usa la zona de la cabeza de cada persona que detectó YOLO y, si la versión de
    OpenCV lo incluye (4.x), también el detector de rostros Haar.
    """
    import cv2

    salida = imagen_bgr.copy()
    regiones = regiones_de_cabeza(cajas_personas)
    if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data"):
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        gris = cv2.cvtColor(salida, cv2.COLOR_BGR2GRAY)
        for x, y, w, h in detector.detectMultiScale(gris, scaleFactor=1.1, minNeighbors=5, minSize=(24, 24)):
            m = 0.15 * w  # un margen para cubrir bien la cara
            regiones.append((x - m, y - m, x + w + m, y + h + m))
    alto, ancho = salida.shape[:2]
    for x1, y1, x2, y2 in regiones:
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(ancho, int(x2)), min(alto, int(y2))
        if x2 - x1 < 2 or y2 - y1 < 2:
            continue
        k = max(15, ((x2 - x1) // 3) | 1)
        salida[y1:y2, x1:x2] = cv2.GaussianBlur(salida[y1:y2, x1:x2], (k, k), 0)
    return salida


def extraer_texto(respuesta: dict) -> str:
    """Saca el texto de la respuesta de la API de Responses de OpenAI."""
    if respuesta.get("output_text"):
        return respuesta["output_text"].strip()
    partes = []
    for item in respuesta.get("output", []):
        for contenido in item.get("content", []) or []:
            if contenido.get("type") == "output_text":
                partes.append(contenido.get("text", ""))
    return " ".join(partes).strip()


def configuracion_ia(cfg: dict) -> tuple[str | None, str | None]:
    """Devuelve (api_key, modelo) si la IA está activa y bien configurada; si no, (None, motivo)."""
    ia = cfg.get("ia") or {}
    if not ia.get("activa"):
        return None, "desactivada en config.yaml"
    clave = os.environ.get("OPENAI_API_KEY")
    if not clave:
        return None, "falta la variable OPENAI_API_KEY"
    if not ia.get("modelo"):
        return None, "falta ia.modelo en config.yaml"
    return clave, ia["modelo"]


class DescriptorIA:
    def __init__(self, api_key: str, modelo: str, almacen: Almacen, al_describir=None,
                 url: str = URL_OPENAI, sesion=None):
        self.api_key = api_key
        self.modelo = modelo
        self.almacen = almacen
        self.al_describir = al_describir  # función(alerta_id, texto), por ejemplo para Telegram
        self.url = url
        self.http = sesion or requests.Session()
        self._cola: queue.Queue = queue.Queue()
        self._activo = False

    def iniciar(self) -> None:
        self._activo = True
        threading.Thread(target=self._trabajar, daemon=True).start()

    def detener(self) -> None:
        self._activo = False

    def describir_async(self, alerta_id: int, mensaje: str, imagen: str, cajas_personas=()) -> None:
        self._cola.put((alerta_id, mensaje, imagen, list(cajas_personas)))

    def _trabajar(self) -> None:
        while self._activo:
            try:
                alerta_id, mensaje, imagen, cajas = self._cola.get(timeout=1)
            except queue.Empty:
                continue
            try:
                texto = self.describir(mensaje, imagen, cajas)
            except Exception as e:  # la IA es un extra: si falla, la demo sigue
                print(f"[IA] No se pudo describir la alerta #{alerta_id}: {e}")
                continue
            if texto:
                self.almacen.guardar_descripcion(alerta_id, texto)
                print(f"[IA] Alerta #{alerta_id}: {texto}")
                if self.al_describir:
                    self.al_describir(alerta_id, texto)

    def describir(self, mensaje: str, imagen: str, cajas_personas=()) -> str:
        import cv2

        foto = cv2.imread(imagen)
        if foto is None:
            raise ValueError(f"No se pudo leer {imagen}")
        foto = difuminar_rostros(foto, cajas_personas)
        alto, ancho = foto.shape[:2]
        if ancho > 1024:  # imágenes más chicas = respuesta más rápida y barata
            foto = cv2.resize(foto, (1024, int(alto * 1024 / ancho)))
        ok, jpg = cv2.imencode(".jpg", foto, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ok:
            raise ValueError("No se pudo codificar la imagen")
        b64 = base64.b64encode(jpg.tobytes()).decode()
        cuerpo = {
            "model": self.modelo,
            "input": [{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": INSTRUCCIONES.format(mensaje=mensaje)},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"},
                ],
            }],
            "max_output_tokens": 400,
        }
        r = self.http.post(self.url, json=cuerpo, timeout=30,
                           headers={"Authorization": f"Bearer {self.api_key}"})
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
        return extraer_texto(r.json())
