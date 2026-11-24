import ctypes
import time
import tkinter as tk
from ctypes import wintypes as wt

PUERTO = 'COM6'
IMAGEN = 'imagen_prueba.png'
W = H = 128
N = W * H * 3

k = ctypes.WinDLL('kernel32', use_last_error=True)
k.CreateFileW.restype = wt.HANDLE
k.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, wt.LPVOID, wt.DWORD, wt.DWORD, wt.HANDLE]
k.ReadFile.argtypes = [wt.HANDLE, wt.LPVOID, wt.DWORD, ctypes.POINTER(wt.DWORD), wt.LPVOID]
k.WriteFile.argtypes = [wt.HANDLE, wt.LPCVOID, wt.DWORD, ctypes.POINTER(wt.DWORD), wt.LPVOID]
k.CloseHandle.argtypes = [wt.HANDLE]
k.GetCommState.argtypes = k.SetCommState.argtypes = k.SetCommTimeouts.argtypes = [wt.HANDLE, ctypes.c_void_p]
k.SetupComm.argtypes = [wt.HANDLE, wt.DWORD, wt.DWORD]
k.PurgeComm.argtypes = [wt.HANDLE, wt.DWORD]


class DCB(ctypes.Structure):
    _fields_ = [('DCBlength', wt.DWORD), ('BaudRate', wt.DWORD), ('flags', wt.DWORD),
                ('wReserved', wt.WORD), ('XonLim', wt.WORD), ('XoffLim', wt.WORD),
                ('ByteSize', ctypes.c_ubyte), ('Parity', ctypes.c_ubyte), ('StopBits', ctypes.c_ubyte),
                ('XonChar', ctypes.c_char), ('XoffChar', ctypes.c_char), ('ErrorChar', ctypes.c_char),
                ('EofChar', ctypes.c_char), ('EvtChar', ctypes.c_char), ('wReserved1', wt.WORD)]


def abrir(nombre):
    h = k.CreateFileW('\\\\.\\' + nombre, 0xC0000000, 0, None, 3, 0, None)
    if h in (None, ctypes.c_void_p(-1).value):
        raise ctypes.WinError(ctypes.get_last_error())
    k.SetupComm(h, 1 << 16, 1 << 16)
    dcb = DCB(DCBlength=ctypes.sizeof(DCB))
    k.GetCommState(h, ctypes.byref(dcb))
    dcb.BaudRate, dcb.ByteSize, dcb.Parity, dcb.StopBits = 115200, 8, 0, 0
    dcb.flags = 0x1 | (1 << 4) | (1 << 12)
    if not k.SetCommState(h, ctypes.byref(dcb)):
        raise ctypes.WinError(ctypes.get_last_error())
    k.SetCommTimeouts(h, ctypes.byref((wt.DWORD * 5)(0xFFFFFFFF, 0xFFFFFFFF, 200, 0, 0)))
    k.PurgeComm(h, 0x000F)
    return h


def enviar_recibir(h, datos):
    n = wt.DWORD()
    k.WriteFile(h, ctypes.create_string_buffer(datos, N), N, ctypes.byref(n), None)
    rx = bytearray()
    buf = ctypes.create_string_buffer(N)
    fin, ultimo = time.time() + 20, None
    while len(rx) < N and time.time() < fin and not (ultimo and time.time() - ultimo > 3):
        k.ReadFile(h, buf, N - len(rx), ctypes.byref(n), None)
        if n.value:
            rx += buf.raw[:n.value]
            ultimo = time.time()
    return bytes(rx)


def cargar(root):
    foto = tk.PhotoImage(master=root, file=IMAGEN)
    if (foto.width(), foto.height()) != (W, H):
        raise ValueError('La imagen debe ser de 128x128 pixeles.')
    px = bytearray()
    for y in range(H):
        for x in range(W):
            v = foto.get(x, y)
            v = v.split() if isinstance(v, str) else v
            px += bytes(int(t) for t in v[:3])
    return bytes(px)


def a_foto(root, px):
    im = tk.PhotoImage(master=root, width=W, height=H)
    im.put(' '.join('{' + ' '.join('#%02x%02x%02x' % tuple(px[i:i + 3])
                                   for i in range(y * W * 3, (y + 1) * W * 3, 3)) + '}'
                    for y in range(H)))
    return im.zoom(3, 3)


root = tk.Tk()
root.title('Proyecto 8 - Image Processor')
entrada = cargar(root)
h = abrir(PUERTO)
try:
    salida = enviar_recibir(h, entrada)
finally:
    k.CloseHandle(h)
print(f'Recibidos {len(salida)} de {N} bytes')
salida += bytes(N - len(salida))
fotos = [a_foto(root, entrada), a_foto(root, salida)]
for c, (im, texto) in enumerate(zip(fotos, ('Entrada', 'Salida de la FPGA'))):
    tk.Label(root, image=im).grid(row=0, column=c, padx=6, pady=6)
    tk.Label(root, text=texto).grid(row=1, column=c)
root.mainloop()
