# Instrucciones (prompts) dadas a la IA

Herramienta: Claude (Anthropic), en un proyecto de claude.ai ("ELDI-FINAL").
Los mensajes se copian tal como se escribieron (con su ortografía original), en orden.

## 1. Instrucciones fijas del proyecto (se aplican a toda la conversación)

> Eres mi tutor y co-diseñador para el proyecto final de Electrónica Digital (Escuela Colombiana de Ingeniería).
> Trabajo con un compañero. Entrega final: 25 de noviembre de 2026; hay avances todos los miércoles.
>
> CONTEXTO
> - Los archivos 00_ y 01_ contienen los requisitos mínimos (parte 1 y parte 2 en español). Cumplir ABSOLUTAMENTE TODOS es obligatorio: si falta uno, pierdo la materia.
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

Archivos de referencia cargados en el proyecto: `Projects-Proposals.pdf`, `Requrimientos Minimos parte 2.pdf`,
`5_Implementacion_Operaciones_Puntuales.pdf` (guía del profesor) y las diapositivas 1 a 10 del curso.

## 2. Mensajes que llevaron al esquemático

### Elección del proyecto y planteamiento

1. *(con `Projects-Proposals.pdf`)* "Actúa como un ingeniero electrónico experto en Electrónica Digital… Necesito que me propongas únicamente 3 opciones de proyectos… No inventes los requisitos del profesor. Si necesitas información…hazme primero las preguntas indispensables."
2. "Opcion 1, cuales son los primeros pasos o metodologia"
3. "Vamos a hacer el proyecto #8, no se preocupe por mi compañero, la placa que vamos a usar va a ser la que antes le mencione, por lka parte del codigo con IA en clase se hablo con profesor y lo que necistamos es entender como funciona el codigo entero, la fecha tampoco importa pues debe estar funcionando desde mucho antes"
4. "De qué trata este proyecto explíquelo en poco y sencillo"
5. "Explique porq usara python y no c++, que es UART, FSM"
6. "Nombres: Edison Torres y Juan Guaman, cuando acabe Explique cada uno de los filtros, como va a hacer q se puedan usar 2 diferentes individual y 2 combinados, tambien: Implement a communication interface based on the RS232 protocol… 3. Use switches… 4. Add noise…"

### Guía del profesor y decisiones de diseño

7. "revise el archivo Implementacion_Operaciones_puntuales pdf esta es una guia del profesor para hacer el proyecto y es el archivo mas IMPORTANTE, En la retroalimentacion nos dijo que podemos usar phyton para cargar y leer la imagen pero la parte del hardware y la matematica tiene que hacerse desde la FPGA"
8. *(con la guía del profesor)* "Analice el PDF de nuevo y tome decisiones para las predicciones pendientes pensando en lago no mediocre pero simple y que se pueda entender, (el profesor dijo que enviar los bits 1 a 1 por UART estaba bien pero hay que mirar como los enviamos)"

### Esquemático v1 (avance)

9. "Necesito entregar un adelanto, preferiblemente un diagrama o dibujo relacionado junto la explicacion y planeacion de como vamos a realizar el proyecto" (formato elegido: "Ambos", documento y presentación)
10. "Explique y justifique de forma que yo pueda entender sencillo"

### Esquemático v2 (después de la retroalimentación del profesor, 28-oct)

11. "El profesor me dijo que los diagramas de multiplexsores deben estar mas a detalle y la arquitectura deberia ser continua, osea no por partes, Haga todo el diseño de forma mas profesional"

### Material de estudio y código

12. "AHORA EXPLIQUEME EL ESQUEMATICO BLOQUE POR BLOQUE, CREE UNA PRESENTACION O PDF DONDE EXPLIQUE QUE HACE CADA COSA, COMO SE COMBINAN Y NECESITAN ENTRE AMBAN,USE LOS NOMBRES COMPLETOS SI VA A DECIR FF O SR_TX PONGA UN PARENTESIS CON EL NOMBRE COMPLETO, Y TODO DEBE SER CLARO EXPLICADO OARTE POR PARTE Y QUE HACE CADA COSA COMO MUX BUS, LOGICA, MOTOR ETC"
13. "Según la guía del esquemático haga el codigo para viviado, use claude code si necesario, que quede lo mejor y sencillo de entender posible siguiendo tambien la presentacion del profesor"

## 3. Resultado de cada etapa

| Mensajes | Entregable | Dónde está |
|---|---|---|
| 1–6 | Requisitos R-xx, preguntas al profesor, arquitectura base | `docs/01_requisitos.md`, `docs/02_arquitectura.md` |
| 7–8 | Decisiones D1–D7 | `docs/04_decisiones.md` |
| 9–10 | Avance con esquemático v1 por bloques | presentado en clase |
| 11 | Esquemático RTL v2 continuo (hoja A1), M1–M21, decisiones D8–D10 (`docs/04_decisiones.md`) | `docs/diagramas/Esquematico_RTL_v2_A1.pdf`, `docs/diagramas/Diseno_RTL_v2.pdf` |
| 12 | Guía bloque a bloque | `docs/diagramas/Guia_Esquematico_Bloque_a_Bloque.pdf` |
| 13 | Código SystemVerilog, testbenches, XDC, scripts | `rtl/`, `tb/`, `constraints/`, `scripts/`, `python/` |
