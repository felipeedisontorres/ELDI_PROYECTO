# Procesador de imágenes con filtros 2D en FPGA

Proyecto final de Electrónica Digital (ELDI), Escuela Colombiana de Ingeniería, 2026-2.
Proyecto #8 de la lista de propuestas: **Image Processor (2D filters)**.

**Integrantes:** Edison Torres · Juan Guaman

## Qué hace

1. Desde el PC, un script de Python abre una imagen a color, la reduce a 128 × 128 y la envía a la FPGA por UART.
2. La FPGA guarda la imagen en su memoria interna (BRAM), le añade ruido sal y pimienta si está activado
   y aplica el filtro elegido con los switches:
   - **Gaussiano:** suaviza la imagen.
   - **Laplaciano:** resalta los bordes.
   - **LoG:** Gaussiano y luego Laplaciano (bordes con menos ruido).
   - **Unsharp:** aumenta la nitidez (2·imagen − Gaussiano).
   - **Bypass:** devuelve la imagen sin filtrar.
3. La FPGA devuelve la imagen filtrada por UART y el script la muestra junto a la original.

Toda la matemática (filtros y ruido) se hace en la FPGA. Python solo carga, envía, recibe y muestra la imagen.

## Hardware y herramientas

| Elemento | Detalle |
|---|---|
| Tarjeta | Digilent Nexys A7-100T / Nexys 4 DDR (Artix-7 `xc7a100tcsg324-1`) |
| HDL | SystemVerilog, con el estilo de las presentaciones del curso |
| Síntesis | Vivado ML Standard 2025.2 |
| Simulación | Simulador de Vivado (xsim) o Icarus Verilog + GTKWave |
| PC | Python 3 con `pyserial`, `numpy`, `pillow` y `matplotlib` |
| Conexión | Cable micro-USB de la tarjeta (programación y UART a 115 200 baudios, 8N1) |

## Estructura del repositorio

```
rtl/                    Diseño: un archivo por bloque del esquemático (top: image_proc_top.sv)
tb/                     Un testbench autoverificable por módulo + el del sistema completo
sim/run_all.sh          Corre los 10 testbenches con Icarus Verilog
sim/full/               Prueba con la imagen de 128 × 128 (img_in.hex) y hex2png.py para ver las salidas
sim/wave/               Testbench corto y script para dibujar las formas de onda del informe
sim/syn.ys              Síntesis de prueba con Yosys (solo estimación)
constraints/            Pines (XDC) tomados del archivo maestro oficial de Digilent
vivado/                 Script Tcl que crea el proyecto de Vivado
python/                 Script del PC: envía la imagen y muestra el resultado
docs/                   Requisitos, arquitectura, decisiones, verificación, esquemático y explicación
AI_USAGE.md             Registro del uso de IA (R-G08)
```

| Documento | Contenido |
|---|---|
| [`docs/01_requisitos.md`](docs/01_requisitos.md) | Requisitos con ID, cómo se cumple cada uno y preguntas al profesor |
| [`docs/02_arquitectura.md`](docs/02_arquitectura.md) | Resumen de la arquitectura v4.1 |
| [`docs/03_decisiones.md`](docs/03_decisiones.md) | Decisiones de diseño D1–D36 e historial de versiones |
| [`docs/04_verificacion.md`](docs/04_verificacion.md) | Qué prueba cada testbench y resultados de Vivado |
| [`docs/esquematico/esquematico_v4_1.pdf`](docs/esquematico/esquematico_v4_1.pdf) | Esquemático RTL completo en una hoja A1 (en `generador/` está el programa que lo dibuja) |
| [`docs/explicacion/Explicacion_v4_1.pdf`](docs/explicacion/Explicacion_v4_1.pdf) | Explicación bloque por bloque: funcionamiento, anchos de bus, recorrido de un byte ciclo a ciclo, verificación, cierre de tiempos y preguntas de sustentación |

## Cómo reproducir el proyecto

### 1. Simular

**Con Vivado:** después del paso 2, *Flow Navigator → Run Simulation → Run Behavioral Simulation*. El script
deja la simulación configurada para correr hasta el final; en la Tcl Console debe aparecer:

```
TB tb_image_proc_top (W=8, CPB=8): 4441 verificaciones, 0 errores -> PASS
```

**Con Icarus Verilog** (Linux, macOS o WSL):

```bash
sudo apt install iverilog gtkwave        # Ubuntu / WSL, una sola vez
bash sim/run_all.sh                      # debe terminar en "TODOS LOS TESTBENCHES: PASS"
```

Prueba con la imagen completa de 128 × 128 (unos 5 minutos):

```bash
cd sim/full
iverilog -g2012 -s tb_image_proc_top -o full.vvp \
   -P tb_image_proc_top.LOG_W=7 -P tb_image_proc_top.FULL=1 \
   ../../rtl/*.sv ../../tb/tb_image_proc_top.sv
vvp full.vvp
python3 hex2png.py out_*.hex             # convierte las salidas a .png para verlas
```

Formas de onda (`sim/wave/`):

```bash
cd sim/wave
iverilog -g2012 -s tb_wave -o wave.vvp ../../rtl/*.sv tb_wave.sv && vvp wave.vvp
gtkwave wave.vcd                         # o: python3 plot_wave.py wave.vcd .
```

### 2. Crear el proyecto de Vivado y generar el bitstream

1. Abrir Vivado **sin abrir ningún proyecto** y en la **Tcl Console** escribir (con barras `/`, no `\`):
   ```
   source C:/ruta/al/repositorio/vivado/configurar_proyecto.tcl
   ```
   El script crea el proyecto en `vivado/proyecto/` con la parte `xc7a100tcsg324-1`, agrega `rtl/`, `tb/`
   y el XDC de `constraints/`, y deja `image_proc_top` y `tb_image_proc_top` como módulos principales.
   Para la Nexys 4 original se cambia la variable `placa` al inicio del script.
2. *Run Synthesis → Run Implementation → Generate Bitstream*.
3. Resultado esperado: 313 LUT, 137 flip-flops, 32 RAMB36 y WNS +2,112 ns (cumple a 100 MHz).

### 3. Programar la tarjeta

1. Conectar la tarjeta por USB y encenderla.
2. *Open Hardware Manager → Open Target → Auto Connect → Program Device*.

### 4. Enviar una imagen desde el PC

Desde la carpeta `python/`:

```bash
pip install -r requirements.txt                                   # una sola vez
python procesar_imagen.py --listar                                # ver en qué puerto COM quedó la tarjeta
python procesar_imagen.py imagen_prueba.png --puerto COM5 --filtro G
```

Envío y recepción tardan unos 4,3 s cada uno. Se abre una ventana con la imagen enviada y la devuelta,
y las dos se guardan en `python/resultados/`. Para aplicar otro filtro **sin reenviar** la imagen: cambiar
los switches, ejecutar `python procesar_imagen.py --reprocesar --puerto COM5 --filtro LoG` y pulsar BTNC
antes de 30 s.

Primera prueba recomendada: bypass sin ruido (SW = `00100`). La imagen debe volver idéntica; así se
comprueba la UART sola antes de probar los filtros.

## Uso de la tarjeta

| Control | Función |
|---|---|
| SW[1:0] | Filtro: `00` Gaussiano · `01` Laplaciano · `10` LoG · `11` Unsharp |
| SW[2] | Bypass |
| SW[4:3] | Ruido: `00` sin ruido · `01` 6,25 % · `10` 12,5 % · `11` 18,75 % |
| BTNC | Reprocesar la última imagen con el modo actual, sin reenviarla |
| CPU_RESETN | Reset (también si se pierde un byte en la transmisión) |
| LED[2:0] | Modo activo |
| LED[7:6] | Estado: `00` esperando · `01` primera pasada · `10` segunda pasada (solo LoG) |

Los switches se leen cuando la tarjeta está esperando (estado IDLE).

## Estado

| Parte | Estado |
|---|---|
| Diseño v4.1 y esquemático | Terminado |
| Testbenches de los 10 módulos y del sistema | PASS |
| Síntesis, implementación y bitstream en Vivado | Terminado, cumple tiempos |
| Prueba en la tarjeta con Python | Pendiente |
| Informe IEEE y presentación | Pendiente |
