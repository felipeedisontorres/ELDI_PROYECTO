# Requisitos del proyecto #8: Image Processor (2D filters)

Fuentes: `Projects-Proposals.pdf` (parte 1) y `Requerimientos Mínimos parte 2.pdf`.
Cada requisito tiene un ID para poder rastrear en qué parte del diseño se cumple.

## Requisitos generales

| ID | Requisito | Cómo se cumple | Estado |
|---|---|---|---|
| R-G01 | Máximo 2 estudiantes por proyecto | Equipo de 2 | ✔ |
| R-G02 | Se puede usar cualquier FPGA | Nexys 4 DDR (Artix-7 XC7A100T) | ✔ |
| R-G03 | Testbench de cada módulo; la simulación debe probar todos los casos límite | Un testbench autoverificable por módulo (`tb/`) + testbench de sistema contra el modelo de referencia en Python | Pendiente |
| R-G04 | Se puede agregar funcionalidad, pero no quitar la requerida | Extras previstos: modo bypass, estado en 7 segmentos | Pendiente |
| R-G05 | Conocimiento profundo del proyecto, incluido el código generado por IA | Explicación módulo por módulo; ensayos de preguntas | Continuo |
| R-G06 | Esquemático detallado con bloques funcionales (memorias, FSM, registros, sumadores, multiplexores, contadores…) indicando el ancho de los buses | `docs/02_arquitectura.md` + diagramas en `docs/diagramas/` | En progreso |
| R-G07 | Mostrar avance en cada sesión de laboratorio | Plan de avances semanal | Continuo |
| R-G08 | Documentar todo uso de IA (cómo, para qué, qué código generó) | `AI_USAGE.md` | En progreso |
| R-G09 | Informe final de 6 páginas, plantilla IEEE, en PDF: Introducción, Solución y metodología, Configuración experimental, Resultados experimentales, Conclusiones, Referencias (máx. 10) | — | Pendiente |
| R-G10 | Repositorio en GitHub con ambos estudiantes como colaboradores | Este repositorio | En progreso |
| R-G11 | README que explique cómo reproducir el proyecto | `README.md` | En progreso |
| R-G12 | Enviar el enlace del repositorio el día antes de la evaluación | — | Pendiente |
| R-G13 | Presentación oral de 10 min + 5 min de preguntas | — | Pendiente |

## Requisitos específicos del proyecto #8

| ID | Requisito (resumen del enunciado) | Propuesta | Estado |
|---|---|---|---|
| R-P1 | Cuatro filtros sobre una imagen **a color**, "using two different filters individually and combined": Gaussian, Laplacian, LoG, Unsharp | Dos núcleos base (Gaussiano y Laplaciano) usados solos y combinados (LoG = L∘G; Unsharp = 2·I − G) | Pendiente (ver pregunta 1) |
| R-P2 | Interfaz basada en el protocolo RS232 para recibir la imagen del PC y devolver el resultado | UART 8N1 por el puente USB-UART de la tarjeta | Pendiente (ver pregunta 3) |
| R-P3 | Usar los switches de la tarjeta para elegir la operación | SW[2:0] | Pendiente |
| R-P4 | Añadir ruido a las imágenes, por software en el PC o en hardware | Ruido gaussiano y "sal y pimienta" desde Python | Pendiente |

## Preguntas para el profesor

1. **R-P1:** El enunciado dice "four different filters … using two different filters individually and combined". ¿Es válido que los dos filtros base sean el Gaussiano y el Laplaciano, y que LoG (Gaussiano y luego Laplaciano) y Unsharp (imagen + (imagen − Gaussiano)) sean las combinaciones? ¿O espera además poder encadenar dos filtros cualesquiera elegidos con los switches?
2. **R-P1:** ¿Se acepta implementar LoG como la cascada de dos kernels 3×3 (Gaussiano → Laplaciano), o debe ser un único kernel LoG (por ejemplo 5×5)?
3. **R-P2:** La Nexys 4 DDR trae un puente USB-UART. ¿Es suficiente implementar el protocolo UART (trama 8N1) sobre ese puente, o exige niveles eléctricos RS232 reales (transceptor tipo MAX232 y conector DB9)?
4. **R-P1:** ¿Hay un tamaño mínimo de imagen? Proponemos 128×128 píxeles RGB de 24 bits por la capacidad de memoria interna (BRAM).

| Pregunta | Fecha | Respuesta del profesor |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |

## Relación con los temas del curso

| Bloque del proyecto | Tema del curso (presentación) |
|---|---|
| UART (recepción/transmisión) | Registros de desplazamiento serie↔paralelo, contadores, FSM (8 – Sequential Logic Design) |
| Sincronización de la entrada RX | Sincronizadores (8 – Sequential Logic Design) |
| Buffers de imagen | Arreglos de memoria (7 – Comb Blocks), memoria y mapa de memoria (9 – Computer Architecture) |
| Kernels con sumas y desplazamientos | Circuitos aritméticos, sumadores, desplazadores (7 – Comb Blocks) |
| Selección de filtro | Multiplexores y decodificadores (7 – Comb Blocks) |
| Control general | FSM Moore/Mealy (8 – Sequential Logic Design) |

Notas:
- La UART solo se **menciona** en 9 – Computer Architecture (diapositiva 22), sin desarrollarse. Se usa porque la exige R-P2 y se construye con bloques vistos en clase.
- La convolución 2D no aparece en las presentaciones. Es el contenido propio del proyecto (la exige R-P1).

## Decisiones de diseño abiertas

| ID | Decisión | Opciones | Elegida |
|---|---|---|---|
| D1 | Manejo de bordes de la imagen | Replicar el borde / tomar ceros / copiar el píxel original | |
| D2 | Representación del Laplaciano negativo | Valor absoluto saturado / L + 128 saturado / saturar a 0 | |
| D3 | Factor k del Unsharp | Fijo k = 1 / seleccionable por switch (extra) | |
