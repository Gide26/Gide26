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


def _tel(c, x, y, color, cap=6.2, align="right"):
    if getattr(B, "TEL", ""):
        B.label(c, x, y, "TEL " + B.TEL, cap, color, "Inter-500", 0.9, align)


def _plate(c, w, h, panel):
    """Reference-literal white logo plate, top-left, sitting over the photo."""
    plate = getattr(B, "plate", None)
    ph = 104.0
    x, y = M, h - 26.0 - ph
    if plate:
        plate(c, x, y, ph, dark=B.CP_NAVY, ground=B.WHITE, accent=B.CP_CYAN)
    B.label(c, w - M, h - 40, panel["id"], 5.2, B.WHITE, "Inter-500", 1.4, "right")


def draw(c, panel, bleed=BLEED):
    B.register_fonts()
    w, h = panel["w"], panel["h"]
    c.setFillColor(B.CP_NAVY)
    c.rect(-bleed, -bleed, w + bleed * 2, h + bleed * 2, stroke=0, fill=1)

    plate_style = getattr(B, "PLATE_STYLE", False)
    block = 400 if h >= PN.UPPER_H else 420     # navy caption block at the foot
    if plate_style:
        block = 372 if h >= PN.UPPER_H else 392

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
        B.caps(c, M, block - (128 if not plate_style else 120), panel["service"], cap,
               B.WHITE, "Manrope-800", tracking=cap * 0.02, max_w=w - 2 * M)
        c.setFillColor(B.CP_CYAN)
        c.rect(M, block - (168 if not plate_style else 158), 110 if not plate_style else 140,
               6 if not plate_style else 7, stroke=0, fill=1)
        B.label(c, M, block - (218 if not plate_style else 206), panel["sub"],
                9.0 if not plate_style else 11.0, B.CP_CYAN, "Inter-600", 2.8)

        # foot
        B.hairline(c, M, 96, w - M, 96, B.WHITE, 0.4, 0.2)
        B.label(c, M, 62, B.SLOGAN, 6.2, B.CP_MIST, "Inter-400", 1.0)
        _tel(c, w - M, 62, B.CP_CYAN)
        B.label(c, w - M, 34, panel["id"], 4.6, B.CP_GREY, "Inter-500", 1.0, "right")

    else:
        # ---- directory pane ----------------------------------------------
        perforation(c, -bleed, -bleed, w + bleed * 2, h + bleed * 2, 12, 1.25, 0.04)
        if plate_style:
            _plate(c, w, h, panel)
        else:
            B.monogram(c, M, h - 112, 56, dark=B.WHITE, accent=B.CP_CYAN)
            B.label(c, M + 68, h - 76, B.LINE1, 9.4, B.WHITE, "Manrope-700", 2.0)
            B.label(c, M + 68, h - 100, B.LINE2, 5.6, B.CP_CYAN, "Inter-600", 1.6)

        top = h - (232 if plate_style else 208)
        B.caps(c, M, top, panel["service"], 66, B.WHITE, "Manrope-800",
               tracking=1.6, max_w=w - 2 * M)
        c.setFillColor(B.CP_CYAN)
        c.rect(M, top - 38, 110, 6, stroke=0, fill=1)
        B.label(c, M, top - 80, panel["sub"], 6.4, B.CP_CYAN, "Inter-500", 2.2)

        y = top - 192
        n = max(len(panel["list_items"]) - 1, 1)
        step = min(74.0, (y - 190) / n)
        for item in panel["list_items"]:
            B.asterisk(c, M + 9, y + 9, 8.4, B.CP_CYAN, 4.0)
            B.caps(c, M + 30, y, item, 19.0, B.WHITE, "Manrope-500", 0.2,
                   max_w=w - 2 * M - 30)
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
