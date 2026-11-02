# AutoPark

Sistema de gestión de estacionamiento por consola (Python 3.9+, sin dependencias).

    python main.py

| Módulo            | Responsabilidad                                        |
|-------------------|--------------------------------------------------------|
| `main.py`         | Menú y flujo de pantallas                              |
| `ui.py`           | Presentación: colores, tablas, comprobantes, prompts   |
| `servicios.py`    | Casos de uso (cobro manual, lote, historial)           |
| `tarifas.py`      | Reglas de negocio y cálculo                            |
| `validaciones.py` | Parsers/validadores (`ErrorValidacion`)                |
| `persistencia.py` | Lectura de JSON y escritura de CSV                     |
| `models.py`       | Dataclasses: `Movimiento`, `Liquidacion`, `Rechazo`, `Estadia`, `HistorialPatente` |
| `config.py`       | Tarifas, reglas de tiempo y rutas                      |

Las tarifas de `config.py` son valores de ejemplo. Variable `NO_COLOR=1` desactiva los colores.