# -*- coding: utf-8 -*-
"""Lee wave.vcd (Icarus) y dibuja formas de onda para el informe.
Uso: python3 plot_wave.py wave.vcd <carpeta_de_salida>  ->  wave_rx.png y wave_mac.png"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


def parse_vcd(fn):
    ids, sigs, scope = {}, {}, []
    t = 0
    with open(fn) as f:
        lines = iter(f.read().split('\n'))
        for ln in lines:
            ln = ln.strip()
            if ln.startswith('$scope'):
                scope.append(ln.split()[2])
            elif ln.startswith('$upscope'):
                scope.pop()
            elif ln.startswith('$var'):
                p = ln.split()
                width, ident, name = int(p[2]), p[3], p[4]
                full = '.'.join(scope + [name])
                ids.setdefault(ident, []).append(full)
                sigs[full] = {'w': width, 'ch': []}
            elif ln.startswith('#'):
                t = int(ln[1:])
            elif ln and ln[0] in '01xzXZ' and not ln.startswith('$'):
                v, ident = ln[0], ln[1:]
                for n in ids.get(ident, []):
                    sigs[n]['ch'].append((t, v))
            elif ln and ln[0] in 'bB':
                v, ident = ln[1:].split()
                for n in ids.get(ident, []):
                    sigs[n]['ch'].append((t, v))
    return sigs


def val_at(ch, t):
    v = None
    for tt, vv in ch:
        if tt <= t:
            v = vv
        else:
            break
    return v


def to_int(v, signed=False, w=1):
    if v is None or any(c in 'xzXZ' for c in v):
        return None
    x = int(v, 2)
    if signed and x >= 1 << (w - 1):
        x -= 1 << w
    return x


def plot(sigs, rows, t0, t1, fn, title, period=10000, mark=None):
    """rows: lista de (nombre_mostrado, nombre_vcd, formato). formato: 'bit', 'dec', 'sdec', 'hex', 'rc'"""
    n = len(rows)
    fig, ax = plt.subplots(figsize=(13, 0.52 * n + 1.1))
    H = 0.62
    for i, (lab, nm, fmt) in enumerate(rows):
        y = n - 1 - i
        s = sigs[nm]
        ch = [(t, v) for t, v in s['ch']]
        # puntos de cambio dentro de la ventana
        times = [t0] + [t for t, v in ch if t0 < t < t1] + [t1]
        ax.text(t0 - (t1 - t0) * 0.008, y + H / 2, lab, ha='right', va='center', fontsize=9,
                family='DejaVu Sans', color='#1f4e9c' if s['w'] == 1 else '#000')
        for a, b in zip(times, times[1:]):
            v = val_at(ch, a)
            if s['w'] == 1 or fmt == 'bit':
                lv = to_int(v)
                yy = y + (H if lv == 1 else 0)
                ax.plot([a, b], [yy, yy], color='#1f4e9c', lw=1.4)
                v2 = val_at(ch, b)
                if b < t1 and v2 != v:
                    ax.plot([b, b], [y, y + H], color='#1f4e9c', lw=1.4)
            else:
                d = min((b - a) * 0.12, period * 0.25)
                poly = [(a, y + H / 2), (a + d, y + H), (b - d, y + H), (b, y + H / 2), (b - d, y), (a + d, y)]
                ax.add_patch(Polygon(poly, closed=True, fill=True, facecolor='#f4f4f4', edgecolor='#000', lw=0.9))
                x = to_int(v, signed=(fmt == 'sdec'), w=s['w'])
                if x is None:
                    txt = 'x'
                elif fmt == 'hex':
                    txt = f'{x:02X}'
                elif fmt == 'rc':           # {row, col, ch} con LOG_W = 2 -> 6 b
                    txt = f'{x >> 4},{(x >> 2) & 3},{x & 3}'
                else:
                    txt = str(x)
                if (b - a) > period * 0.75:
                    ax.text((a + b) / 2, y + H / 2, txt, ha='center', va='center', fontsize=7.5)
    # rejilla de reloj
    k = (t0 // period) * period
    while k <= t1:
        ax.axvline(k, color='#e6e6e6', lw=0.5, zorder=0)
        k += period
    if mark:
        for tm, txt in mark:
            ax.axvline(tm, color='#c0392b', lw=1.0, ls='--')
            ax.text(tm, n + 0.05, txt, color='#c0392b', fontsize=8, ha='center', va='bottom')
    ax.set_xlim(t0 - (t1 - t0) * 0.10, t1)
    ax.set_ylim(-0.3, n + 0.5)
    ax.set_yticks([])
    ax.set_xlabel('tiempo de simulación (ns) · rejilla = 1 ciclo de 10 ns', fontsize=9)
    xt = ax.get_xticks()
    ax.set_xticks(xt)
    ax.set_xticklabels([f'{v / 1000:.0f}' for v in xt], fontsize=8)
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)
    ax.set_title(title, fontsize=10.5, loc='left')
    fig.tight_layout()
    fig.savefig(fn, dpi=170)
    plt.close(fig)


if __name__ == '__main__':
    vcd, outdir = sys.argv[1], sys.argv[2]
    S = parse_vcd(vcd)
    P = 'tb_wave.dut.'
    # ---------------- recepcion del primer byte (0x11) ----------------
    t_start = [t for t, v in S['tb_wave.UART_TXD_IN']['ch'] if v == '0'][0]
    rows = [('UART_TXD_IN (rx)', 'tb_wave.UART_TXD_IN', 'bit'),
            ('rx_busy', P + 'u_rx.rx_busy', 'bit'),
            ('baud_rx', P + 'u_rx.baud_rx', 'dec'),
            ('sample', P + 'u_rx.sample', 'bit'),
            ('bit_rx', P + 'u_rx.bit_rx', 'dec'),
            ('rx_data (SR_RX)', P + 'rx_data', 'hex'),
            ('rx_valid', P + 'rx_valid', 'bit'),
            ('wr_in', P + 'wr_in', 'bit'),
            ('pos {row,col,ch}', P + 'pos', 'rc')]
    plot(S, rows, t_start - 20000, t_start + 860000, f'{outdir}/wave_rx.png',
         'Recepción del primer byte (0x11) con CLKS_PER_BIT = 8: se muestrea a mitad de cada bit (sample)',
         mark=[(t_start, 'flanco de inicio')])
    # ---------------- calculo de los primeros bytes en P1 ----------------
    st = S[P + 'state']['ch']
    t_p1 = [t for t, v in st if v.lstrip('b').endswith('01') or v == 'b1' or v == '1'][0]
    rows = [('state', P + 'state', 'dec'),
            ('tap', P + 'tap', 'dec'),
            ('naddr {row,col,ch}', P + 'naddr', 'rc'),
            ('pix (dout_in)', P + 'pix', 'dec'),
            ('w (ROM_W)', P + 'u_mac.w', 'sdec'),
            ('pix_q (REG_PIX)', P + 'u_mac.pix_q', 'dec'),
            ('w_q (REG_W)', P + 'u_mac.w_q', 'sdec'),
            ('acc', P + 'acc', 'sdec'),
            ('y', P + 'y', 'dec'),
            ('at11', P + 'at11', 'bit'),
            ('go', P + 'go', 'bit'),
            ('tx_start', P + 'tx_start', 'bit'),
            ('tx_busy', P + 'tx_busy', 'bit'),
            ('pos {row,col,ch}', P + 'pos', 'rc')]
    plot(S, rows, t_p1 - 20000, t_p1 + 300000, f'{outdir}/wave_mac.png',
         'Primeros bytes de la pasada P1 (Gaussiano, v4.1): 12 ciclos por byte y espera en tap = 11 mientras la UART está ocupada',
         mark=[(t_p1, 'entra a P1')])
    print('ok', t_start, t_p1)
