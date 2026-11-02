"""Acceso a archivos: lectura de JSON y escritura de CSV."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from models import Liquidacion, Movimiento, Rechazo

CAMPOS_LIQUIDACION = [
    "patente", "tipo", "dias", "hora_entrada", "hora_salida", "minutos",
    "lavado", "base", "bonificacion", "monto_lavado", "total_cobrado",
]
CAMPOS_RECHAZOS = ["indice", "patente", "motivo"]


def leer_movimientos(ruta: Path) -> list:
    """Lee el JSON de movimientos (lista, o dict con clave 'movimientos')."""
    with open(ruta, "r", encoding="utf-8") as f:
        datos = json.load(f)
    if isinstance(datos, dict):
        datos = datos.get("movimientos", [])
    if not isinstance(datos, list):
        raise ValueError("el JSON debe contener una lista de movimientos")
    return datos


def leer_csv(ruta: Path) -> list[dict]:
    """Lee un CSV como lista de diccionarios. Si no existe, devuelve lista vacía."""
    if not ruta.exists():
        return []
    with open(ruta, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def a_fila(mov: Movimiento, liq: Liquidacion) -> dict:
    return {
        "patente": mov.patente, "tipo": mov.tipo, "dias": mov.dias,
        "hora_entrada": mov.hora_entrada, "hora_salida": mov.hora_salida,
        "minutos": liq.minutos, "lavado": "S" if mov.lavado else "N",
        "base": liq.base, "bonificacion": liq.bonificacion,
        "monto_lavado": liq.lavado, "total_cobrado": liq.total,
    }


def escribir_csv(ruta: Path, campos: list[str], filas: list[dict]) -> None:
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


def agregar_csv(ruta: Path, campos: list[str], fila: dict) -> None:
    """Agrega una fila acumulando transacciones (crea el encabezado si falta)."""
    nuevo = not ruta.exists() or ruta.stat().st_size == 0
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        if nuevo:
            escritor.writeheader()
        escritor.writerow(fila)


def rechazo_a_fila(r: Rechazo) -> dict:
    return {"indice": r.indice, "patente": r.patente, "motivo": r.motivo}