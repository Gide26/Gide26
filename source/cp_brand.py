"""CarePoint Medical Center — brand primitives.

Colours are sampled from the client's fascia sign and re-stated as clean print
values. The monogram is an HONEST RECREATION drawn in vector from the sign
photograph, not the official asset — replace with the client's vector logo
before release.
"""
import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "source", "fonts")

# --- palette (sampled from the fascia sign, 2026-10-28) ----------------------
CP_NAVY    = HexColor("#16233F")   # sign ground
CP_NAVY_MD = HexColor("#20304F")
CP_NAVY_LT = HexColor("#2C3F63")
CP_CYAN    = HexColor("#2BA9E0")   # "MEDICAL CENTER", logo P
CP_CYAN_DK = HexColor("#1B87B8")
CP_MIST    = HexColor("#E8EEF4")   # logo block ground
CP_GREY    = HexColor("#8FA2B8")
WHITE      = HexColor("#FFFFFF")
PAPER      = HexColor("#F4F7F9")
# aliases so the shared document toolkit can reuse this palette
NAVY, NAVY_MID, TEAL, TEAL_LT, MIST, GREY = CP_NAVY, CP_NAVY_MD, CP_CYAN, CP_CYAN, CP_MIST, CP_GREY

CLIENT = "CAREPOINT"
CLIENT_FULL = "CAREPOINT MEDICAL CENTER"
SLOGAN = "Your Health. Our Commitment"
TEL = "0784 747 461  ·  0700 817 054"
TEL_FULL = "(+256) 078 474 7461  ·  070 081 7054"

FONTS = ["Manrope-400", "Manrope-500", "Manrope-600", "Manrope-700", "Manrope-800",
         "Inter-400", "Inter-500", "Inter-600"]
CAP_RATIO = {"Manrope": 0.715, "Inter": 0.727}

_registered = False


def register_fonts():
    global _registered
    if _registered:
        return
    for fname in FONTS:
        pdfmetrics.registerFont(TTFont(fname, os.path.join(FONT_DIR, fname + ".ttf")))
    _registered = True


def font_for(cap_mm, family="Manrope"):
    return cap_mm / CAP_RATIO[family]


def _char_space(c, v):
    if hasattr(c, "setCharSpace"):
        c.setCharSpace(v)
    else:
        c._charSpace = v


def caps(c, x, y, text, cap, color=WHITE, weight="Manrope-800", tracking=0.0,
         align="left", max_w=None, tracking_mm=None):
    if tracking_mm is not None:
        tracking = tracking_mm
    fam = "Inter" if weight.startswith("Inter") else "Manrope"
    size = font_for(cap, fam)
    if max_w:
        w = pdfmetrics.stringWidth(text, weight, size) + tracking * max(len(text) - 1, 0)
        if w > max_w:
            size *= max_w / w * 0.995
    w = pdfmetrics.stringWidth(text, weight, size) + tracking * max(len(text) - 1, 0)
    if align == "right":
        x -= w
    elif align == "center":
        x -= w / 2
    c.setFillColor(color)
    c.setFont(weight, size)
    _char_space(c, tracking)
    c.drawString(x, y, text)
    _char_space(c, 0)
    return w


def label(c, x, y, text, cap=6, color=CP_CYAN, weight="Inter-600", tracking=1.2,
          align="left", max_w=None, tracking_mm=None):
    if tracking_mm is not None:
        tracking = tracking_mm
    return caps(c, x, y, text.upper(), cap, color, weight, tracking, align, max_w)


# ---------------------------------------------------------------------------
# Monogram — an open "C" carrying a figure, joined to a "P"
# Drawn on a 100 × 100 unit grid, scaled to size.
# ---------------------------------------------------------------------------
def monogram(c, x, y, size, dark=CP_NAVY, accent=CP_CYAN, knock=None):
    """CarePoint-style cp mark. knock = optional plate colour behind it."""
    c.saveState()
    if knock is not None:
        c.setFillColor(knock)
        c.rect(x, y, size, size, stroke=0, fill=1)
    s = size / 100.0
    lw = 8.2 * s

    # C — open to the right
    c.setStrokeColor(dark)
    c.setLineWidth(lw)
    c.setLineCap(1)
    p = c.beginPath()
    cx, cy, r = x + 33 * s, y + 58 * s, 26 * s
    p.moveTo(cx + r * 0.62, cy + r * 0.78)
    p.curveTo(cx - r * 0.35, cy + r * 1.35,
              cx - r * 1.35, cy + r * 0.30,
              cx - r * 0.55, cy - r * 0.75)
    p.curveTo(cx - r * 0.15, cy - r * 1.22,
              cx + r * 0.35, cy - r * 1.12,
              cx + r * 0.62, cy - r * 0.80)
    c.drawPath(p, stroke=1, fill=0)

    # figure head inside the C
    c.setFillColor(dark)
    c.circle(x + 41.0 * s, y + 64 * s, 5.2 * s, stroke=0, fill=1)

    # P — bowl joined to the C shoulder, stem descending
    c.setStrokeColor(accent)
    c.setLineWidth(7.0 * s)
    bp = c.beginPath()
    bcx, bcy, br = x + 64 * s, y + 63 * s, 14.5 * s
    bp.moveTo(bcx - br, bcy)
    bp.curveTo(bcx - br, bcy + br * 1.25,
               bcx + br * 1.15, bcy + br * 1.05,
               bcx + br * 0.92, bcy - br * 0.02)
    bp.curveTo(bcx + br * 0.95, bcy - br * 1.02,
               bcx - br * 0.35, bcy - br * 1.15,
               bcx - br, bcy - br * 0.35)
    c.drawPath(bp, stroke=1, fill=0)
    c.setFillColor(accent)
    c.rect(x + 59.6 * s, y + 20 * s, 8.8 * s, 44 * s, stroke=0, fill=1)
    c.circle(x + 64 * s, y + 20 * s, 4.4 * s, stroke=0, fill=1)
    c.restoreState()


def wordmark(c, x, y, cap, tone=WHITE, sub=CP_CYAN, slogan=None, slogan_cap=None):
    """CAREPOINT / MEDICAL CENTER stacked wordmark. x,y = bottom-left of 'CAREPOINT'."""
    w1 = caps(c, x, y, "CAREPOINT", cap, tone, "Manrope-800", tracking=cap * 0.045)
    caps(c, x, y - cap * 1.16, "MEDICAL CENTER", cap * 0.62, sub, "Manrope-600",
         tracking=cap * 0.16)
    if slogan:
        label(c, x, y - cap * 1.16 - (slogan_cap or cap * 0.5) * 1.9, slogan,
              slogan_cap or cap * 0.5, CP_MIST, "Inter-400", cap * 0.02)
    return w1


def lockup(c, x, y, mark, tone=WHITE, sub=CP_CYAN, slogan=None):
    """Monogram + wordmark, horizontally. x,y = bottom-left of the mark."""
    dark = tone
    accent = sub
    monogram(c, x, y, mark, dark=dark, accent=accent)
    tx = x + mark + mark * 0.30
    caps(c, tx, y + mark * 0.52, "CAREPOINT", mark * 0.30, tone, "Manrope-800",
         tracking=mark * 0.014)
    label(c, tx, y + mark * 0.19, "MEDICAL CENTER", mark * 0.105, sub, "Inter-600",
          tracking=mark * 0.04)
    if slogan:
        label(c, tx, y - mark * 0.04, slogan, mark * 0.075, CP_GREY, "Inter-400",
              tracking=mark * 0.012)
    return tx


def hairline(c, x1, y1, x2, y2, color=WHITE, width=0.35, alpha=0.2):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.setStrokeAlpha(alpha)
    c.line(x1, y1, x2, y2)
    c.restoreState()


def asterisk(c, cx, cy, r, color=CP_CYAN, weight=3.2):
    """The six-arm asterisk used on the client's own services board."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(weight * r / 6.0)
    c.setLineCap(1)
    for k in range(3):
        import math
        a = math.pi * k / 3
        c.line(cx - r * math.cos(a), cy - r * math.sin(a),
               cx + r * math.cos(a), cy + r * math.sin(a))
    c.restoreState()
