"""BCM Medical Centre — door 1, built from the measured glazing.

Eight panes on one double door: four at 900 × 500 mm and four at 900 × 400 mm,
stacked two columns by two rows per leaf. Everything else in the system —
palette, plate, caption band, film spec — carries over from the BCM set.
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.units import mm as MM

import bcm_brand as B
import cp_build_artwork as ART
import cp_docutil as D
import cp_panels as PN
import cp_photos as P
import cp_render as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "bcm", "door-1")
ART_DIR = os.path.join(BASE, "artwork")

WIDE, NARROW, PANE_H = 500, 400, 900

#   id        service          pane w   photo        headline position
SPEC = [
    ("D1-P1", "HIV TESTING",  WIDE,   "hiv",        ("Left leaf", "upper left", "900 × 500")),
    ("D1-P2", "PHARMACY",     NARROW, "pharmacy",   ("Left leaf", "upper right", "900 × 400")),
    ("D1-P3", "MALARIA",      WIDE,   "malaria",    ("Left leaf", "lower left", "900 × 500")),
    ("D1-P4", "CBC",          NARROW, "cbc",        ("Left leaf", "lower right", "900 × 400")),
    ("D1-P5", "ANTENATAL",    WIDE,   "ultrasound", ("Right leaf", "upper left", "900 × 500")),
    ("D1-P6", "LABORATORY",   NARROW, "lab",        ("Right leaf", "upper right", "900 × 400")),
    ("D1-P7", "OUR SERVICES", WIDE,   None,         ("Right leaf", "lower left", "900 × 500")),
    ("D1-P8", "CONSULTATION", NARROW, "consult",    ("Right leaf", "lower right", "900 × 400")),
]

SUB = {"HIV TESTING": "RAPID TEST & LAB", "PHARMACY": "DISPENSARY", "MALARIA": "TESTING",
       "CBC": "FULL BLOOD COUNT", "ANTENATAL": "ANTENATAL CARE",
       "LABORATORY": "TESTS & RESULTS", "RECEPTION": "WELCOME",
       "CONSULTATION": "DOCTOR'S ROOM", "OUR SERVICES": "DEPARTMENT DIRECTORY"}

FOCUS = {"hiv": (0.50, 0.42), "pharmacy": (0.62, 0.44), "malaria": (0.50, 0.55),
         "cbc": (0.50, 0.45), "ultrasound": (0.50, 0.40), "reception": (0.50, 0.46),
         "lab": (0.52, 0.36), "consult": (0.50, 0.30)}

# the client's own list, verbatim — no additions
SERVICES = ["HIV testing", "Malaria testing", "CBC (Full blood count)", "Antenatal care",
            "Pharmacy", "Laboratory", "Consultation"]

EDITS = {"pharmacy": "ph-pharmacy.jpg", "reception": "ph-reception.jpg",
         "lab": "ph-lab.jpg", "consult": "ph-consult.jpg"}

EDITS = {"dental": "ph-dental.jpg", "paeds": "ph-paeds.jpg", "lab": "ph-lab.jpg",
         "physio": "ph-physio.jpg", "pharmacy": "ph-pharmacy.jpg",
         "reception": "ph-reception.jpg"}


# --------------------------------------------------------------------------- panels
def configure():
    for mod in (ART, B, D, R):
        if hasattr(mod, "use_brand"):
            mod.use_brand(B)
    ART.OUT = ART_DIR
    P.CACHE_DIR = os.path.join(ROOT, "source", ".work", "bcm_d1_photos")
    for key, fname in EDITS.items():
        path = os.path.join(ROOT, "assets", "photos", "edited", fname)
        w, h = Image.open(path).size
        P.PHOTOS[key]["src"] = os.path.join("edited", fname)
        P.PHOTOS[key]["px"] = (w, h)
        P.PHOTOS[key]["edit"] = True


def panels():
    out = []
    for pid, service, w, photo, _pos in SPEC:
        p = {
            "id": pid, "service": service, "sub": SUB[service], "w": w, "h": PANE_H,
            "photo": photo,
            "focus": FOCUS.get(photo, (0.5, 0.4)) if photo else (0.5, 0.4),
            "zoom": 1.0, "title_cap": 64, "accent": "cyan",
            "orientation": "PORTRAIT — GLAZED DOOR PANE (MEASURED)",
            "aspect": f"1 : {PANE_H / w:.2f}",
            "note": "",
            "list_items": SERVICES if service == "OUR SERVICES" else None,
        }
        out.append(p)
    return out


# -------------------------------------------------------------------------- mockup
def mockup(panels_by_id, night=False, name="M-01-door-1-day.png"):
    S = 1.5                                   # px per mm
    FRAME, LEAF_W, LEAF_H = 60, WIDE + NARROW + 180, PANE_H * 2 + 180
    total_w = LEAF_W * 2 + FRAME
    SIGN_H, WALL = 560, 240
    w = int((total_w + WALL * 2) * S)
    h = int((LEAF_H + SIGN_H + 100 + 40 + 210) * S)

    g = np.linspace(0.92, 0.78, h).reshape(h, 1, 1)
    base = np.array([0.93, 0.91, 0.86]) if not night else np.array([0.14, 0.17, 0.24])
    arr = np.repeat(g * base.reshape(1, 1, 3), w, axis=1)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    ox = int(WALL * S)
    # fascia sign first, so the door below it can be laid out to its true height
    sx, sy = ox - int(FRAME * S), int(60 * S)
    sw, sh = int((total_w + FRAME * 2) * S), int(SIGN_H * S)
    d.rectangle([sx, sy, sx + sw, sy + sh], fill=(22, 35, 63))
    d.rectangle([sx, sy, sx + int(300 * S), sy + sh], fill=(232, 238, 244))
    sign_pdf = os.path.join(ROOT, "source", ".work", "d1_sign.pdf")
    c = rl_canvas.Canvas(sign_pdf, pagesize=((total_w + 120) * MM, SIGN_H * MM))
    B.register_fonts()
    c.scale(MM, MM)
    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, total_w + 120, SIGN_H, stroke=0, fill=1)
    c.setFillColor(B.CP_MIST)
    c.rect(0, 0, 300, SIGN_H, stroke=0, fill=1)
    B.monogram(c, 55, (SIGN_H - 190) / 2, 190, dark=B.CP_NAVY, accent=B.CP_CYAN)
    B.caps(c, 370, SIGN_H - 180, B.LINE1, 112, B.WHITE, "Manrope-800", 4.0,
           max_w=total_w - 400)
    B.caps(c, 370, SIGN_H - 290, B.LINE2, 74, B.CP_CYAN, "Manrope-600", 9.0,
           max_w=total_w - 400)
    B.label(c, 372, SIGN_H - 372, B.SLOGAN, 42, B.CP_MIST, "Inter-400", 0.8)
    c.showPage()
    c.save()
    doc = pdfium.PdfDocument(sign_pdf)
    page = doc[0]
    sign = page.render(scale=sw / page.get_size()[0]).to_pil()
    doc.close()
    if night:
        a = np.asarray(sign).astype(np.float32) * 0.80 + 18
        sign = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    img.paste(sign, (sx - int(FRAME * S), sy))

    top_y = sy + sh + int(40 * S)
    floor_y = top_y + int(LEAF_H * S)
    d.rectangle([0, floor_y, w, h], fill=(150, 146, 140) if not night else (24, 26, 32))
    d.rectangle([sx, top_y, sx + sw, floor_y], fill=(38, 40, 44) if not night else (10, 12, 16))

    for leaf in range(2):
        lx = ox + int(leaf * (LEAF_W + FRAME) * S)
        ly = top_y
        lw, lh = int(LEAF_W * S), floor_y - top_y
        d.rectangle([lx, ly, lx + lw, ly + lh], fill=(196, 152, 74))
        d.rectangle([lx, ly, lx + lw, ly + int(5 * S)], fill=(214, 172, 96))
        # louvred transom at the head of the leaf
        yy = ly + int(10 * S)
        while yy < ly + int(70 * S):
            d.rectangle([lx + int(10 * S), yy, lx + lw - int(10 * S), yy + int(3.4 * S)],
                        fill=(168, 126, 58))
            yy += int(11 * S)
        rows = [("upper", ly + int(80 * S)), ("lower", ly + int(80 * S) + int((PANE_H + FRAME) * S))]
        for rname, ry in rows:
            for col, pw_mm in enumerate((WIDE, NARROW)):
                px = lx + int((FRAME + (0 if col == 0 else WIDE + FRAME)) * S)
                pid = f"D1-P{leaf * 4 + (1 if rname == 'upper' else 3) + col}"
                panel = panels_by_id.get(pid)
                pw, ph = int(pw_mm * S), int(PANE_H * S)
                if panel is None:
                    d.rectangle([px, ry, px + pw, ry + ph], fill=(120, 132, 142))
                    continue
                png = _panel_png(panel, 900)
                art = Image.open(png).convert("RGB").resize((pw, ph), Image.LANCZOS)
                if night:
                    a = np.asarray(art).astype(np.float32) * 0.80 + 26
                    art = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
                img.paste(art, (px, ry))
        # handles on the meeting stiles
        hx = lx + lw - int(64 * S) if leaf == 0 else lx + int(40 * S)
        d.rounded_rectangle([hx, ly + int(760 * S), hx + int(24 * S), ly + int(1300 * S)],
                            radius=int(12 * S), fill=(206, 210, 214))

    out_dir = os.path.join(BASE, "lookbook")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    if img.width > 2600:
        img = img.resize((2600, round(img.height * 2600 / img.width)), Image.LANCZOS)
    img.save(path, "PNG", optimize=True)
    return path


def _panel_png(panel, px_h=900):
    import cp_mockup as MK
    return MK.panel_png(panel, px_h)


# ------------------------------------------------------------------------ documents
def schedule(panels_list):
    path = os.path.join(BASE, "docs", "BCM-Door-1-Schedule.pdf")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    D.use_brand(B)
    c = D.new_doc(path, "BCM Medical Centre — door 1 pane schedule")
    D.page_bg(c, "BCM / D1 / 01", "Rev A  ·  2026-10-28  ·  MEASURED", 1,
              eyebrow="BCM MEDICAL CENTRE  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Door 1 — pane schedule", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "Eight panes on one double door. Four measure 900 × 500 mm and four measure "
               "900 × 400 mm — all 900 mm high, so every design is portrait and the width is the "
               "only variable. Sizes here come from the client's measurement, not from a "
               "photograph, so the artwork can be cut to them; confirm each pane on site before "
               "the film is plotted.",
               (D.PW - 2 * D.M) / MM, 3.3, B.NAVY_MID)
    y -= 2 * MM
    cols = [("Pane", 16, "left"), ("Service", 34, "left"), ("Glass H × W", 26, "left"),
            ("Aspect", 18, "left"), ("Leaf", 24, "left"), ("Position", 26, "left"),
            ("Photo", 16, "left"), ("File", 40, "left")]
    rows = []
    for p, (_pid, _s, _w, photo, pos) in zip(panels_list, SPEC):
        rows.append([p["id"], p["service"], f"{p['h']} × {p['w']}", p["aspect"],
                     pos[0], pos[1], (P.PHOTOS[photo]["asset"] if photo else "GRAPHIC"),
                     f"{p['id']}.pdf"])
    y = D.table(c, D.M, y, cols, rows, row_h=9.6 * MM, cap=2.9) - 6 * MM

    B.label(c, D.M, y, "WHAT CHANGED FROM THE FIRST SET", 4.0, B.TEAL, "Inter-600", 1.6)
    y -= 6 * MM
    D.bullets(c, D.M, y, [
        "The earlier panes were 810 × 1120 mm, scaled from a photograph and carrying general "
        "services. These are measured — 900 mm high, 500 or 400 mm wide — and carry the "
        "services BCM actually offers: HIV testing, malaria testing, CBC, antenatal care, "
        "pharmacy, laboratory and the doctor's room. No dentistry, no physiotherapy.",
        "Type is set to the pane, not to taste: the service name is capped at 13.5 % of the pane "
        "width, so a 400 mm pane carries a smaller name than a 500 mm one and reads the same "
        "from the pavement.",
        "The white logo plate is measured from its own type and squeezed to fit the narrowest "
        "pane, so the badge and wordmark sit identically on all eight.",
        "The slogan moved into the plate. At 400 mm wide there is no room for it twice.",
    ], 168 * MM, 3.1, B.NAVY_MID)
    c.showPage()

    # schematic
    D.page_bg(c, "BCM / D1 / 01", "Rev A  ·  2026-10-28  ·  MEASURED", 2,
              eyebrow="BCM MEDICAL CENTRE  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Layout as measured", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "Two leaves, two columns and two rows per leaf: the 500 mm column on the left of each "
           "leaf, the 400 mm column on the right. If the site is the other way round, say so — "
           "the artwork is width-agnostic, but the pane numbers would swap.",
           (D.PW - 2 * D.M) / MM, 3.2, B.NAVY_MID)

    scale = 0.148
    x0, y0 = D.M + 26 * MM, 44 * MM
    leaf_w, leaf_h = (WIDE + NARROW + 180), (PANE_H * 2 + 180)
    for leaf in range(2):
        lx = x0 + leaf * (leaf_w + 60) * scale
        c.setFillColor(B.PAPER)
        c.rect(lx, y0, leaf_w * scale, leaf_h * scale, stroke=0, fill=1)
        c.setStrokeColor(B.TEAL)
        c.setLineWidth(0.6)
        c.rect(lx, y0, leaf_w * scale, leaf_h * scale, stroke=1, fill=0)
        for r, rname in enumerate(("upper", "lower")):
            for col, pw in enumerate((WIDE, NARROW)):
                px = lx + (60 + (0 if col == 0 else WIDE + 60)) * scale
                py = y0 + (leaf_h - 60 - PANE_H - r * (PANE_H + 60)) * scale
                c.setFillColor(B.CP_NAVY)
                c.rect(px, py, pw * scale, PANE_H * scale, stroke=0, fill=1)
                pid = f"D1-P{leaf * 4 + (1 if rname == 'upper' else 3) + col}"
                B.label(c, px + 3 * MM, py + PANE_H * scale - 8 * MM, pid, 4.2,
                        B.WHITE, "Inter-600", 0.8)
                svc = next(s for i, s, _w, _p, _pos in SPEC if i == pid)
                B.label(c, px + 3 * MM, py + 4 * MM, svc, 3.6, B.CP_CYAN, "Inter-500", 0.6)
        B.label(c, lx, y0 - 8 * MM, f"LEAF {'A' if leaf == 0 else 'B'} — "
                f"{'LEFT' if leaf == 0 else 'RIGHT'}", 3.6, B.GREY, "Inter-600", 1.4)

    tx = x0 + (leaf_w * 2 + 60) * scale + 26 * MM
    tw = D.PW - tx - D.M
    B.label(c, tx, D.PH - 74 * MM, "WHY THE TWO WIDTHS MATTER", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, tx, D.PH - 82 * MM, [
        "Left column of each leaf: 900 × 500 — HIV testing, malaria and antenatal carry the "
        "subject at full width.",
        "Right column: 900 × 400 — the narrower panes take equipment and hands: pharmacy "
        "shelving, the microscope, the blood draw, the doctor's room.",
        "Eight panes, eight different photographs. No image repeats anywhere on the door.",
        "Bleed is 10 mm on every edge, so the printed piece is 920 × 520 and 920 × 420 mm.",
        "The directory pane needs its nine lines at 14 mm cap to stay legible on a 400 mm "
        "pane — which is why it sits in the wide column.",
    ], tw, 3.0, B.NAVY_MID, gap=2.4)
    c.showPage()
    c.save()
    return path


def spec():
    path = os.path.join(BASE, "docs", "BCM-Door-1-Specification.pdf")
    D.use_brand(B)
    c = D.new_doc(path, "BCM Medical Centre — door 1 production specification")
    D.page_bg(c, "BCM / D1 / 02", "Rev A  ·  2026-10-28", 1,
              eyebrow="BCM MEDICAL CENTRE  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Production specification — door 1", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "Eight panes, two widths, one film. Values marked “confirm with printer” are "
               "industry-typical placeholders, not something the printer has agreed to.",
               (D.PW - 2 * D.M) / MM, 3.3, B.NAVY_MID)
    y -= 2 * MM
    rows = [
        ["Trim size", "900 × 500 mm (4 panes) and 900 × 400 mm (4 panes)"],
        ["With bleed", "920 × 520 mm and 920 × 420 mm"],
        ["Bleed", "10 mm all round"],
        ["Live / safe", "25 mm inside trim — 20 mm on the 400 mm panes"],
        ["Crop marks", "Offset 4 mm, 4 mm long, outside bleed"],
        ["Slug", "20 mm at the foot, outside bleed"],
        ["Service name", "Cap height 13.5 % of pane width — 64 mm on the wide pane, 54 mm on "
                         "the narrow"],
        ["Smallest live type", "6 mm cap"],
        ["Resolution", "75 ppi floor, 100 ppi target in the placed crop"],
        ["Colour", "CMYK, coated profile; navy #16233F, cyan #2BA9E0"],
        ["Fonts", "Manrope + Inter, SIL OFL, embedded"],
    ]
    y = D.table(c, D.M, y, [("Item", 44, "left"), ("Value", 150, "left")], rows,
                row_h=7.0 * MM, cap=2.9) - 7 * MM
    B.label(c, D.M, y, "FILM", 4.2, B.TEAL, "Inter-600", 1.8)
    y -= 6 * MM
    D.bullets(c, D.M, y, [
        "Perforated one-way vision vinyl, white-backed, 140–160 µm plus liner — confirm with "
        "printer.",
        "1.6 mm holes on a 2.3 mm staggered pitch, ≈44 % open by geometry. The mesh, not the "
        "file, is the limit on detail.",
        "Matte anti-glare face, UV or latex print, four colour plus white backing layer.",
        "Eight pieces per door. Cut from one roll run so the navy matches across all eight.",
    ], 168 * MM, 3.1, B.NAVY_MID, gap=2.4)
    c.showPage()

    D.page_bg(c, "BCM / D1 / 02", "Rev A  ·  2026-10-28", 2,
              eyebrow="BCM MEDICAL CENTRE  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Installation — door 1", 8.0)
    D.bullets(c, D.M, y + 2 * MM, [
        "Re-measure every pane with a tape, corner to corner, before plotting. Measured figures "
        "were supplied for this door; the next door may not match.",
        "Number the panes on the back of each print in pencil as they are cut — eight pieces, "
        "two sizes, and they all look alike in a stack.",
        "Clean the glass and apply one pane as a control: the narrowest, most awkward one, low "
        "on the leaf, where mistakes are least visible.",
        "Keep the perforation grid square to the frame, not to the handle. On two 900 mm rows "
        "stacked, a skewed grid reads as a crooked poster.",
        "Trim inside the rebate, 2 mm clear of the glass edge. Clear 25 mm around handles, "
        "locks and hinges.",
        "Do not stretch the film to fit a pane. If a pane is out of square by more than 3 mm, "
        "re-cut the artwork to the measured diagonal — the design has room for it.",
        "Leave 24 hours before cleaning or closing the door against the film.",
    ], 120 * MM, 3.0, B.NAVY_MID, gap=2.2)

    tx = D.M + 132 * MM
    tw = D.PW - tx - D.M
    B.label(c, tx, D.PH - 44 * MM, "OPEN ITEMS", 4.2, B.TEAL, "Inter-600", 1.8)
    D.bullets(c, tx, D.PH - 52 * MM, [
        "Confirm the column order on the leaf: 500 mm on the left as drawn, or mirrored?",
        "BCM's vector logo, for the plate on all eight panes.",
        "Telephone numbers, if they are to appear — currently none do.",
        "The printer's own film standard, to replace the flagged values.",
        "Full-resolution originals for the six retouched photographs, or a shoot of the real "
        "team. The current files are proof resolution.",
    ], tw, 3.0, B.NAVY_MID, gap=2.2)
    c.showPage()
    c.save()
    return path


def combined(paths):
    path = os.path.join(BASE, "BCM-Door-1-Panels.pdf")
    w = PdfWriter()
    for p in paths:
        for page in PdfReader(p).pages:
            w.add_page(page)
    with open(path, "wb") as fh:
        w.write(fh)
    return path


def web(panels_list):
    web_dir = os.path.join(BASE, "web")
    os.makedirs(web_dir, exist_ok=True)
    cards = []
    for p in panels_list:
        pdf = os.path.join(ART_DIR, f"{p['id']}.pdf")
        doc = pdfium.PdfDocument(pdf)
        page = doc[0]
        img = page.render(scale=760 / page.get_size()[0]).to_pil().convert("RGB")
        doc.close()
        thumb = os.path.join(web_dir, f"{p['id']}.jpg")
        img.save(thumb, "JPEG", quality=88, optimize=True)
        photo = (P.PHOTOS[p["photo"]]["creator"] if p["photo"] else "No photograph")
        cards.append(f"""
    <figure class="card">
      <a href="artwork/{p['id']}.pdf"><img src="web/{p['id']}.jpg" alt="{p['service']} pane"></a>
      <figcaption><b>{p['id']}</b> · {p['service'].title()} · {p['w']}×{p['h']} mm<br>
      <span>{photo}</span></figcaption>
    </figure>""")
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BCM Medical Centre — door 1</title>
<style>
body{{margin:0;background:#f4f7f9;color:#16233f;font:16px/1.6 Inter,Helvetica,Arial,sans-serif}}
header{{background:#16233f;color:#fff;padding:48px 6vw 40px}}
h1{{font-size:clamp(30px,5vw,54px);margin:.2em 0 .4em;line-height:1.02}}
p{{max-width:66ch;color:#cfd9e6}}
.grid{{display:grid;gap:24px;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));padding:40px 6vw}}
.card{{margin:0;background:#fff;border-radius:6px;overflow:hidden;box-shadow:0 2px 14px rgba(22,35,63,.08)}}
.card img{{width:100%;display:block}}
figcaption{{padding:12px 14px;font-size:12px;line-height:1.5}}
figcaption span{{color:#8fa2b8}}
footer{{padding:32px 6vw;font-size:12.5px;color:#4b5b73}}
a{{color:#2ba9e0}}
</style></head><body>
<header>
  <div style="letter-spacing:.3em;font-size:11px;color:#2ba9e0">BCM MEDICAL CENTRE · DOOR 1</div>
  <h1>Eight panes,<br>two widths.</h1>
  <p>Four panes at 900 × 500 mm and four at 900 × 400 mm, measured on the door rather than scaled
  from a photograph. Same plate, same caption band, sizes set from the glass.</p>
  <p><a style="color:#2ba9e0" href="BCM-Door-1-Panels.pdf">All eight panes (PDF)</a> ·
     <a style="color:#2ba9e0" href="docs/BCM-Door-1-Schedule.pdf">Schedule</a> ·
     <a style="color:#2ba9e0" href="docs/BCM-Door-1-Specification.pdf">Specification</a></p>
</header>
<main class="grid">{''.join(cards)}</main>
<footer>Provisional — rev A. Six photographs carry an AI colour retouch so the people reflect the
community BCM serves; they are models, not staff. Proof resolution only.</footer>
</body></html>"""
    path = os.path.join(BASE, "index.html")
    open(path, "w").write(html)
    return path


def main():
    configure()
    plist = panels()
    os.makedirs(ART_DIR, exist_ok=True)
    paths = []
    for p in plist:
        paths.append(ART.build(p, os.path.join(ART_DIR, f"{p['id']}.pdf")))
    print("artwork", len(paths))
    # the render cache is keyed by pane id only, so clear this door's entries
    work = os.path.join(ROOT, "source", ".work")
    for f in os.listdir(work) if os.path.isdir(work) else []:
        if f.startswith("D1-P"):
            os.remove(os.path.join(work, f))
    by_id = {p["id"]: p for p in plist}
    print(mockup(by_id, False, "M-01-door-1-day.png"))
    print(mockup(by_id, True, "M-02-door-1-night.png"))
    print(schedule(plist))
    print(spec())
    print(combined(paths))
    print(web(plist))


if __name__ == "__main__":
    main()
