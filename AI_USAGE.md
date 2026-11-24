
## 1. Herramienta

- **IA:** Claude (Anthropic), en un proyecto de claude.ai llamado "ELDI-FINAL".
- **Material que le dimos:** los requisitos del curso (`Projects-Proposals.pdf`, `Requrimientos Minimos parte 2.pdf`),
  las diapositivas del curso (1 a 10) y la guía del profesor `5_Implementacion_Operaciones_Puntuales.pdf`.


## 2. Reglas que le pusimos

Le pedimos actuar como tutor y co-diseñador con estas reglas :

1. Usar solo temas vistos en las presentaciones del curso y avisar si algo se sale de ellas.
2. Citar el requisito (R-xx) que respalda cada propuesta.
3. No inventar requisitos, datasheets ni números de pin: los pines salen del XDC maestro oficial de Digilent.
4. Explicar paso a paso, con alternativas y ventajas y desventajas, para que podamos entender y defender el diseño.


## 3. Registro por fecha

| Fecha | Propósito | Cómo se usó | ¿Generó código? |
|---|---|---|---|
| 21-oct | Planteamiento | Propuso la tabla de requisitos R-xx, las preguntas al profesor y la arquitectura base | No |
| 27-oct | Guía del profesor | Analizó `5_Implementacion_Operaciones_Puntuales.pdf` y propuso las decisiones D1–D7 con alternativas; el equipo escogió | No |
| 28-oct | Esquemático v2 | Con la retroalimentación del profesor (R-F02), rediseñó el esquemático en una hoja A1 y escribió una guía de estudio bloque a bloque | Sí (script de dibujo) |
| 03-nov | Código v2 | Escribió los módulos en SystemVerilog, los testbenches y el XDC a partir del esquemático v2 | Sí |
| 17-nov | Diseño v4 | Rediseñó todo el esquemático para simplificarlo (D23–D35), escribió el código, los testbenches, el generador del esquemático y `Explicacion_v4.pdf`, y corrió las simulaciones | Sí |
| 17-nov | Herramientas | Instaló en el computador de Edison las librerías de Python (pyserial, pillow, numpy, matplotlib) | No |
| 18-nov | Cierre de tiempos (v4.1) | Encontró en el reporte de Vivado que la v4 no cumplía tiempos y agregó el registro de segmentación (D36); actualizó el esquemático y la explicación a v4.1 | Sí |
| 18-nov | Estudio | Explicó bloque por bloque `uart_rx` y `pos_counter` con ejemplos numéricos | No |


## 6. Instrucciones (prompts) principales

### Instrucciones fijas del proyecto

> Eres mi tutor y co-diseñador para el proyecto final de Electrónica Digital (Escuela Colombiana de Ingeniería).
>
> CONTEXTO
> - Los archivos 00_ y 01_ contienen los requisitos mínimos (parte 1 y parte 2 en español). Cumplir ABSOLUTAMENTE TODOS es obligatorio.
> - El profesor valora más que el código: cómo planteamos el problema, cómo diseñamos el hardware, cómo lo desarrollamos y que se vea lo aprendido en el curso.
> - Solo podemos usar temas vistos en las presentaciones (archivos 10_ en adelante). Si propones algo fuera de ellas, avísame explícitamente y justifica.
>
> REGLAS
> 1. Antes de proponer algo, verifica que respeta los requisitos y cita sus IDs (R-xx).
> 2. Nunca inventes requisitos, citas, datasheets, números de pin ni páginas. Si algo no está en mis archivos, dilo. Para información externa, remíteme a fuentes oficiales (manual de la tarjeta, documentación del fabricante) y dime qué debo verificar yo.
> 3. Modo aprendizaje: explica paso a paso y de forma muy detallada; justifica cada decisión con alternativas y trade-offs; antes de darme una solución completa, pídeme que lo intente o que prediga el resultado, salvo que yo escriba "dame la solución directa".
> 4. Honestidad total: si mi idea o mi razonamiento tiene un problema, dímelo sin suavizarlo.
> 5. Si hay ambigüedad o contradicción entre requisitos, no elijas por mí: señálala y redacta la pregunta para el profesor.
> 6. Prefiero respuestas largas y completas antes que cortas e incompletas. Los entregables van en markdown o en documento descargable.
> 7. Al terminar cada sesión de trabajo, cuando te lo pida, genera la actualización de STATE.md con la plantilla de abajo.


## 7. Cómo verificamos el código generado

1. **Testbenches autoverificables:** cada módulo tiene su testbench y todos terminan en PASS
   (ver [`docs/04_verificacion.md`](docs/04_verificacion.md)).

