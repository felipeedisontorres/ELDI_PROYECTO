"""Esquemático RTL completo y continuo del procesador de imágenes (proyecto #8)."""
import os
from sch import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
os.makedirs(OUT, exist_ok=True)

W, H = 4480, 2600
s = Sheet(W, H)

s.text(40, 46, "Procesador de imágenes con filtros 2D — esquemático RTL completo (registros, multiplexores, memorias y control)",
       26, "start", INK, "bold")
s.text(40, 74, "Un solo dominio de reloj: CLK = 100 MHz para todos los registros, contadores y BRAM (triángulo = entrada de reloj). "
               "Negro grueso = bus con su ancho · rojo punteado = control · etiqueta = conexión por nombre de red.", 15, "start", "#444")

# =====================================================================================
# 1. ENTRADA SERIE: pin -> sincronizador -> uart_rx
# =====================================================================================
tip = s.pin(30, 345, "UART_TXD_IN", "in")
s.group(205, 283, 190, 122, "SYNC 2FF")
f1 = s.reg(222, 317, 64, 56, "FF")
f2 = s.reg(312, 317, 64, 56, "FF")
s.wire([tip, f1["d"]], "w", arrow=True)
s.wire([f1["q"], f2["d"]], "w", arrow=True)

s.group(420, 118, 630, 520, "uart_rx · receptor 8N1 (115 200 baudios)")
ys = 250  # eje del registro de desplazamiento
cat_rx = s.op(575, ys, "{ }", r=17, size=12)
m1 = s.mux("M1", 640, ys - 136 * 2 / 3, 2, 136, labels=["0 ret.", "1 desp."], sel="bottom")
srx = s.reg(740, ys - 35, 120, 70, "SR_RX", "8 b")
s.wire([f2["q"], (520, 345), (520, ys), cat_rx["l"]], "w", arrow=True, label="rx_s", lpos=0, ldx=8)
s.wire([cat_rx["r"], m1["ins"][1]], "b", arrow=True, width=8)
s.text(560, ys + 32, "{rx_s, sr[7:1]}", 10.5, "middle", "#555", mono=True)
m1o = m1["out"]
s.wire([m1o, (700, m1o[1]), (700, ys), srx["d"]], "b", arrow=True, width=8, wpos=2)
s.dot(890, ys)
s.wire([srx["q"], (890, ys), (890, 158), (610, 158), (610, m1["ins"][0][1]), m1["ins"][0]], "b", arrow=True)
s.text(750, 152, "sr[7:0] (retener)", 10.5, "middle", "#555", mono=True)
s.dot(610, 190)
s.wire([(610, 190), (575, 190), cat_rx["t"]], "b", arrow=True)
s.text(570, 185, "sr[7:1]", 10.5, "end", "#555", mono=True)
s.flag_to(m1["sel"], "sample", "bottom", gap=18)

bcnt = s.reg(560, 395, 120, 66, "BAUD_CNT", "10 b  (+1)", fill=CNTF, clr=True)
c867 = s.op(780, 405, "=", r=16)
c433 = s.op(780, 478, "=", r=16)
s.const(c867["t"][0] + 13, 377, "867")
s.wire([(c867["t"][0], 388), c867["t"]], "b")
s.dot(730, 428)
s.wire([bcnt["q"], (730, 428), (730, 405), c867["l"]], "b", width=10, wpos=0)
s.wire([(730, 428), (730, 478), c433["l"]], "b")
s.const(c433["b"][0] + 13, 509, "433")
bitc = s.reg(560, 535, 120, 66, "BIT_CNT", "3 b  (+1)", fill=CNTF, en=True, clr=True)
c7 = s.op(780, 568, "=", r=16)
s.const(c7["b"][0] + 10, 598, "7")
s.wire([bitc["q"], c7["l"]], "b", width=3)
s.flag_to(bcnt["clr"], "cnt_clr", "top", gap=14)
s.flag_to(bitc["en"], "bit_en", "top", gap=12)
s.flag_to(bitc["clr"], "cnt_clr", "top", gap=12)
s.block(880, 385, 155, 225, ["FSM_RX", "2 b", "IDLE · START", "DATA · STOP", "", "salidas:", "sample, bit_en,", "cnt_clr, rx_valid"],
        fill=FSMF, size=11.5)
s.wire([c867["r"], (880, 405)], "c", arrow=True, label="tick", ldx=6, ldy=-6)
s.wire([c433["r"], (880, 478)], "c", arrow=True, label="half", ldx=6, ldy=-6)
s.wire([c7["r"], (880, 568)], "c", arrow=True, label="last_bit", ldx=6, ldy=-6)
s.dot(520, 345)
s.wire([(520, 345), (520, 620), (860, 620), (860, 595), (880, 595)], "w", arrow=True)
s.text(690, 614, "rx_s (detección del bit de start)", 10.5, "middle", "#555", mono=True)

# =====================================================================================
# 2. ENSAMBLADOR DE PÍXEL
# =====================================================================================
s.group(1075, 118, 470, 520, "Ensamblador de píxel (cabecera 0xAA)")
s.wire([srx["q"], (1110, ys)], "b", width=8, label="rx_data[7:0]", ldx=36, ldy=-12)
s.dot(1110, ys)
cAA = s.op(1165, 190, "=", r=16)
s.const(cAA["b"][0] + 22, 228, "0xAA")
s.wire([(1110, ys), (1110, 190), cAA["l"]], "b")
s.flag_from(cAA["r"], "hdr", "right", gap=14)
rreg = s.reg(1250, 278, 100, 60, "R_REG", "8 b", en=True)
greg = s.reg(1250, 375, 100, 60, "G_REG", "8 b", en=True)
s.dot(1200, ys)
s.wire([(1200, ys), (1200, 308), rreg["d"]], "b", arrow=True)
s.dot(1200, 308)
s.wire([(1200, 308), (1200, 405), greg["d"]], "b", arrow=True)
s.flag_to(rreg["en"], "en_R", "top", gap=10)
s.flag_to(greg["en"], "en_G", "top", gap=10)
cat = s.op(1475, 350, "{R,G,B}", r=30, size=11)
s.wire([(1110, ys), (1475, ys), cat["t"]], "b", arrow=True)
s.text(1440, ys - 8, "B = rx_data", 10.5, "end", "#555", mono=True)
s.wire([rreg["q"], (1415, 308), (1415, 338), (1446, 338)], "b", arrow=True)
s.wire([greg["q"], (1415, 405), (1415, 362), (1446, 362)], "b", arrow=True)
byc = s.reg(1095, 478, 110, 62, "BYTE_CNT", "2 b mód 3", fill=CNTF, en=True, clr=True)
s.block(1235, 472, 95, 74, ["DEC", "2 → 3"], size=12)
s.wire([byc["q"], (1235, 509)], "b", arrow=True, width=2)
s.text(1283, 562, "→ en_R, en_G, pix_valid", 10.5, "middle", CTRL, mono=True)
s.flag_to(byc["en"], "rx_valid", "top", gap=10)
wrc = s.reg(1365, 478, 112, 62, "WR_CNT", "14 b", fill=CNTF, en=True, clr=True)
s.flag_to(wrc["en"], "pix_valid", "top", gap=10)
s.dot(1500, 509)
c16k = s.op(1500, 585, "=", r=15)
s.wire([wrc["q"], (1500, 509), (1500, 570)], "b")
s.const(c16k["l"][0] - 4, 585, "16383")
s.flag_from(c16k["b"], "last_px", "bottom", gap=10)
toc = s.reg(1095, 572, 110, 56, "TOUT_CNT", "24 b", fill=CNTF)
s.text(1150, 566, "clr: rx_valid", 10, "middle", CTRL, mono=True)
cto = s.op(1270, 600, "=", r=15)
s.const(cto["r"][0] + 50, 600, "10⁷")
s.wire([(cto["r"][0] + 10, 600), cto["r"]], "b")
s.wire([toc["q"], cto["l"]], "b", width=24)
s.flag_from(cto["b"], "tout", "bottom", gap=4)

# =====================================================================================
# 3. GENERADOR DE RUIDO
# =====================================================================================
s.group(1570, 118, 485, 520, "Ruido sal y pimienta (LFSR)")
lfsr = s.reg(1595, 172, 130, 66, "LFSR", "16 b · XOR", en=True)
s.flag_to(lfsr["en"], "pix_valid", "left", gap=8) if False else None
s.text(1628, 166, "en: pix_valid", 10, "start", CTRL, mono=True)
m2 = s.mux("M2", 1660, 300, 4, 210, labels=["0", "1", "2", "3"], sel="bottom", desc="umbral")
for i, v in enumerate(["0", "8", "16", "32"]):
    s.const(m2["ins"][i][0] - 16, m2["ins"][i][1], v)
    s.wire([(m2["ins"][i][0] - 16, m2["ins"][i][1]), m2["ins"][i]], "b")
s.flag_to(m2["sel"], "sw_s[4:3]", "bottom", gap=14)
clt = s.op(1815, 262, "<", r=17, size=17)
lq = lfsr["q"]
s.dot(1750, lq[1])
s.wire([lq, (1750, lq[1]), (1750, 252), (1798, 252)], "b", arrow=True, width=8, wpos=1)
s.text(1744, 240, "r[7:0]", 10.5, "end", "#555", mono=True)
s.wire([m2["out"], (1775, m2["out"][1]), (1775, 272), (1798, 272)], "b", arrow=True, width=8, wpos=0)
s.text(1780, m2["out"][1] + 18, "thr", 10.5, "start", "#555", mono=True)
m3 = s.mux("M3", 1835, 430, 2, 120, labels=["0", "1"], sel="bottom", desc="sal / pimienta")
s.const(m3["ins"][0][0] - 14, m3["ins"][0][1], "0")
s.const(m3["ins"][1][0] - 14, m3["ins"][1][1], "255")
s.wire([(m3["ins"][0][0] - 14, m3["ins"][0][1]), m3["ins"][0]], "b")
s.wire([(m3["ins"][1][0] - 14, m3["ins"][1][1]), m3["ins"][1]], "b")
s.wire([(1750, lq[1]), (1738, lq[1]), (1738, 612), (m3["sel"][0], 612), m3["sel"]], "w", arrow=True)
s.text(1790, 606, "r[8]", 10.5, "middle", "#555", mono=True)
rep = s.op(1950, 490, "{n,n,n}", r=28, size=10.5)
s.wire([m3["out"], rep["l"]], "b", arrow=True, width=8)
m4 = s.mux("M4", 1985, 268, 2, 130, labels=["0", "1"], sel="top", desc="¿ruido?")
s.wire([clt["r"], (m4["sel"][0], 262), m4["sel"]], "c", arrow=True, label="hit", ldx=10, ldy=-6)
s.wire([rep["t"], (1950, m4["ins"][1][1]), m4["ins"][1]], "b", arrow=True, width=24, wpos=1)
s.wire([cat["r"], (1530, 350), (1530, 100), (1965, 100), (1965, m4["ins"][0][1]), m4["ins"][0]], "b", arrow=True, width=24, wpos=2,
       label="pix_rx[23:0]", lpos=2, ldx=-140, ldy=-6)

# =====================================================================================
# 4. MEMORIAS
# =====================================================================================
bin_ = s.bram(2150, 150, 240, 310, "BRAM_IN", "16 384 × 24 b")
btmp = s.bram(2150, 770, 240, 310, "BRAM_TMP", "16 384 × 24 b")
bout = s.bram(4160, 770, 240, 310, "BRAM_OUT", "16 384 × 24 b")
s.wire([m4["out"], (2080, m4["out"][1]), (2080, bin_["wd"][1]), bin_["wd"]], "b", arrow=True, width=24, wpos=1)
s.text(2088, 300, "pix_in", 10.5, "start", "#555", mono=True)
s.flag_to(bin_["we"], "we_in", "top", gap=18)
s.flag_to(btmp["we"], "we_tmp", "top", gap=18)
s.flag_to(bout["we"], "we_out", "top", gap=18)
s.wire([(1500, 509), (1520, 509), (1520, 655), (2118, 655), (2118, bin_["wa"][1]), bin_["wa"]], "b", arrow=True,
       width=14, wpos=2, label="wr_addr[13:0]", lpos=2, ldx=190, ldy=-6)

# =====================================================================================
# 5. GENERADOR DE DIRECCIONES
# =====================================================================================
s.group(30, 690, 1000, 920, "Generador de direcciones · recorrido + vecinos (borde replicado)")
YC, YR = 790, 990
colc = s.reg(60, YC - 33, 120, 66, "COL_CNT", "7 b", fill=CNTF, en=True, clr=True)
rowc = s.reg(60, YR - 33, 120, 66, "ROW_CNT", "7 b", fill=CNTF, en=True, clr=True)
tapc = s.reg(60, 1232, 120, 66, "TAP_CNT", "4 b", fill=CNTF, en=True, clr=True)
s.flag_to(colc["en"], "px_next", "top", gap=10)
s.flag_to(rowc["en"], "row_next", "top", gap=10)
s.flag_to(tapc["en"], "seq_en", "top", gap=10)
s.flag_to(tapc["clr"], "px_next", "top", gap=10)
s.block(250, 1210, 140, 110, ["ROM_OFF", "tap → dr, dc", "{−1, 0, +1}"], fill="#eeeeee", size=11.5)
s.dot(205, 1265)
s.wire([tapc["q"], (205, 1265), (250, 1265)], "b", arrow=True, width=4, wpos=0)
addc = s.op(520, YC, "+", r=17, size=18)
addr_ = s.op(470, YR, "+", r=17, size=18)
s.dot(215, YC)
s.wire([colc["q"], (215, YC), addc["l"]], "b", arrow=True, width=7, wpos=1)
s.dot(235, YR)
s.wire([rowc["q"], (235, YR), addr_["l"]], "b", arrow=True, width=7, wpos=1)
s.wire([(390, 1240), (470, 1240), addr_["b"]], "b", arrow=True, width=2, wpos=0, label="dr", lpos=0, ldx=4, ldy=-6)
s.wire([(390, 1292), (520, 1292), addc["b"]], "b", arrow=True, width=2, wpos=0, label="dc", lpos=0, ldx=4, ldy=-6)


def clamp(y, adder, n1, n2, lab):
    s.wire([adder["r"], (560, y)], "b", width=9)
    s.text(548, y - 32, "v = " + lab, 10, "middle", "#555", mono=True)
    ma = s.mux(n1, 640, y - 40, 2, 120, labels=["0", "1"], sel="bottom")
    s.wire([(560, y), ma["ins"][0]], "b", arrow=True)
    s.const(ma["ins"][1][0] - 14, ma["ins"][1][1], "0")
    s.wire([(ma["ins"][1][0] - 14, ma["ins"][1][1]), ma["ins"][1]], "b")
    s.dot(612, y)
    s.wire([(612, y), (612, y + 82), (ma["sel"][0], y + 82), ma["sel"]], "w", arrow=True)
    s.text(670, y + 80, "v[8] (v < 0)", 10, "start", "#555", mono=True)
    s.dot(590, y)
    cmp_ = s.op(735, y + 108, ">", r=16, size=17)
    s.wire([(590, y), (590, y + 108), cmp_["l"]], "b", arrow=True)
    s.const(cmp_["r"][0] + 42, y + 108, "127")
    s.wire([(cmp_["r"][0] + 4, y + 108), cmp_["r"]], "b")
    mb = s.mux(n2, 790, y - 20, 2, 120, labels=["0", "1"], sel="bottom")
    s.wire([ma["out"], mb["ins"][0]], "b", arrow=True)
    s.const(mb["ins"][1][0] - 14, mb["ins"][1][1], "127")
    s.wire([(mb["ins"][1][0] - 14, mb["ins"][1][1]), mb["ins"][1]], "b")
    s.wire([cmp_["b"], (735, y + 138), (mb["sel"][0], y + 138), mb["sel"]], "w", arrow=True)
    s.text(845, y + 134, "v > 127", 10, "start", "#555", mono=True)
    return mb["out"]


nc_o = clamp(YC, addc, "M5", "M6", "col + dc")
nr_o = clamp(YR, addr_, "M7", "M8", "row + dr")
cn = s.op(905, 905, "{ }", r=17, size=12)
s.wire([nc_o, (870, nc_o[1]), (870, 893), (888, 893)], "b", arrow=True, width=7, wpos=0)
s.wire([nr_o, (870, nr_o[1]), (870, 917), (888, 917)], "b", arrow=True, width=7, wpos=0)
s.text(880, nc_o[1] - 10, "nc", 10.5, "middle", "#555", mono=True)
s.text(880, nr_o[1] + 20, "nr", 10.5, "middle", "#555", mono=True)
cp = s.op(905, 1170, "{ }", r=17, size=12)
s.wire([(215, YC), (215, 1158), (888, 1158)], "b", arrow=True)
s.wire([(235, YR), (235, 1182), (888, 1182)], "b", arrow=True)
s.text(330, 1152, "col", 10.5, "middle", "#555", mono=True)
s.text(330, 1176, "row", 10.5, "middle", "#555", mono=True)
m9 = s.mux("M9", 955, 860, 2, 150, labels=["0", "1"], sel="bottom", desc="dir. de lectura")
s.wire([cn["r"], m9["ins"][0]], "b", arrow=True, width=14)
s.dot(935, 1170)
s.wire([cp["r"], (935, 1170), (935, m9["ins"][1][1]), m9["ins"][1]], "b", arrow=True, width=14, wpos=0)
s.text(905, 1205, "pix_addr", 10.5, "middle", "#555", mono=True)
s.text(905, 878, "naddr", 10.5, "middle", "#555", mono=True)
s.flag_to(m9["sel"], "pt_op", "bottom", gap=14)
tapd = s.reg(250, 1350, 120, 62, "TAP_D", "4 b (retardo)")
s.wire([(205, 1265), (205, 1381), tapd["d"]], "b", arrow=True)
s.dot(205, 1381)
s.flag_from(tapd["q"], "tap_d[3:0]", "right", gap=14, kind="b")
c10 = s.op(310, 1470, "=", r=16)
s.wire([(205, 1381), (205, 1470), c10["l"]], "b", arrow=True)
s.const(c10["r"][0] + 130, 1470, "pt_op ? 1 : 10")
s.wire([(c10["r"][0] + 10, 1470), c10["r"]], "b")
s.flag_from(c10["b"], "wr_px", "bottom", gap=10)
c0 = s.op(640, 1470, "=", r=16)
s.wire([(560, 1470), c0["l"]], "b", arrow=True)
s.flag(470, 1470, "tap_d", "right", color=INK)
s.const(c0["r"][0] + 40, 1470, "0")
s.wire([(c0["r"][0] + 10, 1470), c0["r"]], "b")
s.flag_from(c0["b"], "first", "bottom", gap=10)
s.text(50, 1550, "Por píxel (convolución): ciclos 0–8 piden los 9 vecinos, 1–9 acumulan, 10 escribe → 11 ciclos/píxel (≈1,8 ms por pasada).",
       11.5, "start", "#444")
s.text(50, 1570, "Operación puntual (Unsharp, bypass): 0 pide, 1 escribe → 2 ciclos/píxel.", 11.5, "start", "#444")
s.text(50, 1590, "acc_en = seq_en · (1 ≤ tap ≤ 9)   ·   px_next = wr_px   ·   row_next = wr_px · (col = 127)", 11.5, "start", "#444", mono=True)

m9o = m9["out"]
s.wire([m9o, (1012, m9o[1]), (1012, 1630), (2060, 1630), (2060, bin_["ra"][1]), bin_["ra"]], "b", arrow=True,
       width=14, wpos=2, label="raddr[13:0]", lpos=2, ldx=300, ldy=-6)
s.dot(2060, btmp["ra"][1])
s.wire([(2060, btmp["ra"][1]), btmp["ra"]], "b", arrow=True)
s.wire([(935, 1170), (935, 1665), (4128, 1665), (4128, bout["wa"][1]), bout["wa"]], "b", arrow=True, width=14, wpos=2,
       label="pix_addr[13:0] (dirección de escritura de TMP y OUT)", lpos=2, ldx=420, ldy=-6)
s.dot(2100, 1665)
s.wire([(2100, 1665), (2100, btmp["wa"][1]), btmp["wa"]], "b", arrow=True)

# =====================================================================================
# 6. PROCESAMIENTO
# =====================================================================================
inq = bin_["rd"]
s.wire([inq, (2440, inq[1])], "b", width=24)
s.text(2400, inq[1] + 18, "in_q", 10.5, "start", "#555", mono=True)
s.dot(2440, inq[1])
tq = btmp["rd"]
s.wire([tq, (2465, tq[1])], "b", width=24)
s.text(2400, tq[1] + 18, "tmp_q", 10.5, "start", "#555", mono=True)
s.dot(2465, tq[1])
m10 = s.mux("M10", 2495, 830, 2, 130, labels=["0 IN", "1 TMP"], sel="bottom", desc="fuente")
s.wire([(2440, inq[1]), (2440, m10["ins"][0][1]), m10["ins"][0]], "b", arrow=True)
s.wire([(2465, tq[1]), (2465, m10["ins"][1][1]), m10["ins"][1]], "b", arrow=True)
s.flag_to(m10["sel"], "src_sel", "bottom", gap=14)
s.dot(2440, 620)

LX, LY, LW, LH = 2590, 770, 1360, 470
s.lane_stack(LX, LY, LW, LH, "Motor de convolución 3×3 · un carril por canal (×3: R = [23:16], G = [15:8], B = [7:0])")
py = 905
s.wire([m10["out"], (2560, m10["out"][1]), (2560, py), (2640, py)], "b", width=24, wpos=0)
s.e.append(f'<line x1="2560" y1="{py - 24}" x2="2560" y2="{py + 24}" stroke="{INK}" stroke-width="5"/>')
s.text(2572, py + 40, "24 → 3×8", 10.5, "start", "#555", mono=True)
s.text(2600, py - 8, "p", 11, "start", "#555", mono=True)
m11 = s.mux("M11", 2800, py - 113, 4, 255, labels=["0", "1", "2", "3"], sel="top", desc="peso: 0, ×1, ×2, ×4")
s.const(m11["ins"][0][0] - 14, m11["ins"][0][1], "0")
s.wire([(m11["ins"][0][0] - 14, m11["ins"][0][1]), m11["ins"][0]], "b")
s.dot(2640, py)
s.wire([(2640, py), (2640, m11["ins"][1][1]), m11["ins"][1]], "b", arrow=True, width=8, wpos=1)
s.text(2700, m11["ins"][1][1] - 8, "×1", 11, "middle", "#555")
sh1 = s.op(2700, m11["ins"][2][1], "<<1", r=18, size=11.5)
sh2 = s.op(2700, m11["ins"][3][1], "<<2", r=18, size=11.5)
s.wire([(2640, m11["ins"][1][1]), (2640, m11["ins"][3][1]), sh2["l"]], "b", arrow=True)
s.dot(2640, m11["ins"][2][1])
s.dot(2640, m11["ins"][1][1])
s.wire([(2640, m11["ins"][2][1]), sh1["l"]], "b", arrow=True)
s.wire([sh1["r"], m11["ins"][2]], "b", arrow=True, width=9)
s.wire([sh2["r"], m11["ins"][3]], "b", arrow=True, width=10)
s.block(2700, 660, 300, 72, ["ROM_W · 32 × 3 b", "dir = {kernel_sel, tap_d}"], fill="#eeeeee", size=11.5)
s.flag_to((2700, 684), "kernel_sel", "left", gap=12)
s.flag_to((2700, 710), "tap_d[3:0]", "left", gap=12, kind="b")
s.wire([(m11["sel"][0], 732), m11["sel"]], "c", arrow=True)
s.text(m11["sel"][0] + 8, 760, "w_code[1:0]", 10.5, "start", CTRL, mono=True)
y12 = m11["out"][1]
m12 = s.mux("M12", 2990, y12 - 130 / 3, 2, 130, labels=["0", "1"], sel="top", desc="signo")
s.dot(2885, y12)
s.wire([m11["out"], (2885, y12), m12["ins"][0]], "b", arrow=True, width=10, wpos=0)
neg = s.op(2935, m12["ins"][1][1], "−x", r=17, size=13)
s.wire([(2885, y12), (2885, m12["ins"][1][1]), neg["l"]], "b", arrow=True)
s.wire([neg["r"], m12["ins"][1]], "b", arrow=True)
s.wire([(2980, 732), (m12["sel"][0], 732), m12["sel"]], "c", arrow=True)
s.text(m12["sel"][0] + 8, 760, "neg", 10.5, "start", CTRL, mono=True)
ty = m12["out"][1]
add = s.op(3120, ty, "+", r=18, size=19)
s.dot(3075, ty)
s.wire([m12["out"], add["l"]], "b", arrow=True, width=11, wpos=0)
s.text(3090, ty - 26, "ext. signo", 10, "middle", "#555")
m13 = s.mux("M13", 3195, ty - 130 / 3, 2, 130, labels=["0", "1"], sel="top", desc="acumula / carga")
s.wire([add["r"], m13["ins"][0]], "b", arrow=True, width=13)
s.wire([(3075, ty), (3075, 1135), (3168, 1135), (3168, m13["ins"][1][1]), m13["ins"][1]], "b", arrow=True)
s.text(3122, 1128, "término (tap 0)", 10, "middle", "#555")
s.flag_to(m13["sel"], "first", "top", gap=40)
acc = s.reg(3290, m13["out"][1] - 35, 120, 70, "ACC", "13 b con signo", en=True)
s.wire([m13["out"], acc["d"]], "b", arrow=True, width=13)
s.flag_to(acc["en"], "acc_en", "top", gap=16)
ay = acc["q"][1]
s.dot(3440, ay)
s.wire([acc["q"], (3440, ay), (3440, 1180), (3120, 1180), add["b"]], "b", arrow=True)
s.text(3280, 1173, "realimentación del acumulador", 10, "middle", "#555")
shr = s.op(3500, 840, ">>4", r=19, size=11.5)
s.wire([(3440, ay), (3440, 840), shr["l"]], "b", arrow=True)
s.text(3447, 824, "acc[11:4]", 10, "start", "#555", mono=True)
s.dot(3470, ay)
m14 = s.mux("M14", 3575, ay - 130 / 3, 2, 130, labels=["0", "1"], sel="bottom", desc="|acc|")
s.wire([(3440, ay), m14["ins"][0]], "b", arrow=True)
neg2 = s.op(3515, m14["ins"][1][1] + 22, "−x", r=16, size=12)
s.wire([(3470, ay), (3470, m14["ins"][1][1] + 22), neg2["l"]], "b", arrow=True)
s.wire([neg2["r"], (3553, m14["ins"][1][1] + 22), (3553, m14["ins"][1][1]), m14["ins"][1]], "b", arrow=True)
s.dot(3440, 1100)
s.wire([(3440, 1100), (m14["sel"][0], 1100), m14["sel"]], "w", arrow=True)
s.text(3500, 1094, "acc[12] (signo)", 10, "middle", "#555", mono=True)
my = m14["out"][1]
s.dot(3650, my)
s.wire([m14["out"], (3650, my)], "b", width=12)
m15 = s.mux("M15", 3740, my - 130 / 3, 2, 130, labels=["0", "1"], sel="bottom", desc="satura")
s.wire([(3650, my), m15["ins"][0]], "b", arrow=True)
s.const(m15["ins"][1][0] - 14, m15["ins"][1][1], "255")
s.wire([(m15["ins"][1][0] - 14, m15["ins"][1][1]), m15["ins"][1]], "b")
cg = s.op(3700, 1140, ">", r=16, size=17)
s.wire([(3650, my), (3650, 1140), cg["l"]], "b", arrow=True)
s.const(cg["b"][0] + 20, 1182, "255")
s.wire([(3700, 1171), cg["b"]], "b")
s.wire([cg["r"], (m15["sel"][0], 1140), m15["sel"]], "w", arrow=True)
m16 = s.mux("M16", 3845, 800, 2, 140, labels=["0 G", "1 L"], sel="top", desc="G / L")
s.wire([shr["r"], (3820, 840), (3820, m16["ins"][0][1]), m16["ins"][0]], "b", arrow=True, width=8, wpos=0)
s.wire([m15["out"], (3815, m15["out"][1]), (3815, m16["ins"][1][1]), m16["ins"][1]], "b", arrow=True, width=8, wpos=0)
s.flag_to(m16["sel"], "kernel_sel", "top", gap=36)
s.wire([m16["out"], (3950, m16["out"][1])], "b", width=8)
mg = s.op(3985, m16["out"][1], "×3", r=17, size=12)
s.wire([(3950, m16["out"][1]), mg["l"]], "b", arrow=True)
cvy = (4012, m16["out"][1])
s.wire([mg["r"], cvy], "b")
s.dot(*cvy)

UX, UY, UW, UH = 2590, 1300, 860, 290
s.lane_stack(UX, UY, UW, UH, "Unsharp · Y = 2·I − G saturado a 0…255 (×3 canales)")
iy, gy = 1385, 1485
s.dot(2440, m10["ins"][0][1])
s.wire([(2440, m10["ins"][0][1]), (2440, iy), (2620, iy)], "b", arrow=True)
s.dot(2465, m10["ins"][1][1])
s.wire([(2465, m10["ins"][1][1]), (2465, gy), (2620, gy)], "b", arrow=True)
s.text(2628, iy - 10, "I = in_q", 10.5, "start", "#555", mono=True)
s.text(2628, gy - 10, "G = tmp_q", 10.5, "start", "#555", mono=True)
u1 = s.op(2740, iy, "<<1", r=18, size=11.5)
s.wire([(2620, iy), u1["l"]], "b", arrow=True)
s.buswidth(2700, iy, 8)
sub = s.op(2860, 1435, "−", r=19, size=22)
s.wire([u1["r"], (2860, iy), sub["t"]], "b", arrow=True, width=9, wpos=0)
s.wire([(2620, gy), (2860, gy), sub["b"]], "b", arrow=True, width=8, wpos=0)
s.dot(2920, 1435)
s.wire([sub["r"], (2920, 1435)], "b", width=10)
s.text(2925, 1428, "d (10 b, con signo)", 10, "start", "#555")
cl = s.op(3010, 1352, "<", r=16, size=17)
s.const(cl["t"][0] + 13, 1322, "0")
s.wire([(cl["t"][0], 1333), cl["t"]], "b")
s.wire([(2920, 1435), (2920, 1352), cl["l"]], "b", arrow=True)
cu = s.op(3010, 1530, ">", r=16, size=17)
s.const(cu["b"][0] + 22, 1562, "255")
s.wire([(cu["b"][0], 1551), cu["b"]], "b")
s.wire([(2920, 1435), (2920, 1530), cu["l"]], "b", arrow=True)
m17 = s.mux("M17", 3100, 1435 - 130 / 3, 2, 130, labels=["0", "1"], sel="top", desc="< 0 → 0")
s.wire([(2920, 1435), m17["ins"][0]], "b", arrow=True)
s.const(m17["ins"][1][0] - 14, m17["ins"][1][1], "0")
s.wire([(m17["ins"][1][0] - 14, m17["ins"][1][1]), m17["ins"][1]], "b")
s.wire([cl["r"], (m17["sel"][0], 1352), m17["sel"]], "w", arrow=True)
m18 = s.mux("M18", 3225, 1435 + 65 - 260 / 3, 2, 130, labels=["0", "1"], sel="bottom", desc="> 255 → 255")
s.wire([m17["out"], m18["ins"][0]], "b", arrow=True, width=8)
s.const(m18["ins"][1][0] - 14, m18["ins"][1][1], "255")
s.wire([(m18["ins"][1][0] - 14, m18["ins"][1][1]), m18["ins"][1]], "b")
s.wire([cu["r"], (m18["sel"][0], 1530), m18["sel"]], "w", arrow=True)
s.wire([m18["out"], (3450, m18["out"][1])], "b", width=8)
mgu = s.op(3485, m18["out"][1], "×3", r=17, size=12)
s.wire([(3450, m18["out"][1]), mgu["l"]], "b", arrow=True)

m19 = s.mux("M19", 4060, 810, 4, 300, labels=["0 conv", "1 US", "2 IN", "3"], sel="bottom", w=50, desc="dato a OUT")
s.wire([cvy, (4040, cvy[1]), (4040, m19["ins"][0][1]), m19["ins"][0]], "b", arrow=True)
s.text(3990, cvy[1] + 34, "conv_y", 10.5, "middle", "#555", mono=True)
s.buswidth(4026, cvy[1], 24)
s.wire([mgu["r"], (4025, mgu["r"][1]), (4025, m19["ins"][1][1]), m19["ins"][1]], "b", arrow=True, width=24, wpos=0)
s.text(3520, mgu["r"][1] + 22, "us_y", 10.5, "start", "#555", mono=True)
s.wire([(2440, 620), (4048, 620), (4048, m19["ins"][2][1]), m19["ins"][2]], "b", arrow=True, width=24, wpos=0,
       label="in_q (bypass)", lpos=0, ldx=420, ldy=-6)
s.const(m19["ins"][3][0] - 14, m19["ins"][3][1], "0")
s.wire([(m19["ins"][3][0] - 14, m19["ins"][3][1]), m19["ins"][3]], "b")
s.flag_to(m19["sel"], "out_sel[1:0]", "bottom", gap=14)
s.wire([m19["out"], (4138, m19["out"][1]), (4138, bout["wd"][1]), bout["wd"]], "b", arrow=True, width=24, wpos=0)
s.wire([cvy, (4012, 1648), (2080, 1648), (2080, btmp["wd"][1]), btmp["wd"]], "b", arrow=True, width=24, wpos=1,
       label="conv_y → BRAM_TMP (pasada 1 de LoG y Unsharp)", lpos=1, ldx=-1450, ldy=-6)

# =====================================================================================
# 7. TRANSMISIÓN
# =====================================================================================
rd = bout["rd"]
s.wire([rd, (4440, rd[1]), (4440, 1705), (2560, 1705), (2560, 1760)], "b", width=24, wpos=2,
       label="out_q[23:0]", lpos=2, ldx=900, ldy=-6)
m20 = s.mux("M20", 2620, 1745, 3, 190, labels=["0 R", "1 G", "2 B"], sel="bottom", desc="byte a enviar")
for i, sl in enumerate(["[23:16]", "[15:8]", "[7:0]"]):
    yy = m20["ins"][i][1]
    s.wire([(2560, 1760), (2560, yy), m20["ins"][i]], "b", arrow=True)
    s.text(2566, yy - 6, sl, 10, "start", "#555", mono=True)
    s.dot(2560, yy)
s.group(2735, 1735, 980, 450, "uart_tx · transmisor 8N1")
catd = s.op(2830, 1900, "{1,d,0}", r=27, size=10)
s.wire([m20["out"], (2760, m20["out"][1]), (2760, 1900), catd["l"]], "b", arrow=True, width=8, wpos=0)
s.text(2672, m20["out"][1] - 26, "tx_data", 10.5, "start", "#555", mono=True)
cats = s.op(2830, 1810, "{1,sr}", r=26, size=10)
m21 = s.mux("M21", 2920, 1790, 2, 135, labels=["0", "1"], sel="bottom")
s.text(2943, 1960, "0 desplaza · 1 carga", 10.5, "middle", "#555")
s.wire([cats["r"], (2895, 1810), (2895, m21["ins"][0][1]), m21["ins"][0]], "b", arrow=True, width=10, wpos=0)
s.wire([catd["r"], (2895, 1900), (2895, m21["ins"][1][1]), m21["ins"][1]], "b", arrow=True, width=10, wpos=0)
s.flag_to(m21["sel"], "load", "bottom", gap=8)
srt = s.reg(3020, m21["out"][1] - 35, 120, 70, "SR_TX", "10 b")
s.text(3080, m21["out"][1] + 52, "reset = 1…1 (línea en reposo)", 10, "middle", "#555")
s.wire([m21["out"], srt["d"]], "b", arrow=True, width=10)
qy = srt["q"][1]
s.dot(3175, qy)
s.wire([srt["q"], (3175, qy), (3175, 1770), (2830, 1770), cats["t"]], "b", arrow=True)
s.text(3010, 1764, "sr[9:1]", 10.5, "middle", "#555", mono=True)
s.wire([(3175, qy), (3740, qy)], "w", label="tx = sr[0]", lpos=0, ldx=40, ldy=-8)
otip = s.pin(3740, qy, "UART_RXD_OUT", "out")
btx = s.reg(2800, 2020, 120, 64, "BAUD_TX", "10 b (+1)", fill=CNTF, clr=True)
bit_tx = s.reg(2800, 2105, 120, 64, "BIT_TX", "4 b (+1)", fill=CNTF, en=True, clr=True)
ctk = s.op(2990, 2052, "=", r=16)
s.const(ctk["t"][0] + 13, 2022, "867")
s.wire([(ctk["t"][0], 2033), ctk["t"]], "b")
s.wire([btx["q"], ctk["l"]], "b", width=10)
c9 = s.op(2990, 2137, "=", r=16)
s.const(c9["b"][0] + 13, 2167, "9")
s.wire([(c9["b"][0], 2156), c9["b"]], "b")
s.wire([bit_tx["q"], c9["l"]], "b", width=4)
s.block(3250, 2000, 200, 170, ["FSM_TX", "1 b", "IDLE · ENVIANDO", "salidas: load,", "bit_en, cnt_clr, tx_busy"],
        fill=FSMF, size=11.5)
s.wire([ctk["r"], (3250, 2052)], "c", arrow=True, label="tick_tx", ldx=6, ldy=-6)
s.wire([c9["r"], (3250, 2137)], "c", arrow=True, label="last_bit", ldx=6, ldy=-6)
s.flag_to((3250, 2018), "tx_start", "left", gap=150)
s.flag_from((3450, 2085), "tx_busy", "right", gap=14)
txa = s.reg(2290, 1800, 125, 64, "TX_ADDR", "14 b", fill=CNTF, en=True, clr=True)
txb = s.reg(2290, 1975, 125, 64, "TX_BYTE", "2 b mód 3", fill=CNTF, en=True, clr=True)
s.wire([txb["q"], (m20["sel"][0], txb["q"][1]), m20["sel"]], "b", arrow=True, width=2, wpos=0)
s.flag_to(txa["en"], "tx_next_px", "top", gap=12)
s.flag_to(txb["en"], "tx_start", "top", gap=12)
s.wire([txa["q"], (2470, txa["q"][1]), (2470, 2225), (4118, 2225), (4118, bout["ra"][1]), bout["ra"]], "b", arrow=True,
       width=14, wpos=2, label="tx_addr[13:0]", lpos=2, ldx=300, ldy=-6)

# =====================================================================================
# 8. CONTROL
# =====================================================================================
s.group(1060, 690, 980, 560, "Control · FSM principal (Moore) + registro de modo")
s.block(1085, 760, 210, 250, ["Lógica de", "estado", "siguiente"], fill="#f3e3df", size=12.5)
st = s.reg(1335, 845, 120, 80, "STATE", "3 b")
s.block(1500, 740, 230, 290, ["Lógica de salida", "(estado + modo)"], fill="#f3e3df", size=12.5)
s.wire([(1295, 885), st["d"]], "b", arrow=True, width=3)
s.wire([st["q"], (1500, 885)], "b", arrow=True, width=3)
s.dot(1475, 885)
s.wire([(1475, 885), (1475, 1040), (1070, 1040), (1070, 885), (1085, 885)], "b", arrow=True)
s.text(1080, 1066, "entradas: hdr · rx_valid · last_px · tout · frame_done · two_pass · tx_done · btn_p", 11, "start", CTRL, mono=True)
outs = ["we_in", "we_tmp", "we_out", "seq_en", "src_sel", "kernel_sel", "pt_op", "out_sel[1:0]", "mode_ld", "tx_en"]
for i, n in enumerate(outs):
    s.flag_from((1730, 758 + i * 27), n, "right", gap=14)
s.text(1395, 960, "IDLE=000 RECV=001", 10.5, "middle", "#555", mono=True)
s.text(1395, 975, "P1=010 P2=011", 10.5, "middle", "#555", mono=True)
s.text(1395, 990, "SEND=100", 10.5, "middle", "#555", mono=True)
mreg = s.reg(1160, 1110, 120, 62, "MODE", "3 b", en=True)
s.wire([(1080, 1141), mreg["d"]], "b", arrow=True, width=3)
s.text(1084, 1130, "sw_s[2:0]", 10, "start", "#555", mono=True)
s.flag_to(mreg["en"], "mode_ld", "top", gap=8)
s.block(1330, 1095, 300, 92, ["Decodificador de modo", "000 G · 001 L · 010 LoG · 011 US · 1xx bypass"], fill="#eeeeee", size=11.5)
s.wire([mreg["q"], (1330, 1141)], "b", arrow=True, width=3)
s.text(1640, 1135, "→ two_pass, is_L, is_LoG,", 10.5, "start", CTRL, mono=True)
s.text(1640, 1150, "   is_US, bypass", 10.5, "start", CTRL, mono=True)
s.text(1080, 1230, "MODE captura los switches al iniciar: moverlos durante el proceso no mezcla filtros.", 11, "start", "#444")

s.group(1060, 1275, 980, 330, "Entradas de la tarjeta · sincronización, antirrebote y flanco")
tsw = s.pin(1075, 1340, "SW[4:0]", "in")
sw1 = s.reg(1225, 1312, 70, 56, "FF×5")
sw2 = s.reg(1320, 1312, 70, 56, "FF×5")
s.wire([tsw, sw1["d"]], "b", arrow=True, width=5)
s.wire([sw1["q"], sw2["d"]], "b", arrow=True)
s.wire([sw2["q"], (1440, 1340)], "b", width=5)
s.flag(1440, 1340, "sw_s[4:0]", "right", color=INK)
tbt = s.pin(1075, 1440, "BTNC", "in")
b1 = s.reg(1225, 1412, 70, 56, "FF")
b2 = s.reg(1320, 1412, 70, 56, "FF")
s.wire([tbt, b1["d"]], "w", arrow=True)
s.wire([b1["q"], b2["d"]], "w", arrow=True)
deb = s.reg(1430, 1408, 150, 64, "DEB_CNT", "20 b (≈10 ms)", fill=CNTF)
s.wire([b2["q"], deb["d"]], "w", arrow=True)
edg = s.reg(1640, 1412, 80, 56, "FF")
s.dot(1605, 1440)
s.wire([deb["q"], edg["d"]], "w", arrow=True)
andg = s.op(1780, 1440, "&", r=17, size=15)
s.wire([edg["q"], andg["l"]], "w", arrow=True)
s.text(1745, 1430, "¬", 12, "middle")
s.wire([(1605, 1440), (1605, 1495), (1780, 1495), andg["b"]], "w", arrow=True)
s.text(1690, 1512, "estable · ¬anterior = flanco", 10, "middle", "#555")
s.flag_from(andg["r"], "btn_p", "right", gap=14)
trs = s.pin(1075, 1555, "CPU_RESETN", "in")
r1 = s.reg(1270, 1527, 70, 56, "FF")
r2 = s.reg(1365, 1527, 70, 56, "FF")
s.wire([trs, r1["d"]], "w", arrow=True)
s.wire([r1["q"], r2["d"]], "w", arrow=True)
s.flag_from(r2["q"], "rst (síncrono)", "right", gap=14)
s.text(1770, 1330, "LED[2:0] = MODE", 11, "start", "#444", mono=True)
s.text(1770, 1350, "LED[7:5] = STATE", 11, "start", "#444", mono=True)

# =====================================================================================
# 9. TABLAS, LEYENDA Y CAJETÍN
# =====================================================================================
def table(x0, y0, cols, cw, rows, rh=27, size=12, hsize=12.5):
    x = x0
    for c, w in zip(cols, cw):
        s.e.append(f'<rect x="{x}" y="{y0}" width="{w}" height="{rh}" fill="#2f4b6e" stroke="#2f4b6e"/>')
        s.text(x + w / 2, y0 + rh * 0.68, c, hsize, "middle", "white", "bold")
        x += w
    for r_i, r in enumerate(rows):
        yy2 = y0 + rh + r_i * rh
        x = x0
        for c, w in zip(r, cw):
            fill = "#f4f6fa" if r_i % 2 else "white"
            s.e.append(f'<rect x="{x}" y="{yy2}" width="{w}" height="{rh}" fill="{fill}" stroke="#b9c3d1"/>')
            s.text(x + w / 2, yy2 + rh * 0.68, c, size, "middle", INK, mono=True)
            x += w
    return y0 + rh * (len(rows) + 1)


tx0, ty0 = 30, 1745
s.text(tx0, ty0, "Salidas de control de la FSM principal (Moore: dependen de STATE y MODE)", 15, "start", INK, "bold")
yb = table(tx0, ty0 + 14,
           ["Estado", "we_in", "we_tmp", "we_out", "src_sel", "kernel_sel", "pt_op", "out_sel", "otras"],
           [130, 110, 160, 180, 100, 120, 90, 120, 330],
           [["IDLE", "0", "0", "0", "–", "–", "–", "–", "mode_ld = rx_valid·hdr | btn_p"],
            ["RECV", "pix_valid", "0", "0", "–", "–", "–", "–", "ruido activo (M4)"],
            ["P1", "0", "wr_px·two_pass", "wr_px·¬two_pass", "0 (IN)", "is_L", "bypass", "bypass?10:00", "seq_en = 1"],
            ["P2 (LoG)", "0", "0", "wr_px", "1 (TMP)", "1 (L)", "0", "00", "seq_en = 1"],
            ["P2 (US)", "0", "0", "wr_px", "–", "–", "1", "01", "seq_en = 1"],
            ["SEND", "0", "0", "0", "–", "–", "–", "–", "tx_en = 1"]])
s.text(tx0, yb + 22, "Transiciones: IDLE→RECV (rx_valid·hdr) · IDLE→P1 (btn_p) · RECV→P1 (last_px) · RECV→IDLE (tout) · "
                     "P1→P2 (frame_done·two_pass) · P1→SEND (frame_done·¬two_pass) · P2→SEND (frame_done) · SEND→IDLE (tx_done)",
       11.5, "start", "#333")
s.text(tx0, yb + 42, "frame_done = wr_px·(row=127)·(col=127)  ·  tx_start = tx_en_d·¬tx_busy (tx_en retrasado 1 ciclo por la latencia de BRAM_OUT)  ·  "
                     "tx_next_px = tx_start·(tx_byte=2)  ·  tx_done = tx_next_px·(tx_addr=16383)", 11.5, "start", "#333", mono=True)

ym = yb + 74
s.text(tx0, ym, "Inventario de multiplexores (ancho = bits por entrada; ×3 = uno por canal R, G, B)", 15, "start", INK, "bold")
mcols = ["Id", "Tipo", "Ancho", "Entradas (0, 1, 2, 3)", "Selección"]
mcw = [52, 60, 70, 520, 210]
L = [["M1", "2:1", "8", "sr (retener) · {rx_s, sr[7:1]}", "sample"],
     ["M2", "4:1", "8", "0 · 8 · 16 · 32 (umbral de ruido)", "sw_s[4:3]"],
     ["M3", "2:1", "8", "0 (pimienta) · 255 (sal)", "r[8]"],
     ["M4", "2:1", "24", "pix_rx · {n, n, n}", "hit = r[7:0] < thr"],
     ["M5,M7", "2:1", "7", "v[6:0] · 0", "v[8] (v < 0)"],
     ["M6,M8", "2:1", "7", "salida M5/M7 · 127", "v > 127"],
     ["M9", "2:1", "14", "naddr (vecino) · pix_addr (puntual)", "pt_op"],
     ["M10", "2:1", "24", "in_q · tmp_q", "src_sel"],
     ["M11 ×3", "4:1", "10", "0 · p · p<<1 · p<<2", "w_code[1:0]"]]
R = [["M12 ×3", "2:1", "11", "+peso · −peso", "neg"],
     ["M13 ×3", "2:1", "13", "acc + término · término", "first"],
     ["M14 ×3", "2:1", "12", "acc · −acc (valor absoluto)", "acc[12]"],
     ["M15 ×3", "2:1", "8", "|acc| · 255 (saturación)", "|acc| > 255"],
     ["M16 ×3", "2:1", "8", "acc[11:4] (G) · L saturado", "kernel_sel"],
     ["M17 ×3", "2:1", "8", "d[7:0] · 0", "d < 0"],
     ["M18 ×3", "2:1", "8", "salida M17 · 255", "d > 255"],
     ["M19", "4:1", "24", "conv_y · us_y · in_q · 0", "out_sel[1:0]"],
     ["M20 / M21", "3:1 / 2:1", "8 / 10", "R·G·B de out_q  /  {1,sr[9:1]} · {1,d,0}", "tx_byte / load"]]
table(tx0, ym + 14, mcols, mcw, L, rh=25, size=11.5, hsize=12)
table(tx0 + sum(mcw) + 30, ym + 14, mcols, [80, 80, 70, 470, 180], R, rh=25, size=11.5, hsize=12)

lx, ly = 1890, 2050
s.text(lx, ly - 10, "Notación", 15, "start", INK, "bold")
s.wire([(lx, ly + 20), (lx + 60, ly + 20)], "b", arrow=True, width=8, wpos=0)
s.text(lx + 75, ly + 25, "bus de 8 bits", 12, "start")
s.wire([(lx, ly + 50), (lx + 60, ly + 50)], "c", arrow=True)
s.text(lx + 75, ly + 55, "señal de control", 12, "start")
s.flag(lx, ly + 82, "señal", "right")
s.text(lx + 75, ly + 87, "conexión por nombre de red", 12, "start")
s.mux("", lx + 14, ly + 100, 2, 56, w=28, labels=["0", "1"], sel="bottom")
s.text(lx + 75, ly + 132, "multiplexor (ver inventario)", 12, "start")
s.reg(lx + 4, ly + 170, 52, 40, "R")
s.text(lx + 75, ly + 195, "registro / contador (CLK)", 12, "start")
s.op(lx + 30, ly + 245, "+", r=15, size=16)
s.text(lx + 75, ly + 250, "operación combinacional", 12, "start")
s.const(lx + 56, ly + 285, "255")
s.text(lx + 75, ly + 290, "constante", 12, "start")
s.dot(lx + 30, ly + 318)
s.text(lx + 75, ly + 323, "unión (sin punto = cruce)", 12, "start")
s.text(lx + 220, ly + 25, "×3", 13, "start", "#3d5a80", "bold")
s.text(lx + 250, ly + 25, "carril replicado por canal", 12, "start")


# temporización del secuenciador por píxel
tx1, ty1 = 2300, 2280
s.text(tx1, ty1, "Secuencia por píxel en la convolución (BRAM con 1 ciclo de latencia)", 15, "start", INK, "bold")
cyc = [str(i) for i in range(11)]
rows_t = [["tap"] + cyc,
          ["RA (vecino)"] + [f"v{i}" for i in range(9)] + ["–", "–"],
          ["RD / tap_d"] + ["–"] + [f"v{i}" for i in range(9)] + ["–"],
          ["ACC"] + ["–", "carga"] + ["+="] * 8 + ["listo"],
          ["escritura"] + ["–"] * 10 + ["WE"]]
table(tx1, ty1 + 14, ["Ciclo"] + cyc, [130] + [112] * 11, rows_t[1:], rh=26, size=11.5, hsize=12)
s.text(tx1, ty1 + 14 + 26 * 5 + 22, "first = (tap_d = 0) carga el primer término · acc_en activo en los ciclos 1–9 · "
                                      "wr_px en el ciclo 10 escribe y avanza al siguiente píxel.", 11.5, "start", "#333")

cx0, cy0 = 3760, 2275
s.e.append(f'<rect x="{cx0}" y="{cy0}" width="690" height="300" fill="white" stroke="{INK}" stroke-width="2"/>')
rowsc = [("Proyecto", "Procesador de imágenes con filtros 2D (#8) · ELDI 2026"),
         ("Hoja", "Esquemático RTL completo · 1 de 1"),
         ("Autores", "Edison Torres · Juan Guaman"),
         ("Tarjeta", "Nexys 4 DDR · Artix-7 XC7A100T · CLK 100 MHz"),
         ("Revisión", "v2 · 28 oct 2026"),
         ("Contenido", "21 multiplexores (M1–M21) · 3 BRAM · FSM Moore")]
for i, (k, v) in enumerate(rowsc):
    y = cy0 + i * 50
    if i:
        s.e.append(f'<line x1="{cx0}" y1="{y}" x2="{cx0 + 690}" y2="{y}" stroke="{INK}"/>')
    s.text(cx0 + 12, y + 31, k, 13, "start", "#555", "bold")
    s.text(cx0 + 132, y + 31, v, 13.5, "start", INK)
s.e.append(f'<line x1="{cx0 + 120}" y1="{cy0}" x2="{cx0 + 120}" y2="{cy0 + 300}" stroke="{INK}"/>')

s.save(os.path.join(OUT, "esquematico_completo.svg"))
print("ok")
