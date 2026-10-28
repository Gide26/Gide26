"""Lookbook — A4 landscape presentation of the design system and panel suite."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image

import docutil as D
import brand as B
import panels as PN
import photos as P
import build_previews as PV

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "one-way-vision-film", "lookbook")
MM = D.MM


def img(c, path, x, y, w=None, h=None):
    iw, ih = Image.open(path).size
    if w and not h:
        h = w * ih / iw
    elif h and not w:
        w = h * iw / ih
    c.drawImage(path, x, y, w, h, mask=None)
    return w, h


def img_cover(c, path, x, y, w, h):
    """Place an image filling the box, cropping (never distorting)."""
    iw, ih = Image.open(path).size
    box_ar, im_ar = w / h, iw / ih
    if im_ar > box_ar:
        new_w = h * im_ar
        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)
        c.drawImage(path, x - (new_w - w) / 2, y, new_w, h, mask=None)
        c.restoreState()
    else:
        new_h = w / im_ar
        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)
        c.drawImage(path, x, y - (new_h - h) / 2, w, new_h, mask=None)
        c.restoreState()


def dark_page(c, footer, page):
    c.setFillColor(B.NAVY)
    c.rect(0, 0, D.PW, D.PH, stroke=0, fill=1)
    B.label(c, D.M, 10 * MM, footer, 3.6, B.GREY, "Inter-400", 1.2)
    B.label(c, D.PW - D.M, 10 * MM, str(page), 3.6, B.GREY, "Inter-500", 1.2, "right")


def opening():
    path = os.path.join(OUT, "GMC-One-Way-Vision-Lookbook.pdf")
    B.register_fonts()
    c = D.new_doc(path, "One-way vision film — design lookbook")

    # ---------------- 1. COVER ------------------------------------------
    c.setFillColor(B.NAVY)
    c.rect(0, 0, D.PW, D.PH, stroke=0, fill=1)
    # perforation field bottom-right
    c.saveState()
    c.setFillColor(B.WHITE)
    c.setFillAlpha(0.05)
    for i in range(38):
        for j in range(22):
            c.circle(D.PW - 8 * MM - i * 6 * MM * 0.55, 6 * MM + j * 3.3 * MM, 0.75 * MM,
                     stroke=0, fill=1)
    c.restoreState()

    B.label(c, D.M, D.PH - 26 * MM, "PREMIUM HEALTHCARE  ·  GLASS DOOR GRAPHICS", 4.6,
            B.TEAL_LT, "Inter-600", 2.0)
    B.caps(c, D.M, D.PH - 62 * MM, "ONE-WAY", 22, B.WHITE, "Manrope-800", 0.6)
    B.caps(c, D.M, D.PH - 92 * MM, "VISION FILM", 22, B.WHITE, "Manrope-800", 0.6)
    B.accent_rule(c, D.M, D.PH - 108 * MM, 74, 3.2, B.TEAL)
    (lambda y: (D.para(c, D.M, y,
                       "A coordinated system of perforated window graphics for the reception, "
                       "consultation rooms, laboratory, pharmacy and imaging suite of a private "
                       "medical centre. Real photography, quiet colour, type that survives "
                       "perforation.",
                       (D.PW / 2 - 10 * MM), 4.2, B.MIST, 1.8)))(D.PH - 122 * MM)

    B.label(c, D.M, 42 * MM, "CLIENT", 3.4, B.GREY, "Inter-500", 1.4)
    B.caps(c, D.M, 36 * MM, "MEDICAL CENTER (PLACEHOLDER)", 5.4, B.WHITE, "Manrope-600", 0.7)
    B.label(c, D.M, 26 * MM, "GMC / OWV / DESIGN LOOKBOOK  ·  REV R1  ·  2026-10-28", 3.4,
            B.GREY, "Inter-500", 1.4)
    B.label(c, D.PW - D.M, 26 * MM, "PROVISIONAL — AWAITING MEASUREMENTS", 3.6, B.TEAL_LT,
            "Inter-600", 1.4, "right")
    c.showPage()

    # ---------------- 2. INTENT -----------------------------------------
    dark_page(c, "GMC / OWV  ·  R1  ·  2026-10-28", 2)
    B.label(c, D.M, D.PH - 24 * MM, "01  DESIGN INTENT", 4.2, B.TEAL_LT, "Inter-600", 1.8)
    B.caps(c, D.M, D.PH - 36 * MM, "Quiet authority, not decoration", 7.6, B.WHITE,
           "Manrope-700", 0.3)
    y = D.PH - 48 * MM
    col_w = (D.PW - 2 * D.M) / 3 - 8 * MM
    for i, (head, body) in enumerate([
        ("TRUST BEFORE STYLE",
         "Patients read a building before they read a sign. The panels use a single deep navy "
         "field, one photograph and one headline, so the impression is competence rather than "
         "marketing."),
        ("BUILT FOR PERFORATION",
         "One-way film removes roughly two-fifths of the surface and softens edge contrast. "
         "Headlines are 70–78 mm cap height, weights stay at 600 or above, and no live detail "
         "sits on a mid-tone."),
        ("ONE SYSTEM, FIVE SERVICES",
         "Every panel shares the same photographic band, the same baseline for the department "
         "name, and the same lockup position — so a corridor reads as one institution even "
         "though each door names a different service."),
    ]):
        x = D.M + i * (col_w + 12 * MM)
        B.accent_rule(c, x, D.PH - 46 * MM, 26, 2.0, B.TEAL)
        B.label(c, x, y, head, 3.8, B.WHITE, "Inter-600", 1.5)
        D.para(c, x, y - 8 * MM, body, col_w, 3.6, B.MIST, 1.75)

    # palette
    py = 96 * MM
    B.label(c, D.M, py + 30 * MM, "PALETTE", 3.8, B.TEAL_LT, "Inter-600", 1.8)
    sw = [("NAVY", B.NAVY, "#0A2642", "ground / 80% of panel area"),
          ("NAVY DEEP", B.NAVY_DEEP, "#06182A", "shadows, lockup ground"),
          ("TEAL", B.TEAL, "#0F8C8C", "accent, rules, labels"),
          ("MEDICAL GREEN", B.GREEN, "#2E7A5F", "secondary accent only"),
          ("MIST", B.MIST, "#DCE6EC", "typography on navy"),
          ("WHITE", B.WHITE, "#FFFFFF", "headlines")]
    sw_w = 41 * MM
    for i, (name, col, hexv, use) in enumerate(sw):
        x = D.M + i * (sw_w + 6 * MM)
        c.setFillColor(col)
        c.rect(x, py, sw_w, 24 * MM, stroke=0, fill=1)
        if name in ("MIST", "WHITE"):
            c.setStrokeColor(B.GREY)
            c.setLineWidth(0.2)
            c.rect(x, py, sw_w, 24 * MM, stroke=1, fill=0)
        B.label(c, x, py - 6 * MM, name, 3.2, B.WHITE, "Inter-600", 1.2)
        B.label(c, x, py - 11 * MM, hexv, 3.0, B.GREY, "Inter-400", 1.0)
        D.para(c, x, py - 17 * MM, use, sw_w, 3.0, B.GREY, 1.5)

    # type
    B.label(c, D.M, 58 * MM, "TYPOGRAPHY", 3.8, B.TEAL_LT, "Inter-600", 1.8)
    B.caps(c, D.M, 44 * MM, "MANROPE", 7.0, B.WHITE, "Manrope-800", 0.4)
    D.para(c, D.M, 36 * MM,
           "Department names, 300–800. Geometric, open apertures, holds up at 70 mm cap height "
           "and still reads through a 38% perforation.", 78 * MM, 3.3, B.MIST, 1.7)
    B.caps(c, D.M + 92 * MM, 44 * MM, "INTER", 7.0, B.WHITE, "Inter-500", 0.4)
    D.para(c, D.M + 92 * MM, 36 * MM,
           "Labels, indices and technical text, 400–600 with 0.15–0.25 em tracking. Used at 5–8 mm "
           "cap height; never below 4 mm anywhere on a panel.", 78 * MM, 3.3, B.MIST, 1.7)
    B.caps(c, D.M + 184 * MM, 44 * MM, "NO THIRD FACE", 7.0, B.WHITE, "Manrope-500", 0.4)
    D.para(c, D.M + 184 * MM, 36 * MM,
           "One display family and one text family. Weight and scale carry hierarchy — not a "
           "third typeface, not italics, not outline type.", 78 * MM, 3.3, B.MIST, 1.7)
    c.showPage()

    # ---------------- 3–4. PANEL SUITE ----------------------------------
    intro = ("Eight independent panels, five services. Fixed elements — photographic band, headline "
             "baseline, accent rule, lockup — sit at identical heights across the set so adjacent "
             "doors align. Sidelights are graphic-only, giving the eye a rest between photographic "
             "panels and preserving daylight into the corridor.")
    for si, chunk in enumerate([PN.PANELS[:4], PN.PANELS[4:]]):
        page = 3 + si
        D.page_bg(c, "GMC / OWV / LOOKBOOK", "Rev R1  ·  2026-10-28  ·  PROVISIONAL", page)
        y = D.h1(c, D.PH - 34 * MM, "The panel suite" if si == 0 else "The panel suite, continued", 7.6)
        D.para(c, D.M, y + 2 * MM, intro if si == 0 else
               "Laboratory, pharmacy and imaging panels, plus the second fixed sidelight. The "
               "imaging door is a pair of 600 mm leaves carried on one plot, split at the centre "
               "line; no headline crosses the meeting stile.",
               (D.PW - 2 * D.M) / MM, 3.4, B.NAVY_MID)

        scale_h = 120 * MM
        widths = [scale_h * q["w"] / q["h"] for q in chunk]
        total = sum(widths) + 7 * MM * (len(chunk) - 1)
        x = (D.PW - total) / 2
        for q, w_scaled in zip(chunk, widths):
            path = PV.preview(q, 1400)
            img(c, path, x, 30 * MM, w=w_scaled, h=scale_h)
            B.label(c, x, 24 * MM, q["id"], 3.4, B.NAVY, "Inter-600", 1.2)
            B.label(c, x, 19 * MM, f"{q['w']/10:.0f} × {q['h']/10:.0f} cm  ·  {q['aspect']}",
                    3.0, B.GREY, "Inter-400", 0.6)
            x += w_scaled + 7 * MM
        B.label(c, D.M, 13 * MM,
                "SHOWN AT 1 : 17.5 — TRUE RELATIVE SIZES, ALL PANELS 210 CM HIGH", 3.4, B.GREY,
                "Inter-500", 1.3)
        c.showPage()

    # ---------------- 4–5. DEPARTMENT SPREADS ---------------------------
    spreads = [
        ([("P-01", 0), ("P-03", 1)], "RECEPTION & CONSULTATION",
         "Arrival, then privacy. Reception carries the warmest frame in the set — an exchange "
         "between a receptionist and a patient — while consultation panels use a seated, "
         "eye-level exchange held at a respectful distance. No exposed patients, no procedure "
         "imagery, no stock-smile close-ups."),
        ([("P-05", 0), ("P-06", 1), ("P-07", 2)], "LABORATORY · PHARMACY · IMAGING",
         "Competence, order, technology. The laboratory frame is a working bench, not a prop; the "
         "pharmacy frame is organised shelving with faces held sharp; imaging uses the symmetry of "
         "the scanner, echoed by the double door's centreline."),
    ]
    page_no = 5
    for panels, title, blurb in spreads:
        dark_page(c, "GMC / OWV  ·  R1  ·  2026-10-28", page_no)
        B.label(c, D.M, D.PH - 22 * MM, "02  ART DIRECTION", 4.2, B.TEAL_LT, "Inter-600", 1.8)
        B.caps(c, D.M, D.PH - 33 * MM, title, 6.6, B.WHITE, "Manrope-700", 0.3)
        D.para(c, D.M, D.PH - 42 * MM, blurb, 176 * MM, 3.4, B.MIST, 1.7)

        big_h = 108 * MM
        x = D.M
        ytop = 36 * MM
        for pid, idx in panels:
            p = next(q for q in PN.PANELS if q["id"] == pid)
            path = PV.preview(p, 1600)
            w_scaled = big_h * p["w"] / p["h"]
            img(c, path, x, ytop, w=w_scaled, h=big_h)
            B.label(c, x, ytop - 6 * MM, f"{pid}  ·  {p['dept']}", 3.4, B.MIST, "Inter-500", 1.1)
            asset = p["photo"] and P.PHOTOS[p["photo"]]
            if asset:
                B.label(c, x, ytop - 10.5 * MM, f"{asset['asset']}  {asset['creator']} / Pexels",
                        3.0, B.GREY, "Inter-400", 0.6)
            else:
                B.label(c, x, ytop - 10.5 * MM, "graphic panel — no photography", 3.0,
                        B.GREY, "Inter-400", 0.6)
            x += w_scaled + 10 * MM
        c.showPage()
        page_no += 1

    # ---------------- 6. IN SITU ------------------------------------------
    dark_page(c, "GMC / OWV  ·  R1  ·  2026-10-28", 6)
    B.label(c, D.M, D.PH - 22 * MM, "IN SITU", 4.2, B.TEAL_LT, "Inter-600", 1.8)
    B.caps(c, D.M, D.PH - 33 * MM, "How it reads on the door", 6.6, B.WHITE, "Manrope-700", 0.3)
    D.para(c, D.M, D.PH - 42 * MM,
           "Elevations composed at true scale from the actual artwork, with hardware drawn to "
           "position. Handle, closer and meeting stile are all shown where they will sit.",
           176 * MM, 3.4, B.MIST, 1.7)
    mk_h = 104 * MM
    x = D.M
    for fname, label in [("M-01-reception.png", "P-01 + P-02  ·  RECEPTION ENTRANCE"),
                         ("M-02-consultation.png", "P-03  ·  CONSULTATION ROOM"),
                         ("M-03-imaging.png", "P-07 + P-08  ·  IMAGING SUITE")]:
        src = os.path.join(OUT, "mockups", fname)
        if not os.path.exists(src):
            continue
        im = Image.open(src)
        w = mk_h * im.width / im.height
        img(c, src, x, 42 * MM, w=w, h=mk_h)
        B.label(c, x, 36 * MM, label, 3.3, B.MIST, "Inter-500", 1.0)
        x += w + 8 * MM
    B.label(c, D.M, 26 * MM,
            "ELEVATIONS AT 1 : 20.2  ·  HARDWARE SHOWN FOR CLEARANCE ONLY AND IS NOT PRINTED",
            3.3, B.GREY, "Inter-500", 1.2)
    c.showPage()

    # ---------------- 7. ONE-WAY VISION HANDLING -----------------------
    D.page_bg(c, "GMC / OWV / LOOKBOOK", "Rev R1  ·  2026-10-28", 7)
    y = D.h1(c, D.PH - 34 * MM, "Designing for perforation", 7.6)
    D.para(c, D.M, y + 2 * MM,
           "The film removes a regular grid of holes — typically 1.6 mm holes on a 2.3 mm pitch, "
           "about 38% open area. Ink only survives on the 62% that remains, so fine hairlines, "
           "small type and low-contrast detail disappear at distance. Each rule below is a direct "
           "consequence of that, not a style preference.",
           (D.PW - 2 * D.M) / MM, 3.4, B.NAVY_MID)

    # 1:1 detail with dot grid
    p = PN.PANELS[0]
    path = PV.preview(p, 2400)
    im = Image.open(path)
    w_mm, h_mm = p["w"], p["h"]
    px_per_mm = im.width / w_mm
    crop_w_mm, crop_h_mm = 250, 132
    top_mm = h_mm - 470          # band from the accent rule to the kick zone
    crop = im.crop((0, int(top_mm * px_per_mm),
                     int(crop_w_mm * px_per_mm), int((top_mm + crop_h_mm) * px_per_mm)))
    cpath = os.path.join(PV.CACHE, "detail_title_1to1.png")
    crop.save(cpath)

    scale = 0.60
    box_w, box_h = crop_w_mm * scale * MM, crop_h_mm * scale * MM
    bx, by = D.M, 84 * MM
    img(c, cpath, bx, by, w=box_w, h=box_h)
    PITCH = 2.3 * scale
    c.saveState()
    c.setFillColor(B.NAVY)
    c.setFillAlpha(0.42)
    xx = bx
    while xx < bx + box_w:
        yy = by
        while yy < by + box_h:
            c.circle(xx, yy, PITCH * 0.27, stroke=0, fill=1)
            yy += PITCH
        xx += PITCH
    c.restoreState()
    B.label(c, bx, by - 7 * MM, "DETAIL AT 1 : 1.7 — SIMULATED 1.6 MM HOLES / 2.3 MM PITCH", 3.3,
            B.GREY, "Inter-500", 1.2)
    D.para(c, bx, by - 12 * MM,
           "Headline counters stay open at 78 mm cap height; the 4.6 mm accent rule still reads as a "
           "line; nothing thinner survives the grid.",
           box_w, 3.1, B.NAVY_MID, 1.55)

    bx2 = bx + box_w + 16 * MM
    cw2 = D.PW - bx2 - D.M
    B.label(c, bx2, by + box_h, "RULES APPLIED TO THIS SET", 3.8, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, bx2, by + box_h - 8 * MM, [
        "Minimum live type: 4 mm cap height; labels are 6–7 mm, headlines 70–78 mm.",
        "Minimum stroke 0.3 mm printed — hairline rules are decorative, never load-bearing.",
        "Headlines sit on solid navy, never over photography, for maximum edge contrast.",
        "Photography covers 40–45% of a door panel; sidelights carry no photograph at all.",
        "One gradient only: the 260 mm navy hold-down that ties image to field.",
        "Bottom 140 mm of every panel is a kick zone — no live content below the lockup.",
    ], cw2, 3.3, B.NAVY_MID)

    # visibility balance table
    cols = [("PANEL TYPE", 62, "left"), ("PHOTO COVERAGE", 32, "left"),
            ("DARK FIELD", 28, "left"), ("TO OUTSIDE", 26, "left"),
            ("INTENDED EFFECT", 92, "left")]
    rows = [["Single door 1000 mm", "40%", "60%", "Good", "Readable sign, silhouettes visible"],
            ["Single door 900 mm", "40%", "60%", "Good", "Same rhythm, narrower headline"],
            ["Double door 2 × 600 mm", "40%", "60%", "Good", "Centre split keeps handle zone clear"],
            ["Fixed sidelight 450 mm", "0%", "100%", "Excellent", "Graphic only — maximum daylight"]]
    B.label(c, D.M, 58 * MM, "VISIBILITY BALANCE", 3.8, B.TEAL, "Inter-600", 1.6)
    D.table(c, D.M, 52 * MM, cols, rows, row_h=6.8 * MM, cap=2.9)
    c.showPage()

    # ---------------- 7. DELIVERY --------------------------------------
    dark_page(c, "GMC / OWV  ·  R1  ·  2026-10-28", 8)
    B.label(c, D.M, D.PH - 24 * MM, "03  DELIVERY", 4.2, B.TEAL_LT, "Inter-600", 1.8)
    B.caps(c, D.M, D.PH - 36 * MM, "What is in the package, and what is still provisional", 6.6,
           B.WHITE, "Manrope-700", 0.2)

    col_w = (D.PW - 2 * D.M) / 2 - 10 * MM
    y = D.PH - 50 * MM
    B.label(c, D.M, y, "SUPPLIED NOW", 3.8, B.TEAL_LT, "Inter-600", 1.6)
    D.bullets(c, D.M, y - 9 * MM, [
        "Eight true-size artwork PDFs (artwork folder) with 10 mm bleed, crop marks, registration "
        "target and a technical slug outside the trim.",
        "Panel schedule: dimensions, orientation, hardware, crop logic, coverage and print notes.",
        "Image source and licence log with creator, provider, licence and original pixel size.",
        "Resolution audit at final print size, per panel.",
        "Production specification, installation schedule and a printer RFQ.",
        "This lookbook.",
    ], col_w, 3.4, B.MIST)

    B.label(c, D.M + col_w + 20 * MM, y, "NEEDED BEFORE FINAL OUTPUT", 3.8, B.TEAL_LT,
            "Inter-600", 1.6)
    D.bullets(c, D.M + col_w + 20 * MM, y - 9 * MM, [
        "Measured width and height of every glass section, in centimetres, plus a photograph of "
        "each door with hardware in frame.",
        "Exact department names, room numbers and any secondary language text.",
        "Client logo in vector form, plus approved contact details and any claims permitted.",
        "The film maker's technical sheet: hole size and pitch, ink coverage limit, bleed and "
        "safe-zone allowance, and sheet width.",
        "Confirmation of installation method and whether the film is to be applied inside or out.",
    ], col_w, 3.4, B.MIST)

    steps = [("01", "RECEIVE", "Measured schedule, door photographs, logo, printer sheet"),
             ("02", "RE-CUT", "Panel engine re-flows type and crop to the real dimensions"),
             ("03", "PROOF", "Colour-managed proof at 100% on the specified film"),
             ("04", "OUTPUT", "Print-ready PDFs with bleed, marks and a per-panel slug"),
             ("05", "INSTALL", "Wet or dry application, then a 1 m inspection")]
    sy = 74 * MM
    swd = (D.PW - 2 * D.M) / len(steps) - 6 * MM
    for i, (num, head, body) in enumerate(steps):
        x = D.M + i * (swd + 6 * MM)
        B.caps(c, x, sy + 16 * MM, num, 9.0, B.TEAL, "Manrope-700", 0.4)
        B.label(c, x, sy + 8 * MM, head, 3.8, B.WHITE, "Inter-600", 1.5)
        D.para(c, x, sy + 1 * MM, body, swd, 3.0, B.GREY, 1.5)
        if i < len(steps) - 1:
            c.setStrokeColor(B.GREY)
            c.setStrokeAlpha(0.4)
            c.setLineWidth(0.25)
            c.line(x + swd + 3 * MM, sy + 4 * MM, x + swd + 3 * MM, sy + 22 * MM)

    B.accent_rule(c, D.M, 46 * MM, 90, 2.6, B.TEAL)
    D.para(c, D.M, 38 * MM,
           "Until the measured schedule arrives, treat every dimension in this package as a "
           "representative module. The layout engine is parametric: supply the real numbers and "
           "the set is re-cut — type re-fits, crops re-centre, nothing is stretched.",
           (D.PW - 2 * D.M) / MM, 3.6, B.MIST)
    c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("built", opening())
