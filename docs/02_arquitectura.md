# Arquitectura del sistema (versión 4.1)

Este documento es el resumen de cómo está armado el circuito. El esquemático completo, con todos los cables y
el ancho de cada bus, está en [`esquematico/esquematico_v4_1.pdf`](esquematico/esquematico_v4_1.pdf) (hoja A1).
La explicación bloque por bloque, con ejemplos con números, está en
[`explicacion/Explicacion_v4_1.pdf`](explicacion/Explicacion_v4_1.pdf).

## En palabras sencillas

La imagen llega por el cable un byte a la vez: primero el rojo, el verde y el azul del primer píxel, después
los del segundo, y así fila por fila. La FPGA guarda cada byte en una memoria interna (BRAM_IN) y, si se pidió,
cambia algunos píxeles por blanco o negro, que es el ruido.

Cuando llega el último byte empieza el filtrado. Para cada byte de la imagen el circuito lee de la memoria sus
9 vecinos, uno por uno, los multiplica por los pesos del filtro y los va sumando. Al final divide entre 16, deja
el resultado entre 0 y 255 y lo manda de vuelta por el cable. Como el cable es mucho más lento que el cálculo,
el circuito calcula un byte, espera a que el transmisor quede libre y sigue con el siguiente.

El LoG es el único filtro que necesita dos pasadas. La primera calcula el Gaussiano y lo guarda en otra memoria
(BRAM_TMP); la segunda le aplica el Laplaciano a eso y lo envía.

## Datos generales

| Qué | Valor | Por qué |
|---|---|---|
| Reloj | 100 MHz, uno solo para todo el circuito | Así ninguna señal tiene que pasar de un reloj a otro. Los bloques lentos usan señales de habilitación (enable) |
| Reset | Síncrono (actúa en el flanco del reloj), con el botón CPU RESET | Es el estilo de la presentación 8 |
| Imagen | 128 × 128 píxeles a color, 24 bits por píxel (8 por cada color) | 128 es potencia de 2, así la dirección de memoria se arma solo con cables |
| Camino de datos | 1 byte (un color a la vez) | D23: es el mismo orden en que llegan y salen los bytes por el cable |
| Dirección de memoria | 16 bits = {fila (7 bits), columna (7 bits), color (2 bits)} | D24: un vecino se encuentra sumando ±1 a la fila y a la columna |
| Memorias | BRAM_IN y BRAM_TMP, de 65 536 × 8 bits cada una, con lectura síncrona (el dato sale un ciclo después de pedirlo) | D24. BRAM_TMP solo se usa en el LoG |
| Comunicación | UART (Universal Asynchronous Receiver-Transmitter) a 115 200 baudios, 8 bits de datos, sin paridad y 1 bit de parada. Cada bit dura 868 ciclos de reloj | 100 000 000 / 868 ≈ 115 207 baudios, un error de apenas 0,006 % |
| Bytes por imagen | 49 152 en cada sentido, fila por fila, y en cada píxel rojo, verde y azul | Sin cabecera (D17) |
| Tiempo del cable | 49 152 × 10 bits / 115 200 ≈ 4,27 s en cada sentido | Cada byte lleva 10 bits: el de inicio, los 8 de datos y el de parada |
| Tiempo de cálculo | 12 ciclos por byte, o sea 12 × 49 152 ≈ 5,9 ms por pasada sin contar el cable | En la última pasada el ritmo lo pone el cable: sale un byte cada 8 681 ciclos |

```

Los números sobre las flechas son el ancho del bus en bits. Este dibujo solo muestra el camino principal; el
esquemático en PDF es el que vale.

## Bloques

Los nombres en mayúscula (BAUD_RX, SR_TX, MUX_A…) son los nombres que tiene cada pieza en el esquemático y en
el código. Las abreviaturas que se repiten son: MUX, multiplexor; SR, registro de desplazamiento (shift
register); REG, registro; ACC, acumulador; ROM, memoria de solo lectura (Read-Only Memory); FSM, máquina de
estados (Finite State Machine); LFSR, registro de desplazamiento con realimentación lineal (Linear Feedback
Shift Register).

| # | Módulo (`rtl/`) | Qué hace | Piezas que lo forman |
|---|---|---|---|
| 1 | `uart_rx` | Convierte los bits que llegan por el cable en un byte y avisa con `rx_valid` (un pulso de 1 ciclo) | RX_BUSY + MUX_BUSY, BAUD_RX que cuenta hasta 868 (10 bits; muestrea en 433, la mitad del bit), BIT_RX de 4 bits (`rx_valid` en la muestra 9) y SR_RX de 8 bits (D32) |
| 2 | `noise_gen` | Cambia algunos píxeles por blanco o negro (sal y pimienta) | LFSR de 16 bits (x¹⁶+x¹⁴+x¹³+x¹¹+1, semilla 0xACE1), XOR de 4 entradas, NOR → `lfsr_en`, desplazador «4, comparador <, {8{lfsr[8]}} y MUX_RUIDO (D31) |
| 3 | `pos_counter` | Lleva la posición {fila, columna, color} del byte actual | CH de 2 bits, COL de 7 bits y ROW de 7 bits en cascada; comparadores =2 y =127; compuertas AND → `e_col`, `e_row`, `fin` (D27) |
| 4 | `bram_sdp` (×2) | Guarda la imagen recibida (BRAM_IN) y el resultado intermedio del LoG (BRAM_TMP) | 65 536 × 8 bits, un puerto de escritura y uno de lectura síncrona (D24) |
| 5 | `tap_seq` | Recorre los 9 vecinos del byte actual y calcula su dirección; en los bordes repite el borde | Contador TAP de 4 bits (0 a 11), ROM_OFF (taps 0 a 8 recorren los vecinos, 9 a 11 apuntan al centro), sumadores de 8 bits + MUX_ROW/MUX_COL → `naddr` (D28, D29, D36) |
| 6 | `conv_mac` | Multiplica cada vecino por su peso y va acumulando (MAC, Multiply-Accumulate) | REG_PIX, REG_W, ROM_W {ksel, tap}, multiplicador de 9 × 8 bits con signo, sumador y ACC de 15 bits que se borra en tap = 0 (D25, D36) |
| 7 | `post_proc` | Divide entre 16, saca el valor absoluto cuando toca y deja el resultado entre 0 y 255 | ÷16 con cables, negador, MUX_A, MUX_B, comparador >255 y MUX_SAT → `y` de 8 bits (D26) |
| 8 | `uart_tx` | Envía el byte `y` por el cable | SR_TX de 10 bits (carga {1, y, 0}), BIT_TX de 4 bits que cuenta hacia abajo y BAUD_TX que cuenta hasta 868 (D33) |
| 9 | `ctrl` | Decide qué se hace en cada momento | FSM de Moore de 2 bits (IDLE 00, P1 01, P2 10), registro MODE de 3 bits (solo se actualiza en IDLE) y decodificador → `ksel`, `absm`, `src_tmp`, `tmp_wr`, `idle`, `two_pass`; compuertas para `wr_in`, `cnt_en`, `tap_en`, `go` y `tx_start` (D30) |
| — | `image_proc_top` | Conecta todos los bloques con los pines de la tarjeta | — |

## Modos de operación

IDLE es el estado de espera, P1 la primera pasada y P2 la segunda (solo para el LoG).

| SW2 | SW1 SW0 | Modo | Tabla de pesos (`ksel`) | Pasada P1 | Pasada P2 |
|---|---|---|---|---|---|
| 0 | 00 | Gaussiano | G | BRAM_IN → cable | — |
| 0 | 01 | Laplaciano | 16·L, con valor absoluto | BRAM_IN → cable | — |
| 0 | 10 | LoG | G y después 16·L | BRAM_IN → BRAM_TMP | BRAM_TMP → cable |
| 0 | 11 | Unsharp | US = 32δ − G | BRAM_IN → cable | — |
| 1 | cualquiera | Bypass | 16·δ | BRAM_IN → cable | — |

## Tablas de pesos

Cada filtro es una tabla de 3 × 3 pesos (en inglés se llama *kernel*). Para que todos usen el mismo camino de
datos, las tablas están multiplicadas por 16 y al final siempre se divide entre 16. Dividir entre 16 es tomar
los bits `acc[14:4]` del acumulador, o sea, solo cables. δ es la tabla "identidad": un 1 en el centro y 0 en el
resto, que deja la imagen igual.

```
Gaussiano (G)        16·Laplaciano (16·L)     Unsharp (US = 32δ − G)    Bypass (16·δ)
 1  2  1               0  16   0               −1  −2  −1                 0   0   0
 2  4  2              16 −64  16               −2  28  −2                 0  16   0
 1  2  1               0  16   0               −1  −2  −1                 0   0   0
```

Así un solo camino de datos sirve para los cinco modos.

## Recursos y tiempos (Vivado 2025.2, FPGA xc7a100tcsg324-1, después de la implementación)

| Recurso | Usado | Qué es |
|---|---|---|
| LUT | 313 | Look-Up Table: las celdas de lógica de la FPGA |
| Flip-flops | 137 | Los bits de memoria de los registros |
| RAMB36 | 32 (23,7 %) | Bloques de memoria interna de 36 kilobits |
| DSP48 | 0 | Bloques de multiplicación (Digital Signal Processing). Vivado armó el multiplicador con LUT |
| IOB | 18 | Input/Output Blocks: los pines que usa el diseño |
| WNS a 100 MHz | +2,112 ns (cumple) | Worst Negative Slack: lo que le sobra al camino más lento dentro del periodo de 10 ns. Si es positivo, el diseño cumple los tiempos |
