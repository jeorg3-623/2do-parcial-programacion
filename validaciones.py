"""Parsers y validadores. Todos lanzan ErrorValidacion con un mensaje claro."""
from __future__ import annotations

import re

import config


class ErrorValidacion(ValueError):
    """Dato de entrada inválido. El mensaje es apto para mostrar al usuario."""


_TRADICIONAL = re.compile(r"[A-Z]{3}[0-9]{3}")        # ABC123
_MERCOSUR = re.compile(r"[A-Z]{2}[0-9]{3}[A-Z]{2}")   # AA123BB
_HORA = re.compile(r"([01]?[0-9]|2[0-3]):([0-5][0-9])")


def parse_patente(valor: object) -> str:
    patente = "".join(str(valor).split()).upper()
    if not (_TRADICIONAL.fullmatch(patente) or _MERCOSUR.fullmatch(patente)):
        raise ErrorValidacion("Patente inválida: use ABC123 o AA123BB")
    return patente


def parse_tipo(valor: object) -> str:
    tipo = str(valor).strip().lower()
    if tipo not in config.TARIFAS:
        opciones = ", ".join(config.TARIFAS)
        raise ErrorValidacion(f"Tipo de vehículo inválido: use {opciones}")
    return tipo


def parse_dias(valor: object) -> int:
    if isinstance(valor, bool):
        raise ErrorValidacion("Días inválidos: ingrese un entero mayor o igual a 0")
    try:
        dias = int(str(valor).strip())
    except ValueError:
        raise ErrorValidacion("Días inválidos: ingrese un entero mayor o igual a 0") from None
    if dias < 0:
        raise ErrorValidacion("Días inválidos: ingrese un entero mayor o igual a 0")
    return dias


def parse_hora(valor: object) -> str:
    """Valida 'H:MM' / 'HH:MM' y la devuelve normalizada como 'HH:MM'."""
    m = _HORA.fullmatch(str(valor).strip())
    if not m:
        raise ErrorValidacion("Horario inválido o faltante: use el formato HH:MM")
    return f"{int(m.group(1)):02d}:{m.group(2)}"


def parse_lavado(valor: object) -> bool:
    if isinstance(valor, bool):
        return valor
    texto = str(valor).strip().lower()
    if texto in {"s", "si", "sí", "true", "1"}:
        return True
    if texto in {"n", "no", "false", "0"}:
        return False
    raise ErrorValidacion("Respuesta inválida: indique S o N")


def _a_minutos(hora: str) -> int:
    h, m = hora.split(":")
    return int(h) * 60 + int(m)


def calcular_minutos(entrada: str, salida: str) -> int:
    """Minutos entre dos horas 'HH:MM' del mismo día (salida > entrada)."""
    minutos = _a_minutos(salida) - _a_minutos(entrada)
    if minutos <= 0:
        raise ErrorValidacion("La hora de salida debe ser posterior a la de entrada")
    return minutos
