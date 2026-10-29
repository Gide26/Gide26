"""CarePoint panel renderer — true scale, millimetres, built for perforation."""
import os

import cp_brand as B


def use_brand(mod):
    """Swap the active identity module (CarePoint, BCM, …)."""
    global B
    B = mod
import cp_photos as P
import cp_panels as PN

M = 22.0                 # live margin inside the safe zone
BLEED = 14.0
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".work")


def perforation(c, x, y, w, h, pitch=9.0, r=1.05, alpha=0.045, color=B.WHITE):
    c.saveState()
    p = c.beginPath()
    p.rect(x, y, w, h)
    c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(color)
    c.setFillAlpha(alpha)
    yy = y
    while yy < y + h:
        xx = x
        while xx < x + w:
            c.circle(xx, yy, r, stroke=0, fill=1)
            xx += pitch
        yy += pitch
    c.restoreState()


def fade(c, x, y, w, h, top=False):
    g = os.path.join(WORK, "grad_top.png" if top else "grad_navy.png")
    if os.path.exists(g):
        c.drawImage(g, x, y, w, h, mask="auto")


def photo(c, panel, y0, y1, bleed=BLEED, dpi=110):
    w = panel["w"]
    path = P.prepare(panel["photo"], w, y1 - y0, panel["focus"], dpi=dpi,
                     zoom=panel.get("zoom", 1.0))
    c.drawImage(path, -bleed, y0, w + bleed * 2, y1 - y0,
                preserveAspectRatio=False, mask=None)


def _scrim(c, x, y, w, h, top=True, alpha=0.92):
    steps = 40
    for i in range(steps):
        t = i / float(steps - 1)
        a = alpha * (t if top else 1 - t)
        c.saveState()
        c.setFillColor(B.CP_NAVY)
        c.setFillAlpha(a)
        c.rect(x, y + h * i / steps, w, h / steps + 0.4, stroke=0, fill=1)
        c.restoreState()


def _width(text, cap, weight="Manrope-800"):
    from reportlab.pdfbase import pdfmetrics
    size = B.font_for(cap, "Manrope")
    return pdfmetrics.stringWidth(text, weight, size) + cap * 0.02 * max(len(text) - 1, 0)


def _fits(text, cap, avail):
    return _width(text, cap) <= avail


def _split(text, cap, avail):
    """Greedy two-line break at the space that balances the two lines."""
    words = text.split(" ")
    if len(words) == 1:
        return [text]
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = max(_width(a, cap), _width(b, cap))
        if best is None or score < best[0]:
            best = (score, [a, b])
    return best[1]


def _tel(c, x, y, color, cap=6.2, align="right"):
    if getattr(B, "TEL", ""):
        B.label(c, x, y, "TEL " + B.TEL, cap, color, "Inter-500", 0.9, align)


def _plate(c, w, h, panel):
    """Reference-literal white logo plate, top-left, sitting over the photo."""
    plate = getattr(B, "plate", None)
    ph = min(w * 0.21, 108.0) if h > 950 else min(w * 0.22, 96.0)
    x, y = M, h - (26.0 if h > 950 else 20.0) - ph
    if plate:
        B._plate_avail = w - 2 * M
        try:
            plate(c, x, y, ph, dark=B.CP_NAVY, ground=B.WHITE, accent=B.CP_CYAN,
                  slogan=w >= 470)
        finally:
            B._plate_avail = None
    B.label(c, w - M, h - (40 if h > 950 else 34), panel["id"],
            5.2 if h > 950 else 4.6, B.WHITE, "Inter-500", 1.4, "right")


def draw(c, panel, bleed=BLEED):
    B.register_fonts()
    w, h = panel["w"], panel["h"]
    c.setFillColor(B.CP_NAVY)
    c.rect(-bleed, -bleed, w + bleed * 2, h + bleed * 2, stroke=0, fill=1)

    plate_style = getattr(B, "PLATE_STYLE", False)
    compact = h <= 950                       # measured door panes, not photo-scaled
    opaque = panel.get("film") == "opaque"   # solid vinyl: no mesh over the artwork
    block = 400 if h >= PN.UPPER_H else 420     # navy caption block at the foot
    if plate_style:
        block = 372 if h >= PN.UPPER_H else 392
    if compact:
        block = round(h * 0.30)

    if panel["photo"]:
        # full-bleed photograph
        photo(c, panel, -bleed, h + bleed)
        # top scrim so the identity stays legible over any image
        fade(c, -bleed, h - 230, w + bleed * 2, 230, top=True)
        # navy caption block
        c.setFillColor(B.CP_NAVY)
        c.rect(-bleed, -bleed, w + bleed * 2, block, stroke=0, fill=1)

        if plate_style:
            _plate(c, w, h, panel)
        else:
            B.monogram(c, M, h - 104, 44, dark=B.WHITE, accent=B.CP_CYAN)
            B.label(c, M + 56, h - 74, B.LINE1, 8.6, B.WHITE, "Manrope-700", 1.8)
            B.label(c, M + 56, h - 96, B.LINE2, 5.2, B.CP_CYAN, "Inter-600", 1.5)
            B.label(c, w - M, h - 84, panel["id"], 5.0, B.CP_MIST, "Inter-500", 1.4, "right")

        # service name
        cap = panel["title_cap"]
        if plate_style:
            n = len(panel["service"])
            cap = 78 if n <= 8 else (66 if n <= 11 else 54)
        if compact:
            cap = min(round(w * 0.135), 64)
        # a long service name breaks to two lines rather than shrinking away:
        # a 400 mm pane would otherwise set GENERAL CONSULTATION at half size.
        lines = [panel["service"]]
        if compact:
            avail = w - 2 * M
            fit = _fits(panel["service"], cap, avail)
            if not fit and " " in panel["service"]:
                lines = _split(panel["service"], cap, avail)
                cap = min(cap, 46)
                lines = _split(panel["service"], cap, avail)
                while len(lines) > 2 and cap > 24:
                    cap -= 4
                    lines = _split(panel["service"], cap, avail)
        lead = cap * 1.06
        top_y = block - 68 if compact else block - (128 if not plate_style else 120)
        for i, line in enumerate(lines):
            B.caps(c, M, top_y - i * lead, line, cap,
                   B.WHITE, "Manrope-800", tracking=cap * 0.02, max_w=w - 2 * M)
        c.setFillColor(B.CP_CYAN)
        drop = lead * (len(lines) - 1)
        if compact:
            c.rect(M, block - 105 - drop, min(w * 0.26, 120), 5, stroke=0, fill=1)
            B.label(c, M, block - 148 - drop, panel["sub"], 8.0, B.CP_CYAN,
                    "Inter-600", 2.2)
        else:
            c.rect(M, block - (168 if not plate_style else 158),
                   110 if not plate_style else 140, 6 if not plate_style else 7,
                   stroke=0, fill=1)
            B.label(c, M, block - (218 if not plate_style else 206), panel["sub"],
                    9.0 if not plate_style else 11.0, B.CP_CYAN, "Inter-600", 2.8)

        # foot
        if compact:
            B.hairline(c, M, 52, w - M, 52, B.WHITE, 0.4, 0.2)
            _tel(c, M, 30, B.CP_CYAN, 6.0, "left")
            B.label(c, w - M, 30, panel["id"], 4.4, B.CP_GREY, "Inter-500", 1.0, "right")
        else:
            B.hairline(c, M, 96, w - M, 96, B.WHITE, 0.4, 0.2)
            B.label(c, M, 62, B.SLOGAN, 6.2, B.CP_MIST, "Inter-400", 1.0)
            _tel(c, w - M, 62, B.CP_CYAN)
            B.label(c, w - M, 34, panel["id"], 4.6, B.CP_GREY, "Inter-500", 1.0, "right")

    else:
        # ---- directory pane ----------------------------------------------
        if not opaque:
            perforation(c, -bleed, -bleed, w + bleed * 2, h + bleed * 2, 12, 1.25, 0.04)
        if plate_style:
            _plate(c, w, h, panel)
        else:
            B.monogram(c, M, h - 112, 56, dark=B.WHITE, accent=B.CP_CYAN)
            B.label(c, M + 68, h - 76, B.LINE1, 9.4, B.WHITE, "Manrope-700", 2.0)
            B.label(c, M + 68, h - 100, B.LINE2, 5.6, B.CP_CYAN, "Inter-600", 1.6)

        if plate_style:
            plate_h = min(w * 0.21, 108.0) if h > 950 else min(w * 0.22, 96.0)
            inset = 26.0 if h > 950 else 20.0
            cap_t = min(60, round(w * 0.115)) if compact else 66
            top = h - inset - plate_h - 26 - cap_t
        else:
            top = h - 208
            cap_t = 66
        B.caps(c, M, top, panel["service"], cap_t, B.WHITE, "Manrope-800",
               tracking=1.6, max_w=w - 2 * M)
        c.setFillColor(B.CP_CYAN)
        c.rect(M, top - (28 if compact else 38), 110, 6, stroke=0, fill=1)
        B.label(c, M, top - (60 if compact else 80), panel["sub"], 6.4, B.CP_CYAN,
                "Inter-500", 2.2)

        y = top - (110 if compact else 192)
        n = max(len(panel["list_items"]) - 1, 1)
        step = min(84.0, (y - 190) / n)
        for item in panel["list_items"]:
            B.asterisk(c, M + 6, y + 7, 6.0 if compact else 7.4, B.CP_CYAN, 1.8)
            B.caps(c, M + 24 if compact else M + 30, y, item, 15.0 if compact else 22.0,
                   B.WHITE, "Manrope-500", 0.2, max_w=w - 2 * M - (24 if compact else 30))
            y -= step

        B.hairline(c, M, 96, w - M, 96, B.WHITE, 0.4, 0.2)
        B.label(c, M, 62, B.SLOGAN, 6.2, B.CP_MIST, "Inter-400", 1.0)
        _tel(c, w - M, 62, B.CP_CYAN)
        B.label(c, w - M, 34, panel["id"], 4.6, B.CP_GREY, "Inter-500", 1.0, "right")

    c.saveState()
    c.setStrokeColor(B.WHITE)
    c.setStrokeAlpha(0.10)
    c.setLineWidth(0.2)
    c.rect(-bleed + 1, -bleed + 1, w + bleed * 2 - 2, h + bleed * 2 - 2, stroke=1, fill=0)
    c.restoreState()
