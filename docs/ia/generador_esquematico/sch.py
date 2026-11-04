"""Primitivas SVG para un esquemático RTL en la notación de la guía del profesor:
mux trapezoidal con entradas numeradas, registros con triángulo de reloj, círculos de
operación, cajas de constantes, ancho de bus con raya inclinada y señales de control
en rojo punteado con etiqueta de red."""

FONT = "DejaVu Sans, Arial, sans-serif"
MONO = "DejaVu Sans Mono, monospace"
INK = "#1b1b1b"
CTRL = "#b3261e"
GRAY = "#dcdcdc"
REGF = "#cfe0f3"
MEMF = "#d8ecd2"
FSMF = "#f6d9d2"
CNTF = "#e6dcf2"
CONSTF = "#f3f3f3"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Sheet:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.back = []   # fondos (grupos, sombras)
        self.e = []      # cables y símbolos
        self.top = []    # etiquetas por encima

    # ------------------------------------------------------------ texto
    def text(self, x, y, s, size=14, anchor="middle", color=INK, weight="normal", italic=False,
             mono=False, layer=None, rotate=None):
        fam = MONO if mono else FONT
        st = ' font-style="italic"' if italic else ""
        rot = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
        (layer if layer is not None else self.top).append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{color}"{st}{rot}>{esc(s)}</text>')

    def lines(self, cx, cy, ls, size=14, lh=None, anchor="middle", bold_first=False, color=INK, mono=False):
        lh = lh or size * 1.28
        y0 = cy - (len(ls) - 1) * lh / 2 + size * 0.35
        for i, l in enumerate(ls):
            self.text(cx, y0 + i * lh, l, size, anchor, color, "bold" if (bold_first and i == 0) else "normal", mono=mono)

    # ------------------------------------------------------------ cables
    def wire(self, pts, kind="w", arrow=False, width=None, wpos=None, label=None, lpos=None, lsize=12,
             lanchor="start", ldx=6, ldy=-6):
        """kind: w = 1 bit, b = bus, c = control. width: número de bits (dibuja la raya) en el
        segmento wpos (índice) o en el más largo."""
        sw = {"w": 1.5, "b": 2.6, "c": 1.4}[kind]
        col = CTRL if kind == "c" else INK
        dash = ' stroke-dasharray="6,4"' if kind == "c" else ""
        d = "M " + " L ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        m = ' marker-end="url(#ahc)"' if (arrow and kind == "c") else (' marker-end="url(#ah)"' if arrow else "")
        self.e.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}"{dash}{m} stroke-linejoin="round"/>')
        if width is not None:
            i = wpos if wpos is not None else max(range(len(pts) - 1),
                                                   key=lambda k: abs(pts[k + 1][0] - pts[k][0]) + abs(pts[k + 1][1] - pts[k][1]))
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            self.buswidth((x1 + x2) / 2, (y1 + y2) / 2, width, vertical=(abs(x2 - x1) < 1))
        if label:
            i = lpos if lpos is not None else 0
            (x1, y1) = pts[i]
            self.text(x1 + ldx, y1 + ldy, label, lsize, lanchor, col, mono=True)

    def buswidth(self, x, y, n, vertical=False, color=INK):
        if vertical:
            self.top.append(f'<line x1="{x - 7}" y1="{y + 5}" x2="{x + 7}" y2="{y - 5}" stroke="{color}" stroke-width="1.6"/>')
            self.text(x + 10, y + 5, str(n), 12, "start", color, "bold")
        else:
            self.top.append(f'<line x1="{x - 5}" y1="{y + 7}" x2="{x + 5}" y2="{y - 7}" stroke="{color}" stroke-width="1.6"/>')
            self.text(x, y - 10, str(n), 12, "middle", color, "bold")

    def dot(self, x, y, color=INK):
        self.top.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{color}"/>')

    # ------------------------------------------------------------ símbolos
    def mux(self, mid, x, y, n, h, w=46, labels=None, sel="bottom", sel_label=None, sel_w=None, title=None, desc=None):
        """Trapecio vertical. Devuelve dict con ins (lista), out, sel."""
        k = 0.13 * h
        p = f"{x},{y} {x + w},{y + k} {x + w},{y + h - k} {x},{y + h}"
        self.e.append(f'<polygon points="{p}" fill="{GRAY}" stroke="{INK}" stroke-width="1.6"/>')
        ins = [(x, y + h * (i + 1) / (n + 1)) for i in range(n)]
        labels = labels or [str(i) for i in range(n)]
        for (ix, iy), l in zip(ins, labels):
            self.text(ix + 6, iy + 4.5, l, 11.5, "start")
        out = (x + w, y + h / 2)
        if sel == "bottom":
            sp = (x + w / 2, y + h - k / 2)
            tp = (x + w / 2, y - 7)
        else:
            sp = (x + w / 2, y + k / 2)
            tp = (x + w / 2, y + h + 15)
        self.text(tp[0], tp[1], mid, 12.5, "middle", "#1f4e8c", "bold")
        title = title or desc
        if title:
            self.text(tp[0], tp[1] + (-15 if sel == "bottom" else 15), title, 10.5, "middle", "#555")
        return {"ins": ins, "out": out, "sel": sp}

    def reg(self, x, y, w, h, title, sub=None, fill=REGF, en=False, clr=False):
        self.e.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{fill}" stroke="{INK}" stroke-width="1.6"/>')
        # triángulo de reloj
        cx = x + w / 2
        self.e.append(f'<path d="M {cx - 8},{y + h} L {cx},{y + h - 10} L {cx + 8},{y + h}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
        ls = [title] + ([sub] if sub else [])
        self.lines(cx, y + h / 2 - 3, ls, 12.5, bold_first=True)
        r = {"d": (x, y + h / 2), "q": (x + w, y + h / 2), "clk": (cx, y + h),
             "top": (cx, y), "bot": (cx, y + h)}
        if en:
            r["en"] = (x + w * 0.25, y)
            self.text(x + w * 0.25, y + 11, "en", 9.5, "middle", CTRL)
        if clr:
            r["clr"] = (x + w * 0.75, y)
            self.text(x + w * 0.75, y + 11, "clr", 9.5, "middle", CTRL)
        return r

    def op(self, x, y, s, r=17, size=15):
        self.e.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{GRAY}" stroke="{INK}" stroke-width="1.6"/>')
        self.text(x, y + size * 0.36, s, size, "middle", INK, "bold")
        return {"l": (x - r, y), "r": (x + r, y), "t": (x, y - r), "b": (x, y + r)}

    def const(self, xr, y, s, h=22):
        w = max(26, len(str(s)) * 8 + 12)
        self.e.append(f'<rect x="{xr - w}" y="{y - h / 2}" width="{w}" height="{h}" fill="{CONSTF}" stroke="{INK}" stroke-width="1.3"/>')
        self.text(xr - w / 2, y + 4.5, s, 11.5, mono=True)
        return {"r": (xr, y), "l": (xr - w, y), "t": (xr - w / 2, y - h / 2), "b": (xr - w / 2, y + h / 2)}

    def const_c(self, cx, cy, s, h=22):
        w = max(26, len(str(s)) * 8 + 12)
        return self.const(cx + w / 2, cy, s, h)

    def block(self, x, y, w, h, ls, fill=GRAY, size=12.5, bold_first=True, rx=3):
        self.e.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{INK}" stroke-width="1.6"/>')
        if ls:
            self.lines(x + w / 2, y + h / 2, ls, size, bold_first=bold_first)

    def group(self, x, y, w, h, title, color="#6b6b6b"):
        self.back.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fbfbfb" stroke="{color}" stroke-width="1.3" stroke-dasharray="7,5"/>')
        self.text(x + 10, y + 18, title, 13, "start", color, "bold", layer=self.back)

    def lane_stack(self, x, y, w, h, title):
        for o in (24, 12):
            self.back.append(f'<rect x="{x + o}" y="{y + o}" width="{w}" height="{h}" rx="8" fill="#f2f6fb" stroke="#7a8ca5" stroke-width="1.2"/>')
        self.back.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fbfdff" stroke="#3d5a80" stroke-width="1.6"/>')
        self.text(x + 12, y + 20, title, 13, "start", "#3d5a80", "bold", layer=self.back)

    def bram(self, x, y, w, h, title, sub):
        self.e.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{MEMF}" stroke="{INK}" stroke-width="1.8"/>')
        cx = x + w / 2
        self.e.append(f'<path d="M {cx - 9},{y + h} L {cx},{y + h - 11} L {cx + 9},{y + h}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
        self.lines(cx + 10, y + h * 0.5, [title, sub, "lectura síncrona", "(1 ciclo)"], 12.5, bold_first=True)
        P = {"wd": (x, y + h * 0.2), "wa": (x, y + h * 0.4), "we": (x + w * 0.5, y), "ra": (x, y + h * 0.82),
             "rd": (x + w, y + h * 0.82)}
        for k, lab in [("wd", "WD[23:0]"), ("wa", "WA[13:0]"), ("ra", "RA[13:0]")]:
            self.text(P[k][0] + 6, P[k][1] + 4.5, lab, 11, "start", mono=True)
        self.text(x + w * 0.5, y + 16, "WE", 11, "middle", mono=True)
        self.text(P["rd"][0] - 6, P["rd"][1] + 4.5, "RD[23:0]", 11, "end", mono=True)
        return P

    def pin(self, x, y, label, d="in", h=28):
        w = len(label) * 8.6 + 26
        if d == "in":
            pts = [(x, y - h / 2), (x + w - 12, y - h / 2), (x + w, y), (x + w - 12, y + h / 2), (x, y + h / 2)]
            tip = (x + w, y)
        else:
            pts = [(x + 12, y - h / 2), (x + w, y - h / 2), (x + w, y + h / 2), (x + 12, y + h / 2), (x, y)]
            tip = (x, y)
        self.e.append('<polygon points="' + " ".join(f"{a},{b}" for a, b in pts) + f'" fill="#fff4c9" stroke="{INK}" stroke-width="1.6"/>')
        self.text(x + w / 2 + (-5 if d == "in" else 5), y + 4.5, label, 12, mono=True, weight="bold")
        return tip

    def flag(self, x, y, label, d="right", color=CTRL):
        """Etiqueta de red (conector por nombre). d = hacia dónde apunta la punta."""
        w = len(label) * 7.6 + 18
        h = 20
        if d == "right":
            pts = [(x, y - h / 2), (x + w - 8, y - h / 2), (x + w, y), (x + w - 8, y + h / 2), (x, y + h / 2)]
            cx = x + w / 2 - 3
            attach, far = (x, y), (x + w, y)
        else:
            pts = [(x, y), (x + 8, y - h / 2), (x + w, y - h / 2), (x + w, y + h / 2), (x + 8, y + h / 2)]
            cx = x + w / 2 + 3
            attach, far = (x + w, y), (x, y)
        self.top.append('<polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) +
                        f'" fill="#fff" stroke="{color}" stroke-width="1.2"/>')
        self.text(cx, y + 4, label, 11, mono=True, color=color)
        return {"attach": attach, "far": far, "w": w}

    def flag_to(self, pt, label, side="left", gap=18, kind="c"):
        """Coloca una etiqueta de red que entra a pt desde 'side' (left/top/bottom/right)."""
        x, y = pt
        L = len(label) * 7.6 + 18
        if side == "left":
            f = self.flag(x - gap - L, y, label, "right")
            self.wire([(x - gap, y), (x, y)], kind, arrow=False)
        elif side == "right":
            f = self.flag(x + gap, y, label, "left")
            self.wire([(x + gap, y), (x, y)], kind)
        elif side == "top":
            f = self.flag(x - L / 2, y - gap - 10, label, "right")
            self.wire([(x, y - gap), (x, y)], kind)
        else:
            f = self.flag(x - L / 2, y + gap + 10, label, "right")
            self.wire([(x, y + gap), (x, y)], kind)
        return f

    def flag_from(self, pt, label, side="right", gap=18, kind="c"):
        x, y = pt
        L = len(label) * 7.6 + 18
        if side == "right":
            self.wire([(x, y), (x + gap, y)], kind)
            self.flag(x + gap, y, label, "right")
        elif side == "left":
            self.wire([(x, y), (x - gap, y)], kind)
            self.flag(x - gap - L, y, label, "left")
        elif side == "top":
            self.wire([(x, y), (x, y - gap)], kind)
            self.flag(x - L / 2, y - gap - 10, label, "right")
        else:
            self.wire([(x, y), (x, y + gap)], kind)
            self.flag(x - L / 2, y + gap + 10, label, "right")

    def save(self, path, bg="white"):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">'
                '<defs>'
                f'<marker id="ah" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="9" refX="10.5" refY="4.5" orient="auto"><path d="M0,0 L11,4.5 L0,9 z" fill="{INK}"/></marker>'
                f'<marker id="ahc" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="8" refX="9.5" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="{CTRL}"/></marker>'
                '</defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="{bg}"/>')
        with open(path, "w") as f:
            f.write(head + "\n".join(self.back + self.e + self.top) + "</svg>")
