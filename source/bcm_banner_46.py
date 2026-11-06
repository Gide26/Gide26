"""BCM Medical Centre — one banner in the sign post's own setting.

The client asked for a banner at the sign's measurements and in the sign's colours:
**46 in x 22 in = 1168.4 x 558.8 mm**, landscape, carrying the same band arrangement
as the panel that is going into the lighting board — BCM on white, MEDICAL CENTRE on
navy, EDDWALIRO knocked out of the red block, OPEN 24 HRS between two arrows, and the
navy foot strip with the numbers and the branch.

The difference from the sign is what the piece is: a **PVC banner on a fence**, so the
artwork keeps clear of a welded hem and the eyelet line, and the plan sheet shows where
the eyelets go. The colours and the type are the sign's, unchanged.

    print/BCM-Banner-1168x559mm-BLEED.pdf    trim + 10 mm bleed + 20 mm slug
    print/BCM-Banner-1168x559mm-EXACT.pdf    page = trim, 1168.4 x 558.8 mm
    print/READ-ME-FIRST.txt                  the printer's note
    BCM-Banner.pdf                           two pages: to scale with dimensions,
                                             and the eyelet / hem plan
    lookbook/M-01-banner-day.png             the banner, flat, with its eyelets
    lookbook/M-02-banner-dimensions.png      the same, dimensioned
"""
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFilter
from reportlab.lib.units import mm as MM
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

import bcm_brand as B
import bcm_sign as SGN
import cp_docutil as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "bcm", "banner-1168x559")
PRINT_DIR = os.path.join(OUT_DIR, "print")
LOOK_DIR = os.path.join(OUT_DIR, "lookbook")
WORK = os.path.join(HERE, ".work", "bcm_banner_46")

# --- the measurement, the same as the sign post -------------------------------
W_IN, H_IN = 46, 22
W, H = round(W_IN * SGN.IN, 1), round(H_IN * SGN.IN, 1)      # 1168.4 x 558.8 mm
FT_TXT = f"{SGN.ftin(W_IN)} × {SGN.ftin(H_IN)}"
TAG = f"{W:.0f}x{H:.0f}"
REV = "Rev A  ·  2026-11-07"

# --- banner making, industry-typical and flagged for the printer ---------------
BLEED = 10.0
SLUG = 20.0
HEM = 25.0                 # welded hem all round
EYELET_PITCH = 300.0       # centres, around the perimeter
EYELET_D = 12.0            # the eyelet's outer diameter, 3 mm wall stainless/brass
SAFE = 45.0                # hem + eyelet zone: no type, no rules inside this

B.register_fonts()
D.use_brand(B)

WORD = SGN.WORD
NAME = SGN.SIGN_COMMUNITY
BRAND = SGN.SIGN_BRAND
BRANCH = SGN.SIGN_BRANCH
TEL = SGN.SIGN_TEL

# the sign's own band weights, unchanged — same proportions, same colours
BAND_W = SGN.BAND_W

MONO = {"keyline": B.CP_NAVY, "ground": B.WHITE}


# --------------------------------------------------------------------- helpers
def fit_cap(text, weight, family, target_w):
    return SGN.fit_cap(text, weight, family, target_w)


def spread(length, pitch):
    """Even positions across `length`, no gap wider than `pitch`, ends included."""
    n = max(1, int(round(length / pitch)))
    return [length * i / n for i in range(n + 1)]


def img(c, pil, x, y, w, h=None, frame=False):
    """Place a PIL image at (x, y) from the bottom-left, w and h in points."""
    if h is None:
        h = w * pil.height / pil.width
    c.drawImage(ImageReader(pil), x, y, width=w, height=h,
                preserveAspectRatio=False, mask=None)
    if frame:
        c.setStrokeColor(B.CP_GREY)
        c.setLineWidth(0.4)
        c.rect(x, y, w, h, stroke=1, fill=0)
    return h


def face(c, w=W, h=H):
    """The banner face at trim size, origin bottom-left, in millimetres.

    Same arrangement and same colours as the sign post panel; the only difference is
    the margin, which here has to clear a hem and an eyelet line.
    """
    mxx = max(SAFE, w * 0.030)
    my = max(SAFE, h * 0.055)
    IW, IH = w - 2 * mxx, h - 2 * my

    c.setFillColor(B.WHITE)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    weights = list(BAND_W)
    total = sum(weights)
    h_brand, h_navy, g1, h_red, h_open, g2, h_foot = [IH * x / total for x in weights]

    top = my + IH
    y_brand = top - h_brand
    y_navy = y_brand - h_navy
    y_red = y_navy - g1 - h_red
    y_open = y_red - h_open
    y_foot = y_open - g2 - h_foot

    # ---- white band: BCM
    cap_w = h_brand * 0.86
    B.caps(c, w / 2, y_brand + (h_brand - cap_w) / 2 - cap_w * 0.02, BRAND, cap_w,
           B.CP_NAVY, "Manrope-800", cap_w * 0.16, align="center", max_w=IW)

    # ---- navy band: MEDICAL CENTRE
    c.setFillColor(B.CP_NAVY)
    c.rect(mxx, y_navy, IW, h_navy, stroke=0, fill=1)
    cap_c = min(h_navy * 0.80, fit_cap(NAME, "Manrope-800", "Manrope", IW * 0.94))
    B.caps(c, w / 2, y_navy + (h_navy - cap_c) / 2 - cap_c * 0.02, NAME, cap_c,
           B.WHITE, "Manrope-800", cap_c * 0.12, align="center", max_w=IW * 0.96)

    # ---- red block: EDDWALIRO knocked out in white
    c.setFillColor(SGN.LIT_RED)
    c.rect(mxx, y_red, IW, h_red, stroke=0, fill=1)
    cap_e = min(h_red * 0.82, fit_cap(WORD, "Manrope-800", "Manrope", IW * 0.94))
    B.caps(c, w / 2, y_red + (h_red - cap_e) / 2 - cap_e * 0.03, WORD, cap_e,
           B.WHITE, "Manrope-800", cap_e * 0.045, align="center", max_w=IW * 0.97)

    # ---- open row: arrow, Open 24 Hrs, arrow
    al = IW * 0.135
    acap = h_open * 0.46
    w1 = pdfmetrics.stringWidth("Open", "Manrope-700", B.font_for(acap, "Manrope"))
    w2 = pdfmetrics.stringWidth("24 Hrs", "Manrope-700", B.font_for(acap, "Manrope"))
    gap = IW * 0.055
    tw = w1 + gap + w2
    cy = y_open + h_open / 2
    tgap = cap_e * 0.10
    x0 = w / 2 - tw / 2
    B.caps(c, x0, cy - acap / 2, "Open", acap, SGN.LIT_RED, "Manrope-700", tgap)
    B.caps(c, x0 + w1 + gap, cy - acap / 2, "24 Hrs", acap, SGN.LIT_RED,
           "Manrope-700", tgap)
    arm = h_open * 0.052
    SGN._arrow(c, mxx + IW * 0.008, cy, al, arm, IW * 0.052, h_open * 0.150,
               SGN.LIT_RED, direction=-1)
    SGN._arrow(c, mxx + IW - IW * 0.008 - al, cy, al, arm, IW * 0.052,
               h_open * 0.150, SGN.LIT_RED, direction=+1)

    # ---- navy foot strip: numbers left, branch right
    c.setFillColor(B.CP_NAVY)
    c.rect(mxx, y_foot, IW, h_foot, stroke=0, fill=1)
    cap_f = min(h_foot * 0.30, fit_cap("TEL " + TEL, "Inter-600", "Inter", IW * 0.62))
    B.caps(c, mxx + IW * 0.014, y_foot + (h_foot - cap_f) / 2, f"TEL  {TEL}", cap_f,
           B.WHITE, "Inter-600", cap_f * 0.06)
    B.caps(c, mxx + IW - IW * 0.014, y_foot + (h_foot - cap_f) / 2, BRANCH, cap_f,
           B.WHITE, "Inter-600", cap_f * 0.12, align="right")


def eyelets(w=W, h=H, pitch=EYELET_PITCH):
    """Eyelet centres, clockwise from the bottom-left corner, incl. the corners."""
    pts = []
    for x in spread(w, pitch):
        pts.append((x, HEM / 2))
        pts.append((x, h - HEM / 2))
    for y in spread(h, pitch)[1:-1]:
        pts.append((HEM / 2, y))
        pts.append((w - HEM / 2, y))
    return pts


# --------------------------------------------------------------------- artwork
def _crop_marks(c, w, h):
    c.saveState()
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.3)
    x0, y0 = BLEED * MM, (BLEED + SLUG) * MM
    x1, y1 = (BLEED + w) * MM, (BLEED + SLUG + h) * MM
    L = 9 * MM
    for (x, y) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        c.line(x - L, y, x - 3 * MM, y)
        c.line(x + 3 * MM, y, x + L, y)
        c.line(x, y - L, x, y - 3 * MM)
        c.line(x, y + 3 * MM, x, y + L)
    c.restoreState()


def artwork(path):
    """The print file: trim + 10 mm bleed + a 20 mm slug at the foot."""
    pw, ph = W + BLEED * 2, H + BLEED * 2 + SLUG
    c = canvas.Canvas(path, pagesize=(pw * MM, ph * MM))
    c.setTitle(f"BCM Medical Centre — banner {W:.0f} x {H:.0f} mm "
               f"({W_IN} x {H_IN} in)")
    c.setAuthor("BCM Medical Centre — banner")

    # the bleed edges carry the field colour, so a trim wobble never shows white
    c.setFillColor(B.WHITE)
    c.rect(0, 0, pw, ph, stroke=0, fill=1)
    c.saveState()
    c.translate(BLEED, BLEED + SLUG)
    c.scale(MM, MM)
    face(c)
    c.restoreState()
    _crop_marks(c, W, H)

    # slug
    c.setFillColor(B.WHITE)
    c.rect(0, 0, pw, SLUG, stroke=0, fill=1)
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.2)
    c.line(0, SLUG, pw, SLUG)
    B.caps(c, 3, SLUG - 6.2,
           f"BCM BANNER  |  {W_IN} x {H_IN} in  |  TRIM {W:.1f} x {H:.1f} mm  |  "
           f"BLEED {BLEED:.0f} mm  |  HEM {HEM:.0f} mm  |  SAFE {SAFE:.0f} mm",
           2.6, B.CP_NAVY, "Inter-600", 0.3)
    B.caps(c, 3, SLUG - 10.8,
           f"PVC BANNER 510 g  |  WELDED HEM {HEM:.0f} mm ALL ROUND  |  EYELETS AT "
           f"{EYELET_PITCH:.0f} mm CENTRES  |  MATTE FINISH  |  DO NOT SCALE — PLOT AT 100 %",
           2.3, B.CP_NAVY, "Inter-500", 0.25)
    B.caps(c, 3, SLUG - 15.0,
           "SAME SETTING AND SAME COLOURS AS THE SIGN POST PANEL — NO MOTTO. "
           "RED #ED1B24, NAVY #16233F, WHITE.",
           2.1, B.CP_NAVY_MD, "Inter-500", 0.2)
    B.caps(c, pw - 3, 3.0, "CROP MARKS — TRIM AT THE MARKS", 2.2, B.CP_GREY,
           "Inter-500", 0.4, "right")
    c.showPage()
    c.save()
    return path


def artwork_exact(path):
    """The banner at exactly 46 x 22 in: page = trim, no bleed, no slug."""
    c = canvas.Canvas(path, pagesize=(W * MM, H * MM))
    c.setTitle(f"BCM Medical Centre — banner {W:.1f} x {H:.1f} mm, page = trim")
    c.scale(MM, MM)
    face(c)
    c.showPage()
    c.save()
    return path


# --------------------------------------------------------------------- images
def _flat(px_w=1800, eyelet=True, hem=False):
    """The face as an image, in pixels, at `px_w` wide."""
    tmp = os.path.join(WORK, "_flat.pdf")
    artwork_exact(tmp)
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(tmp)
    page = doc[0]
    sc = px_w / page.get_size()[0]
    im = page.render(scale=sc).to_pil().convert("RGB")
    doc.close()
    if eyelet or hem:
        im = _draw_hardware(im, hem=hem, eyelet=eyelet)
    return im


def _draw_hardware(im, hem=True, eyelet=True):
    """Hem shadow line and the eyelets, drawn on the flat art."""
    px_per_mm = im.width / W
    dr = ImageDraw.Draw(im, "RGBA")
    if hem:
        # the welded hem: a faint fold line, and a shade over the strip it takes
        inset = HEM * px_per_mm
        dr.rectangle([inset, inset, im.width - inset, im.height - inset],
                     outline=(22, 35, 63, 46), width=max(1, int(1.1 * px_per_mm)))
    if eyelet:
        r = EYELET_D / 2 * px_per_mm
        for (x, y) in eyelets():
            cx, cy = x * px_per_mm, im.height - y * px_per_mm
            dr.ellipse([cx - r * 1.55, cy - r * 1.55, cx + r * 1.55, cy + r * 1.55],
                       fill=(226, 232, 239, 235), outline=(150, 163, 180, 255),
                       width=max(1, int(0.5 * px_per_mm)))
            dr.ellipse([cx - r, cy - r, cx + r, cy + r],
                       fill=(96, 108, 128, 255), outline=(60, 70, 88, 255),
                       width=max(1, int(0.35 * px_per_mm)))
            dr.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55],
                       fill=(250, 251, 252, 255))
    return im


def _sheet(inner, margin=78, ground=(244, 247, 249), shadow=True):
    """Put the art on a paper-coloured sheet with a soft shadow."""
    w = inner.width + margin * 2
    h = inner.height + margin * 2
    sheet = Image.new("RGB", (w, h), ground)
    if shadow:
        sh = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(sh)
        d.rectangle([margin + 6, margin + 10, margin + inner.width + 6,
                     margin + inner.height + 10], fill=90)
        sh = sh.filter(ImageFilter.GaussianBlur(9))
        sheet.paste(Image.new("RGB", (w, h), (60, 72, 92)), (0, 0), sh)
    sheet.paste(inner, (margin, margin))
    return sheet


def mockup():
    im = _draw_hardware(_flat(px_w=1700, eyelet=False, hem=False), hem=True,
                        eyelet=True)
    return _sheet(im)


def dimensioned():
    im = _flat(px_w=2200)
    L, T, R, Bm = 200, 240, 470, 190          # sheet margins around the art
    Wc, Hc = im.width + L + R, im.height + T + Bm
    sheet = Image.new("RGB", (Wc, Hc), (244, 247, 249))
    sh = Image.new("L", (Wc, Hc), 0)
    ImageDraw.Draw(sh).rectangle([L + 8, T + 12, L + im.width + 8, T + im.height + 12],
                                 fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(11))
    sheet.paste(Image.new("RGB", (Wc, Hc), (60, 72, 92)), (0, 0), sh)
    sheet.paste(im, (L, T))
    dr = ImageDraw.Draw(sheet, "RGBA")

    x0, y0 = L, T
    x1, y1 = x0 + im.width, y0 + im.height
    ink = (22, 35, 63, 255)
    faint = (22, 35, 63, 110)
    lw = 4
    k = im.width / W
    try:
        from PIL import ImageFont
        f_big = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        f_sm = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    except Exception:                             # pragma: no cover
        f_big = f_sm = None

    def text(xy, txt, font, fill=ink, anchor="la"):
        dr.text(xy, txt, fill=fill, font=font, anchor=anchor)

    def arrow_h(xa, xb, y):
        dr.line([xa, y, xb, y], fill=ink, width=lw)
        for x, sgn in ((xa, 1), (xb, -1)):
            dr.line([x, y, x + 26 * sgn, y - 12], fill=ink, width=lw)
            dr.line([x, y, x + 26 * sgn, y + 12], fill=ink, width=lw)

    def arrow_v(ya, yb, x):
        dr.line([x, ya, x, yb], fill=ink, width=lw)
        for y, sgn in ((ya, 1), (yb, -1)):
            dr.line([x, y, x - 12, y + 26 * sgn], fill=ink, width=lw)
            dr.line([x, y, x + 12, y + 26 * sgn], fill=ink, width=lw)

    # width, above the banner
    wy = y0 - 60
    dr.line([x0, wy + 6, x0, y0 - 6], fill=faint, width=2)
    dr.line([x1, wy + 6, x1, y0 - 6], fill=faint, width=2)
    arrow_h(x0, x1, wy)
    text(((x0 + x1) / 2, wy - 52),
         f"{W:.1f} mm  ·  {W_IN} in  ·  {SGN.ftin(W_IN)}", f_big, anchor="ma")

    # height, right of the banner
    hx = x1 + 66
    dr.line([x1, y0, hx + 6, y0], fill=faint, width=2)
    dr.line([x1, y1, hx + 6, y1], fill=faint, width=2)
    arrow_v(y0, y1, hx)
    text((hx + 46, y0 + im.height / 2),
         f"{H:.1f} mm\n{H_IN} in\n{SGN.ftin(H_IN)}", f_big, anchor="lm")

    # hem + eyelet callout, above the top-left eyelet, inside the sheet
    cx, cy = x0 + (EYELET_D / 2) * k, y0
    tx, ty = x0 + 40, cy - 128
    dr.line([cx, cy - 8, tx + 26, ty + 40], fill=faint, width=2)
    text((tx, ty),
         f"{len(eyelets())} eyelets at {EYELET_PITCH:.0f} mm centres", f_sm,
         fill=(75, 91, 115, 255), anchor="ls")
    text((tx, ty + 40), f"{HEM:.0f} mm welded hem all round · safe line {SAFE:.0f} mm in",
         f_sm, fill=(75, 91, 115, 255), anchor="ls")
    return sheet


# --------------------------------------------------------------------- documents
def eyelet_table(c, x, y, w):
    pts = eyelets()
    rows = [["Perimeter", f"{2 * (W + H) / 1000:.2f} m"],
            ["Eyelets, this banner", f"{len(pts)}"],
            ["Eyes at", f"{EYELET_PITCH:.0f} mm centres, incl. every corner"],
            ["Eyelet", f"{EYELET_D:.0f} mm outer, 3 mm wall, stainless or brass"],
            ["Hem", f"{HEM:.0f} mm welded all round"],
            ["Fix at", "every eyelet — not every second one"]]
    return D.table(c, x, y,
                   [("Item", 44, "left"), ("Value", 90, "left")],
                   rows, row_h=4.8 * MM, head_h=4.8 * MM, cap=2.5, head_cap=2.4)


def proof(path):
    """Two pages: the banner to scale, and the eyelet / hem plan.

    The sheet is A4 landscape, so the vertical room is 210 mm — the art is sized to
    leave the title block at the top and the notes underneath.
    """
    c = canvas.Canvas(path, pagesize=(D.PW, D.PH))

    # ---- page 1 — the banner to scale
    D.page_bg(c, "THE BANNER", f"{REV}", 1,
              eyebrow="BCM  ·  MEDICAL CENTRE  ·  BANNER")
    y = D.h1(c, D.PH - 34 * MM, "One banner, the sign's own setting", 7.4)
    D.para(c, D.M, y + 2 * MM,
           f"{W_IN} × {H_IN} in — {W:.1f} × {H:.1f} mm — the same measurement as the "
           "sign post panel, in the same colours and the same band arrangement: BCM on "
           "white, MEDICAL CENTRE on navy, EDDWALIRO knocked out of the red block, "
           "OPEN 24 HRS between two arrows, and the navy foot strip with the numbers "
           "and BUSSABALA. The difference is what the piece is: this one is PVC on a "
           "fence, so the artwork keeps clear of a welded hem and the eyelet line.",
           (D.PW - 2 * D.M) / MM * 0.74, 2.9, B.NAVY_MID)

    im = Image.open(os.path.join(WORK, "banner_flat.png"))
    box_w = 126.0
    ph = box_w * im.height / im.width
    bottom = 86.0
    img(c, im, D.M, bottom * MM, box_w * MM, ph * MM)
    B.label(c, D.M, (bottom - 6) * MM,
            f"TO SCALE  ·  {W_IN} × {H_IN} IN  ·  WITH ITS EYELETS", 2.6, B.GREY,
            "Inter-500", 0.8)

    B.label(c, D.M, 74 * MM, "WHAT IT IS", 3.2, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, 68 * MM, [
        f"Trim {W:.1f} × {H:.1f} mm — {W_IN} × {H_IN} in, {FT_TXT}. The exact file's "
        "page is that size, so it measures the banner.",
        "Colours are the sign's: red #ED1B24 block and open row, navy #16233F bands, "
        "white field. Nothing new was introduced for the banner.",
        f"Artwork keeps {SAFE:.0f} mm clear of the trim all round — the hem and the "
        "eyelet line. No type and no rule inside it.",
        "One face only: a banner reads from one side, and a second face is a second "
        "banner.",
    ], 176 * MM, 2.7, B.NAVY_MID)

    # ---- page 2 — the plan
    c.showPage()
    D.page_bg(c, "THE PLAN", f"{REV}", 2,
              eyebrow="BCM  ·  MEDICAL CENTRE  ·  BANNER")
    y = D.h1(c, D.PH - 34 * MM, "Where the eyelets go", 7.4)
    D.para(c, D.M, y + 2 * MM,
           "Industry-typical for a fence banner at this size — confirm with the printer "
           "and the installer before the run. Nothing here is a quotation.",
           (D.PW - 2 * D.M) / MM * 0.62, 2.9, B.NAVY_MID)
    im = Image.open(os.path.join(WORK, "banner_dimensions.png"))
    box_w = 126.0
    ph = box_w * im.height / im.width
    bottom = 96.0
    img(c, im, D.M, bottom * MM, box_w * MM, ph * MM)
    B.label(c, D.M, (bottom - 6) * MM, "DIMENSIONED  ·  HEM AND EYELETS SHOWN", 2.6,
            B.GREY, "Inter-500", 0.8)
    D.bullets(c, D.M, 80 * MM, [
        f"{len(eyelets())} eyelets at {EYELET_PITCH:.0f} mm centres around the "
        f"perimeter, including all four corners; {HEM:.0f} mm welded hem all round.",
        "Fix at every eyelet. A banner this size sails in wind if it is tied at every "
        "second hole.",
        "Plot at 1 : 1 and never scale — the file is drawn in millimetres, and a scaled "
        "banner is a different banner.",
        "The red is the sign's #ED1B24: hold it to the same reference as the light box, "
        "so the fence and the board read as one set in daylight.",
    ], 176 * MM, 2.7, B.NAVY_MID)
    eyelet_table(c, D.M, 50 * MM, 150 * MM)
    c.showPage()
    c.save()
    return path


def readme_txt(path):
    txt = (
        "BCM MEDICAL CENTRE - BANNER, THE SIGN POST'S OWN SETTING\n"
        "========================================================\n\n"
        f"TRIM (finished size):  {W_IN} in x {H_IN} in\n"
        f"                       = {W:.1f} x {H:.1f} mm exactly (25.4 mm to the inch)\n"
        f"                       = {FT_TXT}\n"
        f"BLEED:                 {BLEED:.0f} mm all round (in the bleed file)\n"
        f"SLUG:                  {SLUG:.0f} mm at the foot (trim it off)\n"
        f"HEM:                   {HEM:.0f} mm welded all round\n"
        f"EYELETS:               {EYELET_PITCH:.0f} mm centres, incl. every corner\n"
        f"SAFE AREA:             {SAFE:.0f} mm from trim - no type inside it\n"
        f"PAGE, BLEED FILE:      {W + 2 * BLEED:.1f} x {H + 2 * BLEED + SLUG:.1f} mm\n"
        "                       (trim + bleed + slug. The page is LARGER than the\n"
        "                       banner on purpose.)\n"
        f"PAGE, EXACT FILE:      {W:.1f} x {H:.1f} mm = {W_IN} x {H_IN} in,\n"
        "                       trim only - this is the one that measures the banner.\n"
        "COLOUR:                white field; navy #16233F bands with white type;\n"
        "                       red #ED1B24 block with EDDWALIRO knocked out in\n"
        "                       white; red OPEN 24 HRS row. Nothing else.\n"
        "PLOT AT 100% - NEVER SCALE.\n\n"
        "THE SETTING\n"
        "The same arrangement and the same colours as the sign post panel: BCM on a\n"
        "white band, MEDICAL CENTRE in white on navy, EDDWALIRO knocked out of a\n"
        "full-width red block, OPEN 24 HRS between two arrows, then the navy foot\n"
        "strip with 0788 323 815 - 0754 132 715 at the left and BUSSABALA at the\n"
        "right. There is NO MOTTO on this piece.\n\n"
        "MATERIAL AND FINISH - CONFIRM WITH THE PRINTER\n"
        "PVC banner 510 g, matte finish, welded hem all round, eyelets at the pitch\n"
        "above. These are industry-typical values, not a quotation, and the printer\n"
        "should be allowed to substitute their own standard.\n\n"
        "FILES\n"
        f"  BCM-Banner-{TAG}mm-EXACT.pdf   page = trim, {W_IN} x {H_IN} in\n"
        f"  BCM-Banner-{TAG}mm-BLEED.pdf   trim + {BLEED:.0f} mm bleed + slug + crop marks\n"
        "  READ-ME-FIRST.txt              this note\n")
    open(path, "w").write(txt)
    return path


def write_readme(path):
    txt = f"""# BCM Medical Centre — banner, {W_IN} × {H_IN} in

One banner in the sign post's own setting: **{W:.1f} × {H:.1f} mm ({W_IN} × {H_IN} in,
{FT_TXT})**, landscape, PVC on a fence.

Same measurement, same colours and the same band arrangement as the panel going into the
lighting board:

1. white band: `BCM`
2. navy band (`#16233F`): `MEDICAL CENTRE` in white
3. red block (`#ED1B24`), full width: `EDDWALIRO` knocked out in white
4. white row: an arrow at each end, `Open` and `24 Hrs` in red between them
5. navy foot strip: `TEL 0788 323 815 · 0754 132 715` left, `BUSSABALA` right

No motto, no photograph, no service list — the sign's message, on the fence.

What differs from the sign is only what the piece is: a banner carries a **{HEM:.0f} mm
welded hem** and **eyelets at {EYELET_PITCH:.0f} mm centres**, so all the type stays
**{SAFE:.0f} mm clear of the trim** instead of running to the edge the way the panel does.

| File | What it is |
| --- | --- |
| `print/BCM-Banner-{TAG}mm-EXACT.pdf` | **Exactly {W_IN} × {H_IN} in** — page = trim, no bleed. The file that measures the banner. |
| `print/BCM-Banner-{TAG}mm-BLEED.pdf` | Trim + {BLEED:.0f} mm bleed + {SLUG:.0f} mm slug + crop marks — page {W + 2 * BLEED:.0f} × {H + 2 * BLEED + SLUG:.0f} mm, larger on purpose |
| `print/READ-ME-FIRST.txt` | The printer's note: sizes, hem, eyelets, colours |
| `BCM-Banner.pdf` | Two pages — the banner to scale with dimensions, then the eyelet and hem plan |
| `lookbook/M-01-banner-day.png` | The banner flat, with its eyelets |
| `lookbook/M-02-banner-dimensions.png` | The same, dimensioned |
| `index.html` | Web preview |
| `BCM-Banner-Package.zip` | Everything above in one zip |

## Production — confirm with the printer, none of this is a quotation

- PVC banner 510 g, matte, printed at 1 : 1. Plot at 100 %; do not scale.
- {HEM:.0f} mm welded hem all round; eyelets at {EYELET_PITCH:.0f} mm centres including
  every corner.
- Fix at every eyelet: a banner this size sails in wind if it is tied at every second hole.
- The red is the sign's `#ED1B24`; hold it to the same reference as the light box so the
  fence and the board match in daylight.

## Before plot

1. Check {W_IN} × {H_IN} in against the fence run it is going on.
2. Confirm the branch line reads **`BUSSABALA`** and the numbers are
   **0788 323 815 · 0754 132 715**.
3. Confirm the eyelet pitch with the installer — {EYELET_PITCH:.0f} mm is
   industry-typical, not measured.

Rebuild: `cd source && python3 bcm_banner_46.py`
"""
    open(path, "w").write(txt)
    return path


def write_index(path):
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BCM Medical Centre — banner {W_IN} × {H_IN} in</title>
<style>
 body{{margin:0;background:#f4f7f9;color:#16233f;
   font:16px/1.6 Inter,Helvetica,Arial,sans-serif}}
 header{{background:#16233f;color:#fff;padding:52px 6vw 44px}}
 h1{{font-size:clamp(28px,4.6vw,48px);margin:.15em 0 .3em;line-height:1.05}}
 header p{{max-width:64ch;color:#cfd9e6;margin:0}}
 .eyebrow{{letter-spacing:.3em;font-size:11px;color:#2ba9e0}}
 main{{padding:34px 6vw 72px}}
 h2{{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#8fa2b8;
   margin:0 0 14px}}
 figure{{margin:0 0 30px;background:#fff;border-radius:8px;overflow:hidden;
   box-shadow:0 2px 16px rgba(22,35,63,.09)}}
 figure img{{width:100%;display:block}}
 figcaption{{padding:12px 16px;font-size:12.5px;color:#4b5b73}}
 table{{width:100%;border-collapse:collapse;font-size:14px;background:#fff}}
 th,td{{text-align:left;padding:10px 14px;border-bottom:1px solid #e3eaf2}}
 th{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#8fa2b8}}
 a{{color:#1b87b8}}
 .note{{color:#4b5b73;font-size:13px;max-width:80ch}}
</style></head><body>
<header>
  <div class="eyebrow">BCM · MEDICAL CENTRE · BANNER</div>
  <h1>One banner, the sign's own setting.</h1>
  <p>{W_IN} × {H_IN} in — {W:.0f} × {H:.0f} mm — the same measurement and the same
     colours as the sign post panel: BCM on white, MEDICAL CENTRE in white on navy,
     EDDWALIRO knocked out of the red block, OPEN 24 HRS between two arrows, and the
     navy foot strip with the numbers and BUSSABALA. PVC on a fence, so the type stays
     {SAFE:.0f} mm clear of the trim for the hem and the eyelets.</p>
</header>
<main>
  <figure><img src="lookbook/M-01-banner-day.png" alt="The banner, flat">
    <figcaption>To scale, with the eyelets — {HEM:.0f} mm hem, {EYELET_PITCH:.0f} mm
      centres.</figcaption></figure>
  <figure><img src="lookbook/M-02-banner-dimensions.png" alt="Dimensioned banner">
    <figcaption>Trim {W:.1f} × {H:.1f} mm.</figcaption></figure>
  <table>
    <tr><th>File</th><th>What it is</th></tr>
    <tr><td><a href="print/BCM-Banner-{TAG}mm-EXACT.pdf">BCM-Banner-{TAG}mm-EXACT.pdf</a></td>
        <td>The banner at exactly {W_IN} × {H_IN} in — page = trim</td></tr>
    <tr><td><a href="print/BCM-Banner-{TAG}mm-BLEED.pdf">BCM-Banner-{TAG}mm-BLEED.pdf</a></td>
        <td>Print file — 10 mm bleed, crop marks, slug</td></tr>
    <tr><td><a href="print/READ-ME-FIRST.txt">READ-ME-FIRST.txt</a></td>
        <td>Sizes, hem, eyelets, colours</td></tr>
    <tr><td><a href="BCM-Banner.pdf">BCM-Banner.pdf</a></td>
        <td>Two pages — to scale, and the eyelet plan</td></tr>
    <tr><td><a href="BCM-Banner-Package.zip">BCM-Banner-Package.zip</a></td>
        <td>Everything above</td></tr>
  </table>
  <p class="note">Industry-typical hem and eyelet values — confirm with the printer.
     Nothing here is a quotation.</p>
</main></body></html>
"""
    open(path, "w").write(html)
    return path


def package():
    zpath = os.path.join(OUT_DIR, "BCM-Banner-Package.zip")
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for base, dirs, files in os.walk(OUT_DIR):
            dirs.sort()
            for f in sorted(files):
                if f.endswith(".zip"):
                    continue
                full = os.path.join(base, f)
                rel = os.path.relpath(full, OUT_DIR)
                z.write(full, os.path.join("BCM-Banner", rel))
    return zpath


def main():
    for d in (OUT_DIR, PRINT_DIR, LOOK_DIR, WORK):
        os.makedirs(d, exist_ok=True)

    ex = artwork_exact(os.path.join(PRINT_DIR, f"BCM-Banner-{TAG}mm-EXACT.pdf"))
    bl = artwork(os.path.join(PRINT_DIR, f"BCM-Banner-{TAG}mm-BLEED.pdf"))
    print("print:", os.path.basename(ex), os.path.basename(bl))
    readme_txt(os.path.join(PRINT_DIR, "READ-ME-FIRST.txt"))

    mockup().convert("RGB").save(os.path.join(LOOK_DIR, "M-01-banner-day.png"))
    dimensioned().convert("RGB").save(
        os.path.join(LOOK_DIR, "M-02-banner-dimensions.png"))
    _flat(px_w=1700).save(os.path.join(WORK, "banner_flat.png"))
    dimensioned().save(os.path.join(WORK, "banner_dimensions.png"))
    print("lookbook: day, dimensions")

    proof(os.path.join(OUT_DIR, "BCM-Banner.pdf"))
    write_readme(os.path.join(OUT_DIR, "README.md"))
    write_index(os.path.join(OUT_DIR, "index.html"))
    p = package()
    print("package:", os.path.basename(p),
          f"{os.path.getsize(p) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
