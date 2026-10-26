"""Capa de presentación: colores, cuadros, tablas, comprobantes y prompts."""
from __future__ import annotations

import os
import sys
from typing import Callable, Sequence, TypeVar

from validaciones import ErrorValidacion

T = TypeVar("T")
ANCHO = 66

# ── Soporte de color ANSI (se desactiva si no es una terminal o NO_COLOR) ──
if os.name == "nt":
    os.system("")  # habilita secuencias ANSI en la consola de Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

_COLOR = ("FORCE_COLOR" in os.environ) or (sys.stdout.isatty() and "NO_COLOR" not in os.environ)
_CODIGOS = {"bold": "1", "dim": "2", "red": "31", "green": "32",
            "yellow": "33", "blue": "34", "cyan": "36"}


def estilo(texto: str, *estilos: str) -> str:
    if not _COLOR or not estilos:
        return texto
    codigos = ";".join(_CODIGOS[e] for e in estilos)
    return f"\033[{codigos}m{texto}\033[0m"


# ── Utilidades ─────────────────────────────────────────────────────────────
def dinero(valor: int) -> str:
    return "$ " + f"{valor:,}".replace(",", ".")


def limpiar() -> None:
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def pausa() -> None:
    input(estilo("\n  Presione [ENTER] para volver al menú...", "dim"))


# ── Mensajes ───────────────────────────────────────────────────────────────
def ok(msg: str) -> None:
    print(f"  {estilo('✔', 'green', 'bold')} {msg}")


def error(msg: str) -> None:
    print(f"  {estilo('✖', 'red', 'bold')} {estilo(msg, 'red')}")


def info(msg: str) -> None:
    print(f"  {estilo('ℹ', 'cyan')} {msg}")


# ── Bloques visuales ───────────────────────────────────────────────────────
def banner(titulo: str, subtitulo: str = "") -> None:
    print(estilo("╔" + "═" * (ANCHO - 2) + "╗", "cyan"))
    print(estilo("║", "cyan") + estilo(titulo.center(ANCHO - 2), "bold") + estilo("║", "cyan"))
    if subtitulo:
        print(estilo("║", "cyan") + estilo(subtitulo.center(ANCHO - 2), "dim") + estilo("║", "cyan"))
    print(estilo("╚" + "═" * (ANCHO - 2) + "╝", "cyan"))


def seccion(titulo: str) -> None:
    print(f"\n  {estilo(titulo.upper(), 'bold', 'cyan')}")
    print(estilo("  " + "─" * (ANCHO - 4), "dim"))


def menu(opciones: Sequence[tuple[str, str]]) -> None:
    print()
    for clave, texto in opciones:
        print(f"   {estilo('[' + clave + ']', 'yellow', 'bold')}  {texto}")
    print()


def tabla(encabezados: Sequence[str], filas: Sequence[Sequence[object]],
          alineacion: str = "", pie: Sequence[object] | None = None) -> None:
    """Imprime una tabla con bordes. alineacion: '<' izq, '>' der, '^' centro."""
    n = len(encabezados)
    alin = (alineacion or "<" * n).ljust(n, "<")
    todas = [list(encabezados)] + [list(f) for f in filas] + ([list(pie)] if pie else [])
    anchos = [max(len(str(f[i])) for f in todas) for i in range(n)]

    def borde(izq: str, med: str, der: str) -> str:
        return "  " + izq + med.join("─" * (a + 2) for a in anchos) + der

    def fila(celdas: Sequence[object]) -> str:
        partes = [f" {str(c):{alin[i]}{anchos[i]}} " for i, c in enumerate(celdas)]
        return "  │" + "│".join(partes) + "│"

    print(borde("┌", "┬", "┐"))
    print(estilo(fila(encabezados), "bold"))
    print(borde("├", "┼", "┤"))
    for f in filas:
        print(fila(f))
    if pie:
        print(borde("├", "┼", "┤"))
        print(estilo(fila(pie), "bold", "green"))
    print(borde("└", "┴", "┘"))


def comprobante(titulo: str, renglones: Sequence[tuple[str, str]],
                etiqueta_total: str, total: str) -> None:
    """Comprobante tipo ticket con detalle y total destacado."""
    w = 46
    print("  " + estilo("┏" + "━" * w + "┓", "green"))
    print("  " + estilo("┃", "green") + estilo(titulo.center(w), "bold") + estilo("┃", "green"))
    print("  " + estilo("┣" + "━" * w + "┫", "green"))
    for etiqueta, valor in renglones:
        espacio = w - 2 - len(etiqueta) - len(valor)
        print("  " + estilo("┃", "green") + f" {etiqueta}{' ' * espacio}{valor} " + estilo("┃", "green"))
    print("  " + estilo("┣" + "━" * w + "┫", "green"))
    espacio = w - 2 - len(etiqueta_total) - len(total)
    linea = f" {etiqueta_total}{' ' * espacio}{total} "
    print("  " + estilo("┃", "green") + estilo(linea, "bold", "green") + estilo("┃", "green"))
    print("  " + estilo("┗" + "━" * w + "┛", "green"))


# ── Entrada de datos ───────────────────────────────────────────────────────
def pedir(prompt: str, parser: Callable[[str], T]) -> T:
    """Pregunta hasta que `parser` acepte el valor (lanza ErrorValidacion si no)."""
    while True:
        texto = input(f"  {estilo('›', 'cyan', 'bold')} {prompt}: ")
        try:
            return parser(texto)
        except ErrorValidacion as e:
            error(str(e))
