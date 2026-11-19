#!/usr/bin/env python3
# ============================================================================
# procesar_imagen.py - Proyecto #8 Image Processor (2D filters) - lado del PC
# ----------------------------------------------------------------------------
# Requisito R-F01: Python SOLO carga la imagen, la envia, recibe el resultado
# y lo muestra. NO hace ninguna operacion de filtrado ni de ruido: todo eso lo
# hace la FPGA.
#
# Protocolo (arquitectura v4.1):
#   PC -> FPGA : 49 152 bytes = 128 x 128 pixeles x 3 (R, G, B), fila por fila,
#                sin cabecera.
#   FPGA -> PC : 49 152 bytes con el resultado, en el mismo orden.
#   UART 115 200 baudios, 8 bits de datos, sin paridad, 1 bit de parada (8N1).
#
# Uso (desde la carpeta python/):
#   python procesar_imagen.py imagen_prueba.png                (puerto automatico)
#   python procesar_imagen.py foto.jpg --puerto COM5 --filtro G
#   python procesar_imagen.py --reprocesar --puerto COM5       (no reenvia: se
#        cambian los switches, se pulsa BTNC y el script recibe el nuevo resultado)
#   python procesar_imagen.py --listar                         (muestra los COM)
#
# Antes de enviar, poner los switches:
#   SW[1:0] filtro: 00 Gaussiano, 01 Laplaciano, 10 LoG, 11 Unsharp
#   SW[2]   bypass (devuelve la imagen guardada, con el ruido si lo hay)
#   SW[4:3] ruido: 00 nada, 01 6,25 %, 10 12,5 %, 11 18,75 %
# Si se pierde un byte (llegan menos de 49 152), pulsar CPU_RESET y repetir.
# ============================================================================
import argparse
import os
import sys
import time

import numpy as np
import serial
from serial.tools import list_ports
from PIL import Image
import matplotlib.pyplot as plt

N = 128                     # lado de la imagen (2^LOG_W, LOG_W = 7)
NB = N * N * 3              # 49 152 bytes
BAUD = 115200               # 100 MHz / 868 ciclos por bit
T_BYTE = 10 / BAUD          # 10 bits por byte (inicio + 8 datos + parada)

FILTROS = {"G": "Gaussiano", "L": "Laplaciano", "LOG": "LoG", "US": "Unsharp",
           "BYP": "Bypass"}


def elegir_puerto(nombre):
    """Devuelve el puerto pedido o, si hay uno solo, ese mismo."""
    if nombre:
        return nombre
    puertos = list(list_ports.comports())
    if len(puertos) == 1:
        print(f"Puerto detectado: {puertos[0].device} ({puertos[0].description})")
        return puertos[0].device
    print("No se pudo elegir el puerto automaticamente. Puertos disponibles:")
    for p in puertos:
        print(f"   {p.device}  -  {p.description}")
    print("Ejecute de nuevo con --puerto COMx")
    sys.exit(1)


def cargar_imagen(ruta):
    """Abre la imagen y la entrega como arreglo 128 x 128 x 3 de bytes (uint8).
    Si no mide 128 x 128 se ajusta el tamano al cargarla (es parte de 'cargar la
    imagen'; para cumplir R-F01 al pie de la letra, usar una imagen de 128 x 128)."""
    img = Image.open(ruta).convert("RGB")
    if img.size != (N, N):
        print(f"Aviso: la imagen mide {img.size[0]} x {img.size[1]}; se ajusta a {N} x {N} al cargarla.")
        img = img.resize((N, N))
    return np.asarray(img, dtype=np.uint8)


def recibir(ser, n, espera_max):
    """Lee n bytes del puerto o se rinde despues de espera_max segundos."""
    datos = bytearray()
    t0 = time.time()
    ultimo = -1
    while len(datos) < n and time.time() - t0 < espera_max:
        bloque = ser.read(n - len(datos))
        if bloque:
            datos.extend(bloque)
        pct = 100 * len(datos) // n
        if pct // 10 != ultimo:
            ultimo = pct // 10
            print(f"   recibidos {len(datos):6d} / {n} bytes ({pct} %)")
    return bytes(datos)


def mostrar(entrada, salida, titulo, ruta_png):
    fig, ejes = plt.subplots(1, 2 if entrada is not None else 1, figsize=(9, 4.8))
    ejes = np.atleast_1d(ejes)
    k = 0
    if entrada is not None:
        ejes[0].imshow(entrada, interpolation="nearest")
        ejes[0].set_title("Enviada a la FPGA")
        k = 1
    ejes[k].imshow(salida, interpolation="nearest")
    ejes[k].set_title(f"Devuelta por la FPGA: {titulo}")
    for e in ejes:
        e.axis("off")
    fig.tight_layout()
    fig.savefig(ruta_png.replace(".png", "_comparacion.png"), dpi=150)
    plt.show()


def main():
    ap = argparse.ArgumentParser(description="Envia una imagen a la FPGA y muestra el resultado.")
    ap.add_argument("imagen", nargs="?", help="imagen de entrada (.png, .jpg, ...)")
    ap.add_argument("--puerto", help="puerto serie, por ejemplo COM5")
    ap.add_argument("--reprocesar", action="store_true",
                    help="no envia nada: espera el resultado tras pulsar BTNC")
    ap.add_argument("--filtro", default="", help="etiqueta para el titulo y el archivo: G, L, LoG, US o BYP")
    ap.add_argument("--listar", action="store_true", help="lista los puertos COM y termina")
    a = ap.parse_args()

    if a.listar:
        for p in list_ports.comports():
            print(f"{p.device}  -  {p.description}")
        return
    if not a.reprocesar and not a.imagen:
        ap.error("indique la imagen, o use --reprocesar")

    puerto = elegir_puerto(a.puerto)
    etiqueta = FILTROS.get(a.filtro.upper(), a.filtro or "resultado")
    os.makedirs("resultados", exist_ok=True)
    marca = time.strftime("%Y%m%d_%H%M%S")
    ruta_png = os.path.join("resultados", f"{marca}_{a.filtro or 'salida'}.png")

    # 8N1 a 115 200 baudios: igual que uart_rx / uart_tx del diseno
    with serial.serial_for_url(puerto, baudrate=BAUD, bytesize=serial.EIGHTBITS,
                               parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                               timeout=0.5) as ser:
        ser.reset_input_buffer()
        entrada = None
        if a.reprocesar:
            print("Cambie los switches y pulse BTNC en la tarjeta (tiene 30 s)...")
            espera = 30 + NB * T_BYTE * 2
        else:
            entrada = cargar_imagen(a.imagen)
            datos = entrada.tobytes()          # orden R, G, B de cada pixel, fila por fila
            assert len(datos) == NB
            print(f"Enviando {NB} bytes por {puerto} (unos {NB * T_BYTE:.1f} s)...")
            t0 = time.time()
            ser.write(datos)
            ser.flush()
            print(f"   enviado en {time.time() - t0:.1f} s")
            espera = 10 + NB * T_BYTE * 2      # la vuelta tarda otro tanto (LoG un poco mas)
        print("Recibiendo el resultado...")
        salida = recibir(ser, NB, espera)

    if len(salida) != NB:
        print(f"ERROR: llegaron {len(salida)} de {NB} bytes.")
        print("Revise el puerto y los switches; si se perdio un byte, pulse CPU_RESET y envie de nuevo.")
        sys.exit(2)

    img_out = np.frombuffer(salida, dtype=np.uint8).reshape(N, N, 3)
    Image.fromarray(img_out, "RGB").save(ruta_png)
    print(f"Resultado guardado en {ruta_png}")
    mostrar(entrada, img_out, etiqueta, ruta_png)


if __name__ == "__main__":
    main()
