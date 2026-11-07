"""BCM Medical Centre — sign post panel, name plus the foot line.

Separate deliverable from the door film set: one panel, no services, no
photographs. Built to the client's measurement — 46 in × 22 in, landscape.

Everything is drawn in millimetres on the trim rectangle; the artwork file adds
10 mm bleed, crop marks and a slug strip the same way the door panes do.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageDraw
from reportlab.lib.colors import Color
from reportlab.lib.units import mm as MM
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics

import bcm_brand as B
import cp_docutil as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "bcm", "sign")
ART_DIR = os.path.join(OUT_DIR, "artwork")
WORK = os.path.join(ROOT, "source", ".work", "bcm_sign")

# --- the client's measurement -------------------------------------------------
IN = 25.4


def ftin(inches):
    """46 in -> '3 ft 10 in'."""
    ft, inch = divmod(int(round(inches)), 12)
    return f"{ft} ft {inch} in" if inch else f"{ft} ft"


# --- the client's measurement, 2026-11-06: 46 in long, 22 in high ----------
W_IN, H_IN = 46, 22                                  # client, 2026-11-06
W, H = round(W_IN * IN, 1), round(H_IN * IN, 1)      # 1168.4 × 558.8 mm
W_FT, H_FT = W_IN / 12, H_IN / 12
FT_TXT = f"{ftin(W_IN)} × {ftin(H_IN)}"              # 3 ft 10 in × 1 ft 10 in
MM_TXT = f"{W:.1f} × {H:.1f} mm"
BLEED, SLUG = 10.0, 22.0
SAFE = 25.0
REV = "Rev B  ·  2026-11-06"
NAME = "MEDICAL CENTRE"
WORD = "EDDWALIRO"          # Luganda: the word people on this road actually use
ED_RATIO = 1.0              # cap height of the word as a share of the name's
ED_TRACK = 12.0             # open tracking: bold, but not a slab of ink

B.register_fonts()


# --------------------------------------------------------------------- helpers
def fit_cap(text, weight, family, target_w):
    """Cap height (mm) that makes `text` exactly `target_w` wide."""
    cap = 100.0
    size = B.font_for(cap, family)
    w = pdfmetrics.stringWidth(text, weight, size)
    return cap * target_w / w


# The lockup was approved at 944.9 × 643.1 mm. A 46 in panel is wider
# and slightly shallower, so the block is SCALED from that approved arrangement
# rather than re-fitted: proportions stay identical, and the type never runs to
# the edge or crowds the top and bottom.
REF_W, REF_H = 944.9, 643.1
_REF_M = 46.0
_REF = None


def _ref():
    """The approved lockup's own numbers, at the reference panel."""
    global _REF
    if _REF is None:
        cap_m = fit_cap(NAME, "Manrope-800", "Manrope", REF_W - 2 * _REF_M)
        cap_e = cap_m * ED_RATIO
        ms, cap_b, cap_s = 112.0, 26.0, 22.0
        gap_e, gap_badge, gap_bm, gap_rule = 24.0, 20.0, 16.0, 44.0
        block = cap_e + gap_e + ms + gap_badge + cap_b + gap_bm + cap_m
        tail = gap_rule + 5.0 + 22.0 + cap_s
        _REF = {"cap_m": cap_m, "block": block, "tail": tail}
    return _REF


def lockscale(w, h, m=_REF_M, fill=0.88):
    """Scale factor for the approved lockup on a panel of w × h mm."""
    r = _ref()
    by_width = fit_cap(NAME, "Manrope-800", "Manrope", w - 2 * m) / r["cap_m"]
    by_height = (fill * h) / (r["block"] + r["tail"])
    return min(by_width, by_height)



# ------------------------------------------------------------------ bright faces
# The sign replaces the lit box the clinic already has on the road, and is built to
# that sign's own arrangement (client photograph, 2026-11-06), brought in line with the
# client's later corrections: BCM on a white band, MEDICAL CENTRE in white on navy,
# EDDWALIRO knocked out of a
# full-width red block, OPEN 24 HRS between two arrows, navy foot strip with the
# numbers. The red block is what carries the colour, so the face still shouts in the
# box without a dense field behind the tubes.
LIT_RED = Color(0.929, 0.106, 0.141)      # #ED1B24 — bright red, the shouting colour
DEEP_RED = Color(0.741, 0.078, 0.098)     # #BD1419 — the same red, for small type

LIT = {
    # the shipping face: the client's own sign arrangement — navy bands, red block,
    # EDDWALIRO knocked out in white, red OPEN 24 HRS row, navy foot strip
    "R": dict(ground=B.WHITE, band=B.CP_NAVY, band_txt=B.WHITE, band_txt_alt=B.CP_NAVY,
              mc_band=B.CP_NAVY, mc_txt=B.WHITE,
              block=LIT_RED, block_txt=B.WHITE, mark=B.CP_NAVY, open=LIT_RED,
              slogan=DEEP_RED, key=(B.CP_GREY, 0.45)),
    # spare: the same arrangement on the cyan field, if the client would rather the
    # field carry the colour
    "L": dict(ground=B.CP_CYAN, band=B.CP_NAVY, band_txt=B.WHITE, band_txt_alt=B.CP_NAVY,
              mc_band=B.WHITE, mc_txt=B.CP_NAVY,
              block=B.CP_NAVY, block_txt=B.WHITE, mark=B.CP_NAVY, open=B.WHITE,
              slogan=B.CP_NAVY, key=(B.WHITE, 0.34)),
}
FACE = "R"                       # what the print files carry
# The client's number for the sign: 0788 323 815 first, 0754 132 715 kept. This is the
# newer line they gave (it went onto door panes 1-18); the sign now carries it too.
SIGN_TEL = "0788 323 815  ·  0754 132 715"
VARIANT_NAME = {"R": "LIT — THE CLINIC'S SIGN", "L": "LIT — CYAN FIELD · SPARE",
                "A": "UNLIT — NAVY FACE", "B": "UNLIT — BADGE-LEFT",
                "C": "UNLIT — FASCIA"}


# --- the installed sign, read off the client's own night photograph ----------
# The clinic already has a lit box on the road: a thin brand band at the top with the
# the initials BCM, a navy band carrying MEDICAL CENTRE, the
# branch name EDDWALIRO in white knocked out of a red block, an OPEN 24 HRS row with
# arrows at both ends, and a navy foot strip with the telephone. The new 46 x 22 in
# face keeps that arrangement — it is the sign people on this road already know — and
# only brings it up to date: the client's current numbers, and the motto left off.
SIGN_BRAND = "BCM"                    # the badge and the wordmark became the initials
SIGN_COMMUNITY = "MEDICAL CENTRE"     # on the navy band
SIGN_BRANCH = "BUSSABALA"
SIGN_OPEN = ("Open", "24 Hrs")

# band heights as weights of the inner height (they are normalised to fit)
BAND_W = (84.0, 100.0, 10.0, 148.0, 91.0, 10.0, 57.0)     # brand, navy, gap, red, open, gap, foot


def _arrow(c, x, y, length, thick, head_len, head_h, colour, direction=-1):
    """A solid horizontal arrow. direction -1 points left, +1 points right."""
    c.setFillColor(colour)
    hl = min(head_len, length * 0.55)
    if direction < 0:                     # tip at x, shaft runs to the right
        x_tip = x
        p = c.beginPath()
        p.moveTo(x_tip, y)
        p.lineTo(x_tip + hl, y + head_h / 2)
        p.lineTo(x_tip + hl, y - head_h / 2)
        p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.rect(x_tip + hl, y - thick / 2, length - hl, thick, stroke=0, fill=1)
    else:                                 # tip at x + length, shaft runs to the left
        x_tip = x + length
        p = c.beginPath()
        p.moveTo(x_tip, y)
        p.lineTo(x_tip - hl, y + head_h / 2)
        p.lineTo(x_tip - hl, y - head_h / 2)
        p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.rect(x, y - thick / 2, length - hl, thick, stroke=0, fill=1)


def bright_face(c, w, h, pal, slogan=False, tel=True):
    """The lit face, built to the client's installed sign.

    Top to bottom: white band with BCM, navy band with MEDICAL CENTRE in white,
    red block with EDDWALIRO knocked out in white, the OPEN 24 HRS row with an arrow
    at each end, and the navy foot strip with the numbers.

    `slogan` is accepted for the callers that still pass it, but nothing on this face
    carries the motto — the client asked for it off. `tel=False` drops the foot strip.
    """
    mxx = w * 0.028                       # side margin: the light border round the bands
    my = h * 0.030                        # top / bottom margin
    IW = w - 2 * mxx
    IH = h - 2 * my
    weights = list(BAND_W)
    if not tel:
        weights[-2] = 0.0                 # drop the second gap
        weights[-1] = 0.0                 # and the foot strip
    total = sum(weights)
    band = [IH * x / total for x in weights]
    h_brand, h_navy, g1, h_red, h_open, g2, h_foot = band

    top = my + IH                          # the top edge of the stack
    y_brand = top - h_brand
    y_navy = y_brand - h_navy
    y_red = y_navy - g1 - h_red
    y_open = y_red - h_open
    y_foot = y_open - g2 - h_foot

    # ---- white band: BCM, where the badge and the Bactrimed wordmark used to be
    cap_w = h_brand * 0.86
    B.caps(c, w / 2, y_brand + (h_brand - cap_w) / 2 - cap_w * 0.02, SIGN_BRAND, cap_w,
           pal["band_txt_alt"], "Manrope-800", cap_w * 0.16, align="center")

    # ---- navy band: MEDICAL CENTRE
    c.setFillColor(pal["mc_band"])
    c.rect(mxx, y_navy, IW, h_navy, stroke=0, fill=1)
    cap_c = min(h_navy * 0.80, fit_cap(SIGN_COMMUNITY, "Manrope-800", "Manrope",
                                       IW * 0.94))
    B.caps(c, w / 2, y_navy + (h_navy - cap_c) / 2 - cap_c * 0.02, SIGN_COMMUNITY,
           cap_c, pal["mc_txt"], "Manrope-800", cap_c * 0.12, align="center",
           max_w=IW * 0.94)

    # ---- red block: EDDWALIRO knocked out in white
    c.setFillColor(pal["block"])
    c.rect(mxx, y_red, IW, h_red, stroke=0, fill=1)
    cap_e = min(h_red * 0.80, fit_cap(WORD, "Manrope-800", "Manrope", IW * 0.94))
    B.caps(c, w / 2, y_red + (h_red - cap_e) / 2 - cap_e * 0.03, WORD, cap_e,
           pal["block_txt"], "Manrope-800", cap_e * 0.045, align="center",
           max_w=IW * 0.98)

    # ---- open row: arrow, Open 24 Hrs, arrow
    al = IW * 0.135                       # arrow length
    acap = h_open * 0.48
    w1 = pdfmetrics.stringWidth(SIGN_OPEN[0], "Manrope-700", B.font_for(acap, "Manrope"))
    w2 = pdfmetrics.stringWidth(SIGN_OPEN[1], "Manrope-700", B.font_for(acap, "Manrope"))
    gap = IW * 0.055
    tw = w1 + gap + w2
    cy = y_open + h_open / 2
    tgap = cap_e * 0.10
    x0 = w / 2 - tw / 2
    B.caps(c, x0, cy - acap / 2, SIGN_OPEN[0], acap, pal["open"], "Manrope-700", tgap)
    B.caps(c, x0 + w1 + gap, cy - acap / 2, SIGN_OPEN[1], acap, pal["open"],
           "Manrope-700", tgap)
    arm = h_open * 0.052                  # shaft thickness
    ahl = IW * 0.052                      # head length
    ahh = h_open * 0.150                  # head height
    _arrow(c, mxx + IW * 0.008, cy, al, arm, ahl, ahh, pal["open"], direction=-1)
    _arrow(c, mxx + IW - IW * 0.008 - al, cy, al, arm, ahl, ahh, pal["open"],
           direction=+1)

    # ---- foot strip: numbers left, branch right
    if tel:
        c.setFillColor(pal["band"])
        c.rect(mxx, y_foot, IW, h_foot, stroke=0, fill=1)
        cap_f = min(h_foot * 0.30, fit_cap("TEL " + SIGN_TEL, "Inter-600", "Inter",
                                           IW * 0.62))
        B.caps(c, mxx + IW * 0.014, y_foot + (h_foot - cap_f) / 2, f"TEL  {SIGN_TEL}",
               cap_f, pal["band_txt"], "Inter-600", cap_f * 0.06)
        B.caps(c, mxx + IW - IW * 0.014, y_foot + (h_foot - cap_f) / 2, SIGN_BRANCH,
               cap_f, pal["band_txt"], "Inter-600", cap_f * 0.12, align="right")


def face(c, w=W, h=H, variant=FACE, slogan=False, tel=True):
    """Draw the sign face at trim size, origin bottom-left, in millimetres."""
    M = 46.0
    pal = LIT.get(variant)
    c.setFillColor(pal["ground"] if pal else B.CP_NAVY)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    if pal:                                  # the lit faces
        bright_face(c, w, h, pal, slogan=slogan, tel=tel)
        return

    if variant == "A":                       # centred, typographic
        k = lockscale(w, h, M)
        ms, cap_b, cap_s = 112.0 * k, 26.0 * k, 22.0 * k
        gap_e, gap_badge = 24.0 * k, 20.0 * k
        gap_bm, gap_rule = 16.0 * k, 44.0 * k
        cap_m = _ref()["cap_m"] * k
        cap_e = cap_m * ED_RATIO
        block = cap_e + gap_e + ms + gap_badge + cap_b + gap_bm + cap_m
        # the rule and motto hang below the name: carry them in the centring, or
        # the panel reads top-heavy with the motto crowding the bottom edge
        tail = (gap_rule + 5.0 * k + 22.0 * k + cap_s) if slogan else 0.0
        top = h / 2 + (block + tail) / 2

        # EDDWALIRO heads the panel, above the badge
        B.caps(c, w / 2, top - cap_e, WORD, cap_e, B.CP_CYAN, "Manrope-800",
               ED_TRACK, align="center", max_w=w - 2 * M)

        badge_y = top - cap_e - gap_e - ms
        B.monogram(c, (w - ms) / 2, badge_y, ms, dark=B.WHITE, accent=B.CP_CYAN)

        B.caps(c, w / 2, badge_y - gap_badge - cap_b, "BCM", cap_b, B.CP_CYAN,
               "Inter-600", 26.0, align="center")
        y_m = top - block
        B.caps(c, w / 2, y_m, NAME, cap_m, B.WHITE, "Manrope-800", 1.6,
               align="center")

        ry = y_m - gap_rule
        c.setFillColor(B.CP_CYAN)
        c.rect(w / 2 - 130 * k, ry, 260 * k, 5.0 * k, stroke=0, fill=1)
        if slogan:
            B.label(c, w / 2, ry - 44.0 * k, B.SLOGAN, cap_s, B.CP_MIST,
                    "Inter-400", 3.4, align="center")
        if tel:
            B.label(c, w / 2, 56.0, f"TEL {B.TEL}", 16.0, B.CP_CYAN,
                    "Inter-600", 2.2, align="center")

    elif variant == "B":                     # B: badge-left lockup
        k = lockscale(w, h, M)
        ms, cap_b, cap_s = 112.0 * k, 26.0 * k, 22.0 * k
        gap_e, gap_bm, gap_badge = 24.0 * k, 16.0 * k, 30.0 * k
        gap_rule, gap_sl = 34.0 * k, 30.0 * k
        meas = w - 2 * M - ms - gap_badge
        cap_m = min(fit_cap(NAME, "Manrope-800", "Manrope", meas),
                    _ref()["cap_m"] * k)
        cap_e = cap_m * ED_RATIO
        name_w = pdfmetrics.stringWidth(NAME, "Manrope-800", B.font_for(cap_m))
        word_w = (pdfmetrics.stringWidth(WORD, "Manrope-800", B.font_for(cap_e))
                  + ED_TRACK * (len(WORD) - 1))
        block_w = max(ms + gap_badge + name_w, word_w)
        lower_h = max(ms, cap_b + gap_bm + cap_m)
        block_h = cap_e + gap_e + lower_h + (
            (gap_rule + 5.0 * k + gap_sl + cap_s) if slogan else 0)
        top = h / 2 + block_h / 2
        x0 = (w - block_w) / 2

        # EDDWALIRO heads the panel, above the badge
        B.caps(c, x0, top - cap_e, WORD, cap_e, B.CP_CYAN, "Manrope-800",
               ED_TRACK, max_w=block_w)

        top_lower = top - cap_e - gap_e
        B.monogram(c, x0, top_lower - (lower_h + ms) / 2, ms, dark=B.WHITE,
                   accent=B.CP_CYAN)

        tx = x0 + ms + gap_badge
        ty = top_lower - (lower_h - (cap_b + gap_bm + cap_m)) / 2
        B.caps(c, tx, ty - cap_b, "BCM", cap_b, B.CP_CYAN, "Inter-600", 18.0)
        y_m = ty - cap_b - gap_bm - cap_m
        B.caps(c, tx - 1.2, y_m, NAME, cap_m, B.WHITE, "Manrope-800", 1.2)
        name_w = pdfmetrics.stringWidth(NAME, "Manrope-800", B.font_for(cap_m))
        if slogan:
            ry = y_m - gap_rule
            c.setFillColor(B.CP_CYAN)
            c.rect(tx, ry, name_w * 0.32, 5.0 * k, stroke=0, fill=1)
            B.label(c, tx - 0.6, ry - gap_sl - cap_s, B.SLOGAN, cap_s,
                    B.CP_MIST, "Inter-400", 3.2)
        if tel:
            B.label(c, w - M, 56.0, f"TEL {B.TEL}", 16.0, B.CP_CYAN,
                    "Inter-600", 2.2, align="right")

    elif variant == "C":                     # fascia: badge left, name filling the length
        # A 4:1 panel cannot carry the stacked lockup at any useful size — the
        # height caps the name at about 40 % of the length. This lockup turns the
        # block on its side: the badge and BCM stand at the left, EDDWALIRO,
        # MEDICAL CENTRE and the motto run beside them, so the name can take most
        # of the length. Every element of the approved lockup is still present.
        m = H * 0.075
        ms = H * 0.375
        gap = H * 0.10
        cap_e = H * 0.105
        cap_b = H * 0.050
        gap_rule = H * 0.055
        cap_s = H * 0.062

        tx = m + ms + gap
        avail = w - tx - m * 1.7
        cap_m = min(fit_cap(NAME, "Manrope-800", "Manrope", avail), H * 0.30)

        # stack: EDDWALIRO / name / rule / motto, centred on the panel's axis
        blk = cap_e + H * 0.05 + cap_m + gap_rule + 5.0 + H * 0.045 + cap_s
        top = h / 2 + blk / 2

        B.caps(c, tx, top - cap_e, WORD, cap_e, B.CP_CYAN, "Manrope-800",
               ED_TRACK * 0.55, max_w=avail)
        y_m = top - cap_e - H * 0.05 - cap_m
        B.caps(c, tx, y_m, NAME, cap_m, B.WHITE, "Manrope-800", 1.4, max_w=avail)

        ry = y_m - gap_rule
        c.setFillColor(B.CP_CYAN)
        c.rect(tx, ry, avail * 0.30, 5.0, stroke=0, fill=1)
        if slogan:
            B.label(c, tx + 1.2, ry - H * 0.045 - cap_s, B.SLOGAN, cap_s,
                    B.CP_MIST, "Inter-400", 3.2, max_w=avail)

        # badge, with BCM beneath it, the pair centred on the panel's axis
        gap_bc = H * 0.05
        blk_h = ms + gap_bc + cap_b
        by = h / 2 + blk_h / 2 - ms
        B.monogram(c, m, by, ms, dark=B.WHITE, accent=B.CP_CYAN)
        B.caps(c, m + ms / 2, by - gap_bc - cap_b, "BCM", cap_b, B.CP_CYAN,
               "Inter-600", 14.0, align="center")
        if tel:
            B.label(c, w - m, m, f"TEL {B.TEL}", 16.0, B.CP_CYAN,
                    "Inter-600", 2.2, align="right")

    # engraved keyline, so the panel reads as a made object, not a painted wall
    c.saveState()
    c.setStrokeColor(B.WHITE)
    c.setStrokeAlpha(0.14)
    c.setLineWidth(1.2)
    inset = min(30.0, h * 0.05)
    c.rect(inset, inset, w - inset * 2, h - inset * 2, stroke=1, fill=0)
    c.restoreState()


# --------------------------------------------------------------------- artwork
def artwork(path, variant=FACE, faces=("FACE A", "FACE B"), tel=True):
    pw, ph = W + BLEED * 2, H + BLEED * 2 + SLUG
    c = canvas.Canvas(path, pagesize=(pw * MM, ph * MM))
    c.setTitle(f"BCM Medical Centre — sign post panel {W:.0f} x {H:.0f} mm ({variant})")
    c.setAuthor("BCM Medical Centre — sign post project")
    for label in faces:
        c.setFillColor(B.CP_NAVY)
        c.rect(0, 0, pw, ph, stroke=0, fill=1)
        c.saveState()
        c.translate(BLEED, BLEED + SLUG)
        c.scale(MM, MM)
        face(c, variant=variant, tel=tel)
        c.restoreState()

        c.saveState()
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.3)
        x0, y0 = BLEED * MM, (BLEED + SLUG) * MM
        x1, y1 = (BLEED + W) * MM, (BLEED + SLUG + H) * MM
        L = 9 * MM
        for (x, y) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
            c.line(x - L, y, x - 3 * MM, y)
            c.line(x + 3 * MM, y, x + L, y)
            c.line(x, y - L, x, y - 3 * MM)
            c.line(x, y + 3 * MM, x, y + L)
        c.restoreState()

        c.setFillColor(B.WHITE)
        c.rect(0, 0, pw, SLUG, stroke=0, fill=1)
        c.setStrokeColorRGB(0.6, 0.6, 0.6)
        c.setLineWidth(0.2)
        c.line(0, SLUG, pw, SLUG)
        B.caps(c, 3, SLUG - 6.6,
               f"BCM SIGN POST PANEL  |  {label}  |  {VARIANT_NAME.get(variant, variant)}  |  "
               f"TRIM {W_IN:.0f} x {H_IN:.0f} IN  =  {W:.1f} x {H:.1f} mm  |  "
               f"PAGE {W + 2 * BLEED:.1f} x {H + 2 * BLEED + SLUG:.1f} mm (BLEED + SLUG)",
               2.7, B.CP_NAVY, "Inter-600", 0.3)
        B.caps(c, 3, SLUG - 11.2,
               f"BLEED {BLEED:.0f} mm  |  SAFE {SAFE:.0f} mm  |  {REV}  |  "
               "DOUBLE-SIDED — BOTH FACES IDENTICAL",
               2.3, B.CP_NAVY, "Inter-500", 0.25)
        B.caps(c, 3, SLUG - 15.4,
               ("FOR A LIT BOX — BACKLIT MEDIA, EVEN LIGHT FIELD. NAME + OPEN 24 HOURS + "
                "THE TWO PREMISES NUMBERS. NO MONOGRAM: BCM STANDS IN ITS PLACE."
                if variant in LIT else
                "NAME ONLY — EDDWALIRO / MEDICAL CENTRE, NO SERVICE LIST, NO PHOTOGRAPH. "
                "MONOGRAM IS A RECREATION: REPLACE WITH CLIENT VECTOR LOGO BEFORE PLOT."),
               2.1, B.CP_NAVY_MD, "Inter-500", 0.2)
        B.caps(c, pw - 3, 3.2, "CROP MARKS — TRIM AT THE MARKS", 2.2, B.CP_GREY,
               "Inter-500", 0.4, "right")
        c.showPage()
    c.save()
    return path



def artwork_exact(path, variant=FACE, faces=("FACE A", "FACE B"), tel=True):
    """The face at exactly the client's size: page = trim, 46 x 22 in.

    The print file carries bleed and a slug, so its page is deliberately larger than
    the panel. This one is for anyone who measures the file or drops it straight into
    the box's own template: 1168.4 x 558.8 mm, to the millimetre.
    """
    c = canvas.Canvas(path, pagesize=(W * MM, H * MM))
    c.setTitle(f"BCM Medical Centre — sign face {W_IN:.0f} x {H_IN:.0f} in "
               f"({W:.1f} x {H:.1f} mm)")
    c.setAuthor("BCM Medical Centre — sign post project")
    for _ in faces:
        c.saveState()
        c.scale(MM, MM)
        face(c, variant=variant, tel=tel)
        c.restoreState()
        c.showPage()
    c.save()
    return path


def face_pdf(path, variant=FACE, tel=True):
    """Trim-only face, for mockups and previews."""
    c = canvas.Canvas(path, pagesize=(W * MM, H * MM))
    c.scale(MM, MM)
    face(c, variant=variant, tel=tel)
    c.showPage()
    c.save()
    return path


# --------------------------------------------------------------------- mockups
def _panel_png(variant=FACE, px_w=1200, tel=True):
    import pypdfium2 as pdfium
    os.makedirs(WORK, exist_ok=True)
    pdf = os.path.join(WORK, f"sign_{variant}{'_tel' if tel else ''}.pdf")
    face_pdf(pdf, variant, tel)
    doc = pdfium.PdfDocument(pdf)
    page = doc[0]
    img = page.render(scale=px_w / page.get_size()[0]).to_pil().convert("RGB")
    doc.close()
    return img


def post_count():
    """Posts under the panel: two up to about 1.8 m, then one per 1.5 m."""
    return max(2, min(6, int(round(W / 1500.0)) + 1))


POST_WORD = {2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE", 6: "SIX"}
POST_LC = {2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six"}


def mockup(night=False, variant=FACE, tel=True):
    """Elevation: the panel on its posts, to scale, day and night variants."""
    S = 0.95
    panel = _panel_png(variant, tel=tel)
    GROUND = 170.0                       # ground band drawn at the foot
    PANEL_CENTRE = 1500.0                # panel centre above finished ground level
    TOP_MARGIN = 170.0
    above = PANEL_CENTRE + H / 2 + TOP_MARGIN
    width_mm = max(W + 900.0, 2000.0)
    w, h = int(width_mm * S), int((above + GROUND) * S)

    base = np.array([0.93, 0.91, 0.86]) if not night else np.array([0.10, 0.12, 0.18])
    g = np.linspace(1.0, 0.88, h).reshape(h, 1, 1) if not night else \
        np.linspace(0.6, 1.0, h).reshape(h, 1, 1)
    arr = np.repeat(np.clip(g * base.reshape(1, 1, 3), 0, 1), w, axis=1)
    img = Image.fromarray((arr * 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")

    floor = h - int(GROUND * S)
    d.rectangle([0, floor, w, h],
                fill=(146, 142, 136) if not night else (26, 28, 34))
    d.rectangle([0, floor, w, floor + int(4 * S)], fill=(120, 116, 110))

    cx = w // 2
    post_w = 90.0
    panel_top_mm = PANEL_CENTRE + H / 2
    top_y = floor - int(panel_top_mm * S)
    # posts are spaced along the length, so a long panel cannot sag between two
    n = post_count()
    span = W / 2 - 420.0
    posts = ([0.0] if n == 1 else
             [-span + 2 * span * i / (n - 1) for i in range(n)])
    for sx in posts:
        x = cx + int(sx * S)
        col = (86, 92, 100) if not night else (52, 58, 68)
        d.rectangle([x - int(post_w / 2 * S), top_y, x + int(post_w / 2 * S), floor],
                    fill=col)
        d.rectangle([x - int(post_w / 2 * S), top_y, x + int(post_w / 2 * S),
                     top_y + int(6 * S)],
                    fill=(150, 156, 164) if not night else (78, 86, 98))

    panel_img = panel.resize((int(W * S), int(H * S)), Image.LANCZOS)
    glow = None
    if night:
        # lit from behind: the face lifts and blooms a little onto its own frame
        a = np.asarray(panel_img).astype(np.float32) * 1.10 + 22
        panel_img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        gw, gh = int(panel_img.width * 1.16), int(panel_img.height * 1.60)
        glow = Image.new("RGBA", (gw, gh), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for i in range(60, 0, -1):
            a_ = max(1, int(16 * (i / 60.0) ** 2))
            pad_x = int((gw - panel_img.width) * i / 120.0)
            pad_y = int((gh - panel_img.height) * i / 120.0)
            gd.rounded_rectangle([pad_x, pad_y, gw - pad_x, gh - pad_y],
                                 radius=min(pad_x, pad_y) + 6,
                                 fill=(150, 225, 255, a_))
        from PIL import ImageFilter
        glow = glow.filter(ImageFilter.GaussianBlur(26))
    x0 = cx - panel_img.width // 2
    if glow is not None:
        img.paste(glow, (x0 - (glow.width - panel_img.width) // 2,
                         top_y - (glow.height - panel_img.height) // 2), glow)
    img.paste(panel_img, (x0, top_y))
    d.rectangle([x0 - 2, top_y - 2, x0 + panel_img.width + 1,
                 top_y + panel_img.height + 1], outline=(30, 34, 42), width=3)
    d.ellipse([x0 + 20, floor - int(8 * S), x0 + panel_img.width - 20,
               floor + int(16 * S)],
              fill=(0, 0, 0, 40) if not night else (0, 0, 0, 90))
    return img


def dimensioned(variant=FACE):
    """Scale drawing of the panel with its measurements called out, in mm and ft."""
    from PIL import ImageFont

    # a 5 m panel is 4:1, so the drawing is set by its length, not its height
    S = min(1800.0 / W, 1100.0 / H)
    pw, ph = int(W * S), int(H * S)
    pad_l, pad_r, pad_t, pad_b = 150, 40, 56, 152
    w, h = pad_l + pw + pad_r, pad_t + ph + pad_b
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    panel = _panel_png(variant, px_w=max(2400, pw)).resize((pw, ph), Image.LANCZOS)
    x0, y0 = pad_l, pad_t
    img.paste(panel, (x0, y0))
    d.rectangle([x0, y0, x0 + panel.width - 1, y0 + panel.height - 1],
                outline=(22, 35, 63), width=2)

    navy, cyan = (22, 35, 63), (43, 169, 224)
    f_big = ImageFont.truetype(os.path.join(HERE, "fonts", "Inter-600.ttf"), 30)
    f_sm = ImageFont.truetype(os.path.join(HERE, "fonts", "Inter-500.ttf"), 19)

    def centred(cx, y, text, font, fill):
        tw = d.textbbox((0, 0), text, font=font)[2]
        d.text((cx - tw / 2, y), text, font=font, fill=fill)

    # width, under the panel
    yy = y0 + panel.height + 46
    d.line([x0, yy, x0 + panel.width, yy], fill=cyan, width=2)
    for x in (x0, x0 + panel.width):
        d.line([x, yy - 14, x, yy + 14], fill=cyan, width=2)
    centred(x0 + panel.width / 2, yy + 16,
            f"{W:.1f} MM   ·   {ftin(W_IN)}", f_big, navy)

    # height, to the left of the panel
    xx = x0 - 58
    d.line([xx, y0, xx, y0 + panel.height], fill=cyan, width=2)
    for y in (y0, y0 + panel.height):
        d.line([xx - 14, y, xx + 14, y], fill=cyan, width=2)
    label = f"{H:.1f} MM   ·   {ftin(H_IN)}"
    tw = d.textbbox((0, 0), label, font=f_big)[2]
    tmp = Image.new("RGBA", (tw + 8, 40), (255, 255, 255, 0))
    ImageDraw.Draw(tmp).text((0, 0), label, font=f_big, fill=navy)
    tmp = tmp.rotate(90, expand=True)
    img.paste(tmp, (int(xx - 46), int(y0 + panel.height / 2 - tmp.height / 2)), tmp)

    # the two facts that matter at the signwriter's bench
    foot = (f"TRIM  {W:.1f} × {H:.1f} MM   ·   {FT_TXT}   ·   LANDSCAPE, DOUBLE-SIDED"
            "   ·   LIT FACE")
    fw = d.textbbox((0, 0), foot, font=f_sm)[2]
    d.text((max(8, x0 + panel.width / 2 - fw / 2), y0 + panel.height + 108), foot,
           font=f_sm, fill=(100, 110, 128))
    return img


# ----------------------------------------------------------------------- proof
def proof(path):
    c = D.new_doc(path, "BCM Medical Centre — sign post panel",
                  subject=f"Name-only sign post panel {FT_TXT}")
    eyebrow = "BCM  ·  MEDICAL CENTRE  ·  SIGN POST PANEL"

    # ---- page 1 — the panel, to scale, measured
    D.page_bg(c, "SIGN POST PANEL", f"{REV}", 1, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "The name, on a post", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "One panel: the name, and the two facts a passer-by needs — open all "
               "night, and the numbers to ring. No service list, no photograph. Trim "
               f"{W:.0f} × {H:.0f} mm, the client's {FT_TXT}, double-sided, for a lighting "
               "board. BCM sits at the head, MEDICAL CENTRE on its navy band, and "
               "EDDWALIRO across the full measure below — the name at the largest size the "
               "panel will take.",
               (D.PW - 2 * D.M) / MM * 0.56, 3.3, B.NAVY_MID)

    # fit the panel to the measure, whichever of width or height binds
    measure = (D.PW - 2 * D.M) / MM
    band, top = 88.0, 150.0
    scale = min(measure / W, band / H)          # mm of panel per mm of trim
    pw, ph = W * scale, H * scale
    px = D.M + (measure - pw) / 2.0
    py = (top - ph) * MM
    c.saveState()
    c.translate(px, py)
    c.scale(scale * MM, scale * MM)
    face(c)
    c.restoreState()
    c.setStrokeColor(B.TEAL)
    c.setLineWidth(0.4)
    c.rect(px, py, pw * MM, ph * MM, stroke=1, fill=0)
    B.label(c, px + pw * MM / 2, py - 6.5 * MM,
            f"LONG  {ftin(W_IN)}  /  {W:.1f} mm", 3.4, B.NAVY, "Inter-600", 1.0, "center")
    B.label(c, px, py + ph * MM + 3.5 * MM,
            f"HIGH  {ftin(H_IN)}  /  {H:.1f} mm", 3.4, B.NAVY, "Inter-600", 1.0)

    yy = 44 * MM
    B.label(c, D.M, yy, "MEASUREMENTS", 4.0, B.TEAL, "Inter-600", 1.6)
    col = (D.PW - 2 * D.M) / 2 - 8 * MM
    D.bullets(c, D.M, yy - 6 * MM, [
        f"Trim: {MM_TXT} — {FT_TXT}, i.e. {W_IN:.0f} × {H_IN:.0f} in (25.4 mm to the inch).",
        f"Bleed: {BLEED:.0f} mm all round, so the printed sheet is "
        f"{W + 2 * BLEED:.0f} × {H + 2 * BLEED:.0f} mm. Safe area {SAFE:.0f} mm in from trim.",
    ], col, 3.0, B.NAVY_MID)
    D.bullets(c, D.M + col + 16 * MM, yy - 6 * MM, [
        "Artwork is supplied at 1 : 1 in millimetres — plot it, do not scale it.",
        "Both faces are in the one PDF: print the file twice for a two-sided panel, or "
        "once per face for two single-sided panels back to back.",
    ], col, 3.0, B.NAVY_MID)

    # ---- page 2 — the lit faces
    c.showPage()
    D.page_bg(c, "OPTIONS", f"{REV}", 2, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "Built to the sign you already have", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "The clinic's own lit box is on the road already, so the new face keeps that "
           "arrangement rather than inventing one: BCM on a white band, MEDICAL CENTRE in navy "
           "on a navy band, EDDWALIRO knocked out of a "
           "full-width red block, OPEN 24 HRS between two arrows, and a navy foot strip with "
           "the numbers. Only what has to changes — the numbers are the client's current "
           "ones, and the motto is off. The navy sits in two thin bands with white either "
           "side, so the box still lights evenly.",
           (D.PW - 2 * D.M) / MM * 0.90, 3.2, B.NAVY_MID)

    sw = 82.0                                   # three across the measure
    sc = sw / W
    ph_mm = H * sc
    for i, (v, cap_txt) in enumerate((
            ("R", "THE CLINIC'S SIGN  ·  IN THE PRINT FILES"),
            ("L", "CYAN FIELD  ·  SPARE"),
            ("A", "THE OLD NAVY FACE  ·  NOT FOR THE BOX"))):
        px = D.M + i * 88 * MM              # D.M is in points; add mm here
        py = 104 * MM
        c.saveState()
        c.translate(px, py)
        c.scale(sc * MM, sc * MM)
        face(c, variant=v)
        c.restoreState()
        c.setStrokeColor(B.TEAL)
        c.setLineWidth(0.4)
        c.rect(px, py, sw * MM, ph_mm * MM, stroke=1, fill=0)
        B.label(c, px, py - 6 * MM, cap_txt, 2.9, B.GREY, "Inter-600", 1.0)

    B.label(c, D.M, 90 * MM, "WHAT CHANGED", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, 83 * MM, [
        "The arrangement is the one already standing at the roadside: brand band, "
        "MEDICAL CENTRE on its navy band, the red EDDWALIRO block, OPEN 24 HRS, foot "
        "strip. People "
        "on this road already read that sign, so the new face does not make them learn it "
        "again.",
        "EDDWALIRO is set across 94 % of the panel — the whole measure — and knocked out of "
        "the red block in white, so it is the loudest thing on the face, lit or not.",
        "Red #ED1B24 carries the colour: the block behind the name and the OPEN 24 HRS row. "
        "Everything else is the clinic's navy and white, so nothing competes with the name.",
        "The motto is off this face, as asked. The OPEN 24 HRS row takes the room it used.",
        "The foot strip carries the numbers — 0788 323 815 · 0754 132 715 — with BUSSABALA "
        "at the right.",
        "Nothing here is invented: the brand line, the community name, the branch, the "
        "arrows and the foot strip are all read off the client's own sign photograph.",
    ], 200 * MM, 3.0, B.NAVY_MID)

    B.label(c, D.M, 46 * MM, "IF THE RED IS TOO LOUD", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, 39 * MM, [
        "Say so and I will pull the red back to the clinic's cyan #2BA9E0 at the same size — "
        "the layout does not care which colour it is set in.",
    ], 200 * MM, 3.0, B.NAVY_MID)

    # ---- page 3 — on the post
    c.showPage()
    D.page_bg(c, "ON THE POST", f"{REV}", 3, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "How it sits at the entrance", 8.0)
    posts = post_count()
    D.para(c, D.M, y + 2 * MM,
           f"{W/1000:.2f} m of panel, {(W*H)/1e6:.2f} m² of face: panel centre 1500 mm "
           f"above finished ground level and {posts} posts under it are a proposal — the "
           "post centres and the frame must come from the signwriter who builds it.",
           (D.PW - 2 * D.M) / MM, 3.2, B.NAVY_MID)
    avail = (D.PW - 2 * D.M) / MM
    # the elevation carries a lot of sky; trim it so the sign fills the picture
    CROP = 0.05
    box_h, items = 72.0, []
    for night in (False, True):
        png = os.path.join(WORK, f"sign_mock_{'night' if night else 'day'}.png")
        if not os.path.exists(png):
            continue
        im = Image.open(png)
        im = im.crop((0, int(im.height * CROP), im.width, im.height))
        cut = os.path.join(WORK, f"proof_mock_{'night' if night else 'day'}.png")
        im.save(cut)
        items.append((cut, night, box_h * im.width / im.height))
    total = sum(i[2] for i in items) + 6 * max(len(items) - 1, 0)
    x_at = D.M + (avail - total) / 2
    for cut, night, box_w in items:
        x = x_at * MM
        x_at += box_w + 6
        py = (150 - box_h) * MM
        c.drawImage(cut, x, py, box_w * MM, box_h * MM, mask=None)
        c.setStrokeColor(B.GREY)
        c.setLineWidth(0.2)
        c.rect(x, py, box_w * MM, box_h * MM, stroke=1, fill=0)
        B.label(c, x, py - 5.5 * MM,
                "DAY — MATTE FACE, STREET LIGHT" if not night else
                "NIGHT — IF THE PANEL IS LIT", 3.0, B.GREY, "Inter-600", 1.2)

    B.label(c, D.M, 62 * MM,
            "DRAWN TO SCALE  ·  PANEL CENTRE 1500 MM ABOVE FINISHED GROUND LEVEL  ·  "
            f"{POST_WORD[post_count()]} POSTS SHOWN AS A PROPOSAL", 2.8, B.GREY,
            "Inter-500", 1.0)
    D.bullets(c, D.M, 54 * MM, [
        f"The face is {(W*H)/1e6:.2f} m² of panel, {W:.0f} mm long. The name is set to "
        "read from the road, so it stays legible well past the gate.",
        f"{POST_LC[post_count()]} posts carry it at 520 mm centres, or the whole panel sits "
        "in the lighting board's own carcass — the box carries it.",
        "A lit face is read from further off at night than an unlit one by day, so the name "
        "is set as large as the panel takes.",
    ], 150 * MM, 3.0, B.NAVY_MID)

    # ---- page 4 — specification
    c.showPage()
    D.page_bg(c, "SPECIFICATION", f"{REV}", 4, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "Production specification", 8.0)
    B.label(c, D.M, y - 2 * MM, "SUBSTRATE  —  CONFIRM WITH THE SIGNWRITER", 4.0,
            B.TEAL, "Inter-600", 1.6)
    area = W * H / 1e6
    big = area > 3.0
    sub = [
        "The face is going into a lighting board, so it must be printed on a diffusing, "
        "backlit-grade material — translucent white acrylic or a backlit film for the box's "
        "own face, or backlit banner media if the box takes a soft face. Not vinyl on "
        "opaque composite: that blocks the light.",
        f"The face is {area:.2f} m². The artwork is supplied at 1 : 1 in millimetres, so it "
        "can go straight onto the box's print or be plotted as a spare.",
        "Double-sided: the artwork is identical on both faces, so the same file prints twice.",
        "Print the white field and the navy bands as flat, even coats — no gradient, no "
        "vignette. Banding in a large flat field shows up far more when it is lit from "
        "behind, and navy is the field most likely to show it.",
        "Red is the colour to watch: #ED1B24 bleeds slightly into white when it is lit from "
        "behind, so the letter edges soften and the red can warm towards orange. Hold it as "
        "a flat spot colour if the process allows, and check a lit sample before the run.",
    ]
    D.bullets(c, D.M, y - 10 * MM, sub, 172 * MM, 3.0, B.NAVY_MID)

    B.label(c, D.M, 130 * MM, "FIXING  —  CONFIRM WITH THE INSTALLER", 4.0, B.TEAL,
            "Inter-600", 1.6)
    n = post_count()
    fix = [f"Illumination: internally lit box, face lit from behind. Panel centre 1500 mm "
           "above finished ground level is a proposal — confirm it against the box and the "
           "kerb line, and check that the box takes this face size before it is ordered.",
           "The face fits the box's aperture, not its outer frame: trim is "
           f"{W:.0f} × {H:.0f} mm, so the visible opening should be that size or the artwork "
           "will be cropped by the rebate.",
           "One rule for a lit face: the light must be even across the whole panel. That is "
           "why the bands are thin, the gaps between them are white, and no band is set in a "
           "dense tint.",
           f"If it is also to stand on posts rather than in the box, {POST_LC[n].lower()} "
           "galvanised posts at 520 mm centres, 600 mm into concrete, is the "
           "industry-typical proposal. Not a quotation."]
    D.bullets(c, D.M, 122 * MM, fix, 172 * MM, 3.0, B.NAVY_MID)

    B.label(c, D.M, 92 * MM, "BEFORE PLOT", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, 84 * MM, [
        f"Measurement is the client's: {FT_TXT}. Check it against the panel the "
        "signwriter is actually making before the file is plotted.",
        ("The sheet is supplied at 1 : 1 in millimetres and is close to the largest page a "
         "PDF can hold — do not add margins to the file and do not scale it on the plotter."
         if W + 2 * BLEED > 4500 else
         "The sheet is supplied at 1 : 1 in millimetres — plot it, do not scale it on the "
         "plotter, and leave the crop marks outside the bleed."),
        "Confirm the fascia wording and the spelling of EDDWALIRO with the client before "
        "plot. The old navy face kept a recreated monogram; the lit faces carry BCM instead.",
        "Check the red against a printed sample lit from behind before the full run.",
    ], 172 * MM, 3.0, B.NAVY_MID)

    B.label(c, D.M, 52 * MM, "THE FILE", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, 44 * MM, [
        f"Trim {W:.1f} × {H:.1f} mm, bleed {BLEED:.0f} mm all round, so the page is "
        f"{W + 2 * BLEED:.1f} × {H + 2 * BLEED + SLUG:.1f} mm — 1 : 1, no scaling.",
        f"A {SLUG:.0f} mm slug runs along the foot with the file name, the trim and the "
        f"colour note — trim it off."
        + (f" At {W + 2 * BLEED:.0f} mm the page is close to the largest page a PDF can "
           "hold (5080 mm), so nothing may be added around it."
           if W + 2 * BLEED > 4500 else ""),
        f"Safe area {SAFE:.0f} mm inside trim. Crop marks at the four corners, outside the bleed.",
        "Colour: red #ED1B24 on white, nothing else. Supply as CMYK or let the printer "
        "convert — do not let the red drift towards orange.",
    ], 172 * MM, 3.0, B.NAVY_MID)

    c.save()
    return path


# ------------------------------------------------------------ to printer
def printer_pack():
    """Just the sign post, ready to send: one two-face PDF and a small zip.

    The sign is a separate deliverable from the door film, so a signwriter should
    not have to hunt through a 38-page print set to find it. These files hold the
    panel and nothing else.
    """
    import zipfile

    out = os.path.join(OUT_DIR, "print")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))

    tag = f"{W:.0f}x{H:.0f}"                      # 1168x559
    exact = os.path.join(out, f"BCM-Sign-Post-RED-EXACT-{W_IN:.0f}x{H_IN:.0f}in.pdf")
    both = os.path.join(out, f"BCM-Sign-Post-RED-BOTH-FACES-{tag}mm.pdf")
    face_a = os.path.join(out, f"BCM-Sign-Post-RED-FACE-A-{tag}mm.pdf")
    face_b = os.path.join(out, f"BCM-Sign-Post-RED-FACE-B-{tag}mm.pdf")
    spare = os.path.join(out, f"BCM-Sign-Post-SPARE-CYAN-FIELD-{tag}mm.pdf")

    artwork_exact(exact, faces=("FACE A", "FACE B"))
    artwork(both, faces=("FACE A", "FACE B"))
    artwork(face_a, faces=("FACE A",))
    artwork(face_b, faces=("FACE B",))
    artwork(spare, variant="L", faces=("FACE A",))

    note = os.path.join(out, "READ-ME-FIRST.txt")
    with open(note, "w") as fh:
        fh.write(
            "BCM MEDICAL CENTRE - SIGN POST PANEL, FOR A LIGHTING BOARD\n"
            "===========================================================\n\n"
            f"TRIM (finished size):  {W_IN:.0f} in x {H_IN:.0f} in\n"
            f"                       = {W:.1f} x {H:.1f} mm exactly (25.4 mm to the inch)\n"
            f"                       = {ftin(W_IN)} long x {ftin(H_IN)} high\n"
            "BLEED:                 10 mm all round (in the file)\n"
            "SLUG:                  22 mm at the foot (in the file, trim it off)\n"
            "SAFE AREA:             25 mm from trim\n"
            f"PAGE, PRINT FILE:      {W + 2 * BLEED:.1f} x {H + 2 * BLEED + SLUG:.1f} mm\n"
            "                       (trim + 10 mm bleed all round + 22 mm slug at the foot.\n"
            "                       The page is LARGER than the panel on purpose.)\n"
            f"PAGE, EXACT FILE:      {W:.1f} x {H:.1f} mm = {W_IN:.0f} x {H_IN:.0f} in,\n"
            "                       trim only, no bleed, no slug - this is the one that\n"
            "                       measures the panel size.\n"
            "CROP MARKS:            yes, at all four corners\n"
            "COLOUR:                navy #16233F bands, white type on them; red #ED1B24\n"
            "                       block with EDDWALIRO knocked out in white; red\n"
            "                       OPEN 24 HRS row. Nothing else.\n"
            "PLOT AT 100% - NEVER SCALE.\n\n"
            "THIS FACE IS FOR AN INTERNALLY LIT BOX\n"
            "The face is the arrangement of the sign already standing on the road, brought\n"
            "up to date: BCM on a white band, MEDICAL CENTRE in white on navy,\n"
            "EDDWALIRO knocked out of a full-width red block, OPEN 24 HRS between two arrows,\n"
            "and a navy foot strip with the numbers and BUSSABALA.\n"
            "The navy sits in thin bands with white either side, so the box lights evenly.\n"
            "Print on backlit-grade media: translucent diffusing acrylic or backlit film, or\n"
            "backlit banner media if the box takes a soft face. Vinyl on opaque composite\n"
            "blocks the light.\n\n"
            "RED IS THE ONE COLOUR TO WATCH IN A LIGHT BOX\n"
            "A red this bright will bleed slightly into the white when it is lit from\n"
            "behind - the letter edges soften and the red can warm towards orange. Two\n"
            "things fix it: keep the tube close behind the face and even, and ask the\n"
            "printer to hold the red as a flat spot colour rather than four-colour build\n"
            "if the process allows. Check a lit sample before the full run.\n\n"
            "FILES\n"
            f"  BCM-Sign-Post-RED-EXACT-{W_IN:.0f}x{H_IN:.0f}in.pdf          "
            f"{W_IN:.0f} x {H_IN:.0f} in page, trim only - measures the panel\n"
            f"  BCM-Sign-Post-RED-BOTH-FACES-{tag}mm.pdf      2 pages: face A, face B\n"
            f"  BCM-Sign-Post-RED-FACE-A-{tag}mm.pdf          face A on its own\n"
            f"  BCM-Sign-Post-RED-FACE-B-{tag}mm.pdf          face B on its own\n"
            f"  BCM-Sign-Post-SPARE-CYAN-FIELD-{tag}mm.pdf    the earlier cyan face, spare\n\n"
            "THE SETTING\n"
            "Top band, white: BCM, centred. Then the navy band, MEDICAL CENTRE in white.\n"
            "Then the red block, full width, with\n"
            "EDDWALIRO knocked out of it in white at the largest size the panel will take.\n"
            "Then the white row: an arrow at each end, Open and 24 Hrs between them in red.\n"
            "Then the navy foot strip: the numbers at the left, BUSSABALA at the right.\n"
            "There is NO MOTTO on this face - the client asked for it off.\n\n"
            "THE NUMBERS\n"
            "The sign carries 0788 323 815 and 0754 132 715 - the client's numbers for it.\n"
            "0788 323 815 is the newer line, already on door panes 1-18; the sign leads\n"
            "with it, and the three roadside banners were changed to the same line on\n"
            "2026-11-07, so fenceline and light box read as one set. Panes 19-24 still\n"
            "print 0771 240 104 with 0754 132 715 - say if they should change too.\n\n"
            "WHICH FILE TO USE\n"
            "For the box: send the EXACT file if the face is being made to the panel size,\n"
            "or the bleed file if the printer wants bleed and crop marks. They are the same\n"
            "artwork - only the page edge differs.\n\n"
            "ONE THING TO CHECK BEFORE THE RUN\n"
            "The face must fit the box's aperture, not its outer frame: the visible opening\n"
            "should be the trim size above, or the rebate will crop the lettering.\n\n"
            "STRUCTURE - CONFIRM WITH THE SIGNWRITER\n"
            f"The face is about {(W*H)/1e6:.2f} m2. Panel centre 1500 mm above finished ground\n"
            "is a proposal only. Nothing here is a quotation.\n")

    zpath = os.path.join(OUT_DIR, f"BCM-Sign-Post-Print-{tag}mm.zip")
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in sorted(os.listdir(out)):
            z.write(os.path.join(out, f), os.path.join("BCM-Sign-Post", f))
    return zpath, both


def main():
    os.makedirs(ART_DIR, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "lookbook"), exist_ok=True)

    a = artwork(os.path.join(ART_DIR, "BCM-Sign-Name-Only-Red.pdf"))
    c = artwork(os.path.join(ART_DIR, "BCM-Sign-Name-Only-Spare-Cyan.pdf"),
                variant="L", faces=("FACE A",))
    print("artwork:", os.path.basename(a), os.path.basename(c))

    for night, name in ((False, "M-01-sign-day.png"), (True, "M-02-sign-night.png")):
        img = mockup(night=night)
        img.save(os.path.join(OUT_DIR, "lookbook", name))
        img.save(os.path.join(WORK, f"sign_mock_{'night' if night else 'day'}.png"))
    dimensioned().save(os.path.join(OUT_DIR, "lookbook", "M-03-sign-dimensions.png"))
    print("mockups: day, night, dimensions")

    print("proof:", os.path.basename(
        proof(os.path.join(OUT_DIR, "BCM-Sign-Panel.pdf"))))

    zpath, both = printer_pack()
    print("printer pack:", os.path.basename(zpath),
          f"({os.path.getsize(zpath) / 1e6:.1f} MB)")

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BCM Medical Centre — sign post panel</title>
<style>
 body{{margin:0;background:#f4f7f9;color:#16233f;
   font:16px/1.6 Inter,Helvetica,Arial,sans-serif}}
 header{{background:#16233f;color:#fff;padding:48px 6vw 40px}}
 h1{{font-size:clamp(28px,4.6vw,50px);margin:.2em 0 .4em;line-height:1.03}}
 header p{{max-width:64ch;color:#cfd9e6}}
 .eyebrow{{letter-spacing:.3em;font-size:11px;color:#2ba9e0}}
 main{{padding:32px 6vw 72px}}
 figure{{margin:0 0 28px;background:#fff;border-radius:6px;overflow:hidden;
   box-shadow:0 2px 14px rgba(22,35,63,.08)}}
 figure img{{width:100%;display:block}}
 figcaption{{padding:12px 16px;font-size:12.5px;color:#4b5b73}}
 .two{{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}}
 table{{width:100%;border-collapse:collapse;font-size:14px;background:#fff}}
 th,td{{text-align:left;padding:10px 14px;border-bottom:1px solid #e3eaf2}}
 th{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#8fa2b8}}
 a{{color:#1b87b8}}
 .note{{color:#4b5b73;font-size:13px;max-width:80ch}}
 nav{{padding:0 6vw 8px;font-size:13px}}
 nav a{{margin-right:18px}}
</style></head><body>
<header>
  <div class="eyebrow">BCM · MEDICAL CENTRE · SIGN POST PANEL</div>
  <h1>Eddwaliro. Medical Centre.</h1>
  <p>{FT_TXT} — {W:.0f} × {H:.0f} mm, landscape, double-sided, for a lighting board.
     No service list, no photograph: the name, plus OPEN 24 HOURS and the two premises
     numbers in a strip at the foot. Built to the arrangement of the sign already on the
     road: BCM on a white band, MEDICAL CENTRE in white on navy, EDDWALIRO
     knocked out of a full-width red block, OPEN 24 HRS between two arrows, navy foot strip
     with the numbers and BUSSABALA. No motto.</p>
</header>
<nav><a href="../index.html">All artwork</a>
     <a href="../door-1/index.html">Door 1</a>
     <a href="../door-2/index.html">Door 2</a>
     <a href="../door-3/index.html">Door 3</a>
     <a href="../door-4/index.html">Door 4</a></nav>
<main>
  <figure><img src="lookbook/M-01-sign-day.png" alt="Sign post panel, day elevation">
    <figcaption>On the post — day. Panel centre 1500 mm above finished ground level,
      {POST_LC[post_count()]} posts carrying a {(W*H)/1e6:.2f} m² face, shown as a proposal.</figcaption></figure>
  <div class="two">
    <figure><img src="lookbook/M-03-sign-dimensions.png" alt="Dimensioned panel">
      <figcaption>Trim {W:.1f} × {H:.1f} mm.</figcaption></figure>
    <figure><img src="lookbook/M-02-sign-night.png" alt="Night elevation">
      <figcaption>Night — if the panel is lit.</figcaption></figure>
  </div>
  <table>
    <tr><th>File</th><th>What it is</th></tr>
    <tr><td><a href="artwork/BCM-Sign-Name-Only-Red.pdf">BCM-Sign-Name-Only-Red.pdf</a></td>
        <td>Print file — the lit face, both faces, 10 mm bleed, crop marks, 1 : 1 mm</td></tr>
    <tr><td><a href="artwork/BCM-Sign-Name-Only-Spare-Cyan.pdf">BCM-Sign-Name-Only-Spare-Cyan.pdf</a></td>
        <td>Print file — the same face on the cyan field, spare</td></tr>
    <tr><td><a href="print/BCM-Sign-Post-RED-EXACT-{W_IN:.0f}x{H_IN:.0f}in.pdf">BCM-Sign-Post-RED-EXACT-{W_IN:.0f}x{H_IN:.0f}in.pdf</a></td>
        <td><b>Exactly {W_IN:.0f} × {H_IN:.0f} in</b> — the page <i>is</i> the panel,
            {W:.1f} × {H:.1f} mm, no bleed, no slug. This is the file to send if the face is
            being made to the panel size, and the one whose size can be measured.</td></tr>
    <tr><td><a href="print/BCM-Sign-Post-RED-BOTH-FACES-{W:.0f}x{H:.0f}mm.pdf">BCM-Sign-Post-RED-BOTH-FACES-{W:.0f}x{H:.0f}mm.pdf</a></td>
        <td>The same artwork with 10 mm bleed and crop marks — page is deliberately larger
            ({(W + 2 * BLEED):.1f} × {(H + 2 * BLEED + SLUG):.1f} mm). For a printer who needs
            bleed.</td></tr>
    <tr><td><a href="BCM-Sign-Post-Print-{W:.0f}x{H:.0f}mm.zip">BCM-Sign-Post-Print-{W:.0f}x{H:.0f}mm.zip</a></td>
        <td>The sign post only, as a zip: the two-face file, each face on its own, the
            spare fascia setting, and the printer's note</td></tr>
    <tr><td><a href="BCM-Sign-Panel.pdf">BCM-Sign-Panel.pdf</a></td>
        <td>Four pages — panel to scale, options, on the post, specification</td></tr>
  </table>
  <p class="note">Monogram is a recreation, not BCM's official logo. Measurements are the
     client's: {ftin(W_IN)} × {ftin(H_IN)}. Substrate and fixings are industry-typical
     proposals for a {(W*H)/1e6:.2f} m² face — confirm with the signwriter.
     The sheet is 1 : 1 at {W:.1f} mm long: plot it at 100 %, never rescaled.</p>
</main></body></html>
"""
    open(os.path.join(OUT_DIR, "index.html"), "w").write(html)
    print("index.html")

    # the whole sign folder, so the hub and the master proof always link a
    # current archive rather than the one built at the old size
    import zipfile
    z = os.path.join(OUT_DIR, "BCM-Sign-Package.zip")
    if os.path.exists(z):
        os.remove(z)
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, _, files in os.walk(OUT_DIR):
            for f in sorted(files):
                full = os.path.join(root, f)
                if os.path.abspath(full) == os.path.abspath(z):
                    continue
                zf.write(full, os.path.relpath(full, OUT_DIR))
    print("package:", os.path.basename(z), f"({os.path.getsize(z) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
