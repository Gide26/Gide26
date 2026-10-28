"""
GMC One-Way Vision Film — brand system primitives.

All geometry in this project is expressed in MILLIMETRES. The canvas is scaled
once per page (c.scale(mm, mm)) so every coordinate below is a real millimetre
on the printed panel.
"""
import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.units import mm as MM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "source", "fonts")

# ----------------------------------------------------------------------------
# Palette — navy / white / teal / restrained medical green
# ----------------------------------------------------------------------------
NAVY       = HexColor("#0A2642")
NAVY_DEEP  = HexColor("#06182A")
NAVY_MID   = HexColor("#123A5C")
TEAL       = HexColor("#0F8C8C")
TEAL_LT    = HexColor("#4FB3AE")
GREEN      = HexColor("#2E7A5F")
WHITE      = HexColor("#FFFFFF")
PAPER      = HexColor("#F4F7F8")
MIST       = HexColor("#DCE6EC")
GREY       = HexColor("#8FA3B4")

FONTS = {
    "Manrope-300": "Manrope-Light",
    "Manrope-400": "Manrope-Regular",
    "Manrope-500": "Manrope-Medium",
    "Manrope-600": "Manrope-SemiBold",
    "Manrope-700": "Manrope-Bold",
    "Manrope-800": "Manrope-ExtraBold",
    "Inter-400": "Inter-Regular",
    "Inter-500": "Inter-Medium",
    "Inter-600": "Inter-SemiBold",
}

_registered = False


def register_fonts():
    global _registered
    if _registered:
        return
    for fname in FONTS:
        pdfmetrics.registerFont(TTFont(fname, os.path.join(FONT_DIR, fname + ".ttf")))
    _registered = True


# Cap-height ratios (measured from the supplied font binaries) so type can be
# specified in real millimetre cap heights rather than arbitrary point sizes.
CAP_RATIO = {"Manrope": 0.715, "Inter": 0.727}


def _char_space(c, value):
    """Canvas-level letter spacing (reportlab keeps it on the canvas)."""
    if hasattr(c, "setCharSpace"):
        c.setCharSpace(value)
    else:
        c._charSpace = value


def font_for(size_mm_cap, family="Manrope"):
    """Return a reportlab font size (in mm units) giving the requested cap height."""
    return size_mm_cap / CAP_RATIO[family]


# ----------------------------------------------------------------------------
# Typography helpers
# ----------------------------------------------------------------------------
def caps(c, x, y, text, cap_mm, color=WHITE, weight="Manrope-800",
         tracking_mm=0.0, align="left", max_width=None):
    """Draw uppercase tracked text with a given real-world cap height.

    Returns the advance width in mm. If max_width is given, the font size is
    reduced until the line fits (never below 80% to protect legibility).
    """
    family = "Inter" if weight.startswith("Inter") else "Manrope"
    size = font_for(cap_mm, family)
    c.setFillColor(color)
    c.setFont(weight, size)

    def width_for(sz, trk):
        return pdfmetrics.stringWidth(text, weight, sz) + trk * max(len(text) - 1, 0)

    if max_width:
        trial = size
        while width_for(trial, tracking_mm) > max_width and trial > size * 0.8:
            trial *= 0.985
        size = trial

    w = width_for(size, tracking_mm)
    if align == "right":
        x -= w
    elif align == "center":
        x -= w / 2.0

    _char_space(c, tracking_mm)
    c.drawString(x, y, text)
    _char_space(c, 0)
    return w


def label(c, x, y, text, cap_mm=9, color=TEAL, weight="Inter-600",
          tracking_mm=1.2, align="left", max_width=None):
    return caps(c, x, y, text.upper(), cap_mm, color, weight, tracking_mm, align, max_width)


def body(c, x, y, text, cap_mm=6.5, color=MIST, weight="Inter-400",
         tracking_mm=0.1, align="left", max_width=None):
    return caps(c, x, y, text, cap_mm, color, weight, tracking_mm, align, max_width)


# ----------------------------------------------------------------------------
# Identity lockup (PLACEHOLDER — replace with supplied logo artwork)
# ----------------------------------------------------------------------------
def logomark(c, x, y, size, monogram="MC", fg=WHITE, accent=TEAL, rule=True):
    """Square monogram mark with a medical cross. x,y = bottom-left, size = mm."""
    c.saveState()
    c.setFillColor(NAVY_DEEP)
    c.setFillAlpha(0.55)
    c.rect(x, y, size, size, stroke=0, fill=1)
    c.setFillAlpha(1)
    if rule:
        c.setStrokeColor(fg)
        c.setLineWidth(max(size * 0.018, 0.25))
        c.setStrokeAlpha(0.85)
        c.rect(x, y, size, size, stroke=1, fill=0)
    # cross
    arm = size * 0.46
    bar = size * 0.13
    cx, cy = x + size / 2.0, y + size / 2.0
    c.setFillColor(accent)
    c.rect(cx - bar / 2, cy - arm / 2, bar, arm, stroke=0, fill=1)
    c.rect(cx - arm / 2, cy - bar / 2, arm, bar, stroke=0, fill=1)
    c.restoreState()


def lockup(c, x, y, mark_mm=30, word="MEDICAL CENTER", tone=WHITE,
           sub="PREMIUM HEALTHCARE", sub_cap=4.2):
    """Horizontal identity lockup. x,y = bottom-left of the mark."""
    logomark(c, x, y, mark_mm)
    tx = x + mark_mm + mark_mm * 0.38
    caps(c, tx, y + mark_mm * 0.46, word, mark_mm * 0.235,
         tone, "Manrope-700", tracking_mm=mark_mm * 0.062)
    if sub:
        label(c, tx, y + mark_mm * 0.16, sub, sub_cap, TEAL_LT, "Inter-500",
              tracking_mm=sub_cap * 0.26)
    return tx


def vertical_lockup(c, x, y, mark_mm=28, word="MEDICAL CENTER"):
    logomark(c, x, y, mark_mm)
    label(c, x + mark_mm / 2.0, y - mark_mm * 0.42, word, mark_mm * 0.155,
          WHITE, "Manrope-700", tracking_mm=0.9, align="center")


# ----------------------------------------------------------------------------
# Restrained geometric accents
# ----------------------------------------------------------------------------
def hairline(c, x1, y1, x2, y2, color=MIST, width=0.35, alpha=0.35):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.setStrokeAlpha(alpha)
    c.line(x1, y1, x2, y2)
    c.restoreState()


def accent_rule(c, x, y, w=110, h=5.0, color=TEAL):
    c.setFillColor(color)
    c.rect(x, y, w, h, stroke=0, fill=1)


def arc_motif(c, cx, cy, r, color=WHITE, alpha=0.07, width=0.6, start=200, extent=140):
    c.saveState()
    c.setStrokeColor(color)
    c.setStrokeAlpha(alpha)
    c.setLineWidth(width)
    c.arc(cx - r, cy - r, cx + r, cy + r, startAng=start, extent=extent)
    c.restoreState()


def cross_motif(c, cx, cy, size, color=WHITE, alpha=0.05, bar=0.22):
    c.saveState()
    c.setFillColor(color)
    c.setFillAlpha(alpha)
    c.rect(cx - size * bar / 2, cy - size / 2, size * bar, size, stroke=0, fill=1)
    c.rect(cx - size / 2, cy - size * bar / 2, size, size * bar, stroke=0, fill=1)
    c.restoreState()


# ----------------------------------------------------------------------------
# Production furniture (marks + slug) — outside the trim
# ----------------------------------------------------------------------------
def crop_marks(c, trim_w, trim_h, bleed, mark=8.0, offset=0.0):
    c.saveState()
    c.setStrokeColor(HexColor("#000000"))
    c.setLineWidth(0.25)
    L = mark
    # corner positions in page space where trim corners sit
    xs = [offset, offset + trim_w]
    ys = [offset + bleed, offset + bleed + trim_h]
    for x in xs:
        for y in ys:
            c.line(x, y - bleed, x, y - bleed - L)          # vertical ticks outward
            c.line(x, y + bleed, x, y + bleed + L)
            c.line(x - bleed, y, x - bleed - L, y)
            c.line(x + bleed, y, x + bleed + L, y)
    c.restoreState()


def registration_target(c, x, y, r=1.6):
    c.saveState()
    c.setStrokeColor(HexColor("#000000"))
    c.setFillColor(HexColor("#000000"))
    c.setLineWidth(0.2)
    c.circle(x, y, r, stroke=1, fill=0)
    c.line(x - r * 2, y, x + r * 2, y)
    c.line(x, y - r * 2, x, y + r * 2)
    c.restoreState()


def slug(c, x, y, w, h, lines, tone=HexColor("#111111")):
    """Technical slug strip (sits outside the bleed, trimmed off before mounting)."""
    c.saveState()
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(x, y, w, h, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#999999"))
    c.setLineWidth(0.2)
    c.line(x, y + h, x + w, y + h)
    ty = y + h - 1.9
    for i, (txt, cap, col, weight) in enumerate(lines):
        caps(c, x + 1.2, ty - i * (cap * 1.75), txt, cap, col, weight,
             tracking_mm=cap * 0.16)
    c.restoreState()
