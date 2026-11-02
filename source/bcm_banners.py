"""BCM Medical Centre — three banner designs for the roadside fence.

Three different banners, three different jobs, one identity:

    B-1  3800 × 1000 mm   the road banner — photo left, the name right
    B-2  3400 × 1000 mm   the services banner — type left, two photos right
    B-3  2400 × 1000 mm   the compact banner — the name centred, one photo

Everything is drawn in millimetres on the trim rectangle. The artwork files add
10 mm bleed, eyelet-safe margins, crop marks and a slug strip. Mockups place each
banner on a fence to scale, with the eyelets shown.
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
import cp_photos as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "bcm", "banners")
ART_DIR = os.path.join(OUT_DIR, "artwork")
WORK = os.path.join(ROOT, "source", ".work", "bcm_banners")

BLEED, SLUG = 10.0, 20.0
SAFE = 60.0                    # hem + eyelet zone: nothing important goes here
REV = "Rev A  ·  2026-11-02"
NAME = "MEDICAL CENTRE"
WORD = "EDDWALIRO"
PHONE = "0771 240 104  ·  0754 132 715"

# every frame used here has been colour-retouched so the people read Black African,
# and is recorded on the licence page. Working files are web-resolution.
EDITS = {"pharmacy": "ph-pharmacy.jpg", "lab": "ph-lab.jpg",
         "pharmacy_shelf": "ph-pharmacy-shelf.jpg", "pharm_handover": "ph-pharm-handover.jpg",
         "lab_scientist": "ph-lab-scientist.jpg", "reception": "ph-reception.jpg",
         "tablets_hands": "ph-tablets-hands.jpg", "consult": "ph-consult.jpg",
         "paeds": "ph-paeds.jpg", "immunisation_baby": "ph-immunisation-baby.jpg",
         "scan_obgyn": "ph-scan-obgyn.jpg", "eye_exam": "ph-eye-exam.jpg",
         "ent_exam": "ph-ent-exam2.jpg", "antenatal_consult": "ph-antenatal.jpg",
         "ultrasound_exam": "ph-ultrasound.jpg", "scan_room": "ph-scan-room.jpg",
         "hiv_selftest": "ph-hiv-selftest.jpg", "pharmacy_counter": "ph-pharmacy-counter.jpg",
         "lab_micro": "ph-lab-micro.jpg"}

BANNERS = [
    {
        "id": "B-1", "slug": "B-01", "w": 3800.0, "h": 1000.0,
        "title": "The road banner", "sub": "3.8 m × 1.0 m",
        "job": "Read at speed, from the road. Photograph on the left, the name on the right.",
        "services": ["GENERAL OUTPATIENT", "LABORATORY", "PHARMACY",
                     "ULTRASOUND", "MINOR SURGERY", "HIV CARE"],
        "photos": [("pharmacy", 60.0, 60.0, 1040.0, 880.0, (0.70, 0.30))],
        "layout": "road",
    },
    {
        "id": "B-2", "slug": "B-02", "w": 3400.0, "h": 1000.0,
        "title": "The services banner", "sub": "3.4 m × 1.0 m",
        "job": "Read standing still, at the gate. The list does the work, two photographs carry it.",
        "services": ["PAEDIATRICS", "IMMUNISATION", "ANTENATAL & POSTNATAL",
                     "OBS & GYN", "FAMILY PLANNING", "EYE SERVICES"],
        "photos": [("lab", 2380.0, 540.0, 960.0, 400.0, (0.50, 0.06)),
                   ("pharmacy_shelf", 2380.0, 80.0, 960.0, 400.0, (0.62, 0.10))],
        "layout": "services",
    },
    {
        "id": "B-3", "slug": "B-03", "w": 2400.0, "h": 1000.0,
        "title": "The compact banner", "sub": "2.4 m × 1.0 m",
        "job": "The short run: the name set as large as it will go, one photograph, one line of services.",
        "services": ["INPATIENT CARE", "ENT", "ORTHOPAEDICS", "TRAVEL MEDICAL EXAM"],
        "photos": [("reception", 1740.0, 60.0, 600.0, 880.0, (0.50, 0.55))],
        "layout": "compact",
    },
]

B.register_fonts()


def configure():
    """Point the photo registry at the colour-retouched files."""
    P.CACHE_DIR = os.path.join(WORK, "photos")
    for key, fname in EDITS.items():
        path = os.path.join(ROOT, "assets", "photos", "edited", fname)
        if key in P.PHOTOS and os.path.exists(path):
            w, h = Image.open(path).size
            P.PHOTOS[key].setdefault("px_orig", P.PHOTOS[key]["px"])
            P.PHOTOS[key]["src"] = os.path.join("edited", fname)
            P.PHOTOS[key]["px"] = (w, h)
            P.PHOTOS[key]["edit"] = True


# --------------------------------------------------------------------- helpers
def fit_cap(text, weight, family, target_w, tracking=0.0):
    cap = 100.0
    size = B.font_for(cap, family)
    w = pdfmetrics.stringWidth(text, weight, size) + tracking * (len(text) - 1)
    return cap * target_w / w


def photo(c, key, x, y, w, h, focus=(0.5, 0.45), zoom=1.0, fit=False):
    path = P.prepare(key, w, h, focus=focus, dpi=110, zoom=zoom, fit=fit)
    c.drawImage(path, x, y, w, h, mask=None)
    return path


def keyline(c, x, y, w, h, color=None, alpha=0.14, lw=1.4):
    c.saveState()
    c.setStrokeColor(color or B.WHITE)
    c.setStrokeAlpha(alpha)
    c.setLineWidth(lw)
    c.rect(x, y, w, h, stroke=1, fill=0)
    c.restoreState()


def word(c, x, y, cap, color=None, align="left", track=10.0, max_w=None):
    return B.caps(c, x, y, WORD, cap, color or B.CP_CYAN, "Manrope-800", track,
                  align=align, max_w=max_w)


def badge_row(c, x, y, ms=96.0, cap_b=30.0, gap=26.0):
    """Badge with the initials beside it; returns the height used."""
    B.monogram(c, x, y, ms, dark=B.WHITE, accent=B.CP_CYAN)
    B.caps(c, x + ms + gap, y + ms * 0.36, "BCM", cap_b, B.CP_CYAN, "Inter-600", 14.0)
    return ms


def services_block(c, items, x, y, cols=2, col_w=1120.0, row=62.0, cap=32.0,
                   color=None):
    """Service list: a cyan rule then the name, two columns."""
    color = color or B.CP_MIST
    for i, s in enumerate(items):
        cx = x + (i % cols) * col_w
        cy = y - (i // cols) * row
        c.setFillColor(B.CP_CYAN)
        c.rect(cx, cy + cap * 0.30, 34.0, 4.0, stroke=0, fill=1)
        B.caps(c, cx + 54.0, cy, s, cap, color, "Inter-600", 3.0)


def phone_line(c, x, y, cap=30.0, align="left", color=None):
    B.caps(c, x, y, f"TEL {PHONE}", cap, color or B.CP_CYAN, "Inter-600", 3.0,
           align=align)


# ----------------------------------------------------------------------- faces
def face_road(c, w, h):
    """B-1 — photograph left, the name right, the list under it."""
    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    px, py, pw, ph = 60.0, 60.0, 1040.0, 880.0
    photo(c, "pharmacy", px, py, pw, ph, (0.52, 0.42))
    keyline(c, px, py, pw, ph, B.CP_CYAN, 0.30, 2.0)

    x0 = 1230.0
    cap_e = 118.0
    y_e = 940.0 - cap_e
    word(c, x0, y_e, cap_e, track=9.0, max_w=w - x0 - 60.0)

    ms = 96.0
    y_b = y_e - 34.0 - ms
    badge_row(c, x0, y_b, ms)

    cap_m = fit_cap(NAME, "Manrope-800", "Manrope", 2060.0)
    y_m = y_b - 40.0 - cap_m
    B.caps(c, x0 + 4.0, y_m, NAME, cap_m, B.WHITE, "Manrope-800", 2.0)

    B.label(c, x0 + 6.0, y_m - 62.0, B.SLOGAN, 36.0, B.CP_MIST, "Inter-400", 4.0)

    services_block(c, ["GENERAL OUTPATIENT", "LABORATORY", "PHARMACY",
                       "ULTRASOUND", "MINOR SURGERY", "HIV CARE"],
                   x0 + 4.0, y_m - 196.0, cols=2, col_w=1130.0, row=64.0, cap=32.0)

    phone_line(c, w - 60.0, 96.0, 30.0, align="right")
    B.caps(c, w - 60.0, 150.0, "OPEN 24 HOURS", 26.0, B.CP_MIST, "Inter-600", 3.0,
           align="right")

    keyline(c, 32, 32, w - 64, h - 64)


def face_services(c, w, h):
    """B-2 — type left, two photographs stacked right, a cyan foot rail."""
    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    for key, x, y, ww, hh, focus in BANNERS[1]["photos"]:
        photo(c, key, x, y, ww, hh, focus)
        keyline(c, x, y, ww, hh, B.CP_CYAN, 0.26, 1.8)

    x0 = 60.0
    cap_e = 100.0
    y_e = 940.0 - cap_e
    word(c, x0, y_e, cap_e, track=8.0, max_w=2100.0)

    ms = 88.0
    y_b = y_e - 30.0 - ms
    badge_row(c, x0, y_b, ms, 28.0, 24.0)

    cap_m = fit_cap(NAME, "Manrope-800", "Manrope", 2180.0)
    y_m = y_b - 34.0 - cap_m
    B.caps(c, x0 + 3.0, y_m, NAME, cap_m, B.WHITE, "Manrope-800", 1.8)

    B.label(c, x0 + 5.0, y_m - 64.0, B.SLOGAN, 32.0, B.CP_MIST, "Inter-400", 3.6)

    services_block(c, BANNERS[1]["services"], x0 + 3.0, y_m - 216.0,
                   cols=2, col_w=1090.0, row=62.0, cap=30.0)

    # foot rail: phone left, the promise right
    c.setFillColor(B.CP_CYAN)
    c.rect(60.0, 150.0, 2260.0, 3.0, stroke=0, fill=1)
    phone_line(c, 60.0, 96.0, 28.0)
    B.caps(c, 2320.0, 96.0, "OPEN 24 HOURS", 26.0, B.CP_MIST, "Inter-600", 3.0,
           align="right")

    keyline(c, 32, 32, w - 64, h - 64)


def face_compact(c, w, h):
    """B-3 — the name centred, one photograph at the right hand edge."""
    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    px, py, pw, ph = 1740.0, 60.0, 600.0, 880.0
    photo(c, "reception", px, py, pw, ph, (0.50, 0.55))
    keyline(c, px, py, pw, ph, B.CP_CYAN, 0.30, 2.0)

    col, x0 = 1620.0, 60.0              # the type column, left of the photograph
    xc = x0 + col / 2.0

    cap_e, cap_b, cap_s, cap_r = 96.0, 26.0, 30.0, 24.0
    ms = 84.0
    g_eb, g_bb, g_bm, g_mr, g_rs, g_rp = 24.0, 14.0, 24.0, 34.0, 28.0, 46.0
    stack = (cap_e + g_eb + ms + g_bb + cap_b + g_bm + 0.0 + g_mr + 5.0 + g_rs
             + cap_s + g_rp + cap_r)
    top = h / 2 + stack / 2 + 24.0      # optical centre, a touch high

    # EDDWALIRO heads it
    B.caps(c, xc, top - cap_e, WORD, cap_e, B.CP_CYAN, "Manrope-800", 8.0,
           align="center", max_w=col)

    y_b = top - cap_e - g_eb - ms
    B.monogram(c, xc - ms / 2.0, y_b, ms, dark=B.WHITE, accent=B.CP_CYAN)

    y_bc = y_b - g_bb - cap_b
    B.caps(c, xc, y_bc, "BCM", cap_b, B.CP_CYAN, "Inter-600", 20.0, align="center")

    cap_m = min(fit_cap(NAME, "Manrope-800", "Manrope", col), 150.0)
    y_m = y_bc - g_bm - cap_m
    B.caps(c, xc, y_m, NAME, cap_m, B.WHITE, "Manrope-800", 1.8, align="center")

    y_r = y_m - g_mr
    c.setFillColor(B.CP_CYAN)
    c.rect(xc - 150.0, y_r, 300.0, 5.0, stroke=0, fill=1)

    y_s = y_r - g_rs - cap_s
    B.label(c, xc, y_s, B.SLOGAN, cap_s, B.CP_MIST, "Inter-400", 3.4,
            align="center")

    rail = "   ·   ".join(BANNERS[2]["services"])
    B.caps(c, xc, y_s - g_rp - cap_r, rail, cap_r, B.CP_MIST, "Inter-500", 1.6,
           align="center", max_w=col)

    phone_line(c, xc, 122.0, 28.0, align="center")
    B.caps(c, xc, 76.0, "OPEN 24 HOURS", 24.0, B.CP_MIST, "Inter-600", 4.0,
           align="center")

    keyline(c, 32, 32, w - 64, h - 64)


FACES = {"road": face_road, "services": face_services, "compact": face_compact}


def face(c, b, w=None, h=None):
    FACES[b["layout"]](c, w or b["w"], h or b["h"])


# --------------------------------------------------------------------- artwork
def artwork(b, path):
    w, h = b["w"], b["h"]
    pw, ph = w + BLEED * 2, h + BLEED * 2 + SLUG
    c = canvas.Canvas(path, pagesize=(pw * MM, ph * MM))
    c.setTitle(f"BCM Medical Centre — {b['id']} banner {w / 1000:.1f} x {h / 1000:.1f} m")
    c.setAuthor("BCM Medical Centre — banner project")

    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, pw, ph, stroke=0, fill=1)
    c.saveState()
    c.translate(BLEED, BLEED + SLUG)
    c.scale(MM, MM)
    face(c, b)
    c.restoreState()

    # bleed marks
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

    # slug
    c.setFillColor(B.WHITE)
    c.rect(0, 0, pw, SLUG, stroke=0, fill=1)
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.2)
    c.line(0, SLUG, pw, SLUG)
    B.caps(c, 3, SLUG - 6.2,
           f"BCM BANNER {b['id']}  |  {w / 1000:.1f} m x {h / 1000:.1f} m  |  "
           f"TRIM {w:.0f} x {h:.0f} mm  |  BLEED {BLEED:.0f} mm  |  "
           f"EYELET/HEM SAFE {SAFE:.0f} mm",
           2.6, B.CP_NAVY, "Inter-600", 0.3)
    B.caps(c, 3, SLUG - 10.8,
           "PVC BANNER 510 g  |  HEM 40 mm WELDED ALL ROUND  |  EYELETS AT 500 mm "
           "CENTRES  |  MATTE FINISH  |  DO NOT SCALE — PLOT AT 100 %",
           2.3, B.CP_NAVY, "Inter-500", 0.25)
    B.caps(c, 3, SLUG - 15.0,
           "PHOTOGRAPHS ARE LICENSED STOCK, COLOUR-RETOUCHED TO SHOW BLACK AFRICAN "
           "PEOPLE — SEE THE LICENCE PAGE. MONOGRAM IS A RECREATION, NOT THE OFFICIAL LOGO.",
           2.1, B.CP_NAVY_MD, "Inter-500", 0.2)
    B.caps(c, pw - 3, 3.0, "CROP MARKS — TRIM AT THE MARKS", 2.2, B.CP_GREY,
           "Inter-500", 0.4, "right")
    c.showPage()
    c.save()
    return path


def face_pdf(b, path):
    """Trim-only face, for mockups and the proof."""
    c = canvas.Canvas(path, pagesize=(b["w"] * MM, b["h"] * MM))
    c.scale(MM, MM)
    face(c, b)
    c.showPage()
    c.save()
    return path


def face_png(b, px_w=1600):
    import pypdfium2 as pdfium
    os.makedirs(WORK, exist_ok=True)
    pdf = os.path.join(WORK, f"{b['slug']}.pdf")
    face_pdf(b, pdf)
    doc = pdfium.PdfDocument(pdf)
    page = doc[0]
    img = page.render(scale=px_w / page.get_size()[0]).to_pil().convert("RGB")
    doc.close()
    return img


# --------------------------------------------------------------------- mockups
def mockup(b, night=False):
    """The banner on a fence, to scale, with its eyelets and shadow."""
    panel = face_png(b, 2000)
    S = 0.34
    GROUND, SKY = 120.0, 240.0
    FENCE_TOP = 2150.0              # top rail of the fence
    LIFT = 1150.0                   # bottom edge above finished ground
    width_mm = 4200.0               # one frame width for all three, so they compare
    above = FENCE_TOP + SKY
    w, h = int(width_mm * S), int((above + GROUND) * S)

    # sky
    if not night:
        sky = np.linspace(np.array([0.80, 0.86, 0.93]),
                          np.array([0.95, 0.94, 0.90]), h).reshape(h, 1, 3)
    else:
        sky = np.linspace(np.array([0.03, 0.05, 0.10]),
                          np.array([0.10, 0.13, 0.20]), h).reshape(h, 1, 3)
    arr = np.repeat(np.clip(sky, 0, 1), w, axis=1)
    img = Image.fromarray((arr * 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")

    floor = h - int(GROUND * S)
    fence_top = floor - int((FENCE_TOP - GROUND) * S)

    # the fence: vertical boards, a top rail, a little grain
    board = (198, 194, 186) if not night else (28, 31, 39)
    d.rectangle([0, fence_top, w, floor], fill=board)
    xb = 0
    while xb < w:
        d.line([xb, fence_top, xb, floor], fill=(0, 0, 0, 22), width=2)
        xb += int(46 * S)
    rail = (176, 171, 162) if not night else (36, 40, 50)
    d.rectangle([0, fence_top, w, fence_top + int(26 * S)], fill=rail)

    # grass strip at the foot
    d.rectangle([0, floor, w, h], fill=(120, 128, 108) if not night else (16, 20, 20))

    bw, bh = int(b["w"] * S), int(b["h"] * S)
    x0 = (w - bw) // 2
    y0 = floor - int((LIFT + b["h"]) * S)

    if night:
        a = np.asarray(panel).astype(np.float32) * 1.05 + 6
        panel = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    panel = panel.resize((bw, bh), Image.LANCZOS)

    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rectangle([x0 + 6, y0 + 8, x0 + bw + 8, y0 + bh + 10], fill=(0, 0, 0, 38))
    img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
    img.paste(panel, (x0, y0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x0, y0, x0 + bw, y0 + bh], outline=(70, 74, 80), width=2)

    # eyelets along the top and bottom hems
    r = max(2, int(6 * S))
    step = int(500 * S)
    for i in range(0, bw, step):
        for yy in (y0 + int(10 * S), y0 + bh - int(10 * S)):
            d.ellipse([x0 + i - r, yy - r, x0 + i + r, yy + r],
                      outline=(120, 126, 134), width=2)
    return img


# ----------------------------------------------------------------------- proof
def proof(path):
    c = D.new_doc(path, "BCM Medical Centre — banners",
                  subject="Three PVC banners for the roadside fence")
    eyebrow = "BCM  ·  MEDICAL CENTRE  ·  BANNERS"

    # ---- page 1 — the three, to relative scale
    D.page_bg(c, "BANNERS", f"{REV}", 1, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "Three banners, one identity", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "Three different banners, each doing a different job: B-1 is read from the road "
           "at speed, B-2 is read standing at the gate, B-3 covers the short run. Same "
           "navy, same type, same badge, same motto — EDDWALIRO at the head of each.",
           (D.PW - 2 * D.M) / MM * 0.72, 3.2, B.NAVY_MID)

    yy = 126 * MM
    for b in BANNERS:
        png = os.path.join(WORK, f"{b['slug']}_mock.png")
        iw, ih = Image.open(png).size
        bw = 62 * MM                     # every mockup is framed the same width,
        bh = bw * ih / iw                # so the three lengths read against each other
        c.drawImage(png, D.M, yy, bw, bh, mask=None)
        c.setStrokeColor(B.GREY)
        c.setLineWidth(0.2)
        c.rect(D.M, yy, bw, bh, stroke=1, fill=0)
        B.label(c, D.M + bw + 8 * MM, yy + bh - 4 * MM,
                f"{b['id']} — {b['title']}", 3.6, B.NAVY, "Inter-600", 1.0)
        B.label(c, D.M + bw + 8 * MM, yy + bh - 9 * MM,
                f"{b['w'] / 1000:.1f} m × {b['h'] / 1000:.1f} m  ·  "
                f"{b['w']:.0f} × {b['h']:.0f} mm", 3.0, B.GREY, "Inter-500", 1.0)
        yy -= bh + 6 * MM

    # ---- pages 2-4 — one banner each, to scale
    for n, b in enumerate(BANNERS, start=2):
        c.showPage()
        D.page_bg(c, b["id"], f"{REV}", n, eyebrow=eyebrow)
        y = D.h1(c, D.PH - 34 * MM, f"{b['id']} — {b['title']}", 8.0)
        D.para(c, D.M, y + 2 * MM, b["job"], (D.PW - 2 * D.M) / MM * 0.78, 3.2,
               B.NAVY_MID)

        png = os.path.join(WORK, f"{b['slug']}_trim.png")
        img = face_png(b, 1800)
        img.save(png, "PNG")
        bh = min(244.0 * b["h"] / b["w"], 60.0)     # never crowd the heading
        bw = bh * b["w"] / b["h"]
        px = D.M / MM + (248.0 - bw) / 2.0
        py = (96.0 + (60.0 - bh) / 2.0) * MM
        c.drawImage(png, px * MM, py, bw * MM, bh * MM, mask=None)
        c.setStrokeColor(B.TEAL)
        c.setLineWidth(0.4)
        c.rect(px * MM, py, bw * MM, bh * MM, stroke=1, fill=0)
        B.label(c, px * MM + bw * MM / 2, py - 6 * MM,
                f"W {b['w']:.0f} mm", 3.2, B.NAVY, "Inter-600", 1.0, "center")
        B.label(c, (px + bw) * MM + 2 * MM, py + bh * MM / 2,
                f"H {b['h']:.0f} mm", 3.2, B.NAVY, "Inter-600", 1.0)

        # notes: two columns under the banner, full measure
        ty = 84 * MM
        rows = []
        for key, x, y2, ww, hh, focus in b["photos"]:
            d, st = P.ppi(key, ww, hh)
            rows.append(f"{P.PHOTOS[key]['asset']} — {P.PHOTOS[key]['title']}, "
                        f"{ww:.0f} × {hh:.0f} mm at {d} ppi ({st}).")

        left = [f"Service list: {', '.join(x.lower() for x in b['services'])}.",
                f"Hem and eyelet zone: {SAFE:.0f} mm clear all round — no type, no faces.",
                f"Bleed {BLEED:.0f} mm, crop marks in the slug. Plot at 100 %, never scale."]
        B.label(c, D.M, ty, "HOW IT IS SET", 4.0, B.TEAL, "Inter-600", 1.6)
        D.bullets(c, D.M, ty - 8 * MM, left, 118 * MM, 3.0, B.NAVY_MID)

        B.label(c, D.M + 130 * MM, ty, "PHOTOGRAPHS", 4.0, B.TEAL, "Inter-600", 1.6)
        D.bullets(c, D.M + 130 * MM, ty - 8 * MM, rows +
                  ["Colour-retouched so the people read Black African; licence on page 6."],
                  118 * MM, 3.0, B.NAVY_MID)


    # ---- page 5 — production
    c.showPage()
    D.page_bg(c, "PRODUCTION", f"{REV}", 5, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "Production specification", 8.0)
    B.label(c, D.M, y - 2 * MM, "MATERIAL  —  CONFIRM WITH THE PRINTER", 4.0, B.TEAL,
            "Inter-600", 1.6)
    D.bullets(c, D.M, y - 10 * MM, [
        "510 g/m² PVC banner, matte, printed at 720–1440 dpi. Industry-typical for a "
        "fence banner of this size — not a quotation.",
        "40 mm welded hem all round, eyelets at 500 mm centres, stainless or brass. "
        "The artwork keeps 60 mm clear of the trim so nothing important is hemmed away.",
        "Finish: matte, not gloss. Gloss mirrors the sky and kills the navy.",
        "Fix at every eyelet, not every second one: a 3.8 m banner sails in wind and "
        "will tear at the corners if it is tied off at four points only.",
    ], 150 * MM, 3.0, B.NAVY_MID)

    # sizes table, for the printer
    rows = [[b["id"], f"{b['w']:.0f}", f"{b['h']:.0f}",
             f"{b['w'] / 1000:.2f} m", f"{b['h'] / 1000:.2f} m",
             f"{b['w'] * b['h'] / 1e6:.2f} m²"] for b in BANNERS]
    D.table(c, D.M, 150 * MM,
            [("Banner", 26, "left"), ("Trim W mm", 32, "left"),
             ("Trim H mm", 32, "left"), ("W m", 26, "left"), ("H m", 26, "left"),
             ("Area", 30, "left")],
            rows, row_h=6.4 * MM, head_h=7.0 * MM, cap=3.0, head_cap=2.8)
    B.label(c, D.M, 96 * MM, "FILE SETUP", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, 88 * MM, [
        "One PDF per banner, drawn 1 : 1 in millimetres, 10 mm bleed, crop marks in the "
        "slug. CMYK conversion is left to the printer's profile.",
        "Type is live text in embedded fonts — no outlining needed, but the printer may "
        "outline it.",
        "Photographs are placed at the resolution the working files allow and are "
        "recorded per banner on the previous pages. Before print, the retouch is repeated "
        "on the full-resolution originals (Pexels links in the licence table) or the "
        "clinic's own team is photographed.",
    ], 150 * MM, 3.0, B.NAVY_MID)

    B.label(c, D.M, 52 * MM, "BEFORE PRINT", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, 44 * MM, [
        "Confirm the three sizes with the fence: 3.8 m, 3.4 m and 2.4 m, all 1.0 m high.",
        "Confirm the spelling EDDWALIRO, and that BCM Medical Centre is the wording that "
        "goes on the fence.",
        "The service lists are split across the three banners so no service repeats. "
        "Tell us if any list must change.",
        "The monogram is a recreation, not BCM's official logo.",
    ], 150 * MM, 3.0, B.NAVY_MID)

    # ---- page 6 — photographs and licence
    c.showPage()
    D.page_bg(c, "PHOTOGRAPHS", f"{REV}", 6, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "Photographs and licence", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "All photography is licensed from Pexels under its free licence: commercial use, "
           "modification and no attribution required — credited here as good practice. "
           "Every frame used has been colour-retouched so the people read Black African; "
           "the retouch is recorded against each asset below. The people are models, not "
           "BCM staff or patients.", (D.PW - 2 * D.M) / MM * 0.86, 3.2, B.NAVY_MID)

    used = []
    for b in BANNERS:
        for key, *_ in b["photos"]:
            if key not in used:
                used.append(key)

    rows = []
    for key in used:
        m = P.PHOTOS[key]
        rows.append([m["asset"], f"{m['title']}  ·  pexels.com/photo/{m['id']}",
                     m.get("creator", "—"), "Pexels — free, modified"])

    yy = y - 12 * MM
    B.label(c, D.M, yy, "ASSET", 3.2, B.TEAL, "Inter-600", 1.4)
    B.label(c, D.M + 24 * MM, yy, "PHOTOGRAPH", 3.2, B.TEAL, "Inter-600", 1.4)
    B.label(c, D.M + 154 * MM, yy, "CREATOR", 3.2, B.TEAL, "Inter-600", 1.4)
    B.label(c, D.M + 200 * MM, yy, "LICENCE", 3.2, B.TEAL, "Inter-600", 1.4)
    yy -= 5 * MM
    for r in rows:
        B.label(c, D.M, yy, r[0], 3.0, B.NAVY, "Inter-600", 1.0)
        B.caps(c, D.M + 24 * MM, yy, r[1], 2.9, B.NAVY_MID, "Inter-400", 0.2,
               max_w=126 * MM)
        B.caps(c, D.M + 154 * MM, yy, r[2], 2.9, B.NAVY_MID, "Inter-400", 0.2)
        B.caps(c, D.M + 200 * MM, yy, r[3], 2.9, B.NAVY_MID, "Inter-400", 0.2)
        yy -= 5.2 * MM

    # the four frames, small, for identification
    tw = 50.0
    ty = 96 * MM
    tx = D.M
    for key in used:
        ph = P.prepare(key, tw, tw * 0.66, focus=(0.5, 0.35), dpi=110)
        c.drawImage(ph, tx * MM, ty, tw * MM, tw * 0.66 * MM, mask=None)
        c.setStrokeColor(B.MIST)
        c.setLineWidth(0.3)
        c.rect(tx * MM, ty, tw * MM, tw * 0.66 * MM, stroke=1, fill=0)
        B.label(c, tx * MM, ty - 4 * MM, P.PHOTOS[key]["asset"], 2.6, B.GREY,
                "Inter-500", 0.8)
        tx += tw + 6

    B.caps(c, D.M, 30 * MM,
           "LICENCE: PEXELS FREE LICENCE — COMMERCIAL USE, MODIFICATION AND NO "
           "ATTRIBUTION REQUIRED; NOT FOR RESALE UNALTERED, NOT IMPLYING ENDORSEMENT. "
           "ALL FOUR FRAMES CARRY A COLOUR RETOUCH (AI ASSISTED) SO THE PEOPLE READ "
           "BLACK AFRICAN; THE RETOUCH IS RECORDED HERE AND AGAINST EACH ASSET.",
           2.6, B.GREY, "Inter-500", 0.4)

    c.save()
    return path


def main():
    for d in (ART_DIR, WORK, os.path.join(OUT_DIR, "lookbook")):
        os.makedirs(d, exist_ok=True)
    configure()

    made = []
    for b in BANNERS:
        p = artwork(b, os.path.join(ART_DIR, f"BCM-Banner-{b['id']}.pdf"))
        made.append(p)
    print("artwork:", ", ".join(os.path.basename(p) for p in made))

    for b in BANNERS:
        for night, tag in ((False, "day"), (True, "night")):
            img = mockup(b, night=night)
            img.save(os.path.join(OUT_DIR, "lookbook", f"M-{b['slug']}-{tag}.png"))
        mockup(b).save(os.path.join(WORK, f"{b['slug']}_mock.png"))
    # a single overview strip
    overview(banner_overview(), os.path.join(OUT_DIR, "lookbook", "M-00-banner-set.png"))
    print("mockups: per banner day + night, set overview")

    print("proof:", os.path.basename(proof(os.path.join(OUT_DIR, "BCM-Banners.pdf"))))
    write_index()
    print("index.html")


def banner_overview():
    """All three elevations on one sheet, relative scale."""
    imgs = [mockup(b) for b in BANNERS]
    pad = 60
    W = max(i.width for i in imgs) + pad * 2
    H = sum(i.height for i in imgs) + pad * (len(imgs) + 1)
    out = Image.new("RGB", (W, H), (247, 249, 251))
    y = pad
    for im in imgs:
        out.paste(im, ((W - im.width) // 2, y))
        y += im.height + pad
    return out


def overview(img, path):
    img.save(path)
    return path


def write_index():
    cards = []
    for b in BANNERS:
        cards.append(f"""
    <figure class="card">
      <img src="lookbook/M-{b['slug']}-day.png" alt="{b['id']} banner elevation">
      <figcaption><b>{b['id']} — {b['title']}</b>
        <span>{b['w'] / 1000:.1f} m × {b['h'] / 1000:.1f} m · {b['w']:.0f} × {b['h']:.0f} mm</span>
        <a href="artwork/BCM-Banner-{b['id']}.pdf">print file</a></figcaption>
    </figure>""")

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BCM Medical Centre — banners</title>
<style>
 body{{margin:0;background:#f4f7f9;color:#16233f;
   font:16px/1.6 Inter,Helvetica,Arial,sans-serif}}
 header{{background:#16233f;color:#fff;padding:48px 6vw 40px}}
 h1{{font-size:clamp(28px,4.6vw,50px);margin:.2em 0 .4em;line-height:1.03}}
 header p{{max-width:66ch;color:#cfd9e6}}
 .eyebrow{{letter-spacing:.3em;font-size:11px;color:#2ba9e0}}
 main{{padding:32px 6vw 72px}}
 figure.card{{margin:0 0 26px;background:#fff;border-radius:6px;overflow:hidden;
   box-shadow:0 2px 14px rgba(22,35,63,.08)}}
 figure.card img{{width:100%;display:block}}
 figcaption{{padding:12px 16px;font-size:13px;color:#4b5b73}}
 figcaption span{{display:block;font-size:12px;color:#8fa2b8;margin:2px 0 6px}}
 a{{color:#1b87b8}}
 table{{width:100%;border-collapse:collapse;font-size:14px;background:#fff}}
 th,td{{text-align:left;padding:10px 14px;border-bottom:1px solid #e3eaf2}}
 th{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#8fa2b8}}
 .note{{color:#4b5b73;font-size:13px;max-width:82ch}}
 nav{{padding:0 6vw 8px;font-size:13px}} nav a{{margin-right:18px}}
</style></head><body>
<header>
  <div class="eyebrow">BCM · MEDICAL CENTRE · BANNERS</div>
  <h1>Three banners for the fence</h1>
  <p>3.8 m, 3.4 m and 2.4 m long, all 1.0 m high. Three different layouts, one
     identity: navy field, EDDWALIRO at the head, MEDICAL CENTRE the widest line,
     the motto under it, a licensed photograph and the clinic's own service list.</p>
</header>
<nav><a href="../index.html">All artwork</a>
     <a href="../door-1/index.html">Door 1</a>
     <a href="../door-2/index.html">Door 2</a>
     <a href="../door-3/index.html">Door 3</a>
     <a href="../sign/index.html">Sign post</a></nav>
<main>
  <figure class="card"><img src="lookbook/M-00-banner-set.png" alt="All three banners">
    <figcaption><b>The set</b><span>relative scale</span></figcaption></figure>
  {"".join(cards)}
  <table>
    <tr><th>File</th><th>What it is</th></tr>
    <tr><td><a href="BCM-Banners.pdf">BCM-Banners.pdf</a></td>
        <td>Six pages — the set, each banner to scale, production, photographs and licence</td></tr>
    <tr><td><a href="BCM-Banners-Package.zip">BCM-Banners-Package.zip</a></td>
        <td>Everything: artwork, elevations, proof</td></tr>
  </table>
  <p class="note">Sizes are the client's: 3.8 m, 3.4 m and 2.4 m by 1.0 m. Substrate,
     hem and eyelets are industry-typical for a fence banner — confirm with the printer.
     The monogram is a recreation, not BCM's official logo.</p>
</main></body></html>
"""
    open(os.path.join(OUT_DIR, "index.html"), "w").write(html)


if __name__ == "__main__":
    main()
