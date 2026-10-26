"""Configuración central de AutoPark: tarifas, reglas de tiempo y rutas."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Tarifa:
    """Tarifario de una categoría de vehículo (valores en pesos)."""
    bloque_30: int   # precio de cada bloque de 30 min (primeras 2 h)
    hora: int        # precio por hora o fracción desde el minuto 121
    tope_dia: int    # máximo diario; también es el costo por día completo
    lavado: int      # precio fijo del servicio de lavado


# Valores de ejemplo: reemplazar por los de la consigna.
TARIFAS: dict[str, Tarifa] = {
    "auto":      Tarifa(bloque_30=800,  hora=1400, tope_dia=9000,  lavado=6000),
    "moto":      Tarifa(bloque_30=500,  hora=900,  tope_dia=5000,  lavado=3500),
    "camioneta": Tarifa(bloque_30=1100, hora=1900, tope_dia=12000, lavado=8000),
}

# Reglas de tiempo (minutos)
LIMITE_BLOQUES_30 = 120
BLOQUE_INICIAL = 30
BLOQUE_EXTRA = 60

# Archivos
ARCHIVO_MOVIMIENTOS = BASE_DIR / "movimientos.json"
ARCHIVO_LOTE = BASE_DIR / "liquidacion.csv"
ARCHIVO_RECHAZADOS = BASE_DIR / "rechazados.csv"
ARCHIVO_MANUAL = BASE_DIR / "liquidacion-manual.csv"
