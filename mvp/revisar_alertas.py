"""Muestra las últimas alertas registradas, con sus tiempos (útil para revisar pruebas
desde la terminal o para que un asistente verifique resultados sin mirar el dashboard).

Uso:
    python revisar_alertas.py            # últimas 10
    python revisar_alertas.py --todas
    python revisar_alertas.py --resumen  # conteo por tipo y estado
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from almacen import Almacen, segundos_entre

AQUI = Path(__file__).resolve().parent
DB = AQUI / "data" / "alertas.db"


def describir(a) -> str:
    partes = [f"#{a['id']}", a["fecha"].replace("T", " ")[:19], a["tipo"], a["estado"]]
    if a["duracion_s"] is not None:
        partes.append(f"alerta {a['duracion_s']:.1f} s tras el inicio")
    if a["latencia_ms"] is not None:
        partes.append(f"procesada en {a['latencia_ms']:.0f} ms")
    respuesta = segundos_entre(a["fecha"], a["revisada"])
    if respuesta is not None:
        partes.append(f"revisada en {respuesta:.1f} s por {a['revisado_por']}")
    atencion = segundos_entre(a["fecha"], a["atendida"])
    if atencion is not None:
        partes.append(f"atendida en {atencion:.1f} s")
    linea = " | ".join(partes) + f"\n    {a['mensaje']}"
    if a["imagen"]:
        linea += f"\n    evidencia: {a['imagen']}"
    if a["descripcion_ia"]:
        linea += f"\n    IA: {a['descripcion_ia']}"
    return linea


def main():
    parser = argparse.ArgumentParser(description="Revisar alertas registradas")
    parser.add_argument("--todas", action="store_true")
    parser.add_argument("--resumen", action="store_true")
    parser.add_argument("-n", type=int, default=10)
    args = parser.parse_args()

    if not DB.exists():
        raise SystemExit("Aún no hay alertas: inicia la demo primero (python iniciar_demo.py).")
    alertas = Almacen(DB).listar(None if (args.todas or args.resumen) else args.n)
    if not alertas:
        print("No hay alertas registradas.")
        return
    if args.resumen:
        print(f"Total: {len(alertas)} alertas")
        for (tipo, estado), n in sorted(Counter((a["tipo"], a["estado"]) for a in alertas).items()):
            print(f"  {tipo:20s} {estado:12s} {n}")
        return
    for a in alertas:
        print(describir(a))


if __name__ == "__main__":
    main()
