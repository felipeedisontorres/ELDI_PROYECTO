# Requisitos del proyecto #8: Image Processor (2D filters)

Aquí están todos los requisitos que tenemos que cumplir y dónde se cumple cada uno. Salen de tres lugares:
`Projects-Proposals.pdf` (parte 1), `Requerimientos Mínimos parte 2.pdf` y lo que nos dijo el profesor en los
avances. A cada requisito le pusimos un código (por ejemplo R-G03) para poder rastrearlo en el diseño. Las
decisiones que se mencionan (D1, D2…) están explicadas en [`03_decisiones.md`](03_decisiones.md).

_Estado al 24 de noviembre de 2026._

## Requisitos generales del curso

| Código | Requisito | Cómo lo cumplimos | Estado |
|---|---|---|---|
| R-G01 | Máximo 2 estudiantes por proyecto | Somos Edison Torres y Juan Guaman | ✔ |
| R-G02 | Se puede usar cualquier FPGA (Field-Programmable Gate Array) | Digilent Nexys 4 DDR / Nexys A7-100T, con la FPGA Artix-7 XC7A100T | ✔ |
| R-G03 | Una prueba (testbench) de cada módulo que revise todos los casos límite | Cada bloque tiene su testbench en `tb/` que revisa solo las salidas y dice PASS o FAIL. Los de `tap_seq` y `post_proc` prueban todas las combinaciones posibles. Además hay una prueba del sistema completo que compara cada byte con un modelo de referencia | ✔ (ver [`04_verificacion.md`](04_verificacion.md)) |
| R-G04 | Se puede agregar funcionalidad, pero no quitar la que se pide | Agregamos el modo bypass (SW2), el botón BTNC para reprocesar sin reenviar la imagen y los LED (Light-Emitting Diodes) que muestran el modo y el estado | ✔ |
| R-G05 | Entender a fondo el proyecto, incluido el código hecho con IA (inteligencia artificial) | Estudiamos con la explicación bloque por bloque (`docs/explicacion/`) y ensayamos las preguntas | Se demuestra en la sustentación del 25 de noviembre |
| R-G06 | Esquemático detallado con bloques funcionales (memorias, máquina de estados, registros, sumadores, multiplexores, contadores…) y el ancho de cada bus | Esquemático v4.1 en una sola hoja A1, con todos los cables dibujados (`docs/esquematico/`) | ✔ |
| R-G07 | Mostrar avance en cada sesión de laboratorio | Avances de los miércoles (el historial está en `03_decisiones.md`) | Continuo |
| R-G08 | Documentar todo uso de IA: cómo, para qué y qué código generó | [`AI_USAGE.md`](../AI_USAGE.md) | ✔ |
| R-G09 | Informe final de 6 páginas en plantilla IEEE (Institute of Electrical and Electronics Engineers), en PDF: introducción, solución y metodología, configuración experimental, resultados experimentales, conclusiones y referencias (máximo 10) | Informe aparte, en PDF | ✔ |
| R-G10 | El proyecto debe estar en GitHub, con los dos estudiantes como colaboradores | Este repositorio | Falta confirmar en GitHub (Settings → Collaborators) que Juan esté como colaborador |
| R-G11 | README que explique cómo reproducir el proyecto | [`README.md`](../README.md) | ✔ |
| R-G12 | Enviar el enlace del repositorio el día antes de la evaluación | Martes 24 de noviembre | Se envía el 24 de noviembre |
| R-G13 | Presentación oral de 10 minutos más 5 de preguntas | Miércoles 25 de noviembre | Se presenta el 25 de noviembre |

## Requisitos propios del proyecto #8

| Código | Requisito (resumen del enunciado) | Cómo lo cumplimos | Estado |
|---|---|---|---|
| R-P1 | Cuatro filtros sobre una imagen **a color**, "using two different filters individually and combined": Gaussian, Laplacian, LoG y Unsharp | Dos filtros base, Gaussiano y Laplaciano, usados solos y combinados: el LoG (Laplacian of Gaussian) es el Laplaciano aplicado al resultado del Gaussiano (dos pasadas) y el Unsharp es 2 · imagen − Gaussiano (una sola tabla de pesos, D25) | ✔ Simulado y probado en la tarjeta (23-nov) |
| R-P2 | Comunicación basada en el protocolo RS232 para recibir la imagen del computador y devolver el resultado | UART (Universal Asynchronous Receiver-Transmitter) a 115 200 baudios, 8 bits de datos, sin paridad y 1 bit de parada, por el puente USB-UART que trae la tarjeta | ✔ Simulado y probado en la tarjeta (23-nov) |
| R-P3 | Usar los interruptores de la tarjeta para elegir la operación | SW1 y SW0 eligen el filtro, SW2 el bypass y SW4 y SW3 la cantidad de ruido | ✔ Simulado y probado en la tarjeta (23-nov) |
| R-P4 | Agregar ruido a las imágenes, por software en el computador o en hardware | Ruido sal y pimienta hecho **en la FPGA** con un LFSR (Linear Feedback Shift Register) de 16 bits (D4, D31) | ✔ Simulado. En la tarjeta se vio en bypass (cerca del 14 % de bytes cambiados, revisado a simple vista) |

## Lo que nos pidió el profesor en los avances

| Código | Fecha | Lo que pidió | Qué hicimos |
|---|---|---|---|
| R-F01 | 21-oct | Python solo para cargar, enviar, recibir y mostrar la imagen. Todo el hardware y la matemática van en la FPGA | Los filtros y el ruido están en la FPGA. El programa de Python no hace ninguna cuenta con los píxeles |
| R-F02 | 28-oct | Los multiplexores más detallados y la arquitectura continua, en una sola hoja | Esquemático en una hoja A1 (D8) |
| R-F03 | 10-nov | El diseño tenía cosas de más (flip-flops de entrada, cabecera 0xAA, 3 memorias, la parte final); explicar TAP_CNT y las señales de control | Diseño v3 (D15–D22) y luego v4 (D23–D35) |

## Preguntas al profesor

| # | Pregunta | Enviada | Respuesta |
|---|---|---|---|
| 1 | ¿Es válido que los dos filtros base sean el Gaussiano y el Laplaciano, y que el LoG y el Unsharp sean las combinaciones? | Por confirmar | — |
| 2 | ¿Es suficiente la UART sobre el puente USB-UART de la tarjeta, o pide niveles RS232 reales (con un MAX232 y un conector DB9)? | Por confirmar | — |
| 3 | ¿Hay un tamaño mínimo de imagen? Usamos 128 × 128 a color (24 bits por píxel) | Por confirmar | — |
| 4 | El LoG como una sola tabla de 5 × 5 ([0 1 2 1 0; 1 0 −2 0 1; 2 −2 −8 −2 2; 1 0 −2 0 1; 0 1 2 1 0]/16) eliminaría BRAM_TMP, MUX_SRC y el estado P2. ¿Cuenta como "combinado"? | 10-nov | Pendiente |
| 5 | Como no hay cabecera, ¿es aceptable volver a sincronizar con CPU RESET si se pierde un byte? | 10-nov | Pendiente |
| 6 | ¿Está de acuerdo con quitar los sincronizadores de las entradas (D15)? | 10-nov | Pendiente |
| 7 | ¿Cuatro niveles de ruido (0 / 6,25 / 12,5 / 18,75 %) o solo encendido y apagado? | 10-nov | Pendiente |
| 8 | En la convolución usamos un multiplicador con signo (píxel sin signo por peso en complemento a 2). En la presentación 7 el multiplicador aparece sin signo. ¿Lo acepta así, o prefiere el multiplicador sin signo con la magnitud del peso y un sumador/restador que dependa del signo? | Por enviar | — |

## Relación con los temas del curso

| Bloque del proyecto | Tema del curso (presentación) |
|---|---|
| `uart_rx`, `uart_tx` | Registros de desplazamiento serie ↔ paralelo y contadores (8 – Sequential Logic Design) |
| `noise_gen` | Registro de desplazamiento con realimentación (LFSR), comparador y multiplexor (7 y 8) |
| `pos_counter` | Contadores con habilitación y borrado, comparadores de igualdad (7 y 8) |
| `bram_sdp` | Arreglos de memoria (7 – Comb Blocks), memoria y mapa de memoria (9 – Computer Architecture) |
| `tap_seq` | Contador, ROM (Read-Only Memory, memoria de solo lectura), sumadores y multiplexores (7 y 8) |
| `conv_mac` | Multiplicador, sumador y registro acumulador (7 – Comb Blocks; multiplicador con signo en la 9) |
| `post_proc` | Desplazamiento aritmético (÷16), negación en complemento a 2, comparador y multiplexores (7) |
| `ctrl` | Máquina de estados de Moore y decodificador (8 – Sequential Logic Design, 7 – Comb Blocks) |

Notas:
- La UART solo se **menciona** en la presentación 9 – Computer Architecture (diapositiva 22). La usamos porque
  la pide R-P2, y la armamos solo con bloques vistos en clase.
- La convolución 2D (pasar una tabla de pesos de 3 × 3 por toda la imagen) no aparece en las presentaciones: es
  el tema propio del proyecto, y la pide R-P1. La hicimos con multiplicador, sumador y acumulador, siguiendo el
  estilo de la guía del profesor `5_Implementacion_Operaciones_Puntuales.pdf`.
- El multiplicador sin signo está en la presentación 7 (diapositivas 84 a 86) y la versión con signo en la 9
  (diapositiva 97). Por eso está la pregunta 8.
