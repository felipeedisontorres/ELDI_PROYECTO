# Arquitectura del sistema (versión inicial, pendiente de validar)

## Parámetros generales

| Parámetro | Valor | Justificación |
|---|---|---|
| Reloj | 100 MHz, un solo dominio de reloj | Evita problemas de cruce entre dominios; los bloques lentos usan señales de habilitación |
| Imagen | 128 × 128 píxeles, RGB de 24 bits (8 por canal) | Entra en la BRAM con 3 buffers; 128 es potencia de 2 |
| Dirección de píxel | 14 bits = {fila[6:0], col[6:0]} | Se forma por concatenación, sin multiplicador |
| Tamaño de un buffer | 16 384 × 24 bits = 393 216 bits | — |
| Buffers | IN, TMP, OUT → 1 179 648 bits en total | Verificar la capacidad de BRAM del XC7A100T en Xilinx DS180 |
| UART | 8N1; 115200 baudios al inicio (divisor 868), luego 921600 (divisor 109) | Verificar los baud rates soportados en el Reference Manual de la Nexys 4 DDR |
| Tiempo de transmisión por imagen | 49 152 bytes × 10 bits / 115200 ≈ 4,3 s (≈ 0,53 s a 921600) | — |
| Tiempo de procesamiento | ≈ 16 384 píxeles × ~10 ciclos ≈ 1,6 ms por pasada | Despreciable frente a la UART |

## Diagrama de bloques (nivel superior)

```
           ┌──────────┐ 8  ┌───────────────┐ 24 / addr 14 ┌───────────┐
 UART_RX ─►│ uart_rx  ├───►│ ensamblador   ├─────────────►│ buffer IN │
  (PC→FPGA)└──────────┘    │ de píxel (×3) │              └─────┬─────┘
                           └───────────────┘                    │ 24
                                                                ▼
 SW[2:0] ──► ┌──────────────┐  control   ┌──────────────────────────────┐
 BTNC   ──►  │ FSM de       ├───────────►│ motor conv 3×3 + unsharp     │◄──► buffer TMP
             │ control      │            └──────────────┬───────────────┘
             └──────┬───────┘                           │ 24 / addr 14
                    │                                   ▼
                    │                             ┌───────────┐
                    │                             │ buffer OUT│
                    │                             └─────┬─────┘
                    │                                   │ 24
           ┌──────────┐ 8  ┌───────────────┐            │
 UART_TX ◄─┤ uart_tx  │◄───┤ serializador  │◄───────────┘
 (FPGA→PC) └──────────┘    │ de píxel (×3) │
                           └───────────────┘
```

## Modos de operación (SW[2:0])

| SW | Modo | Pasada 1 | Pasada 2 |
|---|---|---|---|
| 000 | Gaussiano | G: IN → OUT | — |
| 001 | Laplaciano | L: IN → OUT | — |
| 010 | LoG | G: IN → TMP | L: TMP → OUT |
| 011 | Unsharp | G: IN → TMP | 2·IN − TMP (saturado) → OUT |
| 1xx | Bypass (extra) | IN → OUT | — |

## Kernels

```
Gaussiano (÷16)        Laplaciano
 1  2  1                0  1  0
 2  4  2                1 -4  1
 1  2  1                0  1  0
```

Ninguno necesita multiplicadores: los pesos 2 y 4 son desplazamientos a la izquierda, y ÷16 es un desplazamiento de 4 bits a la derecha.

## Lista de módulos

| Módulo | Contenido (bloques funcionales) | Estado |
|---|---|---|
| `uart_tx` | Registro de desplazamiento de 10 bits con carga paralela, contador de baudios, contador de bits, FSM | Pendiente |
| `uart_rx` | Sincronizador de 2 FF, contador de baudios, contador de bits, registro de desplazamiento de 8 bits, FSM | Pendiente |
| `rx_pixel_assembler` | Registro de 24 bits, contador módulo 3, contador de dirección de 14 bits | Pendiente |
| `frame_buffer` | Memoria de 16 384 × 24 bits con lectura síncrona | Pendiente |
| `conv3x3` | Generador de direcciones con manejo de bordes, acumuladores por canal, multiplexor de coeficientes, saturación | Pendiente |
| `unsharp_unit` | Restador, desplazador, saturación | Pendiente |
| `control_fsm` | FSM: IDLE → RECEIVE → PASS1 → PASS2 → SEND | Pendiente |
| `tx_pixel_serializer` | Multiplexor 3:1 de bytes, contador de dirección | Pendiente |
| `ui` | Sincronizador de switches, antirrebote del botón, controlador de 7 segmentos | Pendiente |
| `top` | Interconexión | Pendiente |
