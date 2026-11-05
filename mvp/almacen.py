"""Registro de alertas en SQLite (compartido por el detector, Telegram y el dashboard)."""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path

ESTADOS = ("nueva", "confirmada", "descartada", "atendida")

# Cambios de estado permitidos: el flujo del guardia.
TRANSICIONES = {
    "nueva": {"confirmada", "descartada"},
    "confirmada": {"atendida"},
}

COLUMNAS = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "fecha": "TEXT NOT NULL",  # cuándo se generó la alerta
    "camara": "TEXT NOT NULL",
    "tipo": "TEXT NOT NULL",
    "mensaje": "TEXT NOT NULL",
    "imagen": "TEXT",
    "estado": "TEXT NOT NULL DEFAULT 'nueva'",
    "inicio_situacion": "TEXT",  # cuándo empezó la situación (fecha - duracion_s)
    "duracion_s": "REAL",  # segundos desde el inicio de la situación hasta la alerta
    "latencia_ms": "REAL",  # milisegundos desde la captura del fotograma hasta la alerta
    "revisada": "TEXT",  # cuándo se confirmó o descartó
    "revisado_por": "TEXT",
    "atendida": "TEXT",  # cuándo se marcó como atendida
    "atendido_por": "TEXT",
    "descripcion_ia": "TEXT",  # descripción opcional generada por un modelo de visión
}


def ahora_iso() -> str:
    return datetime.now().isoformat(timespec="milliseconds")


def segundos_entre(inicio, fin) -> float | None:
    """Segundos entre dos fechas ISO; None si falta alguna (también acepta NaN de pandas)."""
    if not isinstance(inicio, str) or not isinstance(fin, str) or not inicio or not fin:
        return None
    return (datetime.fromisoformat(fin) - datetime.fromisoformat(inicio)).total_seconds()


class Almacen:
    def __init__(self, ruta: str | Path):
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()  # el detector y el hilo de Telegram comparten la conexión
        self.conn = sqlite3.connect(str(ruta), timeout=5, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        with self._lock:
            self.conn.execute("PRAGMA journal_mode=WAL")
            columnas = ", ".join(f"{n} {t}" for n, t in COLUMNAS.items())
            self.conn.execute(f"CREATE TABLE IF NOT EXISTS alertas ({columnas})")
            # Si la base es de una versión anterior, agregar las columnas que falten.
            existentes = {f["name"] for f in self.conn.execute("PRAGMA table_info(alertas)")}
            for nombre, tipo in COLUMNAS.items():
                if nombre not in existentes:
                    tipo = tipo.replace(" NOT NULL", "")
                    self.conn.execute(f"ALTER TABLE alertas ADD COLUMN {nombre} {tipo}")
            self.conn.commit()

    def guardar(self, camara: str, tipo: str, mensaje: str, imagen: str | None,
                duracion_s: float | None = None, latencia_ms: float | None = None) -> int:
        fecha = datetime.now()
        inicio = fecha - timedelta(seconds=duracion_s) if duracion_s is not None else None
        with self._lock:
            cur = self.conn.execute(
                "INSERT INTO alertas (fecha, camara, tipo, mensaje, imagen, inicio_situacion,"
                " duracion_s, latencia_ms) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    fecha.isoformat(timespec="milliseconds"), camara, tipo, mensaje, imagen,
                    inicio.isoformat(timespec="milliseconds") if inicio else None,
                    duracion_s, latencia_ms,
                ),
            )
            self.conn.commit()
            return cur.lastrowid

    def obtener(self, alerta_id: int) -> sqlite3.Row | None:
        with self._lock:
            return self.conn.execute("SELECT * FROM alertas WHERE id = ?", (alerta_id,)).fetchone()

    def listar(self, limite: int | None = 50) -> list[sqlite3.Row]:
        with self._lock:
            if limite is None:
                return self.conn.execute("SELECT * FROM alertas ORDER BY id DESC").fetchall()
            return self.conn.execute(
                "SELECT * FROM alertas ORDER BY id DESC LIMIT ?", (limite,)
            ).fetchall()

    def contar_por_estado(self) -> dict[str, int]:
        with self._lock:
            filas = self.conn.execute(
                "SELECT estado, COUNT(*) FROM alertas GROUP BY estado"
            ).fetchall()
        conteo = {e: 0 for e in ESTADOS}
        conteo.update({estado: n for estado, n in filas})
        return conteo

    def guardar_descripcion(self, alerta_id: int, texto: str) -> None:
        with self._lock:
            self.conn.execute("UPDATE alertas SET descripcion_ia = ? WHERE id = ?", (texto, alerta_id))
            self.conn.commit()

    def pendientes_por_camara(self) -> dict[str, int]:
        """Alertas nuevas o confirmadas sin atender, por cámara (para el mapa)."""
        with self._lock:
            filas = self.conn.execute(
                "SELECT camara, COUNT(*) FROM alertas WHERE estado IN ('nueva', 'confirmada')"
                " GROUP BY camara"
            ).fetchall()
        return {camara: n for camara, n in filas}

    def cambiar_estado(self, alerta_id: int, estado: str, por: str = "dashboard") -> bool:
        """Aplica un cambio de estado si el flujo lo permite. Devuelve False si no se pudo
        (por ejemplo, la alerta ya la revisó otra persona desde el dashboard o Telegram)."""
        if estado not in ESTADOS:
            raise ValueError(f"Estado no válido: {estado}")
        with self._lock:
            fila = self.conn.execute(
                "SELECT estado FROM alertas WHERE id = ?", (alerta_id,)
            ).fetchone()
            if fila is None or estado not in TRANSICIONES.get(fila["estado"], set()):
                return False
            campo_fecha, campo_por = (
                ("atendida", "atendido_por") if estado == "atendida" else ("revisada", "revisado_por")
            )
            self.conn.execute(
                f"UPDATE alertas SET estado = ?, {campo_fecha} = ?, {campo_por} = ? WHERE id = ?",
                (estado, ahora_iso(), por, alerta_id),
            )
            self.conn.commit()
            return True
