"""BCM Medical Centre — identity layer on top of the CarePoint print system.

Same press-ready geometry, palette and typography; different identity and a
reference-literal panel layout (white logo plate top-left, photo full bleed,
solid caption band at the foot).
"""
import cp_brand as _cp
from cp_brand import *          # colours, caps(), label(), hairline(), asterisk()
from cp_brand import (CP_NAVY, CP_NAVY_MD, CP_CYAN, CP_MIST, CP_GREY, WHITE,
                      register_fonts, font_for, caps, label, hairline, asterisk)

CLIENT = "BCM"
CLIENT_TITLE = "BCM Medical Centre"
DOC_CODE = "BCM"
CLIENT_FULL = "BCM MEDICAL CENTRE"
LINE1 = "BCM"
LINE2 = "MEDICAL CENTRE"
SLOGAN = "Your Health. Our Commitment"
TEL = ""                       # no telephone numbers supplied for this client
TEL_FULL = ""
PLATE_STYLE = True             # reference-literal layout
ACCENT = CP_CYAN


def _xlate(s):
    """Any prose still written for the CarePoint set, re-branded as it is drawn."""
    if not isinstance(s, str):
        return s
    return (s.replace("CarePoint Medical Center", CLIENT_FULL.title())
             .replace("CarePoint", CLIENT_TITLE)
             .replace("CAREPOINT MEDICAL CENTER", CLIENT_FULL)
             .replace("CAREPOINT", CLIENT))


def caps(c, x, y, text, cap, color=WHITE, weight="Manrope-800", tracking=0.0,
         align="left", max_w=None, tracking_mm=None):
    return _cp.caps(c, x, y, _xlate(text), cap, color, weight, tracking, align, max_w,
                    tracking_mm)


def label(c, x, y, text, cap=6, color=CP_CYAN, weight="Inter-600", tracking=1.2,
          align="left", max_w=None, tracking_mm=None):
    return _cp.label(c, x, y, _xlate(text), cap, color, weight, tracking, align, max_w,
                     tracking_mm)


def monogram(c, x, y, size, dark=CP_NAVY, accent=CP_CYAN, knock=None):
    """BCM badge: open cyan ring around a bold B.

    Drawn as vectors so it scales from a 20 mm web favicon to a 300 mm plate.
    This is a RECREATION in the client's colour language, not their official
    logo — swap it for the real asset before release.
    """
    c.saveState()
    if knock is not None:
        c.setFillColor(knock)
        c.rect(x, y, size, size, stroke=0, fill=1)
    s = size / 100.0
    cx, cy = x + 50 * s, y + 50 * s
    r = 41 * s

    # thin dark ring, opened on the right where the accent arc takes over
    c.setStrokeColor(dark)
    c.setLineWidth(4.6 * s)
    c.circle(cx, cy, r, stroke=1, fill=0)

    # cyan arc: the "pulse" side of the ring
    c.setStrokeColor(accent)
    c.setLineWidth(9.0 * s)
    c.setLineCap(1)
    c.arc(cx - r, cy - r, cx + r, cy + r, startAng=-58, extent=116)

    # the B, optically centred
    cap = 44 * s
    fs = font_for(cap, "Manrope")
    c.setFillColor(dark)
    c.setFont("Manrope-800", fs)
    w = c.stringWidth("B", "Manrope-800", fs)
    c.drawString(cx - w / 2 + 1.2 * s, cy - cap * 0.5 - 0.6 * s, "B")
    c.restoreState()


def plate(c, x, y, h, dark=CP_NAVY, ground=WHITE, accent=CP_CYAN, slogan=True):
    """White logo plate: badge + BCM MEDICAL CENTRE + slogan, as on the boards.

    Width is measured from the type so the plate always hugs its content.
    Returns the width used.
    """
    from reportlab.pdfbase import pdfmetrics

    ms = h * 0.60
    pad = h * 0.20
    gap = h * 0.17
    cap1, cap2, cap3 = h * 0.30, h * 0.115, h * 0.082
    tr1, tr2, tr3 = 1.6, 2.6, 0.9
    w1 = (pdfmetrics.stringWidth(LINE1, "Manrope-800", font_for(cap1))
          + tr1 * (len(LINE1) - 1))
    w2 = (pdfmetrics.stringWidth(LINE2, "Inter-600", font_for(cap2, "Inter"))
          + tr2 * (len(LINE2) - 1))
    w3 = (pdfmetrics.stringWidth(SLOGAN.upper(), "Inter-400", font_for(cap3, "Inter"))
          + tr3 * (len(SLOGAN) - 1))
    tw = max(w1, w2, w3)
    w = pad * 2 + ms + gap + tw

    c.setFillColor(ground)
    c.rect(x, y, w, h, stroke=0, fill=1)
    monogram(c, x + pad, y + (h - ms) / 2, ms, dark=dark, accent=accent, knock=ground)
    tx = x + pad + ms + gap
    caps(c, tx, y + h * 0.50, LINE1, cap1, dark, "Manrope-800", tr1)
    label(c, tx + 0.6, y + h * 0.28, LINE2, cap2, accent, "Inter-600", tr2)
    if slogan:
        label(c, tx + 0.6, y + h * 0.12, SLOGAN, cap3, CP_GREY, "Inter-400", tr3)
    return w
