
## 1. Herramienta

- **IA:** Claude (Anthropic), en un proyecto de claude.ai llamado "ELDI-FINAL".
- **Material que le dimos:** los requisitos del curso (`Projects-Proposals.pdf`, `Requrimientos Minimos parte 2.pdf`),
  las diapositivas del curso (1 a 10) y la guía del profesor `5_Implementacion_Operaciones_Puntuales.pdf`.
- **Acceso al computador:** en las sesiones del 17, 18, 23 y 24 de noviembre le dimos permiso para usar el
  computador de Edison: instalar Vivado y las librerías de Python, ejecutar comandos en la consola Tcl de
  Vivado, el 23 de noviembre programar la tarjeta y correr la prueba con ella, y el 24 de noviembre copiar al
  repositorio el script y las imágenes de esa prueba.

## 2. Reglas que le pusimos

Le pedimos actuar como tutor y co-diseñador con estas reglas (texto completo en la sección 6):

1. Usar solo temas vistos en las presentaciones del curso y avisar si algo se sale de ellas.
2. Citar el requisito (R-xx) que respalda cada propuesta.
3. No inventar requisitos, datasheets ni números de pin: los pines salen del XDC maestro oficial de Digilent.
4. Explicar paso a paso, con alternativas y ventajas y desventajas, para que podamos entender y defender el diseño.
5. Si hay ambigüedad entre requisitos, no decidir por nosotros sino redactar la pregunta para el profesor.

## 3. Registro por fecha

| Fecha | Propósito | Cómo se usó | ¿Generó código? |
|---|---|---|---|
| 14-oct | Elegir el proyecto | Comparó opciones de la lista según facilidad, costo y contenido del curso | No |
| 21-oct | Planteamiento | Propuso la tabla de requisitos R-xx, las preguntas al profesor y la arquitectura base | No |
| 21-oct | Repositorio | Plantilla de README, carpetas y `.gitignore` | No (documentación) |
| 27-oct | Guía del profesor | Analizó `5_Implementacion_Operaciones_Puntuales.pdf` y propuso las decisiones D1–D7 con alternativas; el equipo escogió | No |
| 28-oct | Esquemático v2 | Con la retroalimentación del profesor (R-F02), rediseñó el esquemático en una hoja A1 y escribió una guía de estudio bloque a bloque | Sí (script de dibujo) |
| 03-nov | Código v2 | Escribió los módulos en SystemVerilog, los testbenches y el XDC a partir del esquemático v2 | Sí |
| 10-nov | Diseño v3 | Con la retroalimentación del profesor (R-F03), simplificó el diseño (D15–D22) y redactó las respuestas a las preguntas del profesor | Sí |
| 17-nov | Diseño v4 | Rediseñó todo el esquemático para simplificarlo (D23–D35), escribió el código, los testbenches, el generador del esquemático y `Explicacion_v4.pdf`, y corrió las simulaciones | Sí |
| 17-nov | Herramientas | Instaló en el computador de Edison las librerías de Python (pyserial, pillow, numpy, matplotlib) | No |
| 18-nov | Vivado | Instaló Vivado ML Standard 2025.2, generó los XDC desde el maestro oficial de Digilent, el script Tcl del proyecto y el script de Python; corrió la simulación, la síntesis y la implementación en Vivado | Sí |
| 18-nov | Cierre de tiempos (v4.1) | Encontró en el reporte de Vivado que la v4 no cumplía tiempos y agregó el registro de segmentación (D36); actualizó el esquemático y la explicación a v4.1 | Sí |
| 18-nov | Estudio | Explicó bloque por bloque `uart_rx` y `pos_counter` con ejemplos numéricos | No |
| 19-nov | Repositorio | Organizó el repositorio con la versión v4.1: actualizó la documentación, corrigió comentarios desactualizados del código y reescribió el script de Vivado para que cree el proyecto desde el repositorio | Sí (ajustes menores) |
| 23-nov | Prueba en la tarjeta | En el computador de Edison programó la tarjeta y corrió la prueba (los interruptores y botones los manejamos nosotros). Escribió la primera versión del script de prueba `prueba_fpga.py`, que enviaba una imagen generada y, solo para la prueba, comparaba la respuesta con un modelo. Encontró por qué la primera imagen después de programar llegaba corrida un byte y propuso tres soluciones; nosotros escogimos presionar CPU RESET (D37). Escribió una guía de uso paso a paso | Sí (script de prueba) |
| 23-nov (noche) | Script de demostración | Hizo una versión corta de `prueba_fpga.py` (95 líneas, sin comentarios y sin el modelo): solo abre la imagen, la envía, recibe la respuesta y muestra las dos (R-F01). Es la que está en el repositorio | Sí |
| 24-nov | Repositorio final | A pedido nuestro, reescribió el README y la documentación en lenguaje sencillo, agregó la prueba en la tarjeta y la decisión D37, quitó los comentarios de todo el código y agregó la versión corta de `prueba_fpga.py` (con la imagen de prueba del repositorio en vez de una ruta de nuestro computador) y las imágenes que devolvió la tarjeta. Comprobó que el código quedó igual: mismas pruebas, misma síntesis y mismo esquemático (ver `docs/04_verificacion.md`, sección 5) | Sí (solo se quitaron comentarios) |

## 4. Qué generó la IA, archivo por archivo

| Archivo o carpeta | Qué hizo la IA | Qué hizo el equipo |
|---|---|---|
| `rtl/*.sv` | Escribió los 10 módulos siguiendo el esquemático v4.1 | Pidió los rediseños con la retroalimentación del profesor y debe explicar cada módulo (sección 8) |
| `tb/*.sv` | Escribió los 10 testbenches autoverificables y el modelo de referencia dentro de `tb_image_proc_top` | Corrió la simulación del sistema en Vivado |
| `sim/` | `run_all.sh`, `syn.ys`, `full/hex2png.py`, `wave/tb_wave.sv` y `wave/plot_wave.py` | — |
| `constraints/*.xdc` | Copió las líneas necesarias del XDC maestro oficial de Digilent y les cambió los nombres de puerto | Confirmó en la prueba del 23-nov que funciona en nuestra tarjeta (Nexys 4 DDR) |
| `vivado/configurar_proyecto.tcl` | Script que crea el proyecto de Vivado con las fuentes y la parte correcta | — |
| `python/procesar_imagen.py` | Script que carga, envía, recibe y muestra la imagen (sin cálculos sobre los píxeles, R-F01) | Debe probarlo con la tarjeta |
| `docs/esquematico/` | Dibujó el esquemático con un programa en Python que genera SVG (`generador/`) | Lo revisó y lo presentó en los avances |
| `docs/explicacion/` | Escribió el documento de explicación bloque por bloque (LaTeX) y sus figuras | Lo usa para estudiar |
| `docs/*.md` | Redactó los documentos a partir de las conversaciones y las decisiones del equipo | Tomó las decisiones y trajo la retroalimentación del profesor |
| `README.md` | Lo redactó; la versión en lenguaje sencillo es del 24-nov | Pidió que fuera sencillo y sin tecnicismos |
| Comentarios del código | Los quitó de todos los archivos de código el 24-nov, sin cambiar nada más | Lo pidió |
| `python/prueba_fpga.py` | Escribió la versión de la prueba del 23-nov y después la versión corta para la demostración, que es la que está aquí | Manejó la tarjeta durante la prueba |
| `docs/prueba_tarjeta/` | Copió del computador de Edison las imágenes que devolvió la tarjeta y las aumentó 3 veces para verlas mejor | Son las salidas reales de la tarjeta en nuestra prueba |

## 5. Lo que no hizo la IA

- No presentó los avances ni habló con el profesor.
- No tomó por nosotros las decisiones de qué proyecto, qué tarjeta ni qué nivel de complejidad usar.
- La retroalimentación del profesor (R-F01, R-F02, R-F03) la trajimos nosotros de cada avance.

## 6. Instrucciones (prompts) principales

### Instrucciones fijas del proyecto

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

### Mensajes que guiaron cada etapa

Los mensajes de octubre se copian tal como se escribieron, con su ortografía original. Los de noviembre
están resumidos.

| Etapa | Mensaje |
|---|---|
| Elección | "Actúa como un ingeniero electrónico experto en Electrónica Digital… Necesito que me propongas únicamente 3 opciones de proyectos… No inventes los requisitos del profesor." |
| Elección | "Vamos a hacer el proyecto #8 […] por lka parte del codigo con IA en clase se hablo con profesor y lo que necistamos es entender como funciona el codigo entero" |
| Planteamiento | "Nombres: Edison Torres y Juan Guaman, cuando acabe Explique cada uno de los filtros, como va a hacer q se puedan usar 2 diferentes individual y 2 combinados […]" |
| Guía del profesor | "revise el archivo Implementacion_Operaciones_puntuales pdf esta es una guia del profesor para hacer el proyecto y es el archivo mas IMPORTANTE, En la retroalimentacion nos dijo que podemos usar phyton para cargar y leer la imagen pero la parte del hardware y la matematica tiene que hacerse desde la FPGA" |
| Decisiones | "Analice el PDF de nuevo y tome decisiones para las predicciones pendientes pensando en lago no mediocre pero simple y que se pueda entender […]" |
| Esquemático v1 | "Necesito entregar un adelanto, preferiblemente un diagrama o dibujo relacionado junto la explicacion y planeacion de como vamos a realizar el proyecto" |
| Esquemático v2 | "El profesor me dijo que los diagramas de multiplexsores deben estar mas a detalle y la arquitectura deberia ser continua, osea no por partes, Haga todo el diseño de forma mas profesional" |
| Guía de estudio | "AHORA EXPLIQUEME EL ESQUEMATICO BLOQUE POR BLOQUE, CREE UNA PRESENTACION O PDF DONDE EXPLIQUE QUE HACE CADA COSA […] USE LOS NOMBRES COMPLETOS […]" |
| Código v2 | "Según la guía del esquemático haga el codigo para viviado […] que quede lo mejor y sencillo de entender posible siguiendo tambien la presentacion del profesor" |
| Diseño v3 | Con la retroalimentación del 10-nov: quitar lo que sobraba y explicar TAP_CNT y las señales de control |
| Diseño v4 | Simplificar todo el esquemático sin perder funciones, dibujar cada conexión como un cable (sin etiquetas que entran y salen), hacer un PDF que explique cada bloque y simular antes de entregar |
| Vivado | Instalar Vivado, organizar el código por secciones ("qué poner en cada espacio") e indicar paso a paso cómo cargarlo, simularlo y programar la tarjeta |
| Estudio | Explicar bloque por bloque el código y el esquemático |
| Prueba en la tarjeta | Conectar la tarjeta y probarla; dejar como está lo del primer byte corrido (presionar CPU RESET) y hacer una guía paso a paso para usar el proyecto desde cero |
| Script de demostración | Hacer el script de Python más corto y sin comentarios |
| Repositorio final | Terminar el repositorio de forma sencilla, sin tantos tecnicismos, y quitar los comentarios de todo el código |

## 7. Cómo verificamos el código generado

1. **Testbenches autoverificables:** cada módulo tiene su testbench y todos terminan en PASS
   (ver [`docs/04_verificacion.md`](docs/04_verificacion.md)).
2. **Sistema completo contra un modelo de referencia:** la imagen de 128 × 128 en los 5 modos y con ruido coincide
   byte a byte con el modelo (491 529 comparaciones en Icarus; 4 441 verificaciones con la imagen de 8 × 8 en Vivado).
3. **Vivado:** síntesis e implementación sin errores y con tiempos cumplidos a 100 MHz.
4. **Tarjeta (23-nov):** en una Nexys 4 DDR, los cinco modos sin ruido dieron 0 bytes distintos de 49 152
   comparados con el modelo (ver [`docs/04_verificacion.md`](docs/04_verificacion.md), sección 4).
5. **Después de quitar los comentarios (24-nov):** las 10 pruebas, la imagen completa, la síntesis con Yosys
   y el esquemático dieron exactamente lo mismo que antes.

## 8. Revisión del equipo

Cada integrante marca los módulos que puede explicar sin mirar la documentación.

| Módulo | Edison Torres | Juan Guaman |
|---|---|---|
| `uart_rx` | | |
| `noise_gen` | | |
| `pos_counter` | | |
| `bram_sdp` | | |
| `tap_seq` | | |
| `conv_mac` | | |
| `post_proc` | | |
| `uart_tx` | | |
| `ctrl` | | |
| `image_proc_top` | | |
| `procesar_imagen.py` | | |
