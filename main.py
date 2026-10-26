"""AutoPark - Sistema de gestión de estacionamiento (punto de entrada)."""
from __future__ import annotations

import config
import servicios
import ui
import validaciones as val
from models import Movimiento
from validaciones import ErrorValidacion

SUBTITULO = "Sistema de Gestión de Estacionamiento"


def pantalla(titulo: str) -> None:
    ui.limpiar()
    ui.banner("AUTOPARK", SUBTITULO)
    ui.seccion(titulo)


def pedir_horarios() -> tuple[str, str, int]:
    """Pide entrada y salida hasta que sean coherentes. Devuelve (entrada, salida, minutos)."""
    while True:
        entrada = ui.pedir("Hora de entrada (HH:MM)", val.parse_hora)
        salida = ui.pedir("Hora de salida  (HH:MM)", val.parse_hora)
        try:
            return entrada, salida, val.calcular_minutos(entrada, salida)
        except ErrorValidacion as e:
            ui.error(str(e))


def cobro_manual() -> None:
    pantalla("Cobro manual en ventanilla")
    patente = ui.pedir("Patente (AAA000 / AA000AA)", val.parse_patente)
    tipo = ui.pedir("Tipo de vehículo (auto/moto/camioneta)", val.parse_tipo)
    dias = ui.pedir("Días transcurridos (0 = se retira hoy)", val.parse_dias)

    entrada = salida = ""
    minutos = None
    if dias == 0:
        entrada, salida, minutos = pedir_horarios()
    else:
        ui.info(f"Se liquida por {dias} día(s) completo(s) a costo fijo.")
    lavado = ui.pedir("¿Solicitó lavado? (S/N)", val.parse_lavado)

    mov = Movimiento(patente, tipo, dias, lavado, entrada, salida, minutos)
    liq = servicios.registrar_cobro_manual(mov)

    tiempo = f"{minutos} min ({entrada} - {salida})" if dias == 0 else f"{dias} día(s)"
    print()
    ui.comprobante(
        "COMPROBANTE DE ESTACIONAMIENTO",
        [("Patente", f"{patente}"), ("Categoría", tipo.capitalize()), ("Tiempo", tiempo),
         ("Estacionamiento", ui.dinero(liq.base)),
         ("Bonificación", "- " + ui.dinero(liq.bonificacion)),
         ("Lavado", ui.dinero(liq.lavado))],
        "TOTAL A PAGAR", ui.dinero(liq.total),
    )
    print()
    ui.ok(f"Registro guardado en {config.ARCHIVO_MANUAL.name}")
    ui.pausa()


def procesar_lote() -> None:
    pantalla("Procesamiento de lote (JSON → CSV)")
    try:
        r = servicios.procesar_lote()
    except FileNotFoundError:
        ui.error(f"No se encontró el archivo {config.ARCHIVO_MOVIMIENTOS.name}")
        return ui.pausa()
    except (ValueError, OSError) as e:   # JSON mal formado, permisos, etc.
        ui.error(f"No se pudo procesar el lote: {e}")
        return ui.pausa()

    ui.tabla(["Leídos", "Liquidados", "Rechazados", "Recaudación"],
             [[r.leidos, len(r.liquidados), len(r.rechazos), ui.dinero(r.recaudacion)]],
             alineacion="^^^>")

    LIMITE = 10
    if r.liquidados:
        ui.seccion("Liquidaciones")
        filas = [[m.patente, m.tipo, f"{l.minutos} min" if l.dias == 0 else f"{l.dias} d",
                  "S" if m.lavado else "N", ui.dinero(l.base), ui.dinero(l.bonificacion),
                  ui.dinero(l.lavado), ui.dinero(l.total)]
                 for m, l in r.liquidados[:LIMITE]]
        ui.tabla(["Patente", "Tipo", "Tiempo", "Lav", "Base", "Bonif.", "Lavado", "Total"],
                 filas, alineacion="<<>^>>>>",
                 pie=["TOTAL", "", "", "", "", "", "", ui.dinero(r.recaudacion)])
        if len(r.liquidados) > LIMITE:
            ui.info(f"Se muestran {LIMITE} de {len(r.liquidados)}. Detalle completo en el CSV.")

    if r.rechazos:
        ui.seccion("Registros rechazados")
        ui.tabla(["#", "Patente", "Motivo"],
                 [[x.indice, x.patente or "-", x.motivo] for x in r.rechazos], alineacion=">")

    print()
    ui.ok(f"Generado {config.ARCHIVO_LOTE.name}")
    ui.ok(f"Generado {config.ARCHIVO_RECHAZADOS.name}")
    ui.pausa()


def main() -> None:
    acciones = {"1": cobro_manual, "2": procesar_lote}
    while True:
        ui.limpiar()
        ui.banner("AUTOPARK", SUBTITULO)
        ui.menu([("1", "Registrar / Consultar cobro manual"),
                 ("2", "Procesar lote de movimientos (JSON → CSV)"),
                 ("3", "Salir")])
        opcion = input("  Seleccione una opción: ").strip()
        if opcion == "3":
            ui.info("Hasta luego.")
            return
        accion = acciones.get(opcion)
        if accion:
            accion()
        else:
            ui.error("Opción inválida.")
            ui.pausa()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n")
        ui.info("Sesión finalizada.")
