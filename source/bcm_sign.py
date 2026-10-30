"""BCM Medical Centre — name-only sign post panel.

Separate deliverable from the door film set: one panel, no services, no
photographs. Built to the client's measurement — 3.10 ft × 2.11 ft, landscape.

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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "bcm", "sign")
ART_DIR = os.path.join(OUT_DIR, "artwork")
WORK = os.path.join(ROOT, "source", ".work", "bcm_sign")

# --- the client's measurement -------------------------------------------------
FT = 304.8
W_FT, H_FT = 3.10, 2.11
W, H = round(W_FT * FT, 1), round(H_FT * FT, 1)     # 944.9 × 643.1 mm
BLEED, SLUG = 10.0, 22.0
SAFE = 25.0
REV = "Rev A  ·  2026-10-30"
NAME = "MEDICAL CENTRE"

B.register_fonts()


# --------------------------------------------------------------------- helpers
def fit_cap(text, weight, family, target_w):
    """Cap height (mm) that makes `text` exactly `target_w` wide."""
    cap = 100.0
    size = B.font_for(cap, family)
    w = pdfmetrics.stringWidth(text, weight, size)
    return cap * target_w / w


def face(c, w=W, h=H, variant="A", slogan=True, tel=False):
    """Draw the sign face at trim size, origin bottom-left, in millimetres."""
    M = 46.0
    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    if variant == "A":                       # centred, typographic
        ms, cap_b, cap_s = 132.0, 25.0, 19.0
        gap_badge, gap_mb, gap_rule = 26.0, 24.0, 40.0
        cap_m = min(fit_cap(NAME, "Manrope-800", "Manrope", w - 2 * M), 150.0)
        block = ms + gap_badge + cap_b + gap_mb + cap_m
        top = h / 2 + block / 2
        B.monogram(c, (w - ms) / 2, top - ms, ms, dark=B.WHITE, accent=B.CP_CYAN)
        B.caps(c, w / 2, top - ms - gap_badge - cap_b, "BCM", cap_b, B.CP_CYAN,
               "Inter-600", 26.0, align="center")
        y_m = top - block
        B.caps(c, w / 2, y_m, NAME, cap_m, B.WHITE, "Manrope-800", 1.6,
               align="center")
        ry = y_m - gap_rule
        c.setFillColor(B.CP_CYAN)
        c.rect(w / 2 - 130, ry, 260, 5.0, stroke=0, fill=1)
        if slogan:
            B.label(c, w / 2, ry - 44.0, B.SLOGAN, cap_s, B.CP_MIST,
                    "Inter-400", 3.4, align="center")
        if tel:
            B.label(c, w / 2, 56.0, f"TEL {B.TEL}", 16.0, B.CP_CYAN,
                    "Inter-600", 2.2, align="center")

    else:                                    # B: badge-left lockup
        ms, cap_b, cap_s = 118.0, 26.0, 18.0
        gap_bm, gap_rule, gap_sl, gap_badge = 20.0, 34.0, 30.0, 34.0
        cap_m = min(fit_cap(NAME, "Manrope-800", "Manrope",
                            w - 2 * M - ms - gap_badge), 132.0)
        name_w = pdfmetrics.stringWidth(NAME, "Manrope-800", B.font_for(cap_m))
        block_w = ms + gap_badge + name_w
        block_h = cap_b + gap_bm + cap_m + (
            (gap_rule + 5.0 + gap_sl + cap_s) if slogan else 0)
        top = h / 2 + block_h / 2
        x0 = (w - block_w) / 2

        mid = top - (cap_b + gap_bm + cap_m / 2)
        B.monogram(c, x0, mid - ms / 2, ms, dark=B.WHITE, accent=B.CP_CYAN)

        tx = x0 + ms + gap_badge
        B.caps(c, tx, top - cap_b, "BCM", cap_b, B.CP_CYAN, "Inter-600", 18.0)
        y_m = top - cap_b - gap_bm - cap_m
        B.caps(c, tx - 1.2, y_m, NAME, cap_m, B.WHITE, "Manrope-800", 1.2)
        if slogan:
            ry = y_m - gap_rule
            c.setFillColor(B.CP_CYAN)
            c.rect(tx, ry, name_w * 0.32, 5.0, stroke=0, fill=1)
            B.label(c, tx - 0.6, ry - gap_sl - cap_s, B.SLOGAN, cap_s,
                    B.CP_MIST, "Inter-400", 3.2)
        if tel:
            B.label(c, w - M, 56.0, f"TEL {B.TEL}", 16.0, B.CP_CYAN,
                    "Inter-600", 2.2, align="right")

    # engraved keyline, so the panel reads as a made object, not a painted wall
    c.saveState()
    c.setStrokeColor(B.WHITE)
    c.setStrokeAlpha(0.14)
    c.setLineWidth(1.2)
    c.rect(30, 30, w - 60, h - 60, stroke=1, fill=0)
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
               f"TRIM {W:.1f} x {H:.1f} mm  (3.10 ft x 2.11 ft)",
               2.7, B.CP_NAVY, "Inter-600", 0.3)
        B.caps(c, 3, SLUG - 11.2,
               f"BLEED {BLEED:.0f} mm  |  SAFE {SAFE:.0f} mm  |  {REV}  |  "
               "DOUBLE-SIDED — BOTH FACES IDENTICAL",
               2.3, B.CP_NAVY, "Inter-500", 0.25)
        B.caps(c, 3, SLUG - 15.4,
               "NAME ONLY — NO SERVICE LIST, NO PHOTOGRAPH. MONOGRAM IS A RECREATION: "
               "REPLACE WITH CLIENT VECTOR LOGO BEFORE PLOT.",
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
    """Elevation: the panel on two posts, to scale, bottom-lit and night variants."""
    S = 0.95
    panel = _panel_png(variant, tel=tel)
    GROUND = 120.0                       # ground band drawn at the foot
    PANEL_CENTRE = 1500.0                # panel centre above finished ground level
    TOP_MARGIN = 70.0
    above = PANEL_CENTRE + H / 2 + TOP_MARGIN
    width_mm = 2000.0
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
    gap, post_w = 520.0, 90.0
    panel_top_mm = PANEL_CENTRE + H / 2
    top_y = floor - int(panel_top_mm * S)
    for sx in (-gap / 2, gap / 2):
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
    """Scale drawing of the panel with its measurements called out."""
    S, pad = 0.42, 210
    w, h = int((W + pad * 2) * S), int((H + pad * 2) * S)
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    panel = _panel_png(variant, px_w=1800).resize((int(W * S), int(H * S)),
                                                  Image.LANCZOS)
    x0, y0 = int(pad * S), int(pad * S)
    img.paste(panel, (x0, y0))
    d.rectangle([x0, y0, x0 + panel.width, y0 + panel.height],
                outline=(22, 35, 63), width=2)
    cyan = (43, 169, 224)
    yy = y0 + panel.height + 90
    d.line([x0, yy, x0 + panel.width, yy], fill=cyan, width=2)
    for x in (x0, x0 + panel.width):
        d.line([x, yy - 14, x, yy + 14], fill=cyan, width=2)
    xx = x0 - 90
    d.line([xx, y0, xx, y0 + panel.height], fill=cyan, width=2)
    for y in (y0, y0 + panel.height):
        d.line([xx - 14, y, xx + 14, y], fill=cyan, width=2)
    return img


# ----------------------------------------------------------------------- proof
def proof(path):
    c = D.new_doc(path, "BCM Medical Centre — sign post panel",
                  subject="Name-only sign post panel 3.10 ft x 2.11 ft")
    eyebrow = "BCM  ·  MEDICAL CENTRE  ·  SIGN POST PANEL"

    # ---- page 1 — the panel, to scale, measured
    D.page_bg(c, "SIGN POST PANEL", f"{REV}", 1, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "The name, on a post", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "One panel, the name only — no service list, no photograph. Built to the "
               "client's measurement of 3.10 ft × 2.11 ft, landscape, which is "
               f"{W:.0f} × {H:.0f} mm. Double-sided: both faces carry the same artwork.",
               (D.PW - 2 * D.M) / MM * 0.56, 3.3, B.NAVY_MID)

    scale = 168.0 / W
    pw, ph = W * scale, H * scale
    px, py = D.M, 44 * MM
    c.saveState()
    c.translate(px, py)
    c.scale(scale * MM, scale * MM)
    face(c)
    c.restoreState()
    c.setStrokeColor(B.TEAL)
    c.setLineWidth(0.4)
    c.rect(px, py, pw * MM, ph * MM, stroke=1, fill=0)
    B.label(c, px + pw * MM / 2, py - 8 * MM,
            f"W {W_FT:.2f} ft  /  {W:.0f} mm", 3.4, B.NAVY, "Inter-600", 1.0, "center")
    B.label(c, px, py + ph * MM + 5 * MM,
            f"H {H_FT:.2f} ft  /  {H:.0f} mm", 3.4, B.NAVY, "Inter-600", 1.0)

    tx = px + pw * MM + 22 * MM
    tw = D.PW - tx - D.M
    yy = D.PH - 92 * MM
    B.label(c, tx, yy, "MEASUREMENTS", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, tx, yy - 8 * MM, [
        f"Trim: {W:.1f} × {H:.1f} mm — 3.10 ft × 2.11 ft at 304.8 mm to the foot.",
        f"Bleed: {BLEED:.0f} mm all round, so the printed sheet is "
        f"{W + 2 * BLEED:.0f} × {H + 2 * BLEED:.0f} mm. Safe area {SAFE:.0f} mm in from trim.",
        "Artwork is supplied at 1 : 1 in millimetres — plot it, do not scale it.",
        "Both faces are in the one PDF: print the file twice for a two-sided panel, or "
        "once per face for two single-sided panels back to back.",
    ], tw, 3.0, B.NAVY_MID)

    # ---- page 2 — options
    c.showPage()
    D.page_bg(c, "OPTIONS", f"{REV}", 2, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "Two ways to set the name", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "A is the recommendation: the badge sits above a centred name, so the words "
           "are the widest thing on the sign and the eye lands on MEDICAL CENTRE. B repeats "
           "the lockup used on the door panes, badge left, name right, for continuity "
           "between the sign post and the stickers.",
           (D.PW - 2 * D.M) / MM, 3.2, B.NAVY_MID)

    sw = 118.0
    for i, (v, cap_txt) in enumerate((("A", "OPTION A — centred (recommended)"),
                                      ("B", "OPTION B — badge-left lockup"))):
        sc = sw / W
        px = D.M + i * (sw + 26) * MM
        py = 84 * MM
        c.saveState()
        c.translate(px, py)
        c.scale(sc * MM, sc * MM)
        face(c, variant=v)
        c.restoreState()
        c.setStrokeColor(B.TEAL)
        c.setLineWidth(0.4)
        c.rect(px, py, sw * MM, H * sc * MM, stroke=1, fill=0)
        B.label(c, px, py - 8 * MM, cap_txt, 3.2, B.GREY, "Inter-600", 1.2)

    tx = D.M + 2 * (sw + 26) * MM
    tw = D.PW - tx - D.M
    yy = 150 * MM
    B.label(c, tx, yy, "EITHER WAY", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, tx, yy - 8 * MM, [
        "The name is set at the largest size the panel will take — it spans the full "
        "measure, which is what makes it pointable from across the road.",
        "BCM stays small and cyan above it: the initials, not the headline.",
        "The slogan sits under the name and can be dropped if you want nothing but the "
        "name on the post.",
        "The telephone can be added at the foot — say the word and it goes on both faces.",
    ], tw, 3.0, B.NAVY_MID)

    # ---- page 3 — on the post
    c.showPage()
    D.page_bg(c, "ON THE POST", f"{REV}", 3, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "How it sits at the entrance", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "Drawn to scale: panel centre 1500 mm above finished ground level, posts at 520 mm "
           "centres. Mounting height and post centres are proposals — confirm on site.",
           (D.PW - 2 * D.M) / MM, 3.2, B.NAVY_MID)
    for i, night in enumerate((False, True)):
        png = os.path.join(WORK, f"sign_mock_{'night' if night else 'day'}.png")
        if not os.path.exists(png):
            continue
        iw, ih = Image.open(png).size
        box_w = 118 * MM
        box_h = box_w * ih / iw
        x = D.M + i * 128 * MM
        c.drawImage(png, x, 34 * MM, box_w, box_h, mask=None)
        c.setStrokeColor(B.GREY)
        c.setLineWidth(0.2)
        c.rect(x, 34 * MM, box_w, box_h, stroke=1, fill=0)
        B.label(c, x, 29 * MM,
                "DAY — MATTE FACE, STREET LIGHT" if not night else
                "NIGHT — IF THE PANEL IS LIT", 3.0, B.GREY, "Inter-600", 1.2)
    B.label(c, D.M, 24 * MM, "DRAWN TO SCALE  ·  PANEL CENTRE 1500 MM ABOVE FINISHED GROUND LEVEL",
            2.8, B.GREY, "Inter-500", 1.0)

    # ---- page 4 — specification
    c.showPage()
    D.page_bg(c, "SPECIFICATION", f"{REV}", 4, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "Production specification", 8.0)
    B.label(c, D.M, y - 2 * MM, "SUBSTRATE  —  CONFIRM WITH THE SIGNWRITER", 4.0,
            B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, y - 10 * MM, [
        "3 mm aluminium composite (ACM) panel, matte white, direct-to-substrate UV print, "
        "or 3 mm ACM with cast vinyl applied and laminated — industry-typical, not a "
        "quotation.",
        "Double-sided: either two printed faces bonded back to back on one ACM core, or "
        "two panels on a frame. The artwork is identical on both faces.",
        "Edges: 3 mm radius, sealed. The artwork bleeds 10 mm and is cut back to trim, so "
        "no white edge shows.",
        "Finish: matte anti-glare laminate. Gloss will mirror the sky and kill the contrast "
        "the navy depends on.",
    ], 168 * MM, 3.0, B.NAVY_MID)

    B.label(c, D.M, 108 * MM, "FIXING  —  CONFIRM WITH THE INSTALLER", 4.0, B.TEAL,
            "Inter-600", 1.6)
    D.bullets(c, D.M, 100 * MM, [
        "Two 76 mm galvanised posts at 520 mm centres, set 600 mm into a concrete footing; "
        "panel centre 1500 mm above finished ground level.",
        "Stainless fixings through the face into a bracket, or a channel frame behind the "
        "panel — both keep the face free of bolts. Do not drill the printed face.",
        "Wind loading: a 0.61 m² panel on two posts is a modest sail, but the footing and "
        "the bracket still need the signwriter's own calculation for the site.",
    ], 168 * MM, 3.0, B.NAVY_MID)

    B.label(c, D.M, 70 * MM, "BEFORE PLOT", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, 62 * MM, [
        "Measurement is the client's: 3.10 ft × 2.11 ft. Check it against the panel the "
        "signwriter is actually making before the file is plotted.",
        "The monogram is a recreation, not BCM's official logo — swap the vector in.",
        "Confirm the fascia wording: the clinic's own board reads Community Health Centre; "
        "this sign uses BCM Medical Centre as instructed.",
        "The two help-line numbers, if they go on, come off the clinic's premises boards.",
    ], 168 * MM, 3.0, B.NAVY_MID)

    c.save()
    return path


# ------------------------------------------------------------------------ main
def main():
    os.makedirs(ART_DIR, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "lookbook"), exist_ok=True)

    a = artwork(os.path.join(ART_DIR, "BCM-Sign-Name-Only.pdf"), variant="A")
    b = artwork(os.path.join(ART_DIR, "BCM-Sign-Name-Only-Option-B.pdf"), variant="B",
                faces=("FACE A",))
    print("artwork:", os.path.basename(a), os.path.basename(b))

    for night, name in ((False, "M-01-sign-day.png"), (True, "M-02-sign-night.png")):
        img = mockup(night=night)
        img.save(os.path.join(OUT_DIR, "lookbook", name))
        img.save(os.path.join(WORK, f"sign_mock_{'night' if night else 'day'}.png"))
    dimensioned().save(os.path.join(OUT_DIR, "lookbook", "M-03-sign-dimensions.png"))
    print("mockups: day, night, dimensions")

    print("proof:", os.path.basename(
        proof(os.path.join(OUT_DIR, "BCM-Sign-Panel.pdf"))))

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
  <h1>The name, on a post</h1>
  <p>3.10 ft × 2.11 ft — {W:.0f} × {H:.0f} mm, landscape, double-sided. Name only:
     no service list, no photograph.</p>
</header>
<nav><a href="../index.html">All artwork</a>
     <a href="../door-1/index.html">Door 1</a>
     <a href="../door-2/index.html">Door 2</a>
     <a href="../door-3/index.html">Door 3</a></nav>
<main>
  <figure><img src="lookbook/M-01-sign-day.png" alt="Sign post panel, day elevation">
    <figcaption>On the post — day. Panel centre 1500 mm above finished ground level,
      76 mm posts at 520 mm centres.</figcaption></figure>
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
    <tr><td><a href="artwork/BCM-Sign-Name-Only-Option-B.pdf">BCM-Sign-Name-Only-Option-B.pdf</a></td>
        <td>Print file — option B, badge-left lockup</td></tr>
    <tr><td><a href="BCM-Sign-Panel.pdf">BCM-Sign-Panel.pdf</a></td>
        <td>Four pages — panel to scale, options, on the post, specification</td></tr>
  </table>
  <p class="note">Monogram is a recreation, not BCM's official logo. Measurements are the
     client's. Substrate and fixings are industry-typical proposals — confirm with the
     signwriter.</p>
</main></body></html>
"""
    open(os.path.join(OUT_DIR, "index.html"), "w").write(html)
    print("index.html")


if __name__ == "__main__":
    main()
