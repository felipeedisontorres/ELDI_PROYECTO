#!/usr/bin/env python3
"""Convierte imagenes .hex (49 152 lineas, un byte por linea, orden R,G,B fila por fila)
a .png, y una imagen .png/.jpg cualquiera a img_in.hex de 128 x 128.

Uso:
    python3 hex2png.py out_G.hex            -> out_G.png
    python3 hex2png.py --to-hex foto.jpg    -> img_in.hex (redimensionada a 128 x 128)

Solo sirve para ver o preparar las imagenes de la simulacion: no hace ningun filtrado
(toda la matematica esta en la FPGA, R-F01). Requiere Pillow (pip install pillow).
"""
import sys
from PIL import Image

W = 128


def hex_to_png(path):
    data = bytes(int(line, 16) for line in open(path) if line.strip())
    if len(data) != W * W * 3:
        sys.exit(f"{path}: se esperaban {W*W*3} bytes y hay {len(data)}")
    out = path.rsplit('.', 1)[0] + '.png'
    Image.frombytes('RGB', (W, W), data).save(out)
    print('->', out)


def img_to_hex(path):
    im = Image.open(path).convert('RGB').resize((W, W))
    with open('img_in.hex', 'w') as f:
        for b in im.tobytes():
            f.write(f'{b:02x}\n')
    print('-> img_in.hex')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--to-hex':
        img_to_hex(sys.argv[2])
    elif len(sys.argv) >= 2:
        for p in sys.argv[1:]:
            hex_to_png(p)
    else:
        print(__doc__)
