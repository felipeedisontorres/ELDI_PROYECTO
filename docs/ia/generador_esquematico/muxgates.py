"""Figura: cómo se construye un multiplexor (nivel de compuertas y árbol), para justificar M1–M21."""
import os
from sch import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
os.makedirs(OUT, exist_ok=True)
s = Sheet(1700, 760)


def AND(x, y, h=56):
    w = h * 0.9
    s.e.append(f'<path d="M {x},{y - h / 2} L {x + w * 0.5},{y - h / 2} A {h / 2},{h / 2} 0 0 1 {x + w * 0.5},{y + h / 2} '
               f'L {x},{y + h / 2} Z" fill="{GRAY}" stroke="{INK}" stroke-width="1.6"/>')
    return {"a": (x, y - h / 4), "b": (x, y + h / 4), "o": (x + w * 0.5 + h / 2, y)}


def OR(x, y, h=64):
    w = h
    s.e.append(f'<path d="M {x},{y - h / 2} Q {x + w * 0.55},{y - h / 2} {x + w},{y} Q {x + w * 0.55},{y + h / 2} {x},{y + h / 2} '
               f'Q {x + w * 0.25},{y} {x},{y - h / 2} Z" fill="{GRAY}" stroke="{INK}" stroke-width="1.6"/>')
    return {"a": (x + 8, y - h / 4), "b": (x + 8, y + h / 4), "o": (x + w, y)}


def NOT(x, y, h=30):
    s.e.append(f'<path d="M {x},{y - h / 2} L {x + h * 0.9},{y} L {x},{y + h / 2} Z" fill="{GRAY}" stroke="{INK}" stroke-width="1.6"/>')
    s.e.append(f'<circle cx="{x + h * 0.9 + 5}" cy="{y}" r="5" fill="white" stroke="{INK}" stroke-width="1.5"/>')
    return {"i": (x, y), "o": (x + h * 0.9 + 10, y)}


s.text(30, 36, "Cómo está construido cada multiplexor del diseño", 20, "start", INK, "bold")

# (a) MUX 2:1 de 1 bit
s.text(30, 80, "(a) MUX 2:1 de 1 bit con compuertas:  Y = S̄·D0 + S·D1", 15, "start", INK, "bold")
a1 = AND(260, 170)
a2 = AND(260, 290)
o = OR(380, 230)
n = NOT(140, 340)
s.wire([(60, 156), a1["a"]], "w", arrow=True)
s.text(50, 160, "D0", 14, "end", mono=True)
s.wire([(60, 304), a2["b"]], "w", arrow=True)
s.text(50, 308, "D1", 14, "end", mono=True)
s.text(50, 404, "S", 14, "end", mono=True)
s.wire([(60, 400), (110, 400), (110, 340), n["i"]], "w", arrow=True)
s.dot(110, 400)
s.wire([n["o"], (215, 340), (215, 184), a1["b"]], "w", arrow=True)
s.text(222, 330, "S̄", 13, "start", mono=True)
s.wire([(110, 400), (235, 400), (235, 276), a2["a"]], "w", arrow=True)
s.wire([a1["o"], (360, 170), (360, o["a"][1]), o["a"]], "w", arrow=True)
s.wire([a2["o"], (360, 290), (360, o["b"][1]), o["b"]], "w", arrow=True)
s.wire([o["o"], (500, 230)], "w", arrow=True)
s.text(508, 235, "Y", 14, "start", mono=True)
s.text(60, 460, "Un MUX 2:1 de N bits (por ejemplo M10, 24 bits) son N copias", 13, "start")
s.text(60, 480, "de este circuito con la misma señal S: una por bit.", 13, "start")
s.text(60, 512, "Costo: N × (2 AND + 1 OR) + 1 NOT compartido.", 13, "start", "#444")

# (b) MUX 4:1 como árbol de 2:1
s.text(600, 80, "(b) MUX 4:1 (M2, M11, M19) como árbol de MUX 2:1", 15, "start", INK, "bold")
ma = s.mux("", 720, 120, 2, 120, labels=["0", "1"], sel="bottom")
mb = s.mux("", 720, 290, 2, 120, labels=["0", "1"], sel="bottom")
mc = s.mux("", 880, 195, 2, 140, labels=["0", "1"], sel="bottom")
for (m, d0, d1) in [(ma, "D0", "D1"), (mb, "D2", "D3")]:
    s.wire([(650, m["ins"][0][1]), m["ins"][0]], "w", arrow=True)
    s.wire([(650, m["ins"][1][1]), m["ins"][1]], "w", arrow=True)
    s.text(642, m["ins"][0][1] + 5, d0, 14, "end", mono=True)
    s.text(642, m["ins"][1][1] + 5, d1, 14, "end", mono=True)
s.wire([ma["out"], (840, ma["out"][1]), (840, mc["ins"][0][1]), mc["ins"][0]], "w", arrow=True)
s.wire([mb["out"], (840, mb["out"][1]), (840, mc["ins"][1][1]), mc["ins"][1]], "w", arrow=True)
s.wire([mc["out"], (990, mc["out"][1])], "w", arrow=True)
s.text(998, mc["out"][1] + 5, "Y", 14, "start", mono=True)
s.wire([(700, 450), (ma["sel"][0], 450), (ma["sel"][0], 260), ma["sel"]], "c", arrow=True)
s.wire([(ma["sel"][0], 450), mb["sel"]], "c", arrow=True)
s.dot(ma["sel"][0], 450)
s.text(690, 455, "S0", 14, "end", CTRL, mono=True)
s.wire([(860, 470), (mc["sel"][0], 470), mc["sel"]], "c", arrow=True)
s.text(850, 475, "S1", 14, "end", CTRL, mono=True)
s.text(620, 512, "S0 (bit menos significativo) elige dentro de cada par;", 13, "start")
s.text(620, 532, "S1 elige entre el par bajo (D0, D1) y el alto (D2, D3).", 13, "start")

# (c) tabla de verdad y ecuación
x0, y0 = 1130, 100
s.text(x0, 80, "(c) Tabla de verdad del MUX 4:1", 15, "start", INK, "bold")
cols, cw = ["S1", "S0", "Y"], [80, 80, 110]
x = x0
for c, w in zip(cols, cw):
    s.e.append(f'<rect x="{x}" y="{y0}" width="{w}" height="32" fill="#2f4b6e"/>')
    s.text(x + w / 2, y0 + 22, c, 14, "middle", "white", "bold", mono=True)
    x += w
for i, (a, b, y) in enumerate([("0", "0", "D0"), ("0", "1", "D1"), ("1", "0", "D2"), ("1", "1", "D3")]):
    x = x0
    for c, w in zip((a, b, y), cw):
        s.e.append(f'<rect x="{x}" y="{y0 + 32 + i * 32}" width="{w}" height="32" fill="{"#f4f6fa" if i % 2 else "white"}" stroke="#b9c3d1"/>')
        s.text(x + w / 2, y0 + 54 + i * 32, c, 14, "middle", mono=True)
        x += w
s.text(x0, 300, "Y = S̄1·S̄0·D0 + S̄1·S0·D1 + S1·S̄0·D2 + S1·S0·D3", 14, "start", INK, mono=True)
s.text(x0, 330, "El índice de la entrada elegida es el número", 13, "start")
s.text(x0, 350, "binario {S1 S0}: 10₂ = 2 → sale D2.", 13, "start")
s.text(x0, 390, "M20 (3:1) es un 4:1 con la entrada 3 sin usar:", 13, "start")
s.text(x0, 410, "TX_BYTE cuenta 0, 1, 2 y nunca llega a 3.", 13, "start")

# (d) saturación
s.text(30, 590, "(d) Patrón de saturación usado en M5–M8, M15, M17 y M18 (igual a la guía de operaciones puntuales)", 15, "start", INK, "bold")
cl = s.op(220, 650, "<", r=16, size=17)
cu = s.op(220, 720, ">", r=16, size=17)
s.const(cl["r"][0] + 40, 650, "0")
s.wire([(cl["r"][0] + 10, 650), cl["r"]], "b")
s.const(cu["r"][0] + 50, 720, "255")
s.wire([(cu["r"][0] + 4, 720), cu["r"]], "b")
s.dot(120, 685)
s.wire([(60, 685), (120, 685), (120, 650), cl["l"]], "b", arrow=True)
s.wire([(120, 685), (120, 720), cu["l"]], "b", arrow=True)
s.text(55, 690, "x", 14, "end", mono=True)
m1 = s.mux("", 380, 625, 2, 100, labels=["0", "1"], sel="top")
m2 = s.mux("", 500, 641.7, 2, 100, labels=["0", "1"], sel="bottom")
s.wire([(120, 685), (300, 685), (300, m1["ins"][0][1]), m1["ins"][0]], "b", arrow=True)
s.const(m1["ins"][1][0] - 12, m1["ins"][1][1], "0")
s.wire([(m1["ins"][1][0] - 12, m1["ins"][1][1]), m1["ins"][1]], "b")
s.wire([(cl["t"][0], cl["t"][1]), (cl["t"][0], 612), (m1["sel"][0], 612), m1["sel"]], "w", arrow=True)
s.wire([m1["out"], m2["ins"][0]], "b", arrow=True)
s.const(m2["ins"][1][0] - 12, m2["ins"][1][1], "255")
s.wire([(m2["ins"][1][0] - 12, m2["ins"][1][1]), m2["ins"][1]], "b")
s.wire([cu["b"], (220, 748), (m2["sel"][0], 748), m2["sel"]], "w", arrow=True)
s.wire([m2["out"], (620, m2["out"][1])], "b", arrow=True, width=8)
s.text(628, m2["out"][1] + 5, "y ∈ [0, 255]", 14, "start", mono=True)
s.text(700, 660, "Dos comparadores generan las selecciones y dos MUX 2:1 eligen entre el valor y el límite.", 13, "start")
s.text(700, 682, "Las dos condiciones nunca son ciertas a la vez, así que el orden de los MUX no cambia el resultado.", 13, "start")

s.save(os.path.join(OUT, "mux_construccion.svg"))
print("ok")
