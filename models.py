"""Modelos de datos del dominio (inmutables y tipados)."""
from __future__ import annotations

from dataclasses import dataclass

import config


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


@dataclass(frozen=True)
class Estadia:
    """Una estadía histórica leída de los CSV."""
    origen: str      # "Manual" o "Lote"
    tipo: str
    dias: int
    minutos: int
    total: int

    @property
    def duracion_minutos(self) -> int:
        """Duración real: las estadías de varios días cuentan 24 h por día."""
        return self.dias * config.MINUTOS_POR_DIA if self.dias > 0 else self.minutos


@dataclass(frozen=True)
class HistorialPatente:
    """Consolidado histórico de un vehículo."""
    patente: str
    estadias: tuple[Estadia, ...] = ()

    @property
    def ingresos(self) -> int:
        return len(self.estadias)

    @property
    def total_abonado(self) -> int:
        return sum(e.total for e in self.estadias)

    @property
    def promedio_minutos(self) -> float:
        if not self.estadias:
            return 0.0
        return sum(e.duracion_minutos for e in self.estadias) / self.ingresos