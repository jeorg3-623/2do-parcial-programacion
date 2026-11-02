"""Casos de uso de la aplicación (sin entrada/salida por consola)."""
from __future__ import annotations

from dataclasses import dataclass, field

import config
import persistencia as db
import tarifas
import validaciones as val
from models import Estadia, HistorialPatente, Liquidacion, Movimiento, Rechazo
from validaciones import ErrorValidacion


@dataclass
class ResumenLote:
    leidos: int = 0
    liquidados: list[tuple[Movimiento, Liquidacion]] = field(default_factory=list)
    rechazos: list[Rechazo] = field(default_factory=list)

    @property
    def recaudacion(self) -> int:
        return sum(liq.total for _, liq in self.liquidados)


def parse_movimiento(raw: object) -> Movimiento:
    """Convierte un registro crudo del JSON en un Movimiento válido."""
    if not isinstance(raw, dict):
        raise ErrorValidacion("El registro no es un objeto JSON válido")

    patente = val.parse_patente(raw.get("patente", ""))
    tipo = val.parse_tipo(raw.get("tipo", ""))
    dias = val.parse_dias(raw.get("dias", 0))
    lavado = val.parse_lavado(raw.get("lavado", False))

    if dias > 0:
        return Movimiento(patente, tipo, dias, lavado)

    entrada = val.parse_hora(raw.get("hora_entrada", ""))
    salida = val.parse_hora(raw.get("hora_salida", ""))
    minutos = val.calcular_minutos(entrada, salida)
    return Movimiento(patente, tipo, 0, lavado, entrada, salida, minutos)


def registrar_cobro_manual(mov: Movimiento) -> Liquidacion:
    """Liquida un movimiento y lo acumula en liquidacion-manual.csv."""
    liq = tarifas.calcular_liquidacion(mov)
    db.agregar_csv(config.ARCHIVO_MANUAL, db.CAMPOS_LIQUIDACION, db.a_fila(mov, liq))
    return liq


def procesar_lote() -> ResumenLote:
    """Lee el JSON, liquida los válidos y exporta liquidacion.csv y rechazados.csv."""
    crudos = db.leer_movimientos(config.ARCHIVO_MOVIMIENTOS)
    resumen = ResumenLote(leidos=len(crudos))

    for indice, raw in enumerate(crudos, start=1):
        try:
            mov = parse_movimiento(raw)
        except ErrorValidacion as error:
            patente = str(raw.get("patente", "")) if isinstance(raw, dict) else ""
            resumen.rechazos.append(Rechazo(indice, patente, str(error)))
        else:
            resumen.liquidados.append((mov, tarifas.calcular_liquidacion(mov)))

    db.escribir_csv(config.ARCHIVO_LOTE, db.CAMPOS_LIQUIDACION,
                    [db.a_fila(m, l) for m, l in resumen.liquidados])
    db.escribir_csv(config.ARCHIVO_RECHAZADOS, db.CAMPOS_RECHAZOS,
                    [db.rechazo_a_fila(r) for r in resumen.rechazos])
    return resumen


def consultar_historial(patente: str) -> HistorialPatente:
    """Consolida todas las estadías de una patente en los CSV de cobro manual y lote."""
    fuentes = (("Manual", config.ARCHIVO_MANUAL), ("Lote", config.ARCHIVO_LOTE))
    estadias: list[Estadia] = []

    for origen, ruta in fuentes:
        for fila in db.leer_csv(ruta):
            if fila.get("patente") != patente:
                continue
            try:
                estadias.append(Estadia(origen, fila["tipo"], int(fila["dias"]),
                                        int(fila["minutos"]), int(fila["total_cobrado"])))
            except (KeyError, ValueError):
                continue   # fila dañada o editada a mano: se ignora

    return HistorialPatente(patente, tuple(estadias))