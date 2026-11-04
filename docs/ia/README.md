# Uso de IA en el esquemático RTL (y en el resto del proyecto)

Este documento justifica cómo se hizo el esquemático RTL v2 (`docs/diagramas/Esquematico_RTL_v2_A1.pdf`), que fue
dibujado con ayuda de inteligencia artificial. Cumple el requisito del curso de mencionar y documentar todo uso de IA
(R-G08): con qué herramienta, para qué, con qué instrucciones y qué revisamos nosotros.

| Archivo | Contenido |
|---|---|
| `README.md` (este) | Qué hizo la IA, qué hicimos nosotros, cómo se generó el dibujo y cómo se verificó |
| `prompts.md` | Las instrucciones dadas a la IA (configuración del proyecto y mensajes, en orden) |
| `generador_esquematico/` | El código Python que dibuja el esquemático: con él se puede volver a generar |

## 1. Herramienta

- **IA:** Claude (Anthropic), usada como tutor y co-diseñador dentro de un proyecto de claude.ai llamado "ELDI-FINAL".
- **Material que se le dio:** los requisitos del curso (`Projects-Proposals.pdf`, `Requrimientos Minimos parte 2.pdf`),
  las diapositivas del curso (1 a 10) y la guía del profesor `5_Implementacion_Operaciones_Puntuales.pdf`.
- **Regla principal que le pusimos:** usar solo temas vistos en las diapositivas, citar el requisito (R-xx) de cada
  decisión, no inventar datos (pines, datasheets) y explicar todo para que lo entendamos (ver `prompts.md`).

## 2. Qué hizo la IA y qué hicimos nosotros

| Parte | IA | Equipo (Edison Torres, Juan Guaman) |
|---|---|---|
| Elección del proyecto (#8) | Comparó opciones | Eligió el proyecto, la tarjeta y la modalidad |
| Requisitos y preguntas al profesor | Propuso la tabla R-xx y las preguntas | Llevó las preguntas a clase y trajo la retroalimentación |
| Decisiones de diseño D1–D10 | Propuso alternativas con ventajas y desventajas | Escogió, pidiendo "algo no mediocre pero simple y que se pueda entender" |
| Esquemático v1 (por partes) | Lo dibujó | Lo presentó como avance |
| Retroalimentación del 28-oct | — | El profesor pidió MUX más detallados y arquitectura continua |
| Esquemático v2 (una sola hoja A1) | Lo rediseñó y dibujó con un script de Python | Pidió el cambio con la retroalimentación del profesor y lo revisó |
| Guía bloque a bloque | La escribió | La pidió con nombres completos de cada sigla, para estudiar |
| Código Vivado (SystemVerilog) | Lo escribió siguiendo el esquemático | Debe correr las pruebas, entender y explicar cada módulo |

**Lo que no hizo la IA:** no presentó el avance, no tomó la retroalimentación del profesor ni decidió por nosotros
qué proyecto, tarjeta o nivel de complejidad usar.

## 3. Cómo se generó el dibujo (respuesta a "¿en qué programa lo hicieron?")

El esquemático **no** se hizo en un programa de dibujo (Visio, draw.io, KiCad). La IA escribió un programa en
**Python** (`generador_esquematico/`) que dibuja cada pieza como gráfico vectorial **SVG**:

- `sch.py`: biblioteca de símbolos con la notación de la guía del profesor: MUX (trapecio numerado), registro con
  triángulo de reloj, contador, BRAM con puertos WD/WA/WE/RA/RD, comparador, constante, bus con su ancho y señal de control punteada.
- `top.py`: coloca todos los bloques en una hoja A1 y traza los buses. Ahí está la posición de M1–M21, las tablas
  de salidas de la FSM y el inventario de multiplexores.
- `muxgates.py`: la figura de cómo se construye un MUX con compuertas AND/OR.
- `render.py`: convierte los SVG a PNG con un navegador (Playwright). El PDF A1 se imprimió desde el SVG.

Para volver a generarlo: `cd docs/ia/generador_esquematico` y `python top.py`; el SVG queda en `fig/` y se abre en
cualquier navegador.

**Por qué así y no a mano:** queda en un solo archivo vectorial que se puede ampliar sin perder calidad, con la misma
notación del profesor. Además, si cambia el diseño, se edita una línea y se vuelve a generar todo.

## 4. Cómo se verificó que el dibujo corresponde a un diseño real

1. **El código sigue el esquemático 1 a 1:** cada bloque es un archivo de `rtl/` y cada señal tiene el mismo
   nombre (ver `docs/03_codigo.md`).
2. **Modelo ciclo a ciclo:** antes de Vivado, un modelo registro por registro del diseño se comparó con las
   fórmulas de los filtros. Los 5 modos, el ruido, BTNC y el timeout dieron resultados idénticos.
3. **Al escribir el código aparecieron 3 detalles** que el dibujo no mostraba (`rx_en`, `last_px · pix_valid` y el
   borrado de contadores con `¬seq_en`). Están documentados en `docs/03_codigo.md` como pendientes de pasar a la hoja.
4. **Pendiente del equipo:** abrir en Vivado *RTL Analysis → Open Elaborated Design → Schematic* y comparar el
   esquemático que genera Vivado con la hoja A1, y correr `scripts/run_tests.tcl`.

## 5. Revisión del equipo

| Integrante | Bloques que puede explicar sin mirar la guía | Fecha |
|---|---|---|
| Edison Torres | (pendiente) | |
| Juan Guaman | (pendiente) | |
