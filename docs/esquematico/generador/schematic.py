import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schlib import *

S = Sheet(841, 594)
W = S.wire

S.text(12, 14.5, 'Proyecto #8 · Image Processor (2D filters) — esquemático RTL v4.1 (arquitectura simplificada, MAC segmentado)',
       size=7.0, weight='bold')
S.text(12, 22.5, 'Una sola hoja · todas las conexiones son cables dibujados (sin etiquetas que «saltan») · '
       'nombres = señales del código SystemVerilog · /n = ancho del bus en bits · '
       'punto = unión; cruce con salto = NO conectados', size=3.2, color='#333')

S.frame(48, 30, 172, 140, 'uart_rx · receptor UART 8N1', 1)
S.frame(262, 30, 158, 140, 'noise_gen · ruido sal y pimienta', 2)
S.frame(48, 194, 172, 116, 'pos_counter · posición {ROW, COL, CH}', 3, tdx=38)
S.frame(262, 194, 158, 184, 'bram_sdp ×2 (memorias)', 4, tdx=30)
S.frame(48, 314, 172, 150, 'tap_seq · taps y dirección del vecino', 5, tdx=38)
S.frame(430, 194, 92, 184, 'conv_mac · MAC', 6)
S.frame(532, 194, 136, 184, 'post_proc · ÷16, |x|, saturación', 7)
S.frame(678, 194, 124, 184, 'uart_tx · transmisor', 8, tdx=36)
S.frame(250, 400, 581, 124, 'ctrl · unidad de control', 9, tdx=228)

X_AT10, X_FIN, X_GO, X_IDLE, X_WR, X_CH = 224, 227, 241, 245, 249, 257

CLKY, RSTY = 176.0, 180.0
clk_tip = S.port_in(12, CLKY, 'CLK100MHZ')
rstn_tip = S.port_in(12, 187, 'CPU_RESETN')
nrst = S.gate('not', 36.5, 184.5)
W([rstn_tip, nrst['i0']], 'rst', arrow=False)
W([nrst['out'], (44, 187), (44, RSTY), (712, RSTY)], 'rst', arrow=False, name='reset (síncrono)', npos=2,
  nfrac=0.02, net='RST')
W([clk_tip, (710, CLKY)], 'clk', arrow=False, name='clk (100 MHz)', npos=0, nfrac=0.04, net='CLK')


def comb(xc, xr, regs, up):
    rr = [r for r in regs if 'rst' in r]
    ext_c = (min if up else max)(r['clk'][1] for r in regs)
    W([(xc, CLKY), (xc, ext_c)], 'clk', arrow=False, net='CLK')
    S.dot(xc, CLKY, C_CLK)
    if rr:
        ext_r = (min if up else max)(r['rst'][1] for r in rr)
        W([(xr, RSTY), (xr, ext_r)], 'rst', arrow=False, net='RST')
        S.dot(xr, RSTY, C_RST)
    for r in regs:
        c = r['clk']
        W([(xc, c[1]), c], 'clk', arrow=False, net='CLK')
        if abs(c[1] - ext_c) > 1e-6:
            S.dot(xc, c[1], C_CLK)
        if 'rst' in r:
            q = r['rst']
            W([(xr, q[1]), q], 'rst', arrow=False, net='RST')
            if abs(q[1] - ext_r) > 1e-6:
                S.dot(xr, q[1], C_RST)


def bar(x, y1, y2):
    S.rect(x - 0.9, y1, 1.8, y2 - y1, fill='#000', stroke='#000', sw=0.2)


def ctrl_tag(x, y):
    S.rect(x - 3.4, y - 2.3, 6.8, 3.2, fill='#404040', stroke='none', rx=0.6, layer='text')
    S.text(x, y, 'ctrl', size=1.9, anchor='middle', color='#fff', weight='bold')


busy = S.box(92, 46, 26, 20, 'RX_BUSY', '1 FF', pins=[('d', 'l', .35, 'D'), ('q', 'r', .35, 'Q')],
             clk=('l', .7), rst=('l', .9))
m_busy = S.mux(70, busy['d'].y - 8, name='MUX_BUSY')
n_rx = S.gate('not', 59, m_busy['p0'].y - 2.5)
rx_tip = S.port_in(12, m_busy['p0'].y, 'UART_TXD_IN')
W([rx_tip, n_rx['i0']], 'sig', name='rx', dots=[(53, rx_tip.y)], net='rx')
W([n_rx['out'], m_busy['p0']], 'sig')
W([m_busy['out'], busy['d']], 'sig')
n_busy = S.gate('not', 127, busy['q'].y - 2.5)
W([busy['q'], n_busy['i0']], 'sig', dots=[(123, busy['q'].y)], net='rxb')
S.text(121.5, busy['q'].y - 1.2, 'rx_busy', size=2.1, anchor='end', italic=True, color=C_SIG)
W([(123, busy['q'].y), (123, 69), (m_busy['sel'].x, 69), m_busy['sel']], 'sig', net='rxb')

baud = S.box(92, 78, 30, 20, 'BAUD_RX', 'contador mód 868 · 10 b',
             pins=[('clr', 'l', .3, 'CLR'), ('q', 'r', .5, '')], clk=('l', .68), rst=('l', .88), ssize=2.0)
c433 = S.op(138, baud['q'].y, '=')
k433 = S.const(138, baud['q'].y - 10, '433')
W([k433['b'], c433['t']], 'bus')
W([baud['q'], c433['l']], 'bus', width=10, wfrac=0.62)
S.text(124, baud['q'].y + 3.4, 'baud_rx', size=2.1, italic=True)

and_v = S.gate('and', 154, 112, n=2, h=8)
bitc = S.box(92, and_v['i1'].y - 10, 30, 20, 'BIT_RX', 'contador 4 b',
             pins=[('clr', 'l', .3, 'CLR'), ('en', 't', .67, 'EN'), ('q', 'r', .5, '')],
             clk=('l', .68), rst=('l', .88))
c9 = S.op(136, bitc['q'].y, '=')
k9 = S.const(136, bitc['q'].y + 10, '9')
W([k9['t'], c9['b']], 'bus')
W([bitc['q'], c9['l']], 'bus', width=4, wfrac=0.62)
S.text(124, bitc['q'].y + 3.4, 'bit_rx', size=2.1, italic=True)
W([c9['r'], and_v['i1']], 'sig')

srx = S.box(92, 140, 32, 20, 'SR_RX', 'desplaz. 8 b (LSB 1.º)',
            pins=[('si', 'l', .3, 'SI'), ('en', 't', .6, 'EN'), ('q', 'r', .5, 'Q')],
            clk=('l', .68), rst=('l', .88), ssize=2.0)
XS = 149
W([c433['r'], (XS, c433['r'].y), (XS, 136), (srx['en'].x, 136), srx['en']], 'sig', name='sample',
  nsize=2.3, dots=[(XS, 103), (XS, and_v['i0'].y)], net='sample')
W([(XS, 103), (bitc['en'].x, 103), bitc['en']], 'sig', net='sample')
W([(XS, and_v['i0'].y), and_v['i0']], 'sig', net='sample')
W([n_busy['out'], (138, n_busy['out'].y), (138, 72), (88, 72), (88, bitc['clr'].y), bitc['clr']], 'sig',
  name='~rx_busy', npos=2, nfrac=0.32, dots=[(88, baud['clr'].y)], net='nbusy')
W([(88, baud['clr'].y), baud['clr']], 'sig', net='nbusy')
W([(53, rx_tip.y), (53, srx['si'].y), srx['si']], 'sig', net='rx')
n_v = S.gate('not', 171, and_v['out'].y - 2.5)
W([and_v['out'], n_v['i0']], 'sig', dots=[(167, and_v['out'].y)], net='rx_valid')
S.text(168, and_v['out'].y - 4.0, 'rx_valid', size=2.2, anchor='middle', color=C_SIG, italic=True)
W([n_v['out'], (182, n_v['out'].y), (182, 40), (66, 40), (66, m_busy['p1'].y), m_busy['p1']], 'sig',
  name='~rx_valid', npos=2, nfrac=0.5)
comb(84, 86, [busy, baud, bitc, srx], up=True)

and_wr = S.gate('and', X_IDLE - 1.33 - 4.5, 121, n=2, h=8, rot='u')
ctrl_tag(and_wr['out'].x - 8.5, and_wr['out'].y + 3.4)
W([(167, and_v['out'].y), (167, 134), (and_wr['i0'].x, 134), and_wr['i0']], 'sig', net='rx_valid',
  name='rx_valid', npos=1, nfrac=0.7)
YWR = and_wr['out'].y - 3.5
W([and_wr['out'], (and_wr['out'].x, YWR), (X_WR, YWR)], 'sig', arrow=False, net='wr_in', name='wr_in',
  npos=0, nfrac=None, ndx=-9.0, ndy=-1.0)
S.dot(X_WR, YWR, C_SIG)
or_cnt = S.gate('or', 229.5, 201.5, n=2, h=7, rot='l')
ctrl_tag(234.5, 197.2)

lfsr = S.box(300, 64, 44, 26, 'LFSR', '16 b · semilla 0xACE1',
             pins=[('si', 'l', .25, 'SI'), ('en', 'l', .5, 'EN'), ('q', 'r', .5, 'Q')],
             clk=('l', .72), rst=('l', .9), ssize=2.0)
S.text(322, 96.5, 'x¹⁶ + x¹⁴ + x¹³ + x¹¹ + 1', size=2.3, anchor='middle', color='#444')
S.text(322, 100.0, '(período 65 535)', size=2.1, anchor='middle', color='#444')
xr = S.op(290, lfsr['si'].y, '⊕', size=4.4)
W([xr['r'], lfsr['si']], 'sig')
S.text(296.5, lfsr['si'].y - 1.0, 'fb', size=2.1, anchor='middle', italic=True, color=C_SIG)
nor = S.gate('nor', 268, lfsr['en'].y - 5, n=3, h=10)
W([nor['out'], lfsr['en']], 'sig')
S.text(290, lfsr['en'].y + 3.0, 'lfsr_en', size=2.1, anchor='middle', italic=True, color=C_SIG)
cmp_lt = S.op(384, lfsr['q'].y, '<')
W([lfsr['q'], cmp_lt['l']], 'bus', width=16, wfrac=0.1)
S.text(371, lfsr['q'].y - 1.0, 'lfsr[7:0]', size=2.2, anchor='middle', italic=True)
S.slash(376.5, lfsr['q'].y, 8)
W([(352, lfsr['q'].y), (352, 56), (xr['t'].x, 56), xr['t']], 'bus', width=4, wpos=1, wfrac=0.08,
  dots=[(352, lfsr['q'].y)], net='lfsrq')
S.text(321, 54.8, 'lfsr[0], lfsr[2], lfsr[3], lfsr[5]', size=2.2, anchor='middle', italic=True)
sw43 = S.port_in(266, 46, 'SW[4:3]')
shf = S.box(304, 42, 22, 8, '<< 4', None, fill=GRAY, tsize=2.8)
S.text(315, 40.6, 'shifter (cables): ×16', size=2.0, anchor='middle', color='#444')
W([sw43, (304, 46)], 'sig', width=2, wfrac=0.55)
W([(326, 46), (cmp_lt['t'].x, 46), cmp_lt['t']], 'bus', width=8, wpos=1, wfrac=0.6, wdx=0)
S.text(356, 44.8, 'thr = {00, SW[4:3], 0000}', size=2.2, anchor='middle', italic=True)
m_nz = S.mux(398, 150 - 10.67, sel='t', name='MUX_RUIDO')
rep = S.box(364, m_nz['p1'].y - 4, 16, 8, '{8{·}}', None, fill=GRAY, tsize=2.6)
W([(360, lfsr['q'].y), (360, m_nz['p1'].y), (364, m_nz['p1'].y)], 'sig', dots=[(360, lfsr['q'].y)],
  net='lfsrq')
S.text(361.2, 112, 'lfsr[8]', size=2.2, italic=True, color=C_SIG)
W([(380, m_nz['p1'].y), m_nz['p1']], 'bus', width=8, wfrac=0.45)
S.text(372, m_nz['p1'].y + 7.0, '0x00 / 0xFF', size=2.0, anchor='middle', color='#444')
W([cmp_lt['r'], (m_nz['sel'].x, cmp_lt['r'].y), m_nz['sel']], 'sig', name='hit', nsize=2.4)
comb(292, 294, [lfsr], up=True)
W([(X_WR, YWR), (X_WR, nor['ins'][0].y), nor['ins'][0]], 'sig', net='wr_in')

def counter3(y, title, sub, pins):
    return S.box(92, y, 24, 18, title, sub, pins=pins, clk=('l', .55), rst=('l', .85), ssize=2.0)


chc = counter3(212, 'CH', 'cont. 2 b', [('en', 't', .3, 'EN'), ('clr', 't', .75, 'CLR'), ('q', 'r', .5, '')])
colc = counter3(246, 'COL', 'cont. 7 b', [('en', 't', .3, 'EN'), ('q', 'r', .5, '')])
rowc = counter3(280, 'ROW', 'cont. 7 b', [('en', 't', .3, 'EN'), ('q', 'r', .5, '')])
XB = 194
bar(XB, chc['q'].y - 4, rowc['q'].y + 4)
S.text(XB, chc['q'].y - 5.4, 'pos = {row, col, ch}', size=2.3, anchor='middle', weight='bold')
for q, nm, w_, lab in ((chc['q'], 'ch', 2, '[1:0]'), (colc['q'], 'col', 7, '[8:2]'),
                       (rowc['q'], 'row', 7, '[15:9]')):
    W([q, (XB - 0.9, q.y)], 'bus', width=w_, wfrac=0.66, dots=[(128, q.y)], net='q' + nm)
    S.text(119, q.y - 1.0, nm, size=2.3, italic=True)
    S.text(XB - 2.0, q.y + 3.2, lab, size=2.0, anchor='end', color='#444')
cmps = []
for q, k, nm in ((chc['q'], '2', 'ch'), (colc['q'], '127', 'col'), (rowc['q'], '127', 'row')):
    c = S.op(128, q.y + 14, '=')
    kk = S.const(114.5, q.y + 14, k)
    W([(128, q.y), c['t']], 'bus', net='q' + nm)
    W([kk['r'], c['l']], 'bus')
    cmps.append(c)
and_ec = S.gate('and', 142, cmps[0]['r'].y - 5.33, n=2, h=8)
and_er = S.gate('and', 142, cmps[1]['r'].y - 5.33, n=2, h=8)
and_fn = S.gate('and', 142, cmps[2]['r'].y - 5.33, n=2, h=8)
W([cmps[0]['r'], and_ec['i1']], 'sig')
S.text(137, cmps[0]['r'].y + 3.2, 'c_ch', size=2.0, anchor='middle', italic=True, color=C_SIG)
W([cmps[1]['r'], and_er['i1']], 'sig')
S.text(137, cmps[1]['r'].y + 3.2, 'col_max', size=2.0, anchor='middle', italic=True, color=C_SIG)
W([cmps[2]['r'], and_fn['i1']], 'sig')
S.text(137, cmps[2]['r'].y + 3.2, 'row_max', size=2.0, anchor='middle', italic=True, color=C_SIG)
eo = and_ec['out']
W([eo, (157, eo.y), (157, 207.5), (chc['clr'].x, 207.5), chc['clr']], 'sig', dots=[(157, eo.y)], net='e_col')
S.text(158, eo.y - 1.0, 'e_col', size=2.2, italic=True, color=C_SIG)
W([(157, eo.y), (157, 242), (colc['en'].x, 242), colc['en']], 'sig', dots=[(139, 242)], net='e_col')
W([(139, 242), (139, and_er['i0'].y), and_er['i0']], 'sig', net='e_col')
eo2 = and_er['out']
W([eo2, (157, eo2.y), (157, 276), (rowc['en'].x, 276), rowc['en']], 'sig', dots=[(139, 276), (157, eo2.y)],
  net='e_row')
S.text(158, eo2.y - 1.0, 'e_row', size=2.2, italic=True, color=C_SIG)
W([(139, 276), (139, and_fn['i0'].y), and_fn['i0']], 'sig', net='e_row')
YCNT = or_cnt['out'].y
W([or_cnt['out'], (chc['en'].x, YCNT), chc['en']], 'sig', name='cnt_en', npos=0, nfrac=0.42,
  dots=[(135, YCNT)], net='cnt_en')
W([(135, YCNT), (135, and_ec['i0'].y), and_ec['i0']], 'sig', net='cnt_en')
YF = and_fn['out'].y
W([and_fn['out'], (X_FIN, YF)], 'sig', arrow=False, name='fin', npos=0, nfrac=0.3, net='fin')
comb(80, 82, [chc, colc, rowc], up=False)

XP = 204
YPOS = colc['q'].y
Y_TROW, Y_TCOL, Y_TCH = 326, 330, 387
add_r = S.op(158, 348, '+')
add_c = S.op(158, 376, '+')
m_r = S.mux(174, add_r['r'].y - 32 / 3, name=None)
m_c = S.mux(174, add_c['r'].y - 32 / 3, name=None)
S.text(m_r['out'].x + 1.0, m_r['out'].y - 6.6, 'MUX_ROW', size=2.1, weight='bold', color='#333')
S.text(m_c['out'].x + 1.0, m_c['out'].y - 6.6, 'MUX_COL', size=2.1, weight='bold', color='#333')
W([(XB + 0.9, YPOS), (XP, YPOS), (XP, Y_TCH)], 'bus', arrow=False, net='pos', dots=[(XP, Y_TROW), (XP, Y_TCOL)])
W([(XP, Y_TROW), (add_r['t'].x, Y_TROW), add_r['t']], 'bus', width=7, wfrac=0.1, dots=[(170, Y_TROW)],
  net='trow')
S.text(184, Y_TROW - 1.0, 'row = pos[15:9]', size=2.1, anchor='middle', italic=True)
W([(170, Y_TROW), (170, m_r['p1'].y), m_r['p1']], 'bus', net='trow')
W([(XP, Y_TCOL), (165, Y_TCOL), (165, m_c['p1'].y), m_c['p1']], 'bus',
  width=7, wfrac=0.1, dots=[(165, add_c['t'].y - 6)], net='tcol')
S.text(186, Y_TCOL + 3.2, 'col = pos[8:2]', size=2.1, anchor='middle', italic=True)
W([(165, add_c['t'].y - 6), (add_c['t'].x, add_c['t'].y - 6), add_c['t']], 'bus', net='tcol')
W([add_r['r'], m_r['p0']], 'bus', width=8, wfrac=0.78, dots=[(167, add_r['r'].y)], net='rsum')
S.text(168.5, add_r['r'].y + 2.8, 'rsum', size=2.0, italic=True)
W([(167, add_r['r'].y), (167, m_r['sel'].y + 3.2), (m_r['sel'].x, m_r['sel'].y + 3.2), m_r['sel']], 'sig',
  net='rsum')
S.text(186, m_r['sel'].y + 5.6, 'rsum[7]', size=2.0, anchor='middle', italic=True, color=C_SIG)
W([add_c['r'], m_c['p0']], 'bus', width=8, wfrac=0.78, dots=[(167, add_c['r'].y)], net='csum')
S.text(168.5, add_c['r'].y + 2.8, 'csum', size=2.0, italic=True)
W([(167, add_c['r'].y), (167, m_c['sel'].y + 3.2), (m_c['sel'].x, m_c['sel'].y + 3.2), m_c['sel']], 'sig',
  net='csum')
S.text(186, m_c['sel'].y + 5.6, 'csum[7]', size=2.0, anchor='middle', italic=True, color=C_SIG)
XN = 196
YNB = Y_TCH + 3
bar(XN, m_r['out'].y - 4, YNB)
S.text(XN + 3.0, (m_r['out'].y + m_c['out'].y) / 2 + 9, '{nrow, ncol, ch}', size=2.0, weight='bold', rot=-90,
       anchor='middle')
W([m_r['out'], (XN - 0.9, m_r['out'].y)], 'bus', width=7, wfrac=0.6)
S.text(185, m_r['out'].y - 1.0, 'nrow', size=2.0, anchor='middle', italic=True)
W([m_c['out'], (XN - 0.9, m_c['out'].y)], 'bus', width=7, wfrac=0.6)
S.text(185, m_c['out'].y - 1.0, 'ncol', size=2.0, anchor='middle', italic=True)
W([(XP, Y_TCH), (XN + 0.9, Y_TCH)], 'bus', width=2, wfrac=0.5)
S.text(XP + 1.2, Y_TCH + 2.6, 'ch = pos[1:0]', size=2.0, italic=True)
rof = S.box(110, 341, 28, 42, 'ROM_OFF', '12 × 4 b', fill=F_ROM,
            pins=[('a', 'b', .5, 'A'), ('dr', 'r', (348 - 341) / 42, 'dr'), ('dc', 'r', (376 - 341) / 42, 'dc')],
            ssize=2.0)
W([rof['dr'], add_r['l']], 'bus', width=2, wfrac=0.45)
W([rof['dc'], add_c['l']], 'bus', width=2, wfrac=0.45)
tapc = S.box(88, 420, 24, 18, 'TAP', 'cont. 4 b', pins=[('clr', 't', .3, 'CLR'), ('en', 't', .75, 'EN'),
                                                       ('q', 'r', .5, '')],
             clk=('l', .55), rst=('l', .85), ssize=2.0)
XTJ = rof['a'].x
c10 = S.op(132, tapc['q'].y, '=')
k10 = S.const(132, tapc['q'].y + 10, '11')
W([k10['t'], c10['b']], 'bus')
W([tapc['q'], c10['l']], 'bus', width=4, wfrac=0.33, dots=[(XTJ, tapc['q'].y)], net='tap')
S.text(117.5, tapc['q'].y + 3.4, 'tap', size=2.2, italic=True)
YTAP = 395.4
W([(XTJ, tapc['q'].y), rof['a']], 'bus', net='tap', dots=[(XTJ, YTAP)])
nor_t = S.gate('nor', 152, 401, n=2, h=7, rot='l')
ctrl_tag(157.3, 398.6)
YAT = c10['r'].y
W([c10['r'], (X_AT10, YAT)], 'sig', arrow=False, name='at11', npos=0, nfrac=0.12, net='at11',
  dots=[(168, YAT)])
W([(168, YAT), (168, nor_t['ins'][0].y), nor_t['ins'][0]], 'sig', net='at11')
W([nor_t['out'], (tapc['en'].x, nor_t['out'].y), tapc['en']], 'sig')
S.text(132, nor_t['out'].y - 1.0, 'tap_en', size=2.1, anchor='middle', italic=True, color=C_SIG)
comb(80, 82, [tapc], up=False)

XPOS, XNAD, XRR, XCR = 270, 276, 282, 286
bin_ = S.box(292, 208, 80, 54, 'BRAM_IN', '65 536 × 8 b · lectura síncrona (1 ciclo)',
             fill=F_MEM, pins=[('we', 'l', .14, 'WE'), ('wa', 'l', .36, 'WADDR'), ('ra', 'l', .62, 'RADDR'),
                               ('din', 't', .85, 'DIN'), ('do', 'r', .5, 'DOUT')],
             clk=('l', .88), tsize=3.4, ssize=2.1)
btmp = S.box(292, 292, 80, 54, 'BRAM_TMP', '65 536 × 8 b · Gaussiano de la 1.ª pasada (LoG)',
             fill=F_MEM, pins=[('wa', 'l', .2, 'WADDR'), ('ra', 'l', .46, 'RADDR'),
                               ('we', 'b', .875, 'WE'), ('din', 'b', .95, 'DIN'), ('do', 'r', .5, 'DOUT')],
             clk=('l', .72), tsize=3.4, ssize=2.0)
m_src = S.mux(392, 276, name='MUX_SRC', labels=['0', '1'])
W([bin_['do'], (384, bin_['do'].y), (384, m_src['p0'].y), m_src['p0']], 'bus', width=8, wfrac=0.5)
S.text(378, bin_['do'].y + 3.2, 'dout_in', size=2.1, anchor='middle', italic=True)
W([btmp['do'], (384, btmp['do'].y), (384, m_src['p1'].y), m_src['p1']], 'bus', width=8, wfrac=0.5)
S.text(378, btmp['do'].y + 3.2, 'dout_tmp', size=2.1, anchor='middle', italic=True)
W([(XP, YPOS), (XPOS, YPOS)], 'bus', width=16, wfrac=0.84, arrow=False, net='pos', dots=[(XP, YPOS)])
S.text(266, YPOS - 1.0, 'pos', size=2.4, anchor='middle', italic=True)
W([(XPOS, bin_['wa'].y), (XPOS, btmp['wa'].y)], 'bus', arrow=False, net='pos', dots=[(XPOS, YPOS)])
W([(XPOS, bin_['wa'].y), bin_['wa']], 'bus', net='pos')
W([(XPOS, btmp['wa'].y), btmp['wa']], 'bus', net='pos')
S.dot(XPOS, btmp['wa'].y)
YNOR3 = nor['ins'][2].y
W([(X_CH, YPOS), (X_CH, YNOR3 + 4.5)], 'bus', width=2, wfrac=0.18, arrow=False, net='pos', dots=[(X_CH, YPOS)])
S.text(X_CH + 1.4, 120, 'ch = pos[1:0]', size=2.1, italic=True, rot=-90)
bar(X_CH, nor['ins'][1].y - 1.5, YNOR3 + 4.5)
W([(X_CH + 0.9, nor['ins'][1].y), nor['ins'][1]], 'sig', arrow=False)
W([(X_CH + 0.9, YNOR3), nor['ins'][2]], 'sig', arrow=False)
S.text(X_CH + 4.4, nor['ins'][1].y - 0.4, '[1]', size=1.8, color='#444')
S.text(X_CH + 4.4, YNOR3 + 2.4, '[0]', size=1.8, color='#444')
W([(X_WR, YWR), (X_WR, bin_['we'].y), bin_['we']], 'sig', dots=[(X_WR, or_cnt['ins'][1].y)], net='wr_in')
W([(X_WR, or_cnt['ins'][1].y), or_cnt['ins'][1]], 'sig', net='wr_in')
W([m_nz['out'], (412, m_nz['out'].y), (412, 186), (bin_['din'].x, 186), bin_['din']], 'bus', width=8,
  wpos=1, wfrac=0.22)
S.text(414, 160, 'noisy', size=2.4, italic=True)
W([srx['q'], m_nz['p0']], 'bus', width=8, wfrac=0.3, name='rx_data', npos=0, nfrac=0.18, nsize=2.4)
YNAD = 392
W([(XN, YNB), (XN, YNAD), (XNAD, YNAD), (XNAD, bin_['ra'].y), bin_['ra']], 'bus', width=16, wpos=1,
  wfrac=0.45, net='naddr', dots=[(XNAD, btmp['ra'].y)])
S.text(258, YNAD - 1.0, 'naddr', size=2.4, anchor='middle', italic=True)
W([(XNAD, btmp['ra'].y), btmp['ra']], 'bus', net='naddr')

reg_pix = S.box(434, 277, 14, 14, 'REG_PIX', '8 b', pins=[('d', 'l', .5, ''), ('q', 'r', .5, '')],
                clk=('l', .85), tsize=2.3, ssize=2.0)
reg_w = S.box(455, 297, 14, 12, 'REG_W', '8 b', pins=[('d', 'b', .5, ''), ('q', 't', .5, '')],
              clk=('l', .7), tsize=2.3, ssize=2.0)
mul = S.op(462, 284, '×')
add = S.op(480, 284, '+')
acc_r = S.box(492, 272, 22, 24, 'ACC', 'registro 15 b',
              pins=[('d', 'l', .5, 'D'), ('clr', 'b', .62, 'CLR'), ('q', 'r', .5, 'Q')],
              clk=('t', .2), rst=('t', .42), ssize=2.0, title_dy=1.5)
W([m_src['out'], reg_pix['d']], 'bus', width=8, wfrac=0.2)
S.text(423, m_src['out'].y - 1.0, 'pix', size=2.4, anchor='middle', italic=True)
W([reg_pix['q'], mul['l']], 'bus')
S.slash(453.0, 284, 9)
S.text(449.2, 288.3, '{0, pix_q}', size=1.8, color='#444')
S.text(441, 295.4, 'segmentación (v4.1):', size=1.8, anchor='middle', color='#444')
S.text(441, 298.2, 'parte el camino largo', size=1.8, anchor='middle', color='#444')
W([mul['r'], add['l']], 'bus', width=15, wfrac=0.5)
S.text(471, 289.5, 'prod', size=2.1, anchor='middle', italic=True)
W([add['r'], acc_r['d']], 'bus', width=15, wfrac=0.45)
S.text(488, 289.5, 'sum', size=2.1, anchor='middle', italic=True)
W([acc_r['q'], (548, acc_r['q'].y)], 'bus', width=15, wfrac=0.62, dots=[(518, acc_r['q'].y)], net='acc')
S.text(526, acc_r['q'].y - 1.0, 'acc', size=2.4, anchor='middle', italic=True)
W([(518, acc_r['q'].y), (518, 306), (add['b'].x, 306), add['b']], 'bus', net='acc')
romw = S.box(436, 316, 32, 22, 'ROM_W', '64 × 8 b (pesos)', fill=F_ROM,
             pins=[('w', 't', (462 - 436) / 32, ''), ('k', 'b', .78, 'ksel'), ('t', 'b', .28, 'tap')],
             ssize=2.0)
W([romw['w'], reg_w['d']], 'bus', width=8, wfrac=0.5)
S.text(467.2, 313.4, 'w (con signo)', size=2.0, italic=True)
W([reg_w['q'], mul['b']], 'bus')
S.text(464.0, 293.8, 'w_q', size=2.0, italic=True)
c0 = S.op(acc_r['clr'].x, 328, '=')
k0c = S.const(acc_r['clr'].x + 11, 328, '0')
W([k0c['l'], c0['r']], 'bus')
W([c0['t'], acc_r['clr']], 'sig')
S.text(acc_r['clr'].x + 1.4, 312.5, 'acc_clr', size=2.0, italic=True, color=C_SIG)
comb(acc_r['clk'].x, acc_r['rst'].x, [acc_r], up=False)
comb(428, None, [reg_pix, reg_w], up=False)

div = S.op(554, acc_r['q'].y, '/')
k16 = S.const(554, acc_r['q'].y + 11, '16')
W([k16['t'], div['b']], 'bus')
S.text(554, acc_r['q'].y + 18.5, '= acc[14:4]', size=2.0, anchor='middle', color='#444')
S.text(554, acc_r['q'].y + 21.3, '(solo cables)', size=2.0, anchor='middle', color='#444')
YS = acc_r['q'].y
m_b = S.mux(616, YS - 10.67, name='MUX_B')
W([div['r'], m_b['p0']], 'bus', width=11, wfrac=0.1, dots=[(566, YS), (572, YS)], net='s')
S.text(590, YS - 1.0, 's', size=2.4, anchor='middle', italic=True)
neg = S.op(580, 246, '−')
k0n = S.const(580, 236.5, '0')
W([k0n['b'], neg['t']], 'bus')
S.text(586, 238.0, '0 − s', size=2.0, color='#444')
W([(566, YS), (566, neg['l'].y), neg['l']], 'bus', net='s')
m_a = S.mux(598, neg['r'].y - 5.33, name='MUX_A')
W([neg['r'], m_a['p1']], 'bus', width=11, wfrac=0.5)
k0a = S.const(590, m_a['p0'].y + 4.0, '0')
W([k0a['r'], (594, k0a['r'].y), (594, m_a['p0'].y), m_a['p0']], 'bus')
W([m_a['out'], (610, m_a['out'].y), (610, m_b['p1'].y), m_b['p1']], 'bus', width=11, wpos=1, wfrac=0.3)
S.text(612, 262, 'a', size=2.4, italic=True)
W([(572, YS), (572, 304), (m_b['sel'].x, 304), m_b['sel']], 'sig', net='s')
S.text(596, 308.0, 's[10] = signo (s < 0)', size=2.1, anchor='middle', italic=True, color=C_SIG)
m_c2 = S.mux(650, YS - 16, name='MUX_SAT')
W([m_b['out'], (636, m_b['out'].y), (636, m_c2['p0'].y), m_c2['p0']], 'bus', width=11, wpos=0, wfrac=0.5,
  dots=[(636, m_c2['p0'].y)], net='v')
S.text(631, m_b['out'].y + 3.5, 'v', size=2.4, anchor='middle', italic=True)
gt = S.op(642, 318, '>')
k255 = S.const(642, 329, '255')
W([k255['t'], gt['b']], 'bus')
W([(636, m_c2['p0'].y), (636, gt['l'].y), gt['l']], 'bus', net='v')
k255b = S.const(641, m_c2['p1'].y - 6, '255')
W([k255b['r'], (646, k255b['r'].y), (646, m_c2['p1'].y), m_c2['p1']], 'bus', width=8, wpos=1, wfrac=0.5,
  wdx=0.0)
W([gt['r'], (m_c2['sel'].x, gt['r'].y), m_c2['sel']], 'sig', name='big', npos=0, nfrac=0.45)
YY = m_c2['out'].y
W([m_c2['out'], (701, YY)], 'bus', width=8, wfrac=0.17, dots=[(664, YY)], net='y')
S.text(670, YY - 1.0, 'y', size=2.6, anchor='middle', italic=True, weight='bold')

XM = 704
srt = S.box(722, 262, 36, 34, 'SR_TX', 'desplaz. 10 b · SI = 1',
            pins=[('d', 'l', (YY - 262) / 34, 'D'), ('ld', 'l', .5, 'LOAD'), ('sh', 't', .75, 'SH'),
                  ('q', 'r', .3, 'Q[0]')],
            clk=('l', .74), rst=('l', .92), ssize=2.0)
bar(XM, YY - 9, YY + 9)
S.text(XM - 3.0, YY - 10.4, '{1, y, 0}', size=2.2, anchor='middle', weight='bold')
W([(701, YY), (XM - 0.9, YY)], 'bus', net='y', arrow=False)
k1 = S.const(692, YY - 6, '1')
k0t = S.const(692, YY + 6, '0')
W([k1['r'], (XM - 0.9, k1['r'].y)], 'sig')
W([k0t['r'], (XM - 0.9, k0t['r'].y)], 'sig')
W([(XM + 0.9, YY), srt['d']], 'bus', width=10, wfrac=0.5)
baudt = S.box(722, 220, 36, 22, 'BAUD_TX', 'contador mód 868 · 10 b',
              pins=[('clr', 'l', .35, 'CLR'), ('q', 'r', .5, '')], clk=('l', .68), rst=('l', .88), ssize=1.9)
bitt = S.box(722, 316, 36, 24, 'BIT_TX', 'cont. ↓ 4 b · carga 10',
             pins=[('ld', 'l', .3, 'LOAD'), ('dec', 't', .75, 'DEC'), ('q', 'r', .5, '')],
             clk=('l', .62), rst=('l', .85), ssize=1.9)
c867 = S.op(772, baudt['q'].y, '=')
k867 = S.const(772, baudt['q'].y + 10, '867')
W([k867['t'], c867['b']], 'bus')
W([baudt['q'], c867['l']], 'bus', width=10, wfrac=0.5)
S.text(762, baudt['q'].y + 3.4, 'baud_tx', size=1.9, anchor='middle', italic=True)
W([c867['r'], (790, c867['r'].y), (790, 312), (bitt['dec'].x, 312), bitt['dec']], 'sig', name='tick', npos=0,
  nfrac=0.55, dots=[(790, 256)], net='tick')
W([(790, 256), (srt['sh'].x, 256), srt['sh']], 'sig', net='tick')
cne = S.op(772, bitt['q'].y, '≠')
k0b = S.const(772, bitt['q'].y + 10, '0')
W([k0b['t'], cne['b']], 'bus')
W([bitt['q'], cne['l']], 'bus', width=4, wfrac=0.5)
S.text(762, bitt['q'].y + 3.4, 'bit_tx', size=1.9, anchor='middle', italic=True)
n_tb = S.gate('not', 779, bitt['q'].y - 2.5)
W([cne['r'], n_tb['i0']], 'sig')
S.text(780.5, bitt['q'].y - 3.4, 'tx_busy', size=1.9, anchor='middle', italic=True, color=C_SIG)
XNB = 796
W([n_tb['out'], (XNB, n_tb['out'].y), (XNB, 214), (716, 214), (716, baudt['clr'].y), baudt['clr']], 'sig',
  dots=[(XNB, n_tb['out'].y)], net='ntxb')
S.text(XNB + 1.2, 300, '~tx_busy', size=2.1, italic=True, color=C_SIG, rot=-90)
txp = S.port_out(806, srt['q'].y, 'UART_RXD_OUT', size=2.4)
W([srt['q'], txp], 'sig', name='tx', npos=0, nfrac=0.4)
comb(708, 710, [baudt, srt, bitt], up=False)

mode = S.box(300, 412, 28, 18, 'MODE', 'registro 3 b',
             pins=[('d', 'l', .5, 'D'), ('en', 't', .75, 'EN'), ('q', 'r', .5, 'Q')],
             clk=('t', .18), rst=('t', .38), ssize=1.9, title_dy=1.0)
fsm = S.box(300, 444, 40, 32, 'FSM', 'Moore · estado 2 b',
            pins=[('fin', 'l', .3, 'fin'), ('btn', 'l', .62, 'BTNC'), ('tp', 'b', .5, 'two_pass'),
                  ('st', 'r', .5, 'state')],
            clk=('t', .15), rst=('t', .3), ssize=2.0, title_dy=-1.5)
XDEC, WDEC = 356, 62
X_TW = 362.0
dec = S.box(XDEC, 412, WDEC, 60, 'DECODIFICADOR', 'tabla de verdad: arriba a la derecha', fill=F_ROM,
            pins=[('mode', 'l', (421 - 412) / 60, 'mode'), ('st', 'l', (460 - 412) / 60, 'state'),
                  ('idle', 't', (358.5 - XDEC) / WDEC, ''), ('tw', 't', (X_TW - XDEC) / WDEC, ''),
                  ('src', 't', (395.75 - XDEC) / WDEC, ''),
                  ('ksel', 'r', .14, 'ksel'), ('absm', 'r', .3, 'absm'), ('tw2', 'r', .5, 'tmp_wr'),
                  ('tp', 'b', .2, 'two_pass')],
            ssize=1.8, tsize=2.9)
S.text(358.5, 410.6, 'idle', size=1.9, anchor='end', color='#222')
S.text(X_TW + 0.8, 410.6, 'tmp_wr', size=1.9, color='#222')
S.text(395.75 + 0.8, 410.6, 'src_tmp', size=1.9, color='#222')
sw20 = S.port_in(256, mode['d'].y, 'SW[2:0]')
W([sw20, mode['d']], 'busc', width=3, wfrac=0.82)
btn = S.port_in(266, fsm['btn'].y, 'BTNC')
W([btn, fsm['btn']], 'sig')
W([(X_FIN, YF), (X_FIN, fsm['fin'].y), fsm['fin']], 'sig', net='fin')
W([mode['q'], dec['mode']], 'busc', width=3, wfrac=0.75, dots=[(338, mode['q'].y)], net='mode')
S.text(343, mode['q'].y - 1.0, 'mode', size=2.2, anchor='middle', italic=True, color=C_SIG)
W([fsm['st'], dec['st']], 'busc', width=2, wfrac=0.75, dots=[(346, fsm['st'].y)], net='state')
S.text(343.5, fsm['st'].y - 1.0, 'state', size=2.2, anchor='middle', italic=True, color=C_SIG)
YL76, YL20, YL53 = 497, 505, 513
l76 = S.port_out(352, YL76, 'LED[7:6]', size=2.3)
l20 = S.port_out(352, YL20, 'LED[2:0]', size=2.3)
l53 = S.port_out(352, YL53, 'LED[5:3]', size=2.3)
W([(346, fsm['st'].y), (346, YL76), l76], 'busc', net='state', width=2, wpos=1, wfrac=0.5)
W([(338, mode['q'].y), (338, YL20), l20], 'busc', net='mode', width=3, wpos=1, wfrac=0.5)
k000 = S.const(338, YL53, '000')
W([k000['r'], l53], 'bus', width=3, wfrac=0.5)
W([dec['tp'], (dec['tp'].x, 482), (fsm['tp'].x, 482), fsm['tp']], 'sig', net='tp')
YIDL = 398.6
W([dec['idle'], (dec['idle'].x, YIDL), (X_IDLE, YIDL), (X_IDLE, and_wr['i1'].y)], 'sig', net='idle',
  name='idle', npos=1, nfrac=0.75, dots=[(mode['en'].x, YIDL), (X_IDLE, YIDL)])
W([(mode['en'].x, YIDL), mode['en']], 'sig', net='idle')
W([(X_IDLE, YIDL), (X_IDLE, nor_t['ins'][1].y), nor_t['ins'][1]], 'sig', net='idle')
W([dec['tw'], btmp['we']], 'sig', net='tw')
W([dec['src'], m_src['sel']], 'sig', net='src')
S.text(397.0, 365.0, 'src_tmp', size=2.1, italic=True, color=C_SIG, rot=-90)
S.text(X_TW + 1.2, 375.0, 'we_tmp = tmp_wr', size=2.1, italic=True, color=C_SIG, rot=-90)
W([dec['ksel'], (romw['k'].x, dec['ksel'].y), romw['k']], 'busc', width=2, wpos=0, wfrac=0.5, net='ksel')
S.text(440, dec['ksel'].y - 1.0, 'ksel', size=2.2, anchor='middle', italic=True, color=C_SIG)
W([dec['absm'], (m_a['sel'].x, dec['absm'].y), m_a['sel']], 'sig', net='absm')
S.text(520, dec['absm'].y - 1.0, 'absm', size=2.2, anchor='middle', italic=True, color=C_SIG)
and_go = S.gate('and', 470 - 4.5, 506 - 4, n=2, h=8, rot='u', name=None)
S.text(and_go['out'].x + 5.5, and_go['out'].y + 6.0, 'AND_go', size=2.0, color='#666')
S.text(440, 518.0, 'at11', size=2.2, anchor='middle', italic=True, color=C_SIG)
S.text(520, 521.0, '~tx_busy', size=2.2, anchor='middle', italic=True, color=C_SIG)
YA, YB = 519, 522
W([(X_AT10, YAT), (X_AT10, YA), (and_go['i0'].x, YA), and_go['i0']], 'sig', net='at11')
W([(XNB, n_tb['out'].y), (XNB, YB), (and_go['i1'].x, YB), and_go['i1']], 'sig', net='ntxb')
YGO = 490
W([and_go['out'], (and_go['out'].x, YGO), (X_GO, YGO), (X_GO, or_cnt['ins'][0].y), or_cnt['ins'][0]], 'sig',
  net='go', name='go', npos=1, nfrac=0.3, dots=[(and_go['out'].x, YGO), (X_GO, 412)])
W([(X_GO, 412), (tapc['clr'].x, 412), tapc['clr']], 'sig', net='go')
n_tw = S.gate('not', 640, dec['tw2'].y - 2.5)
W([dec['tw2'], n_tw['i0']], 'sig', net='tw')
and_tx = S.gate('and', 690, 468, n=2, h=8)
W([n_tw['out'], (660, n_tw['out'].y), (660, and_tx['i0'].y), and_tx['i0']], 'sig')
S.text(668, n_tw['out'].y - 1.0, '~tmp_wr', size=2.1, anchor='middle', italic=True, color=C_SIG)
W([(and_go['out'].x, YGO), (684, YGO), (684, and_tx['i1'].y), and_tx['i1']], 'sig', net='go')
W([and_tx['out'], (715, and_tx['out'].y), (715, srt['ld'].y), srt['ld']], 'sig', net='txs',
  dots=[(715, bitt['ld'].y)])
W([(715, bitt['ld'].y), bitt['ld']], 'sig', net='txs')
S.text(716.5, 452, 'tx_start', size=2.2, italic=True, color=C_SIG, rot=-90)
XC9, XR9 = 286, 282
W([(XC9, CLKY), (XC9, 440)], 'clk', arrow=False, net='CLK')
W([(XR9, RSTY), (XR9, 438)], 'rst', arrow=False, net='RST')
S.dot(XC9, CLKY, C_CLK); S.dot(XR9, RSTY, C_RST)
W([(XC9, bin_['clk'].y), bin_['clk']], 'clk', arrow=False, net='CLK')
W([(XC9, btmp['clk'].y), btmp['clk']], 'clk', arrow=False, net='CLK')
S.dot(XC9, bin_['clk'].y, C_CLK); S.dot(XC9, btmp['clk'].y, C_CLK)
W([(XC9, 408), (mode['clk'].x, 408), mode['clk']], 'clk', arrow=False, net='CLK')
W([(XR9, 406), (mode['rst'].x, 406), mode['rst']], 'rst', arrow=False, net='RST')
S.dot(XC9, 408, C_CLK); S.dot(XR9, 406, C_RST)
W([(XC9, 440), (fsm['clk'].x, 440), fsm['clk']], 'clk', arrow=False, net='CLK')
W([(XR9, 438), (fsm['rst'].x, 438), fsm['rst']], 'rst', arrow=False, net='RST')

YFB = 383
W([(664, YY), (664, YFB), (btmp['din'].x, YFB), btmp['din']], 'bus', width=8, wpos=1, wfrac=0.45, net='y')
S.text(600, YFB - 1.0, 'y (realimentación a BRAM_TMP)', size=2.2, anchor='middle', italic=True)
W([(XTJ, YTAP), (romw['t'].x, YTAP), romw['t']], 'bus', width=4, wfrac=0.55, net='tap')
S.text(420, YTAP - 1.0, 'tap', size=2.3, anchor='middle', italic=True)
W([(romw['t'].x, YTAP), (c0['b'].x, YTAP), c0['b']], 'bus', net='tap')
S.dot(romw['t'].x, YTAP)

def table(x, y, cols, rows, cw, rh=4.0, title=None, size=2.25, head_fill='#e6e6e6', fills=None):
    if title:
        S.text(x, y - 1.6, title, size=2.7, weight='bold')
    tw = sum(cw)
    nrows = len(rows) + 1
    S.rect(x, y, tw, rh * nrows, fill='#ffffff', stroke='#444', sw=0.3)
    S.rect(x, y, tw, rh, fill=head_fill, stroke='#444', sw=0.3)
    cx = x
    for i, c in enumerate(cols):
        S.text(cx + cw[i] / 2, y + rh * 0.72, c, size=size, anchor='middle', weight='bold')
        cx += cw[i]
    for r, row in enumerate(rows):
        yy = y + rh * (r + 1)
        if fills and fills[r]:
            S.rect(x, yy, tw, rh, fill=fills[r], stroke='none')
        cx = x
        for i, v in enumerate(row):
            S.text(cx + cw[i] / 2, yy + rh * 0.72, str(v), size=size, anchor='middle')
            cx += cw[i]
        S.line(x, yy, x + tw, yy, color='#bbb', sw=0.15, layer='elem')
    cx = x
    for c in cw[:-1]:
        cx += c
        S.line(cx, y, cx, y + rh * nrows, color='#bbb', sw=0.15, layer='elem')
    S.rect(x, y, tw, rh * nrows, fill='none', stroke='#444', sw=0.3)


S.frame(430, 30, 401, 140, 'Contenido de las ROM, decodificador y FSM (mismos valores que el código)', 'T')
KG = [1, 2, 1, 2, 4, 2, 1, 2, 1]
KL = [0, 16, 0, 16, -64, 16, 0, 16, 0]
KI = [0, 0, 0, 0, 16, 0, 0, 0, 0]
KU = [-1, -2, -1, -2, 28, -2, -1, -2, -1]
OFF = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
rows = []
for t in range(12):
    if 1 <= t <= 9:
        rows.append([t, f'{OFF[t-1][0]:+d},{OFF[t-1][1]:+d}', KG[t-1], KL[t-1], KI[t-1], KU[t-1]])
    else:
        rows.append([t, '—', 0, 0, 0, 0])
table(436, 46, ['tap', 'vecino', 'G 00', 'L 01', 'ID 10', 'US 11'], rows, [9, 15, 11, 11, 11, 11],
      rh=3.9, title='ROM_W[{ksel, tap}]')
S.text(436, 100.0, 'fila t = peso del píxel que sale de la BRAM en el tap t', size=2.0, color='#444')
S.text(436, 103.3, '(pedido en t − 1); REG_PIX y REG_W lo pasan al ACC en t + 1', size=2.0, color='#444')
S.text(436, 99.5 + 0 * 4.2 + 40, '', size=1)
rows = []
for t in range(12):
    dr, dc = OFF[t] if t <= 8 else (0, 0)
    rows.append([t, f'{dr:+d}', f'{dc:+d}', f'{dr & 3:02b} {dc & 3:02b}'])
table(530, 46, ['tap', 'dr', 'dc', 'dr dc'], rows, [9, 9, 9, 15], rh=3.9, title='ROM_OFF[tap]')
S.text(530, 100.0, 'taps 9, 10 y 11 = centro', size=2.0, color='#444')
S.text(530, 103.3, '−1 = 11, 0 = 00, +1 = 01', size=2.0, color='#444')
def kmat(x, y, name, K, note):
    S.text(x, y - 1.6, name, size=2.5, weight='bold')
    for i in range(9):
        r, c = divmod(i, 3)
        S.rect(x + c * 8, y + r * 5, 8, 5, fill='#fff', stroke='#666', sw=0.2)
        S.text(x + c * 8 + 4, y + r * 5 + 3.6, str(K[i]), size=2.4, anchor='middle')
    S.text(x, y + 19.2, note, size=1.95, color='#444')


kmat(470, 112, 'Gaussiano (G)', KG, '÷16 → y = G')
kmat(503, 112, 'Laplaciano ×16', KL, '÷16 → |L| sat.')
kmat(536, 112, 'Identidad ×16', KI, 'bypass')
kmat(569, 112, 'Unsharp ×16', KU, '= 32·δ − G ÷16')
S.text(470, 140.5, 'LoG = 2 pasadas: G (BRAM_IN → BRAM_TMP) y luego L (BRAM_TMP → UART).', size=2.1)
S.text(470, 144.0, 'Todos los pesos ×16 → la normalización es siempre ÷16 = acc[14:4] (cables).', size=2.1)
S.text(470, 147.5, 'US: 2·I − G = (32·I − 16·G)/16 → un solo kernel; recorte a 0..255.', size=2.1)
rows = [['IDLE', 'x xx', '—', '—', 0, 0, 1, '—'],
        ['P1', '0 00 (G)', '00', 0, 0, 0, 0, 0],
        ['P1', '0 01 (L)', '01', 1, 0, 0, 0, 0],
        ['P1', '0 10 (LoG)', '00', 0, 0, 1, 0, 1],
        ['P1', '0 11 (US)', '11', 0, 0, 0, 0, 0],
        ['P1', '1 xx (byp)', '10', 0, 0, 0, 0, 0],
        ['P2', 'x xx', '01', 1, 1, 0, 0, 1]]
table(606, 46, ['state', 'MODE', 'ksel', 'absm', 'src_tmp', 'tmp_wr', 'idle', 'two_pass'], rows,
      [11, 17, 9, 9, 13, 12, 9, 15], rh=4.4, title='DECODIFICADOR (combinacional)')
S.text(606, 85.5, 'two_pass = (MODE = 010) · idle = (state = 00) · tx_start = go·¬tmp_wr', size=2.05)
def state_c(x, y, name, code):
    S.circle(x, y, 7.2, fill=F_SEQ, sw=0.4)
    S.text(x, y + 0.2, name, size=2.6, anchor='middle', weight='bold')
    S.text(x, y + 3.6, code, size=2.1, anchor='middle', color='#444')


sx = [640, 700, 760]
sy = 118
state_c(sx[0], sy, 'IDLE', '00')
state_c(sx[1], sy, 'P1', '01')
state_c(sx[2], sy, 'P2', '10')
S.text(606, 98.5, 'FSM Moore (estado = 2 FF; IDLE → P1 cambia solo el bit 0)', size=2.7, weight='bold')


def arc(p, q, bend, label, ldy=0, ldx=0):
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + bend
    S.add('elem', f'<path d="M{p[0]:.2f},{p[1]:.2f} Q{mx:.2f},{my:.2f} {q[0]:.2f},{q[1]:.2f}" fill="none" '
                  f'stroke="#000" stroke-width="0.35"/>')
    import math
    ang = math.atan2(q[1] - my, q[0] - mx)
    L, Wd = 2.0, 0.85
    p1 = (q[0] - L * math.cos(ang) + Wd * math.sin(ang), q[1] - L * math.sin(ang) - Wd * math.cos(ang))
    p2 = (q[0] - L * math.cos(ang) - Wd * math.sin(ang), q[1] - L * math.sin(ang) + Wd * math.cos(ang))
    S.add('elem', f'<polygon points="{q[0]:.2f},{q[1]:.2f} {p1[0]:.2f},{p1[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}" '
                  f'fill="#000"/>')
    S.text((p[0] + q[0]) / 2 + ldx, my + (-1.2 if bend < 0 else 3.0) + ldy, label, size=2.1, anchor='middle')


arc((sx[0] + 6.4, sy - 3.3), (sx[1] - 6.4, sy - 3.3), -9, 'fin + BTNC')
arc((sx[1] + 6.4, sy - 3.3), (sx[2] - 6.4, sy - 3.3), -9, 'fin · two_pass')
arc((sx[1] - 6.4, sy + 3.3), (sx[0] + 6.4, sy + 3.3), 9, 'fin · ¬two_pass')
arc((sx[2] - 5.0, sy + 5.2), (sx[0] + 5.0, sy + 5.2), 20, 'fin (2.ª pasada terminada)', ldy=-0.8)
S.text(606, 150.5, 'IDLE: recibe la imagen (fin = último byte escrito) o espera BTNC.', size=2.05)
S.text(606, 154.0, 'P1: 1.ª pasada (G, L, US o bypass → UART; en LoG: G → BRAM_TMP).', size=2.05)
S.text(606, 157.5, 'P2: solo LoG: L sobre BRAM_TMP → UART. fin = último byte entregado.', size=2.05)
S.text(606, 161.0, 'MODE copia SW[2:0] en IDLE y queda congelado en P1/P2.', size=2.05)

LX, LY = 12, 470
S.rect(LX, LY, 208, 114, fill='#fbfbfb', stroke='#7a7a7a', sw=0.4, dash='2.2,1.2', layer='frame')
S.text(LX + 3, LY + 6.5, 'Cómo leer esta hoja', size=4.0, weight='bold', color='#303030')
yy = LY + 14
W([(LX + 4, yy), (LX + 22, yy)], 'bus', width=8, wfrac=0.5, arrow=True)
S.text(LX + 26, yy + 0.9, 'bus de datos (negro grueso); /8 = 8 bits', size=2.4)
yy += 7
W([(LX + 4, yy), (LX + 22, yy)], 'sig', arrow=True)
S.text(LX + 26, yy + 0.9, 'señal de control o estado de 1 bit (azul)', size=2.4)
yy += 7
W([(LX + 4, yy), (LX + 22, yy)], 'busc', width=3, wfrac=0.5, arrow=True)
S.text(LX + 26, yy + 0.9, 'bus de control (azul grueso), p. ej. ksel, mode', size=2.4)
yy += 7
W([(LX + 4, yy), (LX + 22, yy)], 'clk', arrow=False)
W([(LX + 4, yy + 2.5), (LX + 22, yy + 2.5)], 'rst', arrow=False)
S.text(LX + 26, yy + 2.0, 'reloj (gris) y reset síncrono (lila): llegan a todos los registros', size=2.4)
yy += 9
S.dot(LX + 13, yy)
W([(LX + 4, yy), (LX + 22, yy)], 'sig', arrow=False, net='lg1')
W([(LX + 13, yy), (LX + 13, yy + 4)], 'sig', arrow=False, net='lg1')
S.text(LX + 26, yy + 0.9, 'punto = unión (el cable se reparte)', size=2.4)
yy += 8
W([(LX + 4, yy), (LX + 22, yy)], 'sig', arrow=False, net='lg2')
W([(LX + 13, yy - 3), (LX + 13, yy + 3)], 'sig', arrow=False, net='lg3')
S.text(LX + 26, yy + 0.9, 'salto = cruce SIN conexión', size=2.4)
yy += 8
S.op(LX + 8, yy, '+', r=3.2, size=3.6)
S.const(LX + 18, yy, '255')
S.text(LX + 26, yy + 0.9, 'operador (círculo gris) · constante (rectángulo gris)', size=2.4)
yy += 9
S.mux(LX + 6, yy - 6, h=12, w=6)
S.text(LX + 26, yy + 0.9, 'MUX: la entrada marcada 1 pasa cuando el selector = 1', size=2.4)
yy += 9
S.rect(LX + 4, yy - 3, 8, 6, fill=F_SEQ, sw=0.35)
S.rect(LX + 13, yy - 3, 8, 6, fill=F_MEM, sw=0.35)
S.rect(LX + 22, yy - 3, 8, 6, fill=F_ROM, sw=0.35)
S.text(LX + 33, yy + 0.9, 'registro / contador / FSM · memoria · ROM o tabla', size=2.4)
yy += 8
S.port_in(LX + 4, yy, 'PIN', w=8)
ctrl_tag(LX + 22, yy + 0.8)
S.text(LX + 28, yy + 0.9, 'pin de la FPGA · compuerta del control (9) junto a su uso', size=2.4)
yy += 9
S.text(LX + 4, yy, 'Solo los pines de la FPGA son pentágonos. No hay etiquetas de conexión:', size=2.4, weight='bold')
S.text(LX + 4, yy + 4.2, 'cada señal se sigue por su cable, de la salida que la produce a cada entrada.', size=2.4)
S.text(LX + 4, yy + 8.4, 'Las tablas «T» muestran el contenido de las ROM y del decodificador.', size=2.4)

TX, TY = 560, 530
S.rect(TX, TY, 271, 54, fill='#ffffff', stroke='#303030', sw=0.5, layer='frame')
S.line(TX, TY + 14, TX + 271, TY + 14, color='#303030', sw=0.3, layer='frame')
S.line(TX + 160, TY + 14, TX + 160, TY + 54, color='#303030', sw=0.3, layer='frame')
S.text(TX + 4, TY + 9.5, 'Image Processor (2D filters) · esquemático RTL v4.1', size=5.2, weight='bold')
S.text(TX + 4, TY + 21, 'Electrónica Digital · Escuela Colombiana de Ingeniería', size=2.8)
S.text(TX + 4, TY + 27, 'Equipo: Edison Torres · Juan Guaman', size=2.8)
S.text(TX + 4, TY + 33, 'Tarjeta: Nexys A7-100T (XC7A100T) · 100 MHz', size=2.8)
S.text(TX + 4, TY + 39, 'UART 115 200 Bd 8N1 · imagen 128 × 128 RGB (49 152 B)', size=2.8)
S.text(TX + 4, TY + 45, 'HDL: SystemVerilog · simulación: Icarus Verilog y Vivado xsim (PASS)', size=2.8)
S.text(TX + 4, TY + 51, 'Requisitos: R-P1 (filtros), R-P2 (UART), R-P3 (SW), R-P4 (ruido), R-G06', size=2.8)
S.text(TX + 164, TY + 21, 'Versión: v4.1 (MAC segmentado)', size=2.8)
S.text(TX + 164, TY + 27, 'Fecha: 18-nov-2026', size=2.8)
S.text(TX + 164, TY + 33, 'Hoja: 1 de 1 (A1)', size=2.8)
S.text(TX + 164, TY + 39, 'Recursos (Vivado 2025.2, implementado):', size=2.8)
S.text(TX + 164, TY + 45, '313 LUT · 137 FF · 32 RAMB36 · 0 DSP · WNS +2,11 ns', size=2.5)
S.text(TX + 164, TY + 51, 'Detalle: Explicacion_v4_1.pdf', size=2.8)

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'esquematico_v4_1.svg'), 'w') as f:
    f.write(S.svg())
print('svg ok')
