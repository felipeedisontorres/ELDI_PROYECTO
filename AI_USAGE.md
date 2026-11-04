# Registro de uso de herramientas de IA

Requisito del curso: todo uso de IA debe mencionarse y documentarse, indicando cómo se usó, con qué propósito y qué código generó.

Herramienta usada: Claude (Anthropic).

| Fecha | Propósito | Cómo se usó | Archivos afectados | ¿Generó código? | Qué entendimos / qué revisamos |
|---|---|---|---|---|---|
| 2026-10-14 | Elegir el proyecto | Comparación de opciones de la lista según facilidad, costo y contenido académico | — | No | Se eligió el #8 por no requerir hardware externo |
| 2026-10-21 | Planteamiento | Trazabilidad de requisitos, preguntas para el profesor y arquitectura base | `docs/01_requisitos.md`, `docs/02_arquitectura.md` | No | Revisado por el equipo |
| 2026-10-21 | Estructura del repositorio | Plantilla de README, carpetas y `.gitignore` | `README.md`, `.gitignore`, `AI_USAGE.md` | No (solo documentación) | — |
| 2026-10-27 | Decisiones con la guía del profesor | Análisis de `5_Implementacion_Operaciones_Puntuales.pdf` y propuesta de D1–D7 con alternativas | `docs/04_decisiones.md` | No | El equipo escogió entre las alternativas |
| 2026-10-28 | Esquemático v2 y guía | Tras la retroalimentación del profesor (MUX más detallados, arquitectura continua) la IA rediseñó el esquemático en una hoja A1 con un script de Python que dibuja SVG, y escribió la guía bloque a bloque. Prompts y generador en `docs/ia/` | `docs/diagramas/*.pdf`, `docs/ia/` | Sí (script de dibujo) | Pendiente: comparar con el esquemático elaborado por Vivado |
| 2026-11-03 | Código Vivado completo | A partir del esquemático RTL v2 y la guía bloque a bloque: 14 módulos SystemVerilog, 11 testbenches autoverificables, XDC, scripts Tcl y script de Python. Se verificó la arquitectura con un modelo ciclo a ciclo antes de simular en Vivado | `rtl/*.sv`, `tb/*.sv`, `constraints/nexys4ddr.xdc`, `scripts/*.tcl`, `python/send_image.py`, `docs/03_codigo.md` | Sí | Pendiente: cada integrante debe explicar cada módulo y completar "Revisado y explicado por" en su encabezado |

## Convención para el código generado por IA

Cada archivo que contenga código generado o modificado con IA lleva al inicio un comentario como este:

```verilog
// AI-ASSISTED: Claude (Anthropic). Generado: <qué partes>. Revisado y explicado por: <nombre>.
```
