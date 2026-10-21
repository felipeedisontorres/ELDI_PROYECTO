# Registro de uso de herramientas de IA

Requisito del curso: todo uso de IA debe mencionarse y documentarse, indicando cómo se usó, con qué propósito y qué código generó.

Herramienta usada: Claude (Anthropic).

| Fecha | Propósito | Cómo se usó | Archivos afectados | ¿Generó código? | Qué entendimos / qué revisamos |
|---|---|---|---|---|---|
| 2026-10-14 | Elegir el proyecto | Comparación de opciones de la lista según facilidad, costo y contenido académico | — | No | Se eligió el #8 por no requerir hardware externo |
| 2026-10-21 | Planteamiento | Trazabilidad de requisitos, preguntas para el profesor y arquitectura base | `docs/01_requisitos.md`, `docs/02_arquitectura.md` | No | Revisado por el equipo |
| 2026-10-21 | Estructura del repositorio | Plantilla de README, carpetas y `.gitignore` | `README.md`, `.gitignore`, `AI_USAGE.md` | No (solo documentación) | — |

## Convención para el código generado por IA

Cada archivo que contenga código generado o modificado con IA lleva al inicio un comentario como este:

```verilog
// AI-ASSISTED: Claude (Anthropic). Generado: <qué partes>. Revisado y explicado por: <nombre>.
```
