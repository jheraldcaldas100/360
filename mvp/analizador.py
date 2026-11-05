"""Análisis de un fotograma: YOLO detecta y las reglas deciden.

Lo usan detector.py (en vivo) y evaluar.py (videos etiquetados), para que la
demo y la medición usen exactamente la misma lógica.
"""

from __future__ import annotations

import copy
from pathlib import Path

import yaml

from reglas import Deteccion, Motor

CLASES_DE_INTERES = {"person", "backpack", "handbag", "suitcase"}


def cargar_yaml(ruta: str | Path) -> dict:
    return yaml.safe_load(Path(ruta).read_text(encoding="utf-8")) or {}


def fusionar(base: dict, cambios: dict) -> dict:
    """Combina dos configuraciones; los valores de `cambios` ganan (también en subniveles)."""
    resultado = copy.deepcopy(base)
    for clave, valor in (cambios or {}).items():
        if isinstance(valor, dict) and isinstance(resultado.get(clave), dict):
            resultado[clave] = fusionar(resultado[clave], valor)
        else:
            resultado[clave] = copy.deepcopy(valor)
    return resultado


class Analizador:
    def __init__(self, cfg: dict, modelo=None):
        if modelo is None:
            from ultralytics import YOLO  # import diferido: las pruebas no necesitan el modelo

            modelo = YOLO(cfg.get("modelo", "yolo11n.pt"))
        self.modelo = modelo
        self.clases = [i for i, n in modelo.names.items() if n in CLASES_DE_INTERES]
        self.cfg = cfg
        self.motor = Motor.desde_config(cfg["reglas"])

    def aplicar_config(self, cfg: dict) -> None:
        """Aplica parámetros nuevos sin reiniciar el estado de las reglas."""
        self.cfg = cfg
        self.motor.aplicar_config(cfg["reglas"])

    def reiniciar_reglas(self) -> None:
        self.motor = Motor.desde_config(self.cfg["reglas"])

    def detectar(self, frame) -> list[Deteccion]:
        resultado = self.modelo.predict(
            frame,
            conf=float(self.cfg.get("confianza", 0.4)),
            imgsz=int(self.cfg.get("tamano_imagen", 640)),
            classes=self.clases,
            verbose=False,
        )[0]
        return [
            Deteccion(self.modelo.names[int(c)], float(p), tuple(map(float, caja)))
            for caja, c, p in zip(
                resultado.boxes.xyxy.tolist(),
                resultado.boxes.cls.tolist(),
                resultado.boxes.conf.tolist(),
            )
        ]

    def procesar(self, frame, ahora: float):
        detecciones = self.detectar(frame)
        alto, ancho = frame.shape[:2]
        alertas, estados = self.motor.evaluar(detecciones, ancho, alto, ahora)
        return detecciones, alertas, estados
