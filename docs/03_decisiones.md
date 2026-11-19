# Decisiones de diseño (D1–D36)

Cada decisión tiene las alternativas que descartamos, el motivo y el requisito que cumple
(ver [`01_requisitos.md`](01_requisitos.md)). Las decisiones que una versión posterior reemplazó se dejan
tachadas para que se vea cómo evolucionó el diseño.

Base de todo el diseño: la guía del profesor `5_Implementacion_Operaciones_Puntuales.pdf` (datapath con
anchos de bus, constantes, comparadores + MUX para saturar y líneas punteadas para las etapas de registro)
y la retroalimentación R-F01 (la matemática va en la FPGA; Python solo carga, envía, recibe y muestra).

## Historial de versiones

| Versión | Fecha | Qué cambió | Por qué |
|---|---|---|---|
| v1 | 21-oct | Arquitectura base: 3 BRAM de 16 384 × 24 b, convolución 3×3 secuencial, UART 8N1. Esquemático por bloques | Primer avance |
| v2 | 28-oct | Esquemático en una sola hoja A1 con 21 multiplexores numerados (D8–D10). Primer código en SystemVerilog (D11–D14) | R-F02: MUX más detallados y arquitectura continua |
| v3 | 10-nov | Sin sincronizadores, sin antirrebote, sin cabecera ni timeout, 2 BRAM en vez de 3, sin los estados RECV y SEND (D15–D22) | R-F03: el diseño tenía cosas de más |
| v4 | 17-nov | Camino de datos de 1 byte, kernels en ROM con un multiplicador, un solo contador de posición, FSM de 3 estados, esquemático con todos los cables dibujados (D23–D35) | Simplificar sin perder funciones y que se vea a qué se conecta cada cosa |
| **v4.1** | **18-nov** | Registro de segmentación antes del multiplicador (D36) | En Vivado la v4 no cumplía tiempos a 100 MHz |

## Decisiones vigentes y reemplazadas

| ID | Decisión | Alternativas descartadas | Motivo | Requisito |
|---|---|---|---|---|
| D1 | Bordes: **se replica el borde** (la coordenada del vecino se limita a 0..127) | Ceros (marco oscuro y bordes falsos en el Laplaciano) / copiar el original (el borde queda sin filtrar) | No deja artefactos. En hardware es un sumador + MUX (D28) | R-P1 |
| D2 | Laplaciano y LoG: **valor absoluto saturado a 255** | L+128 (poco contraste) / saturar a 0 (se pierde la mitad de los bordes) | Bordes claros sobre fondo negro | R-P1 |
| D3 | Unsharp con **k = 1 fijo**: 2·I − G, saturado a 0..255 | k seleccionable por switch | Es la definición clásica (desde v4 es un kernel más, D25) | R-P1 |
| D4 | Ruido **sal y pimienta en la FPGA con un LFSR de 16 bits**; densidad con SW[4:3] | Ruido en Python (choca con R-F01) / ruido gaussiano en hardware | Cumple R-P4 y R-F01 a la vez | R-P4, R-F01 |
| ~~D5~~ | ~~Cabecera 0xAA + 49 152 bytes~~ → reemplazada por D17 | — | — | R-P2 |
| ~~D6~~ | ~~Timeout de recepción (TOUT_CNT de 24 b)~~ → reemplazada por D17 | — | — | R-P2 |
| D7 | Notación de la guía del profesor en todos los diagramas | — | Es la notación del profesor | R-G06 |
| D8 | **Esquemático RTL único y continuo** (hoja A1): pin RX → BRAM → procesamiento → pin TX, con el control y las tablas en la misma hoja | Figuras por bloque (v1) | Retroalimentación R-F02 | R-G06 |
| ~~D9~~ | ~~21 multiplexores M1–M21~~ → reemplazada por D22 y luego por D34 | — | — | R-G06 |
| D10 | Motor de convolución **secuencial**: lee los 9 vecinos uno por uno (la BRAM tiene 1 ciclo de latencia). Desde v4.1 son 12 ciclos por byte (D23, D36) | Line buffers / 9 lecturas en paralelo | La UART tarda 4,27 s por imagen, así que más velocidad no aporta. Además es más fácil de verificar y explicar | R-P1, R-G05 |
| D11 | HDL: **SystemVerilog con el estilo de las presentaciones 4 y 8** (`logic`, `always_ff` con reset síncrono, `always_comb` + `case`/`default`, `localparam` para los estados). Un archivo por bloque, con los mismos nombres de señales del esquemático | Verilog-2001 / `typedef enum` | Es el lenguaje de la presentación 8 y Vivado lo soporta | R-G06 |
| ~~D12~~ | ~~Salida rx_en (estado RECV)~~ → reemplazada por D18 | — | — | R-P2 |
| ~~D13~~ | ~~last_px = pix_valid · (WR_CNT = 16383)~~ → reemplazada por D27 | — | — | R-P2 |
| D14 | Parámetros (`LOG_W`, `CLKS_PER_BIT`) para simular el sistema con una imagen de 8×8 y 8 ciclos por bit; en la tarjeta son 7 (128×128) y 868 | Simular siempre 128×128 a 868 ciclos por bit | El hardware es el mismo y la simulación tarda segundos | R-G03 |
| D15 | **Sin sincronizadores**: los pines entran directo. Cada entrada asíncrona llega a un solo flip-flop de decisión (IDLE→P1 cambia 1 bit; `fsm_encoding = "none"`) o se lee a mitad de bit | 2 FF por entrada (v2) / 1 FF | Los FF eran por metaestabilidad, no por ruido. El peor caso es 1 ciclo de retraso | R-P2, R-P3 |
| D16 | **Sin antirrebote** en BTNC | DEB_CNT de 20 b + detector de flanco | La FSM solo mira BTNC en IDLE y no vuelve a IDLE antes de 4,27 s | R-P3 |
| D17 | **Sin cabecera ni timeout**: se envían 49 152 bytes y el contador de posición vuelve solo a 0 (D27). Si se pierde un byte, se resetea con CPU_RESETN | Cabecera 0xAA + TOUT_CNT | Menos hardware, y perder un byte es raro. Pregunta 5 al profesor | R-P2 |
| D18 | **Sin los estados RECV y SEND ni BRAM_OUT**: la última pasada envía cada byte apenas lo calcula y el secuenciador espera hasta que la UART está libre (`go`, D30) | BRAM_OUT + TX_ADDR + FSM_TX | Se pasa de 3 a 2 BRAM y de 5 a 3 estados | R-P2 |
| D19 | **ROM_W corrida un tap** (la fila t guarda el peso del vecino pedido en t−1) y los últimos taps apuntan al centro | TAP_D, pt_op, acc_en, M9 (v2) | El peso queda alineado con el dato que sale de la BRAM | R-P1 |
| ~~D20~~ | ~~Bordes con 2 MUX (M4, M5) y sumas de 9 b~~ → reemplazada por D28 | — | — | R-P1 |
| ~~D21~~ | ~~Unsharp en un carril aparte (d = 2·in_q − conv_y)~~ → reemplazada por D25. BRAM_TMP queda solo para el LoG | Unsharp en 2 pasadas | — | R-P1 |
| ~~D22~~ | ~~15 multiplexores M1–M15 (27 instancias)~~ → reemplazada por D34 | — | — | R-G06 |
| D23 | **Camino de datos serial de 1 byte (8 b)**: se calcula un canal por vez, en el mismo orden en que llega y sale por la UART (R, G, B de cada píxel) | 3 carriles de 8 b en paralelo (v3: SR_PIX, TX_BYTE, M14) | El cuello de botella es la UART. La pasada sube de ≈1,8 ms a ≈5,4 ms (5,9 ms desde v4.1), invisible frente a 4,27 s. Desaparecen el ensamblador de píxel, TX_BYTE, M14 y dos carriles | R-P1, R-P2 |
| D24 | **2 memorias de 65 536 × 8 b**, con dirección {fila 7 b, col 7 b, canal 2 b}. El canal 3 no se usa (25 % de la memoria) | 2 × 16 384 × 24 b (v3) | El vecino sale de sumar ±1 a la fila y a la columna, sin multiplicar por 3: la dirección son solo cables | R-P1 |
| D25 | **Kernels ×16 en ROM_W** {ksel 2 b, tap 4 b}: G, 16·L, 16·δ (bypass) y US = 32δ − G ([−1 −2 −1; −2 28 −2; −1 −2 −1]). Normalización fija ÷16 = acc[14:4] (son cables; desplazamiento aritmético, presentación 7, diap. 82). **Multiplicador con signo {0,pix} (9 b) × w (8 b)** y acumulador de 15 b | Pesos por desplazamiento (M7 0/×1/×2/×4) + M8–M13 (v3) / multiplicador sin signo con magnitud de 7 b + bit de signo y sumador/restador | Un solo camino para los 5 modos: Unsharp y bypass no necesitan hardware extra. La alternativa sin signo da el mismo resultado y es la que usaríamos si el profesor la pide (pregunta 8) | R-P1, R-G04 |
| D26 | **post_proc de 11 b**: s = acc[14:4]; MUX_A (absm ? −s : 0), MUX_B (s[10] ? a : s), comparador >255 + MUX_SAT. Equivale a D2 y D3 | 10 b | Con 10 b, acc = −16 384 daba 0 en vez de 255. Lo encontró el testbench exhaustivo de `post_proc` | R-P1 |
| D27 | **Un solo contador de posición {ROW, COL, CH}** compartido: cnt_en = wr_in + go; fin = e_row · (row = 127). En IDLE `fin` significa "imagen recibida" y en P1/P2 "pasada terminada" | WR_CNT + BYTE_CNT + COL/ROW_CNT (v3) | Un contador y una sola señal `fin` para la FSM | R-P2 |
| D28 | **Bordes con sumador de 8 b**: rsum = {0,row} + ext(dr); si el MSB es 1, el vecino está fuera y MUX_ROW/MUX_COL dejan la fila o columna actual | Comparadores =0 / =127 (v3) | La suma cae en [−1, 128]; en 8 b solo −1 y 128 tienen el MSB en 1 | R-P1 |
| D29 | Secuenciador TAP: CLR = go y EN = NOR(último tap, idle); acc_clr = (tap = 0). En el último tap el peso es 0 y el acumulador se mantiene mientras espera la UART | Señales de enable aparte | Menos compuertas; se mantiene D19 | R-P1 |
| D30 | Control mínimo: wr_in = rx_valid·idle (los bytes que llegan mientras procesa se ignoran), go = último_tap·¬tx_busy, tx_start = go·¬tmp_wr, we_tmp = tmp_wr | WE de BRAM_TMP = tmp_wr·go | En la P1 del LoG, la última escritura de cada dirección ocurre en `go`, con el valor correcto | R-P2 |
| D31 | **Ruido**: el LFSR corre libre (lfsr_en = NOR(ch[1], ch[0], wr_in)) mientras espera el byte R y se congela durante R, G y B. Umbral = SW[4:3]·16 (0 / 6,25 / 12,5 / 18,75 %) con un desplazador; valor = {8{lfsr[8]}}; MUX_RUIDO de 8 b | Un paso por píxel (ruido en rayitas, porque dos decisiones seguidas comparten 7 de 8 bits) / umbral 0/8/16/32 (v3) | Decisiones independientes y los 3 canales reciben la misma decisión. Consecuencia: el patrón cambia en cada envío | R-P4 |
| D32 | **uart_rx sin FSM**: RX_BUSY (MUX_BUSY: busy ? ¬rx_valid : ¬rx), BAUD_RX módulo 868, BIT_RX de 4 b y SR_RX que desplaza en cada muestra; rx_valid = sample·(bit = 9) | FSM_RX de 4 estados (v3) | Menos estado: el "estado" es el número de muestra | R-P2 |
| D33 | **uart_tx**: tx = SR_TX[0] (el registro se rellena con unos) y BIT_TX descendente (≠0 → busy). No se protege contra un start con busy = 1 porque `go` nunca lo produce | M15 a la salida (v3) | Un MUX menos | R-P2 |
| D34 | **Esquemático v4**: una hoja A1 con todos los cables dibujados (sin etiquetas que entran y salen), puntos en las uniones, saltos en los cruces y peines de reloj y reset. 8 MUX: MUX_BUSY, MUX_RUIDO, MUX_SRC, MUX_ROW, MUX_COL, MUX_A, MUX_B y MUX_SAT | Etiquetas de red (v3) | Que se vea a qué se conecta cada cosa | R-G06 |
| D35 | LED = {state, 000, mode} | — | Extra de depuración | R-G04 |
| **D36** | **Registro de segmentación en el MAC (v4.1)**: REG_PIX y REG_W registran el píxel (salida de MUX_SRC) y el peso antes del multiplicador; TAP cuenta 0..11 (`at11`), ROM_OFF taps 9–11 = centro; el resultado está listo en el tap 11 (12 ciclos por byte) | Bajar el reloj (requiere MMCM, fuera del curso) / multiplicador sin registros (margen dudoso) | En Vivado la v4 no cumplía tiempos: camino BRAM → multiplicador → sumador → ACC = 11,35 ns > 10 ns (WNS −1,669 ns). Con el registro: WNS +2,112 ns | R-P1 |

## Diferencias de comportamiento entre v3 y v4

- Densidades de ruido: 0 / 6,25 / 12,5 / 18,75 % (antes 0 / 3,1 / 6,25 / 12,5 %).
- El patrón de ruido cambia en cada envío porque el LFSR corre libre (D31).
- Unsharp: ⌊(32I − G₁₆)/16⌋ en vez de 2I − ⌊G₁₆/16⌋. Pueden diferir en 1 nivel en algunos píxeles.
- El LoG sale oscuro, y es lo correcto: el Gaussiano suaviza antes de derivar.

## Asignación de entradas y salidas

| Señal | Función |
|---|---|
| SW[1:0] | Filtro: 00 Gaussiano · 01 Laplaciano · 10 LoG · 11 Unsharp |
| SW[2] | Bypass (devuelve la imagen sin filtrar, con ruido si está activo) |
| SW[4:3] | Densidad de ruido: 00 sin ruido · 01 6,25 % · 10 12,5 % · 11 18,75 % |
| BTNC | Reprocesar la imagen guardada con el modo actual, sin reenviarla |
| CPU_RESETN | Reset (también para resincronizar si se pierde un byte) |
| LED[2:0] | MODE |
| LED[7:6] | STATE (00 IDLE, 01 P1, 10 P2) |
