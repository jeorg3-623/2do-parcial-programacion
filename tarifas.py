"""Motor de liquidación: estacionamiento, bonificación y lavado."""
from __future__ import annotations

import math

import config
from models import Liquidacion, Movimiento


def _bloques_iniciales(minutos: int) -> int:
    return math.ceil(min(minutos, config.LIMITE_BLOQUES_30) / config.BLOQUE_INICIAL)


def costo_mismo_dia(tipo: str, minutos: int) -> int:
    """Primeras 2 h por bloques de 30 min; desde el minuto 121 por hora completa.
    Nunca supera el tope diario."""
    t = config.TARIFAS[tipo]
    excedente = max(0, minutos - config.LIMITE_BLOQUES_30)
    horas = math.ceil(excedente / config.BLOQUE_EXTRA)
    bruto = _bloques_iniciales(minutos) * t.bloque_30 + horas * t.hora
    return min(bruto, t.tope_dia)


def calcular_liquidacion(mov: Movimiento) -> Liquidacion:
    t = config.TARIFAS[mov.tipo]

    if mov.dias > 0:
        base, bonificacion, minutos = mov.dias * t.tope_dia, 0, 0
    else:
        minutos = mov.minutos or 0
        base = costo_mismo_dia(mov.tipo, minutos)
        bonificacion = 0
        if mov.lavado:
            # Las primeras 2 h quedan bonificadas (hasta el costo base).
            bonificacion = min(base, _bloques_iniciales(minutos) * t.bloque_30)

    lavado = t.lavado if mov.lavado else 0
    return Liquidacion(mov.dias, minutos, base, bonificacion, lavado,
                       total=base - bonificacion + lavado)
