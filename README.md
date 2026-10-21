# ELDI_PROYECTO: Procesador de imágenes con filtros 2D en FPGA

Proyecto final de Electrónica Digital (ELDI), Escuela Colombiana de Ingeniería, 2026.
Proyecto #8 de la lista de propuestas: **Image Processor (2D filters)**.

## ¿Qué hace?

1. Un script de Python en el PC carga una imagen a color, le añade ruido y la envía por UART a la FPGA.
2. La FPGA guarda la imagen en memoria y aplica el filtro elegido con los switches:
   - Gaussiano (suavizado)
   - Laplaciano (bordes)
   - LoG (Gaussiano + Laplaciano)
   - Unsharp (realce de nitidez)
3. La FPGA devuelve la imagen filtrada por UART y el PC la muestra junto a la original.

## Hardware y herramientas

| Elemento | Detalle |
|---|---|
| Tarjeta | Digilent Nexys 4 DDR (Xilinx Artix-7 XC7A100T) |
| HDL | Verilog |
| Síntesis | Vivado |
| Simulación | Icarus Verilog + GTKWave |
| PC | Python 3 (`pyserial`, `numpy`, `pillow`) |

## Estructura del repositorio

```
rtl/          Módulos de hardware en Verilog
tb/           Un testbench por módulo
constraints/  Archivo .xdc con los pines de la Nexys 4 DDR
python/       Scripts del PC: envío/recepción por UART, ruido, modelo de referencia
docs/         Requisitos, arquitectura, diagramas, informe
AI_USAGE.md   Registro del uso de herramientas de IA
```

## Cómo reproducir el proyecto

_En construcción: se completará a medida que avance el proyecto._

1. Simulación: _pendiente_
2. Síntesis y programación de la tarjeta: _pendiente_
3. Ejecución desde el PC: _pendiente_

## Estado

| Módulo | Estado |
|---|---|
| uart_tx | Pendiente |
| uart_rx | Pendiente |
| Buffers de imagen | Pendiente |
| Motor de convolución 3×3 | Pendiente |
| FSM de control | Pendiente |
| Scripts de Python | Pendiente |

## Integrantes

- _Nombre 1_
- _Nombre 2_
