"""Modelos de datos del dominio (inmutables y tipados)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Movimiento:
    """Una estadía ya validada y normalizada."""
    patente: str
    tipo: str
    dias: int
    lavado: bool
    hora_entrada: str = ""
    hora_salida: str = ""
    minutos: int | None = None   # None cuando dias > 0


@dataclass(frozen=True)
class Liquidacion:
    """Desglose contable de un cobro."""
    dias: int
    minutos: int
    base: int
    bonificacion: int
    lavado: int
    total: int


@dataclass(frozen=True)
class Rechazo:
    """Registro del lote que no pasó la validación."""
    indice: int
    patente: str
    motivo: str
