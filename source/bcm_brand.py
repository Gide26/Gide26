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
LINE1 = "BCM"                     # the initials, set small above the name
LINE2 = "MEDICAL CENTRE"          # the line that has to be read from the road
SLOGAN = "Your Health. Our Commitment"
TEL = "0771 240 104  ·  0754 132 715"   # read off the clinic's own boards
TEL_FULL = "0771240104 / 0754132715"
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
    """White logo plate: badge, BCM, then MEDICAL CENTRE at full weight.

    The name does the work, not the initials: MEDICAL CENTRE is set at almost
    twice the cap height of BCM and in the dark navy, so a passer-by reads the
    words first and the badge second. Width is measured from the type so the
    plate always hugs its content. Returns the width used.
    """
    from reportlab.pdfbase import pdfmetrics

    ms = h * 0.60
    pad = h * 0.18
    gap = h * 0.15
    cap_b, cap_m, cap_s = h * 0.185, h * 0.330, h * 0.070
    tr_b, tr_m, tr_s = 2.4, 1.0, 0.9

    w_b = (pdfmetrics.stringWidth(LINE1, "Inter-600", font_for(cap_b, "Inter"))
           + tr_b * (len(LINE1) - 1))
    w_m = (pdfmetrics.stringWidth(LINE2, "Manrope-800", font_for(cap_m))
           + tr_m * (len(LINE2) - 1))
    w_s = (pdfmetrics.stringWidth(SLOGAN.upper(), "Inter-400", font_for(cap_s, "Inter"))
           + tr_s * (len(SLOGAN) - 1))
    tw = max(w_m, w_b, w_s if slogan else 0)
    w = pad * 2 + ms + gap + tw
    avail = globals().get("_plate_avail")
    if avail and w > avail:            # squeeze to the pane it sits on
        k = avail / w
        return plate(c, x, y, h * k, dark=dark, ground=ground, accent=accent,
                     slogan=slogan)

    # vertical rhythm — initials, gap, the name, gap, the slogan
    g1, g2 = h * 0.030, h * 0.030
    block = cap_b + g1 + cap_m + ((g2 + cap_s) if slogan else 0)
    top = y + h - max((h - block) / 2.0, h * 0.06)
    y_b = top - cap_b
    y_m = y_b - g1 - cap_m
    y_s = y_m - g2 - cap_s

    c.setFillColor(ground)
    c.rect(x, y, w, h, stroke=0, fill=1)
    monogram(c, x + pad, y + (h - ms) / 2, ms, dark=dark, accent=accent, knock=ground)
    tx = x + pad + ms + gap
    caps(c, tx, y_b, LINE1, cap_b, accent, "Inter-600", tr_b)
    caps(c, tx - cap_m * 0.012, y_m, LINE2, cap_m, dark, "Manrope-800", tr_m)
    if slogan:
        label(c, tx, y_s, SLOGAN, cap_s, CP_GREY, "Inter-400", tr_s)
    return w
