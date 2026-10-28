"""CarePoint documents: panel schedule + licence log + lookbook."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image

import cp_docutil as D
import cp_brand as B
import cp_panels as PN
import cp_photos as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "carepoint")
MM = D.MM

DOOR_LEAVES = [["CP-08 / CP-07", "Outer leaf, left — fixed", "900", "Two panes",
                "Reception over Antenatal"],
               ["CP-01 / CP-04", "Inner leaf, left — opening", "900", "Two panes",
                "Dental over Physiotherapy"],
               ["CP-02 / CP-05", "Inner leaf, right — opening", "900", "Two panes",
                "Paediatrics over Services board"],
               ["CP-06 / CP-03", "Outer leaf, right — fixed", "900", "Two panes",
                "Pharmacy over Laboratory"]]


WORK = os.path.join(ROOT, "source", ".work")


def jpg(path, max_w=1400):
    """Compressed stand-in for a big PNG, so the PDFs stay a sensible size."""
    os.makedirs(WORK, exist_ok=True)
    out = os.path.join(WORK, os.path.basename(path).rsplit(".", 1)[0]
                       + f"_{max_w}.jpg")
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(path):
        return out
    im = Image.open(path).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(out, "JPEG", quality=90, optimize=True)
    return out


def schedule():
    path = os.path.join(BASE, "docs", "CP-01-Panel-Schedule.pdf")
    c = D.new_doc(path, "CarePoint — panel schedule and licence log")

    # ---- 1 · schedule ---------------------------------------------------
    D.page_bg(c, "CP / OWV / 01", "Rev R2  ·  2026-10-28  ·  PROVISIONAL", 1,
              eyebrow="CAREPOINT MEDICAL CENTER  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Panel schedule", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "Eight panes across four 900 mm door leaves, rebuilt from the client's own shopfront "
               "photograph. Each leaf carries an upper and a lower glass pane, so each pane is its own "
               "print piece. Pane proportions were measured off that photograph and scaled to a "
               "standard 900 mm leaf — confirm every figure on site before release.",
               (D.PW - 2 * D.M) / MM, 3.3, B.NAVY_MID)
    y -= 3 * MM
    cols = [("Panel", 16, "left"), ("Service", 40, "left"), ("W × H (mm)", 26, "left"),
            ("Aspect", 18, "left"), ("Photograph", 22, "left"),
            ("Coverage", 20, "left"), ("Placement", 58, "left"), ("Status", 22, "left")]
    rows = []
    placement = {"CP-01": "Left inner leaf, upper", "CP-04": "Left inner leaf, lower",
                 "CP-02": "Right inner leaf, upper", "CP-05": "Right inner leaf, lower",
                 "CP-03": "Right outer leaf, upper", "CP-06": "Right outer leaf, lower",
                 "CP-07": "Left outer leaf, upper", "CP-08": "Left outer leaf, lower"}
    for p in PN.PANELS:
        rows.append([p["id"], p["service"],
                     f"{p['w']} × {p['h']}", p["aspect"],
                     P.PHOTOS[p["photo"]]["asset"] if p["photo"] else "GRAPHIC",
                     f"{(p['h'] - (400 if p['h'] >= PN.UPPER_H else 420)) / p['h'] * 100:.0f}%",
                     placement[p["id"]], "PROVISIONAL"])
    y = D.table(c, D.M, y, cols, rows, row_h=10.0 * MM, cap=2.9) - 6 * MM

    B.label(c, D.M, y, "DOOR SURVEY USED FOR THIS SET", 4.0, B.TEAL, "Inter-600", 1.6)
    y -= 6 * MM
    cols2 = [("Leaf pair", 30, "left"), ("Movement", 48, "left"), ("Leaf width", 22, "left"),
             ("Panes", 20, "left"), ("Upper / lower", 62, "left")]
    y = D.table(c, D.M, y, cols2, DOOR_LEAVES, row_h=8.0 * MM, cap=2.9) - 5 * MM
    D.para(c, D.M, y,
           "Frames are timber, 60 mm face; two glazed panes per leaf separated by a 60 mm rail. "
           "The site is a shopfront unit under a rendered soffit — the film must be applied to the "
           "inside face if the glazing is single-pane and the leaf is exposed to rain.",
           (D.PW - 2 * D.M) / MM, 3.1, B.NAVY_MID)
    c.showPage()

    # ---- 2 · pane detail ----------------------------------------------
    D.page_bg(c, "CP / OWV / 01", "Rev R2  ·  2026-10-28  ·  PROVISIONAL", 2,
              eyebrow="CAREPOINT MEDICAL CENTER  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Pane detail — crop logic and production notes", 8.0)
    cw, ch = 88 * MM, 46 * MM
    for i, p in enumerate(PN.PANELS):
        col, row = i % 3, i // 3
        x = D.M + col * (cw + 8 * MM)
        cy = D.PH - 46 * MM - ch - row * (ch + 7 * MM)
        c.setFillColor(B.PAPER)
        c.rect(x, cy, cw, ch, stroke=0, fill=1)
        c.setFillColor(B.TEAL)
        c.rect(x, cy + ch - 1.6 * MM, cw, 1.6 * MM, stroke=0, fill=1)
        B.label(c, x + 4 * MM, cy + ch - 8 * MM, p["id"], 4.4, B.NAVY, "Inter-600", 1.0)
        B.caps(c, x + 20 * MM, cy + ch - 8.2 * MM, p["service"], 4.0, B.NAVY, "Manrope-700", 0.5)
        B.label(c, x + 4 * MM, cy + ch - 14 * MM,
                f"{p['w']} × {p['h']} mm  ·  {p['aspect']}  ·  {p['sub']}", 2.9, B.GREY,
                "Inter-400", 0.4)
        asset = (P.PHOTOS[p["photo"]]["asset"] + "  " + P.PHOTOS[p["photo"]]["creator"]
                 if p["photo"] else "No photograph — type only")
        yy = D.para(c, x + 4 * MM, cy + ch - 21 * MM, "ASSET  " + asset, cw - 8 * MM, 2.9,
                    B.TEAL, 1.55, "Inter-600")
        D.para(c, x + 4 * MM, yy - 2 * MM, p["note"], cw - 8 * MM, 2.9, B.NAVY_MID, 1.55)
    c.showPage()

    # ---- 3 · licence log ------------------------------------------------
    D.page_bg(c, "CP / OWV / 01", "Rev R2  ·  2026-10-28", 3,
              eyebrow="CAREPOINT MEDICAL CENTER  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Image source and licence log", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "Real, professionally shot stock photography throughout — no AI-generated imagery, no "
               "synthetic patients. Licence terms checked on Pexels' licence page, 28 October 2026. "
               "The images are licensed material, not portraits of CarePoint staff or patients, and "
               "must never be captioned as such.",
               (D.PW - 2 * D.M) / MM, 3.3, B.NAVY_MID)
    y -= 2 * MM
    cols = [("Asset", 16, "left"), ("Used on", 22, "left"), ("Photograph", 90, "left"),
            ("Creator / provider", 50, "left"), ("Licence", 30, "left"),
            ("Original px", 30, "left"), ("Checked", 24, "left")]
    usage = {}
    for p in PN.PANELS:
        if p["photo"]:
            usage.setdefault(p["photo"], []).append(p["id"])
    rows = []
    for key, m in P.PHOTOS.items():
        rows.append([m["asset"], ", ".join(usage.get(key, ["—"])), m["title"],
                     f"{m['creator']} / Pexels", "Pexels Licence",
                     f"{m['px'][0]:,} × {m['px'][1]:,}", "2026-10-28"])
    y = D.table(c, D.M, y, cols, rows, row_h=9.4 * MM, cap=2.7) - 7 * MM
    B.label(c, D.M, y, "WHAT THE LICENCE ALLOWS", 4.0, B.TEAL, "Inter-600", 1.6)
    y -= 6 * MM
    lw = 128 * MM
    D.para(c, D.M, y,
           "Free commercial use, including printed signage; editing and cropping permitted; "
           "attribution not required (given here as good practice). This workflow — cropping, "
           "grading and compositing into a design — is expressly allowed.",
           lw, 3.0, B.NAVY_MID)
    D.para(c, D.M + lw + 10 * MM, y,
           "Not allowed: selling the images unaltered; implying that the people depicted endorse "
           "CarePoint; using them as part of a trade mark. That last point matters here — the "
           "panels may not present a stock model as the face of a named service as if they were "
           "staff, so no names or titles appear beside any photograph.",
           (D.PW - 2 * D.M) - lw - 10 * MM, 3.0, B.NAVY_MID)
    c.showPage()

    # ---- 4 · resolution + brand note ------------------------------------
    D.page_bg(c, "CP / OWV / 01", "Rev R2  ·  2026-10-28", 4,
              eyebrow="CAREPOINT MEDICAL CENTER  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Resolution audit at final print size", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "Measured from each original file against the final pane size, assuming full bleed "
               "across the pane — the crop is what counts, not the file's headline pixels. Floor "
               "75 ppi, target 100 ppi: on perforated film the 2.3 mm hole pitch is the real limit, "
               "resolving about 11 holes per inch, so finer detail is lost in the mesh regardless.",
               (D.PW - 2 * D.M) / MM, 3.3, B.NAVY_MID)
    y -= 2 * MM
    cols = [("Panel", 16, "left"), ("Asset", 16, "left"), ("Pane (mm)", 26, "left"),
            ("Trim px @ 100 ppi", 34, "left"), ("Effective ppi", 26, "left"),
            ("Result", 40, "left")]
    rows = []
    for p in PN.PANELS:
        if not p["photo"]:
            rows.append([p["id"], "GRAPHIC", f"{p['w']} × {p['h']}", "vector", "—",
                         "PASS (vector)"])
            continue
        d, st = P.ppi(p["photo"], p["w"], p["h"], zoom=p.get("zoom", 1.0))
        rows.append([p["id"], P.PHOTOS[p["photo"]]["asset"], f"{p['w']} × {p['h']}",
                     f"{int(p['w']/25.4*100)} × {int(p['h']/25.4*100)}", str(d), st])
    y = D.table(c, D.M, y, cols, rows, row_h=8.4 * MM, cap=2.9, col_colors={5: B.CP_CYAN_DK}) - 6 * MM
    y = D.para(c, D.M, y,
           "The files in assets/photos are web previews used to build these comps. Before output, "
           "download each original at full resolution from its Pexels page, relink, and re-check the "
           "crop — the focus point is stored per panel so the framing reproduces exactly.",
           (D.PW - 2 * D.M) / MM, 3.1, B.NAVY_MID)

    B.label(c, D.M, y - 6 * MM, "BRAND ASSETS — STATUS", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, y - 14 * MM, [
        "Colours are sampled from the client's existing fascia sign and restated as clean print "
        "values: navy #16233F, cyan #2BA9E0, mist #E8EEF4.",
        "The cp monogram on these panels is a vector recreation drawn from the sign photograph. "
        "It is close, not official — replace it with the client's vector logo before release.",
        "The slogan and both telephone numbers are taken verbatim from the client's own sign.",
        "No opening hours, accreditations or service claims have been invented. The services list "
        "is the client's own board text, transcribed.",
    ], 168 * MM, 3.1, B.NAVY_MID)
    c.showPage()
    c.save()
    return path


def lookbook():
    path = os.path.join(BASE, "lookbook", "CarePoint-One-Way-Vision-Lookbook.pdf")
    B.register_fonts()
    c = D.new_doc(path, "CarePoint — one-way vision film lookbook")

    # cover
    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, D.PW, D.PH, stroke=0, fill=1)
    B.label(c, D.M, D.PH - 26 * MM, "CAREPOINT MEDICAL CENTER  ·  GLASS DOOR GRAPHICS", 4.2,
            B.CP_CYAN, "Inter-600", 1.8)
    B.monogram(c, D.M, D.PH - 74 * MM, 50, dark=B.WHITE, accent=B.CP_CYAN)
    B.caps(c, D.M, D.PH - 90 * MM, "ONE-WAY", 13.5, B.WHITE, "Manrope-800", 0.4)
    B.caps(c, D.M, D.PH - 106 * MM, "VISION FILM", 13.5, B.WHITE, "Manrope-800", 0.4)
    c.setFillColor(B.CP_CYAN)
    c.rect(D.M, D.PH - 116 * MM, 60, 2.4, stroke=0, fill=1)
    D.para(c, D.M, D.PH - 126 * MM,
           "Eight panes across the four glass leaves of the CarePoint frontage — dental, paediatrics, "
           "laboratory, physiotherapy, pharmacy, antenatal, reception and a services directory — "
           "designed for perforated film and rebuilt from the client's own shopfront photograph.",
           96 * MM, 3.6, B.CP_MIST, 1.75)

    img_path = os.path.join(BASE, "lookbook", "mockups", "M-01-shopfront-day.png")
    if os.path.exists(img_path):
        im = Image.open(img_path)
        w = 156 * MM
        h = w * im.height / im.width
        c.drawImage(jpg(img_path, 1700), D.PW - D.M - w, 30 * MM, w, h, mask=None)
        B.label(c, D.PW - D.M - w, 22 * MM,
                "FRONTAGE ELEVATION — ALL EIGHT PANES IN PLACE", 3.2, B.CP_GREY,
                "Inter-500", 1.1)
        B.label(c, D.M, 22 * MM, "DAYLIGHT — PRINTED FACE TOWARDS THE STREET", 3.2,
                B.CP_GREY, "Inter-500", 1.1)
    B.label(c, D.PW - D.M, 15 * MM, "REV R2  ·  2026-10-28  ·  PROVISIONAL", 3.4, B.CP_CYAN,
            "Inter-600", 1.2, "right")
    c.showPage()

    # sheet 2: the set
    D.page_bg(c, "CP / OWV / LOOKBOOK", "Rev R2  ·  2026-10-28  ·  PROVISIONAL", 2,
              eyebrow="CAREPOINT MEDICAL CENTER  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "The eight panes", 7.6)
    D.para(c, D.M, y + 2 * MM,
           "Every pane keeps one architecture: photograph to the head, navy caption block at the foot, "
           "service name at a fixed cap height, CarePoint lockup top-left, slogan and telephone at the "
           "base. The directory pane carries no photograph at all — it reads fastest from the street.",
           (D.PW - 2 * D.M) / MM, 3.1, B.NAVY_MID)

    import cp_mockup as MK
    rows = [PN.PANELS[:4], PN.PANELS[4:]]
    max_w = D.PW - 2 * D.M
    gap = 8 * MM
    scale_h = (max_w - gap * 3) / sum(p["w"] / p["h"] for p in PN.PANELS[:4])
    scale_h = min(scale_h, 62 * MM)
    bottoms = [104 * MM, 23 * MM]
    for ri, row in enumerate(rows):
        widths = [scale_h * p["w"] / p["h"] for p in row]
        total = sum(widths) + gap * (len(row) - 1)
        x = (D.PW - total) / 2
        for p, w in zip(row, widths):
            src = jpg(MK.panel_png(p, 1200), 700)
            c.drawImage(src, x, bottoms[ri], w, scale_h, mask=None)
            B.label(c, x, bottoms[ri] - 5.0 * MM, p["id"], 3.2, B.NAVY, "Inter-600", 1.1)
            B.label(c, x, bottoms[ri] - 9.0 * MM, f"{p['w']} × {p['h']} mm", 2.8, B.GREY,
                    "Inter-400", 0.6)
            x += w + gap
    c.showPage()

    # sheet 3: night + brand
    D.page_bg(c, "CP / OWV / LOOKBOOK", "Rev R2  ·  2026-10-28  ·  PROVISIONAL", 3,
              eyebrow="CAREPOINT MEDICAL CENTER  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "After dark, and the brand it carries", 7.4)
    night = os.path.join(BASE, "lookbook", "mockups", "M-02-shopfront-night.png")
    if os.path.exists(night):
        im = Image.open(night)
        w, h = 112 * MM, 112 * MM * im.height / im.width
        c.drawImage(jpg(night, 1400), D.M, D.PH - 46 * MM - h, w, h, mask=None)
        B.label(c, D.M, D.PH - 50 * MM - h, "NIGHT — INTERIOR LIGHTING BEHIND THE FILM", 3.2,
                B.GREY, "Inter-500", 1.2)

    cx = D.M + 124 * MM
    cw = D.PW - cx - D.M
    B.label(c, cx, D.PH - 50 * MM, "BRAND, AS SUPPLIED", 3.8, B.TEAL, "Inter-600", 1.6)
    D.para(c, cx, D.PH - 58 * MM,
           "The palette, slogan and telephone numbers come straight off the client's fascia sign and "
           "existing boards. Nothing has been invented.", cw, 3.2, B.NAVY_MID)
    sw = [("Navy", "#16233F"), ("Cyan", "#2BA9E0"), ("Mist", "#E8EEF4")]
    for i, (n, hx) in enumerate(sw):
        c.setFillColor(B.HexColor(hx))
        c.rect(cx + i * 30 * MM, D.PH - 82 * MM, 26 * MM, 14 * MM, stroke=0, fill=1)
        B.label(c, cx + i * 30 * MM, D.PH - 87 * MM, n, 3.0, B.NAVY, "Inter-600", 1.0)
        B.label(c, cx + i * 30 * MM, D.PH - 91 * MM, hx, 2.8, B.GREY, "Inter-400", 0.6)
    B.label(c, cx, D.PH - 104 * MM, "TYPE — MANROPE DISPLAY / INTER TEXT", 3.4, B.TEAL,
            "Inter-600", 1.4)
    D.bullets(c, cx, D.PH - 112 * MM, [
        "Service names set at 54–66 mm cap height, weight 800 — sized to survive a 44% perforation — nearly half the surface is holes.",
        "Labels at 8–9 mm, Inter 600 with 2.6 tracking; nothing live below 6 mm.",
        "Panels are readable from the pavement and from a moving car; the directory pane is legible "
        "at 8 m.",
        "Telephone numbers appear at 6.2 mm cap height on every pane — small enough not to shout, "
        "large enough to be photographed.",
    ], cw, 3.1, B.NAVY_MID)
    c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    os.makedirs(os.path.join(BASE, "docs"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "lookbook"), exist_ok=True)
    print("built", schedule())
    print("built", lookbook())
