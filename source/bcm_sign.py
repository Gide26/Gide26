"""BCM Medical Centre — name-only sign post panel.

Separate deliverable from the door film set: one panel, no services, no
photographs. Built to the client's measurement — 16 ft 7 in × 49 in, landscape.

Everything is drawn in millimetres on the trim rectangle; the artwork file adds
10 mm bleed, crop marks and a slug strip the same way the door panes do.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageDraw
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
    """199 in -> '16 ft 7 in'."""
    ft, inch = divmod(int(round(inches)), 12)
    return f"{ft} ft {inch} in" if inch else f"{ft} ft"


# --- the client's measurement, 2026-11-02: 16 ft 7 in long, 49 in high -------
W_IN, H_IN = 16 * 12 + 7, 49                         # 199 in long, 49 in high
W, H = round(W_IN * IN, 1), round(H_IN * IN, 1)      # 5054.6 × 1244.6 mm
W_FT, H_FT = W_IN / 12, H_IN / 12
FT_TXT = f"{ftin(W_IN)} × {ftin(H_IN)}"              # 16 ft 7 in × 4 ft 1 in
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


# The lockup was approved at 944.9 × 643.1 mm. A 16 ft 7 in panel is far wider
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


def face(c, w=W, h=H, variant="A", slogan=True, tel=False):
    """Draw the sign face at trim size, origin bottom-left, in millimetres."""
    M = 46.0
    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, w, h, stroke=0, fill=1)

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
def artwork(path, variant="A", faces=("FACE A", "FACE B"), tel=False):
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
               f"BCM SIGN POST PANEL  |  {label}  |  OPTION {variant}  |  "
               f"TRIM {W:.1f} x {H:.1f} mm  ({ftin(W_IN)} x {ftin(H_IN)})",
               2.7, B.CP_NAVY, "Inter-600", 0.3)
        B.caps(c, 3, SLUG - 11.2,
               f"BLEED {BLEED:.0f} mm  |  SAFE {SAFE:.0f} mm  |  {REV}  |  "
               "DOUBLE-SIDED — BOTH FACES IDENTICAL",
               2.3, B.CP_NAVY, "Inter-500", 0.25)
        B.caps(c, 3, SLUG - 15.4,
               "NAME ONLY — EDDWALIRO / MEDICAL CENTRE, NO SERVICE LIST, NO PHOTOGRAPH. "
               "MONOGRAM IS A RECREATION: REPLACE WITH CLIENT VECTOR LOGO BEFORE PLOT.",
               2.1, B.CP_NAVY_MD, "Inter-500", 0.2)
        B.caps(c, pw - 3, 3.2, "CROP MARKS — TRIM AT THE MARKS", 2.2, B.CP_GREY,
               "Inter-500", 0.4, "right")
        c.showPage()
    c.save()
    return path


def face_pdf(path, variant="A", tel=False):
    """Trim-only face, for mockups and previews."""
    c = canvas.Canvas(path, pagesize=(W * MM, H * MM))
    c.scale(MM, MM)
    face(c, variant=variant, tel=tel)
    c.showPage()
    c.save()
    return path


# --------------------------------------------------------------------- mockups
def _panel_png(variant="A", px_w=1200, tel=False):
    import pypdfium2 as pdfium
    os.makedirs(WORK, exist_ok=True)
    pdf = os.path.join(WORK, f"sign_{variant}{'_tel' if tel else ''}.pdf")
    face_pdf(pdf, variant, tel)
    doc = pdfium.PdfDocument(pdf)
    page = doc[0]
    img = page.render(scale=px_w / page.get_size()[0]).to_pil().convert("RGB")
    doc.close()
    return img


def mockup(night=False, variant="A", tel=False):
    """Elevation: the panel on its posts, to scale, day and night variants."""
    S = 0.95
    panel = _panel_png(variant, tel=tel)
    GROUND = 200.0                       # ground band drawn at the foot
    PANEL_CENTRE = 1500.0                # panel centre above finished ground level
    TOP_MARGIN = 260.0
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
    # posts are spaced along the length: a 5 m panel on two posts would sag
    n = max(2, min(6, int(round(W / 1500.0)) + 1))
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
    if night:
        a = np.asarray(panel_img).astype(np.float32) * 1.06 + 8
        panel_img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    x0 = cx - panel_img.width // 2
    img.paste(panel_img, (x0, top_y))
    d.rectangle([x0 - 2, top_y - 2, x0 + panel_img.width + 1,
                 top_y + panel_img.height + 1], outline=(30, 34, 42), width=3)
    d.ellipse([x0 + 20, floor - int(8 * S), x0 + panel_img.width - 20,
               floor + int(16 * S)],
              fill=(0, 0, 0, 40) if not night else (0, 0, 0, 90))
    return img


def dimensioned(variant="A"):
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
    foot = f"TRIM  {W:.1f} × {H:.1f} MM   ·   {FT_TXT}   ·   LANDSCAPE, DOUBLE-SIDED"
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
               "One panel, the name only — no service list, no photograph. Trim "
               f"{W:.0f} × {H:.0f} mm, the client's {FT_TXT}, double-sided. "
               "EDDWALIRO heads the panel above the badge: the road reads Luganda first, "
               "and the English name keeps the widest line.",
               (D.PW - 2 * D.M) / MM * 0.56, 3.3, B.NAVY_MID)

    # a 4:1 panel is set by the page width, so it runs the full measure
    scale = (D.PW - 2 * D.M) / MM / W           # mm of panel per mm of trim
    pw, ph = W * scale, H * scale
    px, py = D.M, 78 * MM
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

    yy = 62 * MM
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

    # ---- page 2 — options
    c.showPage()
    D.page_bg(c, "OPTIONS", f"{REV}", 2, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "Three ways to set the name", 8.0)
    D.para(c, D.M, y + 1.5 * MM,
           "A is the recommendation and it is what the print files carry. B repeats the "
           "badge-left lockup used on the door panes, for continuity. C is the fascia "
           "setting: at this length the stacked lockup fills only a little over a third "
           "of the panel, so C lets the name run the length at about four times the size.",
           (D.PW - 2 * D.M) / MM * 0.72, 3.1, B.NAVY_MID)

    sw = 128.0
    sc = sw / W
    ph_mm = H * sc
    top = 148.0
    pitch = ph_mm + 12.0
    for i, (v, cap_txt) in enumerate((
            ("A", "OPTION A — centred stack  ·  in the print files"),
            ("B", "OPTION B — badge-left, as on the door panes"),
            ("C", "OPTION C — fascia: the name across the length"))):
        px = D.M
        py = (top - i * pitch - ph_mm) * MM
        c.saveState()
        c.translate(px, py)
        c.scale(sc * MM, sc * MM)
        face(c, variant=v)
        c.restoreState()
        c.setStrokeColor(B.TEAL)
        c.setLineWidth(0.4)
        c.rect(px, py, sw * MM, ph_mm * MM, stroke=1, fill=0)
        B.label(c, px, py - 5.5 * MM, cap_txt, 3.2, B.GREY, "Inter-600", 1.2)

    B.label(c, D.M + (sw + 12) * MM, 96 * MM,
            "EDDWALIRO heads the panel, bold and in cyan:\nthe Luganda word is read first.",
            3.1, B.NAVY_MID, "Inter-400", 0.2)
    B.label(c, D.M + (sw + 12) * MM, 78 * MM,
            "BCM stays small and cyan beside the badge:\nthe initials, not the headline.",
            3.1, B.NAVY_MID, "Inter-400", 0.2)
    B.label(c, D.M + (sw + 12) * MM, 58 * MM,
            "The motto sits under the name and can be\ndropped for a name-only panel.",
            3.1, B.NAVY_MID, "Inter-400", 0.2)
    B.label(c, D.M + (sw + 12) * MM, 38 * MM,
            "The telephone can be added at the foot,\non both faces, on request.",
            3.1, B.NAVY_MID, "Inter-400", 0.2)

    # ---- page 3 — on the post
    c.showPage()
    D.page_bg(c, "ON THE POST", f"{REV}", 3, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "How it sits at the entrance", 8.0)
    D.para(c, D.M, y + 2 * MM,
           f"A {W/1000:.1f} m fascia is a structure, not a sticker: panel centre 1500 mm "
           "above finished ground level and four posts under it are a proposal — the post "
           "centres and the frame must come from the signwriter who builds it.",
           (D.PW - 2 * D.M) / MM, 3.2, B.NAVY_MID)
    avail = (D.PW - 2 * D.M) / MM
    box_w = (avail - 6) / 2
    for i, night in enumerate((False, True)):
        png = os.path.join(WORK, f"sign_mock_{'night' if night else 'day'}.png")
        if not os.path.exists(png):
            continue
        iw, ih = Image.open(png).size
        box_h = box_w * ih / iw
        x = (D.M + i * (box_w + 6) * MM)
        py = 96 * MM
        c.drawImage(png, x, py, box_w * MM, box_h * MM, mask=None)
        c.setStrokeColor(B.GREY)
        c.setLineWidth(0.2)
        c.rect(x, py, box_w * MM, box_h * MM, stroke=1, fill=0)
        B.label(c, x, py - 5.5 * MM,
                "DAY — MATTE FACE, STREET LIGHT" if not night else
                "NIGHT — IF THE PANEL IS LIT", 3.0, B.GREY, "Inter-600", 1.2)

    B.label(c, D.M, 84 * MM,
            "DRAWN TO SCALE  ·  PANEL CENTRE 1500 MM ABOVE FINISHED GROUND LEVEL  ·  "
            "FOUR POSTS SHOWN AS A PROPOSAL", 2.8, B.GREY, "Inter-500", 1.0)
    D.bullets(c, D.M, 76 * MM, [
        f"The face is {(W*H)/1e6:.2f} m² of panel. At that size the sign is read from "
        "well down the road, so the name is set to be legible from 100 m or more.",
        "Two posts would leave a 5 m span unsupported between them; the drawing shows four. "
        "A rail or cleat frame behind the panel is the alternative, and it keeps the face "
        "free of fixings.",
        "If the panel is to be read from one direction only, one face is enough — the "
        "artwork is the same on both.",
    ], 150 * MM, 3.0, B.NAVY_MID)

    # ---- page 4 — specification
    c.showPage()
    D.page_bg(c, "SPECIFICATION", f"{REV}", 4, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "Production specification", 8.0)
    B.label(c, D.M, y - 2 * MM, "SUBSTRATE  —  CONFIRM WITH THE SIGNWRITER", 4.0,
            B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, y - 10 * MM, [
        f"The face is {(W*H)/1e6:.2f} m². At this size 3 mm ACM on its own is marginal "
        "over a long span: propose 4 mm ACM, or 3 mm ACM on a rail frame. "
        "Industry-typical values, not a quotation — the signwriter decides.",
        "Direct-to-substrate UV print, or cast vinyl applied and laminated, on a matte "
        "white core. Edges cut back to trim and sealed.",
        "Double-sided: either two printed faces on one core, or two panels on a frame. "
        "The artwork is identical on both faces.",
        "Finish: matte anti-glare laminate. Gloss will mirror the sky and kill the "
        "contrast the navy depends on.",
        f"Allow for roughly {W*H/1e6*4.0:.0f} kg of 4 mm sheet before the frame — it is "
        "a two-person lift, not a one-person one.",
    ], 172 * MM, 3.0, B.NAVY_MID)

    B.label(c, D.M, 138 * MM, "FIXING  —  CONFIRM WITH THE INSTALLER", 4.0, B.TEAL,
            "Inter-600", 1.6)
    D.bullets(c, D.M, 130 * MM, [
        "Proposal: four galvanised posts under the panel, set into concrete footings, "
        "panel centre 1500 mm above finished ground level. A rail or cleat frame carrying "
        "the panel on four posts is the cleaner build at this length.",
        "Stainless fixings into a bracket or frame behind the panel, never through the "
        "printed face. Do not drill the face.",
        f"Wind loading: {(W*H)/1e6:.2f} m² is a real sail — the footing, the post gauge and "
        "the bracket need the signwriter's own calculation for the site.",
    ], 172 * MM, 3.0, B.NAVY_MID)

    B.label(c, D.M, 104 * MM, "BEFORE PLOT", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, 96 * MM, [
        f"Measurement is the client's: {FT_TXT}. Check it against the panel the "
        "signwriter is actually making before the file is plotted.",
        "The sheet is supplied at 1 : 1 in millimetres and is close to the largest page a "
        "PDF can hold — do not add margins to the file and do not scale it on the plotter.",
        "The monogram is a recreation, not BCM's official logo — swap the vector in.",
        "Confirm the fascia wording and the spelling of EDDWALIRO with the client before plot.",
    ], 172 * MM, 3.0, B.NAVY_MID)

    B.label(c, D.M, 70 * MM, "THE FILE", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, 62 * MM, [
        f"Trim {W:.1f} × {H:.1f} mm, bleed {BLEED:.0f} mm all round, so the page is "
        f"{W + 2 * BLEED:.1f} × {H + 2 * BLEED + SLUG:.1f} mm — 1 : 1, no scaling.",
        f"A {SLUG:.0f} mm slug runs along the foot with the file name, the trim and the "
        f"colour note — trim it off. At {W + 2 * BLEED:.0f} mm the page is close to the "
        "largest page a PDF can hold (5080 mm), so nothing may be added around it.",
        f"Safe area {SAFE:.0f} mm inside trim. Crop marks at the four corners, outside the bleed.",
        "Colour: navy #16233F, cyan #2BA9E0, mist #E8EEF4, white. Supply as CMYK or let the "
        "printer convert — do not colour-manage the navy towards black.",
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

    tag = f"{W:.0f}x{H:.0f}"                      # 5055x1245
    both = os.path.join(out, f"BCM-Sign-Post-BOTH-FACES-{tag}mm.pdf")
    face_a = os.path.join(out, f"BCM-Sign-Post-FACE-A-{tag}mm.pdf")
    face_b = os.path.join(out, f"BCM-Sign-Post-FACE-B-{tag}mm.pdf")
    opt_c = os.path.join(out, f"BCM-Sign-Post-OPTION-C-FASCIA-{tag}mm.pdf")

    artwork(both, variant="A", faces=("FACE A", "FACE B"))
    artwork(face_a, variant="A", faces=("FACE A",))
    artwork(face_b, variant="A", faces=("FACE B",))
    artwork(opt_c, variant="C", faces=("FACE A",))

    note = os.path.join(out, "READ-ME-FIRST.txt")
    with open(note, "w") as fh:
        fh.write(
            "BCM MEDICAL CENTRE - SIGN POST PANEL\n"
            "=====================================\n\n"
            f"TRIM (finished size):  {W:.1f} x {H:.1f} mm\n"
            f"                       = {ftin(W_IN)} long x {ftin(H_IN)} high\n"
            f"                       = {W_IN:.0f} in x {H_IN:.0f} in (25.4 mm to the inch)\n"
            "BLEED:                 10 mm all round (in the file)\n"
            "SLUG:                  22 mm at the foot (in the file, trim it off)\n"
            "SAFE AREA:             25 mm from trim\n"
            f"PRINT SIZE IN FILE:    {W + 20:.1f} x {H + 20 + 22:.1f} mm\n"
            "CROP MARKS:            yes, at all four corners\n"
            "COLOUR:                navy #16233F, cyan #2BA9E0, mist #E8EEF4, white\n"
            "PLOT AT 100% - NEVER SCALE. Do not colour-manage the navy towards black.\n\n"
            "THIS SHEET IS DELIBERATELY AT FULL SIZE\n"
            "A PDF page cannot exceed 5080 mm, and the sheet is 5074.6 mm wide. There is\n"
            "no room for a margin around the artwork, and the file must not be scaled up\n"
            "or down. If your plotter cannot take a 5.07 m sheet, ask for a seamed or\n"
            "half-size version rather than scaling this one - the letterforms are set for\n"
            "1:1 and a rescale changes the stroke weights.\n\n"
            "FILES\n"
            f"  BCM-Sign-Post-BOTH-FACES-{tag}mm.pdf         2 pages: face A, face B\n"
            f"  BCM-Sign-Post-FACE-A-{tag}mm.pdf             face A on its own\n"
            f"  BCM-Sign-Post-FACE-B-{tag}mm.pdf             face B on its own\n"
            f"  BCM-Sign-Post-OPTION-C-FASCIA-{tag}mm.pdf    fascia setting, one face, spare\n\n"
            "FACE A IS THE APPROVED SETTING (OPTION A)\n"
            "EDDWALIRO heads the panel, the badge sits under it, BCM above MEDICAL CENTRE,\n"
            "the motto at the foot. This is the arrangement approved on the earlier sample,\n"
            "kept at this length. It sits centred with wide navy margins either side -\n"
            "that is what the proportions do at 16 ft 7 in.\n\n"
            "OPTION C is the alternative: the same elements turned on their side, badge at\n"
            "the left, EDDWALIRO / MEDICAL CENTRE / motto run beside it. The name is about\n"
            "four times the size and fills the length. Use it only if the client asks -\n"
            "it is not the approved setting.\n\n"
            "STRUCTURE - CONFIRM WITH THE SIGNWRITER\n"
            "The face is about 6.29 m2. 3 mm ACM over this span is marginal: ask for 4 mm\n"
            "ACM or 3 mm ACM on a rail frame, four posts, or a cleat frame. Panel centre\n"
            "1500 mm above finished ground is a proposal only. Nothing here is a quotation.\n"
            "The monogram is a recreated mark, not the clinic's official logo.\n")
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

    a = artwork(os.path.join(ART_DIR, "BCM-Sign-Name-Only.pdf"), variant="A")
    c = artwork(os.path.join(ART_DIR, "BCM-Sign-Name-Only-Option-C-Fascia.pdf"),
                variant="C", faces=("FACE A",))
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
  <p>{FT_TXT} — {W:.0f} × {H:.0f} mm, landscape, double-sided. Name only:
     no service list, no photograph. EDDWALIRO, the Luganda word for hospital, heads
     the panel above the badge, bold and in cyan.</p>
</header>
<nav><a href="../index.html">All artwork</a>
     <a href="../door-1/index.html">Door 1</a>
     <a href="../door-2/index.html">Door 2</a>
     <a href="../door-3/index.html">Door 3</a>
     <a href="../door-4/index.html">Door 4</a></nav>
<main>
  <figure><img src="lookbook/M-01-sign-day.png" alt="Sign post panel, day elevation">
    <figcaption>On the post — day. Panel centre 1500 mm above finished ground level,
      four posts carrying a {(W*H)/1e6:.1f} m² face, shown as a proposal.</figcaption></figure>
  <div class="two">
    <figure><img src="lookbook/M-03-sign-dimensions.png" alt="Dimensioned panel">
      <figcaption>Trim {W:.1f} × {H:.1f} mm.</figcaption></figure>
    <figure><img src="lookbook/M-02-sign-night.png" alt="Night elevation">
      <figcaption>Night — if the panel is lit.</figcaption></figure>
  </div>
  <table>
    <tr><th>File</th><th>What it is</th></tr>
    <tr><td><a href="artwork/BCM-Sign-Name-Only.pdf">BCM-Sign-Name-Only.pdf</a></td>
        <td>Print file — option A, both faces, 10 mm bleed, crop marks, 1 : 1 mm</td></tr>
    <tr><td><a href="artwork/BCM-Sign-Name-Only-Option-C-Fascia.pdf">BCM-Sign-Name-Only-Option-C-Fascia.pdf</a></td>
        <td>Print file — option C, the fascia setting, one face</td></tr>
    <tr><td><a href="print/BCM-Sign-Post-BOTH-FACES-{W:.0f}x{H:.0f}mm.pdf">BCM-Sign-Post-BOTH-FACES-{W:.0f}x{H:.0f}mm.pdf</a></td>
        <td><b>Send this to the signwriter</b> — the sign post only, both faces, 1 : 1 mm,
            10 mm bleed, crop marks</td></tr>
    <tr><td><a href="BCM-Sign-Post-Print-{W:.0f}x{H:.0f}mm.zip">BCM-Sign-Post-Print-{W:.0f}x{H:.0f}mm.zip</a></td>
        <td>The sign post only, as a zip: the two-face file, each face on its own, the
            spare fascia setting, and the printer's note</td></tr>
    <tr><td><a href="BCM-Sign-Panel.pdf">BCM-Sign-Panel.pdf</a></td>
        <td>Four pages — panel to scale, options, on the post, specification</td></tr>
  </table>
  <p class="note">Monogram is a recreation, not BCM's official logo. Measurements are the
     client's: {ftin(W_IN)} × {ftin(H_IN)}. Substrate and fixings are industry-typical
     proposals for a {(W*H)/1e6:.1f} m² face — confirm with the signwriter.
     The sheet is 1 : 1 and {W + 2 * BLEED:.1f} mm wide, close to the largest page a PDF
     will hold: plot it at 100 %, never rescaled.</p>
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
