"""Registro de alertas en SQLite (compartido por el detector y el dashboard)."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

ESTADOS = ("nueva", "confirmada", "descartada")


class Almacen:
    def __init__(self, ruta: str | Path):
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(ruta), timeout=5, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                camara TEXT NOT NULL,
                tipo TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                imagen TEXT,
                estado TEXT NOT NULL DEFAULT 'nueva',
                revisada TEXT
            )"""
        )
        self.conn.commit()

    def guardar(self, camara: str, tipo: str, mensaje: str, imagen: str | None) -> int:
        cur = self.conn.execute(
            "INSERT INTO alertas (fecha, camara, tipo, mensaje, imagen) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().isoformat(timespec="seconds"), camara, tipo, mensaje, imagen),
        )
        self.conn.commit()
        return cur.lastrowid

    def listar(self, limite: int = 50) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM alertas ORDER BY id DESC LIMIT ?", (limite,)
        ).fetchall()

    def contar_por_estado(self) -> dict[str, int]:
        filas = self.conn.execute("SELECT estado, COUNT(*) FROM alertas GROUP BY estado")
        conteo = {e: 0 for e in ESTADOS}
        conteo.update({estado: n for estado, n in filas})
        return conteo

    def cambiar_estado(self, alerta_id: int, estado: str) -> None:
        if estado not in ESTADOS:
            raise ValueError(f"Estado no válido: {estado}")
        self.conn.execute(
            "UPDATE alertas SET estado = ?, revisada = ? WHERE id = ?",
            (estado, datetime.now().isoformat(timespec="seconds"), alerta_id),
        )
        self.conn.commit()
