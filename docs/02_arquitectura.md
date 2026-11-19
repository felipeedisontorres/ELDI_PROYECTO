# Arquitectura del sistema (v4.1)

El esquemático completo, con todos los cables y el ancho de cada bus, está en
[`esquematico/esquematico_v4_1.pdf`](esquematico/esquematico_v4_1.pdf) (hoja A1). La explicación bloque por
bloque, con ejemplos numéricos, está en [`explicacion/Explicacion_v4_1.pdf`](explicacion/Explicacion_v4_1.pdf).
Este documento es el resumen.

## Parámetros generales

| Parámetro | Valor | Justificación |
|---|---|---|
| Reloj | 100 MHz, un solo dominio de reloj | Evita cruces entre dominios; los bloques lentos usan señales de habilitación |
| Reset | Síncrono, desde el botón CPU_RESETN | Estilo de la presentación 8 |
| Imagen | 128 × 128 píxeles, RGB de 24 bits (8 por canal) | 128 es potencia de 2: la dirección se arma con cables |
| Camino de datos | 1 byte (un canal a la vez) | D23: mismo orden en que llegan y salen los bytes por la UART |
| Dirección de memoria | 16 b = {fila[6:0], col[6:0], canal[1:0]} | D24: el vecino se obtiene sumando ±1 a fila y columna |
| Memorias | BRAM_IN y BRAM_TMP, 65 536 × 8 b cada una, lectura síncrona | D24. BRAM_TMP solo se usa en el LoG |
| UART | 8N1, 115 200 baudios → 868 ciclos por bit | 10⁸ / 868 ≈ 115 207 Bd, error ≈ 0,006 % |
| Datos por imagen | 49 152 bytes en cada sentido (fila por fila, R-G-B por píxel) | Sin cabecera (D17) |
| Tiempo de UART | 49 152 × 10 bits / 115 200 ≈ 4,27 s en cada sentido | — |
| Tiempo de proceso | 12 ciclos por byte → 12 × 49 152 ≈ 5,9 ms por pasada sin contar la UART | En la última pasada el ritmo lo pone la UART: 8 681 ciclos entre bytes |

## Diagrama de bloques

```
                  8                    8                        8
UART_TXD_IN ─►[uart_rx]──rx_data──►[noise_gen]──────────►[BRAM_IN 65536×8]──┐
 (PC → FPGA)      │ rx_valid          ▲ SW[4:3]                ▲ WE=wr_in     │ 8
                  ▼                   │                        │ 16         ▼
               [ctrl]◄── SW[2:0], BTNC          [pos_counter]──┴──pos──► [MUX_SRC]◄── BRAM_TMP
               FSM IDLE/P1/P2        ▲ fin          ▲ cnt_en                   │ 8
                  │ ksel, absm,      │              │                          ▼
                  │ src_tmp, tmp_wr  └──────────────┤                 [REG_PIX]  [REG_W]◄─[ROM_W]
                  │                                 │                      │ 8     │ 8
                  ▼                         [tap_seq]──naddr (16)──► RA      ▼       ▼
               go, tx_start                 TAP 0..11, ROM_OFF,        [multiplicador 9×8 con signo]
                                            sumadores + MUX_ROW/COL           │
                                                                       [sumador + ACC 15 b]
                                                                              │ 15
                                            BRAM_TMP ◄──── y (8) ◄──── [post_proc: ÷16, |x|, sat]
                                            (P1 del LoG)                      │ 8
UART_RXD_OUT ◄──────────────────────────────────────────────────────── [uart_tx]
 (FPGA → PC)
```

El esquemático en PDF es la referencia; este diagrama solo muestra el flujo principal.

## Bloques

| # | Módulo (`rtl/`) | Qué hace | Elementos |
|---|---|---|---|
| 1 | `uart_rx` | Convierte la línea serie en un byte y genera `rx_valid` (1 ciclo) | RX_BUSY + MUX_BUSY, BAUD_RX módulo 868 (10 b, sample en 433), BIT_RX 4 b (rx_valid en 9), SR_RX 8 b (D32) |
| 2 | `noise_gen` | Cambia algunos píxeles por blanco o negro (sal y pimienta) | LFSR 16 b (x¹⁶+x¹⁴+x¹³+x¹¹+1, semilla 0xACE1), XOR de 4 entradas, NOR → lfsr_en, desplazador «4, comparador <, {8{lfsr[8]}}, MUX_RUIDO (D31) |
| 3 | `pos_counter` | Lleva la posición {fila, columna, canal} del byte actual | CH 2 b, COL 7 b, ROW 7 b en cascada; comparadores =2 y =127; AND → e_col, e_row, fin (D27) |
| 4 | `bram_sdp` (×2) | Guarda la imagen recibida (BRAM_IN) y el resultado intermedio del LoG (BRAM_TMP) | 65 536 × 8 b, un puerto de escritura y uno de lectura síncrona (D24) |
| 5 | `tap_seq` | Recorre los 9 vecinos del byte actual y calcula su dirección, replicando el borde | TAP 4 b (0..11), ROM_OFF (taps 0–8 en barrido, 9–11 centro), sumadores de 8 b + MUX_ROW/MUX_COL → naddr (D28, D29, D36) |
| 6 | `conv_mac` | Multiplica cada vecino por su peso y acumula | REG_PIX, REG_W, ROM_W {ksel, tap}, multiplicador 9×8 con signo, sumador, ACC 15 b borrado en tap = 0 (D25, D36) |
| 7 | `post_proc` | Normaliza (÷16), aplica valor absoluto si toca y satura a 0..255 | ÷16 con cables, negador, MUX_A, MUX_B, comparador >255, MUX_SAT → y (8 b) (D26) |
| 8 | `uart_tx` | Envía el byte `y` por la línea serie | SR_TX 10 b (carga {1, y, 0}), BIT_TX 4 b descendente, BAUD_TX módulo 868 (D33) |
| 9 | `ctrl` | Decide qué se hace en cada momento | FSM Moore de 2 b (IDLE 00, P1 01, P2 10), registro MODE 3 b (EN = idle) y decodificador → ksel, absm, src_tmp, tmp_wr, idle, two_pass; compuertas para wr_in, cnt_en, tap_en, go y tx_start (D30) |
| — | `image_proc_top` | Conecta todos los bloques con los pines de la tarjeta | — |

## Modos de operación

| SW[2] | SW[1:0] | Modo | Kernel (ksel) | Pasada P1 | Pasada P2 |
|---|---|---|---|---|---|
| 0 | 00 | Gaussiano | G | BRAM_IN → UART | — |
| 0 | 01 | Laplaciano | 16·L, con valor absoluto | BRAM_IN → UART | — |
| 0 | 10 | LoG | G y luego 16·L | BRAM_IN → BRAM_TMP | BRAM_TMP → UART |
| 0 | 11 | Unsharp | US = 32δ − G | BRAM_IN → UART | — |
| 1 | xx | Bypass | 16·δ | BRAM_IN → UART | — |

## Kernels (guardados ×16 en ROM_W)

```
Gaussiano (G)        16·Laplaciano (16·L)     Unsharp (US = 32δ − G)    Bypass (16·δ)
 1  2  1               0  16   0               −1  −2  −1                 0   0   0
 2  4  2              16 −64  16               −2  28  −2                 0  16   0
 1  2  1               0  16   0               −1  −2  −1                 0   0   0
```

Después de acumular, el resultado se divide entre 16 con un desplazamiento (se toman los bits acc[14:4]).
Así un solo camino de datos sirve para los cinco modos.

## Recursos y tiempos (Vivado 2025.2, xc7a100tcsg324-1, implementado)

| Recurso | Usado |
|---|---|
| LUT | 313 |
| Flip-flops | 137 |
| RAMB36 | 32 (23,7 %) |
| DSP48 | 0 (Vivado armó el multiplicador con LUT) |
| IOB | 18 |
| WNS a 100 MHz | +2,112 ns (cumple) |
