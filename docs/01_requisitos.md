# Requisitos del proyecto #8: Image Processor (2D filters)

Fuentes: `Projects-Proposals.pdf` (parte 1), `Requerimientos Mínimos parte 2.pdf` y la retroalimentación
del profesor en los avances. A cada requisito le pusimos un ID para poder rastrear en qué parte del diseño
se cumple. Las decisiones que se citan (Dxx) están en [`03_decisiones.md`](03_decisiones.md).

_Estado al 19 de noviembre de 2026._

## Requisitos generales

| ID | Requisito | Cómo lo cumplimos | Estado |
|---|---|---|---|
| R-G01 | Máximo 2 estudiantes por proyecto | Edison Torres y Juan Guaman | ✔ |
| R-G02 | Se puede usar cualquier FPGA | Digilent Nexys A7-100T / Nexys 4 DDR (Artix-7 XC7A100T) | ✔ |
| R-G03 | Testbench de cada módulo, probando todos los casos límite | Un testbench autoverificable por módulo en `tb/` (los de `tap_seq` y `post_proc` son exhaustivos) y un testbench del sistema completo que compara byte a byte con el modelo de referencia | ✔ (ver [`04_verificacion.md`](04_verificacion.md)) |
| R-G04 | Se puede agregar funcionalidad, pero no quitar la requerida | Extras: modo bypass (SW[2]), reprocesar con BTNC sin reenviar la imagen, LED con el modo y el estado | ✔ |
| R-G05 | Conocimiento profundo del proyecto, incluido el código hecho con IA | Explicación bloque por bloque (`docs/explicacion/`) y ensayo de preguntas | En progreso |
| R-G06 | Esquemático detallado con bloques funcionales (memorias, FSM, registros, sumadores, multiplexores, contadores…) y ancho de cada bus | Esquemático RTL v4.1 en una sola hoja A1, con todos los cables dibujados (`docs/esquematico/`) | ✔ |
| R-G07 | Mostrar avance en cada sesión de laboratorio | Avances de los miércoles (historial en `03_decisiones.md`) | Continuo |
| R-G08 | Documentar todo uso de IA (cómo, para qué, qué código generó) | [`AI_USAGE.md`](../AI_USAGE.md) | ✔ |
| R-G09 | Informe final de 6 páginas en plantilla IEEE (PDF): Introducción, Solución y metodología, Configuración experimental, Resultados experimentales, Conclusiones, Referencias (máx. 10) | `docs/informe/` | Pendiente |
| R-G10 | Repositorio en GitHub con los dos estudiantes como colaboradores | Este repositorio | Falta verificar que Juan sea colaborador |
| R-G11 | README que explique cómo reproducir el proyecto | [`README.md`](../README.md) | ✔ |
| R-G12 | Enviar el enlace del repositorio el día antes de la evaluación | Martes 24 de noviembre | Pendiente |
| R-G13 | Presentación oral de 10 min + 5 min de preguntas | `docs/presentacion/` | Pendiente |

## Requisitos específicos del proyecto #8

| ID | Requisito (resumen del enunciado) | Cómo lo cumplimos | Estado |
|---|---|---|---|
| R-P1 | Cuatro filtros sobre una imagen **a color**, "using two different filters individually and combined": Gaussian, Laplacian, LoG, Unsharp | Dos filtros base (Gaussiano y Laplaciano) usados solos y combinados: LoG = Laplaciano aplicado al Gaussiano (dos pasadas) y Unsharp = 2·I − G (un solo kernel, D25) | Simulado ✔ · falta prueba en la tarjeta |
| R-P2 | Interfaz basada en el protocolo RS232 para recibir la imagen del PC y devolver el resultado | UART 8N1 a 115 200 baudios por el puente USB-UART de la tarjeta | Simulado ✔ · falta prueba en la tarjeta |
| R-P3 | Usar los switches de la tarjeta para elegir la operación | SW[1:0] filtro, SW[2] bypass, SW[4:3] densidad de ruido | Simulado ✔ · falta prueba en la tarjeta |
| R-P4 | Añadir ruido a las imágenes, por software en el PC o en hardware | Ruido sal y pimienta generado **en la FPGA** con un LFSR de 16 bits (D4, D31) | Simulado ✔ · falta prueba en la tarjeta |

## Retroalimentación del profesor

| ID | Fecha | Requisito o comentario | Cómo lo atendimos |
|---|---|---|---|
| R-F01 | 21-oct | Python solo para cargar, enviar, recibir y mostrar la imagen. Todo el hardware y la matemática se hacen en la FPGA | Los filtros y el ruido están en la FPGA. El script de Python no hace ningún cálculo sobre los píxeles |
| R-F02 | 28-oct | Los multiplexores deben estar más detallados y la arquitectura debe ser continua, en una sola hoja | Esquemático en una hoja A1 (D8) |
| R-F03 | 10-nov | El diseño tenía cosas de más (flip-flops de entrada, cabecera 0xAA, 3 BRAM, la parte final); explicar TAP_CNT y las señales de control | Diseño v3 (D15–D22) y luego v4 (D23–D35) |

## Preguntas al profesor

| # | Pregunta | Enviada | Respuesta |
|---|---|---|---|
| 1 | ¿Es válido que los dos filtros base sean el Gaussiano y el Laplaciano, y que LoG y Unsharp sean las combinaciones? | Por confirmar | — |
| 2 | ¿Es suficiente la UART 8N1 sobre el puente USB-UART, o exige niveles RS232 reales (MAX232 + DB9)? | Por confirmar | — |
| 3 | ¿Hay un tamaño mínimo de imagen? Usamos 128×128 RGB de 24 bits | Por confirmar | — |
| 4 | LoG como un único kernel de 5×5 ([0 1 2 1 0; 1 0 −2 0 1; 2 −2 −8 −2 2; 1 0 −2 0 1; 0 1 2 1 0]/16): eliminaría BRAM_TMP, MUX_SRC y el estado P2. ¿Cuenta como "combinado"? | 10-nov | Pendiente |
| 5 | Sin cabecera: ¿es aceptable resincronizar con CPU_RESETN si se pierde un byte? | 10-nov | Pendiente |
| 6 | ¿Está de acuerdo con la justificación para quitar los sincronizadores (D15)? | 10-nov | Pendiente |
| 7 | ¿Cuatro niveles de ruido (0 / 6,25 / 12,5 / 18,75 %) o solo encendido y apagado? | 10-nov | Pendiente |
| 8 | En la convolución usamos un multiplicador con signo (píxel sin signo × peso en complemento a 2). En la presentación 7 el multiplicador aparece sin signo. ¿Lo acepta así, o prefiere el multiplicador sin signo con la magnitud del peso y un sumador/restador controlado por el signo? | Por enviar | — |

## Relación con los temas del curso

| Bloque del proyecto | Tema del curso (presentación) |
|---|---|
| `uart_rx`, `uart_tx` | Registros de desplazamiento serie↔paralelo y contadores (8 – Sequential Logic Design) |
| `noise_gen` | Registro de desplazamiento con realimentación (LFSR), comparador y multiplexor (7 y 8) |
| `pos_counter` | Contadores con habilitación y borrado, comparadores de igualdad (7 y 8) |
| `bram_sdp` | Arreglos de memoria (7 – Comb Blocks), memoria y mapa de memoria (9 – Computer Architecture) |
| `tap_seq` | Contador, ROM, sumadores y multiplexores (7 y 8) |
| `conv_mac` | Multiplicador, sumador y registro acumulador (7 – Comb Blocks; multiplicador con signo en 9) |
| `post_proc` | Desplazamiento aritmético (÷16), negación en complemento a 2, comparador y multiplexores (7) |
| `ctrl` | FSM Moore y decodificador (8 – Sequential Logic Design, 7 – Comb Blocks) |

Notas:
- La UART solo se **menciona** en 9 – Computer Architecture (diapositiva 22). La usamos porque la exige R-P2 y la construimos solo con bloques vistos en clase.
- La convolución 2D no aparece en las presentaciones: es el contenido propio del proyecto (la exige R-P1). La implementamos con multiplicador, sumador y acumulador, siguiendo el estilo de la guía `5_Implementacion_Operaciones_Puntuales.pdf`.
- El multiplicador sin signo está en la presentación 7 (diapositivas 84–86) y la versión con signo en la 9 (diapositiva 97). Por eso está la pregunta 8.
