import math

C_BUS = '#000000'
C_SIG = '#1f4e9c'
C_CLK = '#8c8c8c'
C_RST = '#b07cc6'
GRAY = '#d4d4d4'
F_SEQ = '#fff2cc'
F_MEM = '#dae8fc'
F_ROM = '#e8dcf2'
FONT = 'DejaVu Sans'


def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


class Pin(tuple):
    def __new__(cls, x, y):
        return tuple.__new__(cls, (x, y))

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]


class Sheet:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.L = {k: [] for k in ('bg', 'frame', 'wire', 'elem', 'dot', 'text')}
        self.wires = []

    def add(self, layer, s):
        self.L[layer].append(s)

    def text(self, x, y, t, size=2.6, anchor='start', weight='normal', color='#000',
             italic=False, layer='text', rot=0, family=None):
        st = 'italic' if italic else 'normal'
        tr = f' transform="rotate({rot} {x:.2f} {y:.2f})"' if rot else ''
        fam = family or FONT
        self.add(layer, f'<text x="{x:.2f}" y="{y:.2f}" font-family="{fam}" font-size="{size}" '
                        f'text-anchor="{anchor}" font-weight="{weight}" font-style="{st}" '
                        f'fill="{color}"{tr}>{esc(t)}</text>')

    def rect(self, x, y, w, h, fill='none', stroke='#000', sw=0.35, rx=0, dash=None, layer='elem'):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(layer, f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" '
                        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, color='#000', sw=0.35, layer='elem', dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(layer, f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                        f'stroke="{color}" stroke-width="{sw}"{d}/>')

    def poly(self, pts, fill='none', stroke='#000', sw=0.35, layer='elem', close=True):
        p = ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts)
        tag = 'polygon' if close else 'polyline'
        self.add(layer, f'<{tag} points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
                        f'stroke-linejoin="round"/>')

    def circle(self, cx, cy, r, fill='none', stroke='#000', sw=0.35, layer='elem'):
        self.add(layer, f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" '
                        f'stroke="{stroke}" stroke-width="{sw}"/>')

    def wire(self, pts, kind='bus', width=None, wpos=0, wfrac=0.5, arrow=True, name=None,
             npos=0, nfrac=None, nside='above', ndx=0, ndy=0, nsize=2.4, dots=(), wdx=0, wdy=0,
             net=None):
        col = {'bus': C_BUS, 'sig': C_SIG, 'clk': C_CLK, 'rst': C_RST, 'busc': C_SIG}[kind]
        sw = {'bus': 0.55, 'sig': 0.3, 'clk': 0.22, 'rst': 0.22, 'busc': 0.55}[kind]
        pts = [tuple(map(float, q)) for q in pts]
        self.wires.append((pts, col, sw, net if net else id(pts)))
        if arrow and len(pts) >= 2:
            self.arrow(pts[-2], pts[-1], col)
        if width is not None and len(pts) >= 2:
            a, b = pts[wpos], pts[wpos + 1]
            x = a[0] + (b[0] - a[0]) * wfrac
            y = a[1] + (b[1] - a[1]) * wfrac
            self.slash(x + wdx, y + wdy, width, col, vertical=(abs(b[0] - a[0]) < 1e-6))
        if name:
            a, b = pts[npos], pts[npos + 1]
            if nfrac is None:
                if abs(b[1] - a[1]) < 1e-6:
                    x = a[0] + (3 if b[0] > a[0] else -3)
                    y = a[1]
                else:
                    x, y = a[0], a[1] + (3 if b[1] > a[1] else -3)
            else:
                x = a[0] + (b[0] - a[0]) * nfrac
                y = a[1] + (b[1] - a[1]) * nfrac
            horiz = abs(b[1] - a[1]) < 1e-6
            if horiz:
                anchor = 'start' if b[0] >= a[0] else 'end'
                if nfrac is not None:
                    anchor = 'middle'
                yy = y - 0.9 if nside == 'above' else y + 2.7
                self.text(x + ndx, yy + ndy, name, size=nsize, anchor=anchor, color=col, italic=True)
            else:
                self.text(x + 1.0 + ndx, y + ndy, name, size=nsize, anchor='start', color=col, italic=True)
        for d in dots:
            self.dot(*d, color=col)

    def arrow(self, a, b, col):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        L, Wd = 1.8, 0.75
        x, y = b
        p1 = (x - L * math.cos(ang) + Wd * math.sin(ang), y - L * math.sin(ang) - Wd * math.cos(ang))
        p2 = (x - L * math.cos(ang) - Wd * math.sin(ang), y - L * math.sin(ang) + Wd * math.cos(ang))
        self.add('wire', f'<polygon points="{x:.2f},{y:.2f} {p1[0]:.2f},{p1[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}" '
                         f'fill="{col}" stroke="none"/>')

    def slash(self, x, y, n, col='#000', vertical=False):
        d = 1.5
        self.add('wire', f'<line x1="{x - d:.2f}" y1="{y + d:.2f}" x2="{x + d:.2f}" y2="{y - d:.2f}" '
                         f'stroke="{col}" stroke-width="0.35"/>')
        if vertical:
            self.text(x + 1.9, y + 0.9, str(n), size=2.5, color=col, layer='text')
        else:
            self.text(x + 0.4, y - 2.1, str(n), size=2.5, anchor='middle', color=col, layer='text')

    def dot(self, x, y, color='#000'):
        self.add('dot', f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.75" fill="{color}"/>')

    def frame(self, x, y, w, h, title, num, tdx=0):
        self.rect(x, y, w, h, fill='#fbfbfb', stroke='#7a7a7a', sw=0.4, dash='2.2,1.2', layer='frame')
        bx = x + 2 + tdx
        self.add('frame', f'<rect x="{bx:.2f}" y="{y + 1.6:.2f}" width="6.4" height="6.4" rx="1" '
                          f'fill="#404040"/>')
        self.text(bx + 3.2, y + 6.3, str(num), size=4.6, anchor='middle', weight='bold', color='#fff',
                  layer='frame')
        self.text(bx + 8.5, y + 6.4, title, size=4.0, weight='bold', color='#303030', layer='frame')

    def op(self, cx, cy, sym, r=4.2, size=4.6):
        self.circle(cx, cy, r, fill=GRAY, sw=0.4)
        self.text(cx, cy + size * 0.36, sym, size=size, anchor='middle', weight='bold', layer='elem')
        return dict(l=Pin(cx - r, cy), r=Pin(cx + r, cy), t=Pin(cx, cy - r), b=Pin(cx, cy + r),
                    c=Pin(cx, cy))

    def const(self, cx, cy, t, size=2.7):
        w = max(7.0, len(t) * size * 0.62 + 2.4)
        h = 5.4
        self.rect(cx - w / 2, cy - h / 2, w, h, fill=GRAY, sw=0.35)
        self.text(cx, cy + size * 0.36, t, size=size, anchor='middle', layer='elem')
        return dict(l=Pin(cx - w / 2, cy), r=Pin(cx + w / 2, cy), t=Pin(cx, cy - h / 2),
                    b=Pin(cx, cy + h / 2))

    def mux(self, x, y, h=16, w=7.5, n=2, sel='b', name=None, labels=None, nsize=2.4):
        s = 2.6
        self.poly([(x, y), (x + w, y + s), (x + w, y + h - s), (x, y + h)], fill=GRAY, sw=0.4)
        labels = labels or ['1', '0']
        ins = []
        for i in range(n):
            yy = y + h * (i + 1) / (n + 1)
            ins.append(Pin(x, yy))
            self.text(x + 1.0, yy + 0.9, labels[i], size=2.4, layer='elem')
        out = Pin(x + w, y + h / 2)
        sp = Pin(x + w / 2, y + h - s / 2 - 0.1) if sel == 'b' else Pin(x + w / 2, y + s / 2 + 0.1)
        if name:
            ty = y - 1.2 if sel == 'b' else y + h + 3.0
            self.text(x + w / 2, ty, name, size=nsize, anchor='middle', weight='bold', color='#333')
        P = dict(ins=ins, out=out, sel=sp)
        for lab, pin in zip(labels, ins):
            P['p' + lab] = pin
        return P

    def gate(self, kind, x, y, n=2, h=None, name=None, rot='r'):
        if kind == 'not':
            w, hh = 5.5, 5.0
        else:
            hh = h or max(7.0, 2.6 * n + 1.8)
            w = 9.0 + (1.6 if kind == 'nor' else 0)
        cx, cy = x + w / 2, y + hh / 2
        ang = {'r': 0, 'd': 90, 'l': 180, 'u': -90}[rot]

        def T(px, py):
            dx, dy = px - cx, py - cy
            if rot == 'r':
                return Pin(px, py)
            if rot == 'l':
                return Pin(cx - dx, cy - dy)
            if rot == 'd':
                return Pin(cx - dy, cy + dx)
            return Pin(cx + dy, cy - dx)
        g = [f'<g transform="rotate({ang} {cx:.2f} {cy:.2f})">'] if ang else []
        body = []
        if kind == 'not':
            body.append(f'<polygon points="{x:.2f},{y:.2f} {x + w - 1.6:.2f},{y + hh / 2:.2f} {x:.2f},{y + hh:.2f}" '
                        f'fill="#fff" stroke="#000" stroke-width="0.35"/>')
            body.append(f'<circle cx="{x + w - 0.8:.2f}" cy="{y + hh / 2:.2f}" r="0.8" fill="#fff" '
                        f'stroke="#000" stroke-width="0.35"/>')
            ins = [Pin(x, y + hh / 2)]
            out = Pin(x + w, y + hh / 2)
        else:
            gw = 9.0
            if kind == 'and':
                d = (f'M{x:.2f},{y:.2f} L{x + gw * 0.5:.2f},{y:.2f} '
                     f'A{gw * 0.5:.2f},{hh / 2:.2f} 0 0 1 {x + gw * 0.5:.2f},{y + hh:.2f} L{x:.2f},{y + hh:.2f} Z')
            else:
                d = (f'M{x:.2f},{y:.2f} Q{x + gw * 0.55:.2f},{y:.2f} {x + gw:.2f},{y + hh / 2:.2f} '
                     f'Q{x + gw * 0.55:.2f},{y + hh:.2f} {x:.2f},{y + hh:.2f} '
                     f'Q{x + gw * 0.28:.2f},{y + hh / 2:.2f} {x:.2f},{y:.2f} Z')
            body.append(f'<path d="{d}" fill="#fff" stroke="#000" stroke-width="0.35"/>')
            if kind == 'xor':
                body.append(f'<path d="M{x - 1.4:.2f},{y:.2f} Q{x + gw * 0.28 - 1.4:.2f},{y + hh / 2:.2f} '
                            f'{x - 1.4:.2f},{y + hh:.2f}" fill="none" stroke="#000" stroke-width="0.35"/>')
            outx = x + gw
            if kind == 'nor':
                body.append(f'<circle cx="{outx + 0.8:.2f}" cy="{y + hh / 2:.2f}" r="0.8" fill="#fff" '
                            f'stroke="#000" stroke-width="0.35"/>')
                outx += 1.6
            ins = []
            for i in range(n):
                yy = y + hh * (i + 1) / (n + 1)
                xin = x
                if kind in ('or', 'nor', 'xor'):
                    t = (yy - y) / hh
                    xin = x + 2 * (1 - t) * t * (gw * 0.28)
                    if kind == 'xor':
                        xin = x - 1.4 + 2 * (1 - t) * t * (gw * 0.28)
                ins.append(Pin(xin, yy))
            out = Pin(outx, y + hh / 2)
        self.add('elem', ''.join(g + body + (['</g>'] if ang else [])))
        ins = [T(*p) for p in ins]
        out = T(*out)
        if name:
            self.text(cx, (min(p.y for p in ins + [out]) if rot in 'rl' else y) - 1.6, name, size=2.0,
                      anchor='middle', color='#666')
        P = dict(ins=ins, out=out, i0=ins[0])
        if len(ins) > 1:
            P['i1'] = ins[1]
        if len(ins) > 2:
            P['i2'] = ins[2]
        return P

    def box(self, x, y, w, h, title, sub=None, fill=F_SEQ, pins=(), clk=None, rst=None,
            tsize=3.0, ssize=2.3, title_dy=0):
        self.rect(x, y, w, h, fill=fill, sw=0.45)
        ty = y + h / 2 + (0 if sub else 1.0) + title_dy
        if sub:
            self.text(x + w / 2, ty - 0.3, title, size=tsize, anchor='middle', weight='bold')
            self.text(x + w / 2, ty + ssize + 0.6, sub, size=ssize, anchor='middle', color='#444')
        else:
            self.text(x + w / 2, ty, title, size=tsize, anchor='middle', weight='bold')
        P = {}
        for key, side, frac, lab in pins:
            if side == 'l':
                p = Pin(x, y + h * frac)
                if lab:
                    self.text(x + 1.0, p.y + 0.85, lab, size=2.2, color='#222')
            elif side == 'r':
                p = Pin(x + w, y + h * frac)
                if lab:
                    self.text(x + w - 1.0, p.y + 0.85, lab, size=2.2, anchor='end', color='#222')
            elif side == 't':
                p = Pin(x + w * frac, y)
                if lab:
                    self.text(p.x, y + 2.9, lab, size=2.2, anchor='middle', color='#222')
            else:
                p = Pin(x + w * frac, y + h)
                if lab:
                    self.text(p.x, y + h - 1.0, lab, size=2.2, anchor='middle', color='#222')
            P[key] = p
        if clk:
            side, frac = clk
            if side == 'b':
                cx = x + w * frac
                self.poly([(cx - 1.6, y + h), (cx, y + h - 2.0), (cx + 1.6, y + h)], fill='#fff', sw=0.35)
                P['clk'] = Pin(cx, y + h)
            elif side == 't':
                cx = x + w * frac
                self.poly([(cx - 1.6, y), (cx, y + 2.0), (cx + 1.6, y)], fill='#fff', sw=0.35)
                P['clk'] = Pin(cx, y)
            elif side == 'l':
                cy = y + h * frac
                self.poly([(x, cy - 1.6), (x + 2.0, cy), (x, cy + 1.6)], fill='#fff', sw=0.35)
                P['clk'] = Pin(x, cy)
        if rst:
            side, frac = rst
            if side == 'b':
                rx = x + w * frac
                self.text(rx, y + h - 0.8, 'R', size=2.0, anchor='middle', color=C_RST, weight='bold')
                P['rst'] = Pin(rx, y + h)
            elif side == 't':
                rx = x + w * frac
                self.text(rx, y + 2.5, 'R', size=2.0, anchor='middle', color=C_RST, weight='bold')
                P['rst'] = Pin(rx, y)
            elif side == 'l':
                ry = y + h * frac
                self.text(x + 1.2, ry + 0.8, 'R', size=2.0, color=C_RST, weight='bold')
                P['rst'] = Pin(x, ry)
        P['box'] = (x, y, w, h)
        return P

    def port_in(self, x, y, name, w=None, size=2.6):
        w = w or (len(name) * size * 0.62 + 4)
        pts = [(x, y - 3), (x + w, y - 3), (x + w + 3, y), (x + w, y + 3), (x, y + 3)]
        self.poly(pts, fill=GRAY, sw=0.4)
        self.text(x + w / 2 + 0.3, y + 0.95, name, size=size, anchor='middle', weight='bold')
        return Pin(x + w + 3, y)

    def port_out(self, x, y, name, w=None, size=2.6):
        w = w or (len(name) * size * 0.62 + 4)
        pts = [(x, y - 3), (x + w, y - 3), (x + w + 3, y), (x + w, y + 3), (x, y + 3)]
        self.poly(pts, fill=GRAY, sw=0.4)
        self.text(x + w / 2 + 0.3, y + 0.95, name, size=size, anchor='middle', weight='bold')
        return Pin(x, y)

    def _render_wires(self):
        R = 1.1
        segs = []
        for pts, col, sw, net in self.wires:
            for a, b in zip(pts, pts[1:]):
                if abs(a[0] - b[0]) < 0.05 and abs(a[1] - b[1]) > 0.05:
                    segs.append((a[0], min(a[1], b[1]), max(a[1], b[1]), net))
        out = []
        for pts, col, sw, net in self.wires:
            d = f'M{pts[0][0]:.2f},{pts[0][1]:.2f}'
            for a, b in zip(pts, pts[1:]):
                if abs(a[1] - b[1]) < 0.05 and abs(a[0] - b[0]) > 0.05:
                    y = a[1]
                    lo, hi = min(a[0], b[0]), max(a[0], b[0])
                    xs = sorted({round(x, 3) for x, y1, y2, n in segs
                                 if n != net and lo + R + 0.4 < x < hi - R - 0.4
                                 and y1 + 0.6 < y < y2 - 0.6
                                 and not ({n, net} <= {'CLK', 'RST'})})
                    if b[0] < a[0]:
                        xs = xs[::-1]
                    sgn = 1 if b[0] > a[0] else -1
                    for x in xs:
                        d += f' L{x - sgn * R:.2f},{y:.2f}'
                        sweep = 1 if sgn > 0 else 0
                        d += f' A{R},{R} 0 0 {sweep} {x + sgn * R:.2f},{y:.2f}'
                    d += f' L{b[0]:.2f},{b[1]:.2f}'
                else:
                    d += f' L{b[0]:.2f},{b[1]:.2f}'
            out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" '
                       f'stroke-linejoin="miter"/>')
        return out

    def svg(self):
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}mm" height="{self.h}mm" '
               f'viewBox="0 0 {self.w} {self.h}">',
               f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="#ffffff"/>']
        for k in ('bg', 'frame'):
            out.extend(self.L[k])
        out.extend(self._render_wires())
        for k in ('wire', 'elem', 'dot', 'text'):
            out.extend(self.L[k])
        out.append('</svg>')
        return '\n'.join(out)


def hv(a, b):
    return [a, (b[0], a[1]), b]


def vh(a, b):
    return [a, (a[0], b[1]), b]


def hvh(a, b, xm):
    return [a, (xm, a[1]), (xm, b[1]), b]


def vhv(a, b, ym):
    return [a, (a[0], ym), (b[0], ym), b]
