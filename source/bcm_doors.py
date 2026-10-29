"""BCM Medical Centre — three doorways on one measured geometry.

Every door is the same double leaf measured on site: eight panes, four at
900 × 500 mm and four at 900 × 400 mm, all 900 mm high. Only the subject
matter and the film change. Doors 1 and 2 are perforated one-way vision;
door 3 is opaque white vinyl, so its artwork is not read through a mesh and
must never be see-through.

Run:  python3 bcm_doors.py            (all three doors)
      python3 bcm_doors.py 2 3        (only doors 2 and 3)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
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
WORK = os.path.join(ROOT, "source", ".work")

WIDE, NARROW, PANE_H = 500, 400, 900

# The clinic's own list, now with the three services it added: general
# consultation, immunisation and minor surgery.
SERVICES = ["General outpatient", "Inpatient care", "HIV care", "Immunisation",
            "Pharmacy", "Laboratory", "Ultrasound", "Antenatal & postnatal",
            "Obs & Gyn", "Paediatrics", "Minor surgery", "Family planning",
            "ENT", "Eye services", "Orthopaedics", "Travel medical exam"]

# --------------------------------------------------------------------- doors
DOORS = [
    {
        "n": 1, "folder": "door-1", "prefix": "D1", "film": "one-way",
        "film_name": "ONE-WAY VISION FILM",
        "role": "testing and treatment",
        "edits": {},
        "spec": [
            ("HIV CARE",    WIDE,   "hiv",        ("Left leaf", "upper left", "900 × 500")),
            ("PHARMACY",    NARROW, "pharmacy",   ("Left leaf", "upper right", "900 × 400")),
            ("MALARIA",     WIDE,   "malaria",    ("Left leaf", "lower left", "900 × 500")),
            ("CBC",         NARROW, "cbc",        ("Left leaf", "lower right", "900 × 400")),
            ("ANTENATAL",   WIDE,   "ultrasound", ("Right leaf", "upper left", "900 × 500")),
            ("LABORATORY",  NARROW, "lab",        ("Right leaf", "upper right", "900 × 400")),
            ("OUR SERVICES", WIDE,  None,         ("Right leaf", "lower left", "900 × 500")),
            ("OUTPATIENT",  NARROW, "consult",    ("Right leaf", "lower right", "900 × 400")),
        ],
        "focus": {"hiv": (0.50, 0.42), "pharmacy": (0.62, 0.44), "malaria": (0.50, 0.55),
                  "cbc": (0.50, 0.45), "ultrasound": (0.50, 0.40), "lab": (0.52, 0.36),
                  "consult": (0.50, 0.30)},
        "web_head": "Eight panes,<br>two widths.",
        "web_blurb": "Four panes at 900 × 500 mm and four at 900 × 400 mm, measured on the door "
                     "rather than scaled from a photograph. Same plate, same caption band, sizes "
                     "set from the glass.",
    },
    {
        "n": 2, "folder": "door-2", "prefix": "D2", "film": "one-way",
        "film_name": "ONE-WAY VISION FILM",
        "role": "general medicine and procedures",
        "edits": {},
        "spec": [
            ("WELCOME",             WIDE,   "reception",        ("Left leaf", "upper left", "900 × 500")),
            ("IMMUNISATION",        NARROW, "immunisation",     ("Left leaf", "upper right", "900 × 400")),
            ("GENERAL OUTPATIENT",  WIDE,   "consult_bp",       ("Left leaf", "lower left", "900 × 500")),
            ("LABORATORY",          NARROW, "lab_micro",        ("Left leaf", "lower right", "900 × 400")),
            ("MINOR SURGERY",       WIDE,   "surgery",          ("Right leaf", "upper left", "900 × 500")),
            ("PHARMACY",            NARROW, "pharmacy_counter", ("Right leaf", "upper right", "900 × 400")),
            ("OUR SERVICES",        WIDE,   None,               ("Right leaf", "lower left", "900 × 500")),
            ("HIV CARE",            NARROW, "hiv_selftest",     ("Right leaf", "lower right", "900 × 400")),
        ],
        "zoom": {"reception": 1.30},
        "focus": {"reception": (0.50, 0.38), "immunisation": (0.50, 0.50),
                  "consult_bp": (0.52, 0.40), "lab_micro": (0.50, 0.42),
                  "surgery": (0.48, 0.58), "pharmacy_counter": (0.55, 0.45),
                  "hiv_selftest": (0.65, 0.55)},
        "web_head": "The welcome door.<br>Open 24 hours.",
        "web_blurb": "Door 2 opens with WELCOME and the 24-hour line, then general outpatient, "
                     "immunisation, minor surgery, laboratory, pharmacy and HIV care. Same eight "
                     "measured panes as door 1, seven new photographs, none repeated.",
    },
    {
        "n": 3, "folder": "door-3", "prefix": "D3", "film": "opaque",
        "film_name": "OPAQUE WHITE VINYL  ·  NOT SEE-THROUGH",
        "role": "family and community care",
        "edits": {},
        "spec": [
            ("ANTENATAL & POSTNATAL", WIDE,   "antenatal_consult", ("Left leaf", "upper left", "900 × 500")),
            ("LABORATORY",            NARROW, "lab_scientist",     ("Left leaf", "upper right", "900 × 400")),
            ("PAEDIATRICS",           WIDE,   "paeds",             ("Left leaf", "lower left", "900 × 500")),
            ("PHARMACY",              NARROW, "pharmacy_shelf",    ("Left leaf", "lower right", "900 × 400")),
            ("MINOR SURGERY",         WIDE,   "surgery_tools",     ("Right leaf", "upper left", "900 × 500")),
            ("ULTRASOUND",            NARROW, "ultrasound_exam",   ("Right leaf", "upper right", "900 × 400")),
            ("OUR SERVICES",          WIDE,   None,                ("Right leaf", "lower left", "900 × 500")),
            ("CBC",                   NARROW, "cbc_rack_2",        ("Right leaf", "lower right", "900 × 400")),
        ],
        "focus": {"antenatal_consult": (0.48, 0.50), "lab_scientist": (0.48, 0.42),
                  "paeds": (0.52, 0.42), "pharmacy_shelf": (0.52, 0.45),
                  "surgery_tools": (0.50, 0.50), "ultrasound_exam": (0.60, 0.40),
                  "cbc_rack_2": (0.46, 0.50)},
        "web_head": "The family door.<br>Nothing shows through.",
        "web_blurb": "The third doorway uses solid white vinyl instead of perforated film, so the "
                     "glass behind it disappears and the print carries full detail. Antenatal & "
                     "postnatal, paediatrics and ultrasound lead the family door.",
    },
]

SUB = {
    "HIV TESTING": "RAPID TEST & LAB", "HIV CARE": "TESTING & TREATMENT",
    "PHARMACY": "DISPENSARY", "MALARIA": "TESTING",
    "CBC": "FULL BLOOD COUNT", "ANTENATAL": "ANTENATAL CARE",
    "ANTENATAL & POSTNATAL": "MOTHER & BABY", "LABORATORY": "TESTS & RESULTS",
    "CONSULTATION": "DOCTOR'S ROOM", "OUTPATIENT": "WALK-IN CLINIC",
    "GENERAL OUTPATIENT": "WALK-IN CLINIC", "OUR SERVICES": "SERVICES OFFERED",
    "IMMUNISATION": "VACCINES FOR ALL AGES", "MINOR SURGERY": "DRESSINGS & PROCEDURES",
    "WELCOME": "OPEN 24 HOURS", "PAEDIATRICS": "CHILD HEALTH",
    "ULTRASOUND": "SCANNING",
}

DOOR3_SUB = {"IMMUNISATION": "CHILD HEALTH & VACCINES"}

# every frame whose people were recoloured to Black African, so the doors show the
# community BACTIMED serves. Recorded in each README and on the licence line.
EDITS = {"pharmacy": "ph-pharmacy.jpg", "lab": "ph-lab.jpg", "consult": "ph-consult.jpg",
         "reception": "ph-reception.jpg", "lab_micro": "ph-lab-micro.jpg",
         "pharmacy_counter": "ph-pharmacy-counter.jpg", "hiv_selftest": "ph-hiv-selftest.jpg",
         "antenatal_consult": "ph-antenatal.jpg", "lab_scientist": "ph-lab-scientist.jpg",
         "pharmacy_shelf": "ph-pharmacy-shelf.jpg", "paeds": "ph-paeds.jpg",
         "ultrasound_exam": "ph-ultrasound.jpg"}


# -------------------------------------------------------------------- panels
def configure(door):
    for mod in (ART, B, D, R):
        if hasattr(mod, "use_brand"):
            mod.use_brand(B)
    base = os.path.join(ROOT, "bcm", door["folder"])
    ART.OUT = os.path.join(base, "artwork")
    P.CACHE_DIR = os.path.join(WORK, "bcm_d1_photos")
    for key, fname in EDITS.items():
        path = os.path.join(ROOT, "assets", "photos", "edited", fname)
        w, h = Image.open(path).size
        P.PHOTOS[key]["src"] = os.path.join("edited", fname)
        P.PHOTOS[key]["px"] = (w, h)
        P.PHOTOS[key]["edit"] = True
    return base


def panels(door):
    out = []
    subs = dict(SUB)
    if door["n"] == 3:
        subs.update(DOOR3_SUB)
    for i, (service, w, photo, _pos) in enumerate(door["spec"], start=1):
        p = {
            "id": f"{door['prefix']}-P{i}", "service": service, "sub": subs[service],
            "w": w, "h": PANE_H, "photo": photo,
            "focus": door["focus"].get(photo, (0.5, 0.4)) if photo else (0.5, 0.4),
            "zoom": door.get("zoom", {}).get(photo, 1.0), "title_cap": 64,
            "accent": "cyan", "film": door["film"],
            "orientation": "PORTRAIT — GLAZED DOOR PANE (MEASURED)",
            "aspect": f"1 : {PANE_H / w:.2f}",
            "note": "",
            "list_items": SERVICES if service == "OUR SERVICES" else None,
        }
        out.append(p)
    # no photograph may appear twice on a door
    photos = [p["photo"] for p in out if p["photo"]]
    assert len(photos) == len(set(photos)), f"door {door['n']}: repeated photograph"
    return out


# -------------------------------------------------------------------- mockup
def mockup(door, panels_by_id, night=False):
    base = os.path.join(ROOT, "bcm", door["folder"])
    S = 1.5                                   # px per mm
    FRAME, LEAF_W, LEAF_H = 60, WIDE + NARROW + 180, PANE_H * 2 + 180
    total_w = LEAF_W * 2 + FRAME
    SIGN_H, WALL = 560, 240
    w = int((total_w + WALL * 2) * S)
    h = int((LEAF_H + SIGN_H + 100 + 40 + 210) * S)

    g = np.linspace(0.92, 0.78, h).reshape(h, 1, 1)
    base_rgb = np.array([0.93, 0.91, 0.86]) if not night else np.array([0.14, 0.17, 0.24])
    arr = np.repeat(g * base_rgb.reshape(1, 1, 3), w, axis=1)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    ox = int(WALL * S)
    sx, sy = ox - int(FRAME * S), int(60 * S)
    sw, sh = int((total_w + FRAME * 2) * S), int(SIGN_H * S)
    d.rectangle([sx, sy, sx + sw, sy + sh], fill=(22, 35, 63))
    d.rectangle([sx, sy, sx + int(300 * S), sy + sh], fill=(232, 238, 244))

    sign_pdf = os.path.join(WORK, f"{door['prefix'].lower()}_sign.pdf")
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
        yy = ly + int(10 * S)
        while yy < ly + int(70 * S):
            d.rectangle([lx + int(10 * S), yy, lx + lw - int(10 * S), yy + int(3.4 * S)],
                        fill=(168, 126, 58))
            yy += int(11 * S)
        rows = [("upper", ly + int(80 * S)),
                ("lower", ly + int(80 * S) + int((PANE_H + FRAME) * S))]
        for rname, ry in rows:
            for col, pw_mm in enumerate((WIDE, NARROW)):
                px = lx + int((FRAME + (0 if col == 0 else WIDE + FRAME)) * S)
                pid = f"{door['prefix']}-P{leaf * 4 + (1 if rname == 'upper' else 3) + col}"
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
        hx = lx + lw - int(52 * S) if leaf == 0 else lx + int(20 * S)
        d.rounded_rectangle([hx, ly + int(760 * S), hx + int(24 * S), ly + int(1300 * S)],
                            radius=int(12 * S), fill=(206, 210, 214))

    out_dir = os.path.join(base, "lookbook")
    os.makedirs(out_dir, exist_ok=True)
    tag = "M-02" if night else "M-01"
    path = os.path.join(out_dir, f"{tag}-door-{door['n']}-{'night' if night else 'day'}.png")
    if img.width > 2600:
        img = img.resize((2600, round(img.height * 2600 / img.width)), Image.LANCZOS)
    img.save(path, "PNG", optimize=True)
    return path


def _panel_png(panel, px_h=900):
    import cp_mockup as MK
    return MK.panel_png(panel, px_h)


# ----------------------------------------------------------------- documents
def schedule(door, panels_list):
    base = os.path.join(ROOT, "bcm", door["folder"])
    path = os.path.join(base, "docs", f"BCM-Door-{door['n']}-Schedule.pdf")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    D.use_brand(B)
    eyebrow = f"BACTIMED  ·  COMMUNITY MEDICAL CENTRE  ·  {door['film_name']}"
    c = D.new_doc(path, f"BACTIMED Community Medical Centre — door {door['n']} pane schedule")
    D.page_bg(c, f"BCM / {door['prefix']} / 01", "Rev B  ·  2026-10-29  ·  MEASURED", 1,
              eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, f"Door {door['n']} — pane schedule", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "Eight panes on one double door. Four measure 900 × 500 mm and four measure "
               "900 × 400 mm — all 900 mm high, so every design is portrait and the width is the "
               "only variable. The sizes are the client's own measurement, repeated across the "
               "three doorways; confirm each pane on site before the film is plotted.",
               (D.PW - 2 * D.M) / MM, 3.3, B.NAVY_MID)
    y -= 2 * MM
    cols = [("Pane", 16, "left"), ("Service", 34, "left"), ("Glass H × W", 26, "left"),
            ("Aspect", 18, "left"), ("Leaf", 24, "left"), ("Position", 26, "left"),
            ("Photo", 16, "left"), ("File", 40, "left")]
    rows = []
    for p, (_s, _w, photo, pos) in zip(panels_list, door["spec"]):
        rows.append([p["id"], p["service"], f"{p['h']} × {p['w']}", p["aspect"],
                     pos[0], pos[1], (P.PHOTOS[photo]["asset"] if photo else "GRAPHIC"),
                     f"{p['id']}.pdf"])
    y = D.table(c, D.M, y, cols, rows, row_h=9.6 * MM, cap=2.9) - 6 * MM

    B.label(c, D.M, y, "THIS DOORWAY", 4.0, B.TEAL, "Inter-600", 1.6)
    y -= 6 * MM
    D.bullets(c, D.M, y, door_schedule_notes(door), 168 * MM, 3.1, B.NAVY_MID)
    c.showPage()

    D.page_bg(c, f"BCM / {door['prefix']} / 01", "Rev B  ·  2026-10-29  ·  MEASURED", 2,
              eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "Layout as measured", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "Two leaves, two columns and two rows per leaf: the 500 mm column on the left of each "
           "leaf, the 400 mm column on the right. If the site is the other way round, say so — "
           "the artwork is width-agnostic, but the pane numbers would swap.",
           (D.PW - 2 * D.M) / MM, 3.2, B.NAVY_MID)

    svc_of = {p["id"]: p["service"] for p in panels_list}
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
                pid = f"{door['prefix']}-P{leaf * 4 + (1 if rname == 'upper' else 3) + col}"
                B.label(c, px + 3 * MM, py + PANE_H * scale - 8 * MM, pid, 4.2,
                        B.WHITE, "Inter-600", 0.8)
                B.label(c, px + 3 * MM, py + 4 * MM, svc_of[pid], 3.6,
                        B.CP_CYAN, "Inter-500", 0.6)
        B.label(c, lx, y0 - 8 * MM, f"LEAF {'A' if leaf == 0 else 'B'} — "
                f"{'LEFT' if leaf == 0 else 'RIGHT'}", 3.6, B.GREY, "Inter-600", 1.4)

    tx = x0 + (leaf_w * 2 + 60) * scale + 26 * MM
    tw = D.PW - tx - D.M
    B.label(c, tx, D.PH - 74 * MM, "WHY THE TWO WIDTHS MATTER", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, tx, D.PH - 82 * MM, door_layout_notes(door),
              tw, 3.0, B.NAVY_MID, gap=2.4)
    c.showPage()
    c.save()
    return path


def door_schedule_notes(door):
    n = door["n"]
    if n == 1:
        return [
            "The services are the clinic's own board, dental left out at their instruction: "
            "general outpatient, inpatient care, HIV care, immunisation, pharmacy, laboratory, "
            "ultrasound, antenatal & postnatal, obs & gyn, paediatrics, minor surgery, family "
            "planning, ENT, eye services, orthopaedics and travel medical examination.",
            "Type is set to the pane, not to taste: the service name is capped at 13.5 % of the "
            "pane width, so a 400 mm pane carries a smaller name than a 500 mm one and reads the "
            "same from the pavement.",
            "The white logo plate is measured from its own type and squeezed to fit the narrowest "
            "pane, so the badge and wordmark sit identically on all eight.",
            "The directory pane carries nine lines at 14 mm cap — still one column, still legible "
            "behind the perforation.",
        ]
    if n == 2:
        return [
            "Same door, same eight panes, same measurements as door 1 — this is the second "
            "doorway, not a second design system.",
            "It is the welcome door: the entrance pane sits in the top-left corner of leaf A, "
            "where a patient walking up reads it first, and it carries the 24-hour line from the "
            "clinic's own board.",
            "Behind it, general outpatient, immunisation, minor surgery, laboratory, pharmacy and "
            "HIV care — the walk-in services. Seven new photographs, none used on door 1 or door "
            "3. Two long names (GENERAL OUTPATIENT, WELCOME's neighbours) break to two lines "
            "rather than shrinking away.",
            "The directory repeats door 1's nine lines so the two doors can never disagree.",
        ]
    return [
        "Same door, same eight panes, same measurements — but opaque film, so nothing shows "
        "through the glass.",
        "It leads on family care: antenatal & postnatal, paediatrics and ultrasound, with "
        "pharmacy, laboratory, minor surgery and CBC around them. WELCOME now sits on door 2, "
        "where the client asked for it.",
        "Because the film is solid there is no perforation to read through, so fine detail and "
        "smaller type survive: this is the door where a photograph can be printed as a "
        "photograph.",
        "Opaque film also means the pane can no longer be seen through from either side. That "
        "changes how the entrance looks from inside at night — the client should be shown the "
        "night elevation before this one is ordered.",
    ]


def door_layout_notes(door):
    n = door["n"]
    if n == 1:
        return [
            "Left column of each leaf: 900 × 500 — HIV testing, malaria and antenatal carry the "
            "subject at full width.",
            "Right column: 900 × 400 — the narrower panes take equipment and hands: pharmacy "
            "shelving, the microscope, the blood draw, the doctor's room.",
            "Eight panes, seven photographs and one directory. No image repeats anywhere on the "
            "door, and no image is shared with doors 2 or 3.",
            "Bleed is 10 mm on every edge, so the printed piece is 920 × 520 and 920 × 420 mm.",
            "The directory pane needs its nine lines at 14 mm cap to stay legible on a 400 mm "
            "pane — which is why it sits in the wide column.",
        ]
    if n == 2:
        return [
            "Left leaf reads outward-facing: WELCOME above immunisation, general outpatient "
            "below, laboratory at the foot.",
            "Right leaf carries minor surgery and the dispensary, then the directory and HIV care "
            "at eye level on the approach.",
            "Wide panes take the scenes with people; narrow panes take equipment, hands and "
            "bottles, which survive the perforation better than faces.",
            "Eight panes, seven photographs and one directory — none of them repeated from "
            "another door.",
            "Bleed is 10 mm on every edge, so the printed piece is 920 × 520 and 920 × 420 mm.",
        ]
    return [
        "Left leaf is the family leaf: antenatal & postnatal and paediatrics at full width, "
        "laboratory and pharmacy in the narrow column.",
        "Right leaf opens with minor surgery, then the ultrasound pane at eye level, the "
        "directory, and CBC at the foot.",
        "Opaque vinyl, so the photograph is not interrupted by a mesh. Print it as a photograph: "
        "the file, not the film, is now the limit on detail.",
        "Eight panes, seven photographs and one directory — none repeated from doors 1 or 2.",
        "Bleed is 10 mm on every edge, so the printed piece is 920 × 520 and 920 × 420 mm.",
    ]


def spec(door):
    base = os.path.join(ROOT, "bcm", door["folder"])
    path = os.path.join(base, "docs", f"BCM-Door-{door['n']}-Specification.pdf")
    D.use_brand(B)
    eyebrow = f"BACTIMED  ·  COMMUNITY MEDICAL CENTRE  ·  {door['film_name']}"
    c = D.new_doc(path, f"BACTIMED Community Medical Centre — door {door['n']} production specification")
    D.page_bg(c, f"BCM / {door['prefix']} / 02", "Rev B  ·  2026-10-29", 1, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, f"Production specification — door {door['n']}", 8.0)
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
                         "the narrow; long names break to two lines rather than shrink"],
        ["Smallest live type", ("6 mm cap — the perforation is the limit" if door["film"] == "one-way"
                                else "4 mm cap — opaque vinyl, no mesh limit")],
        ["Resolution", "75 ppi floor, 100 ppi target in the placed crop"],
        ["Colour", "CMYK, coated profile; navy #16233F, cyan #2BA9E0"],
        ["Fonts", "Manrope + Inter, SIL OFL, embedded"],
        ["Film", ("Opaque white blockout vinyl — no perforation, no see-through"
                  if door["film"] == "opaque" else
                  "Perforated one-way vision vinyl, white-backed, 140–160 µm")],
    ]
    y = D.table(c, D.M, y, [("Item", 44, "left"), ("Value", 150, "left")], rows,
                row_h=7.0 * MM, cap=2.9) - 7 * MM
    B.label(c, D.M, y, "FILM", 4.2, B.TEAL, "Inter-600", 1.8)
    y -= 6 * MM
    y = D.bullets(c, D.M, y, film_notes(door), 168 * MM, 3.1, B.NAVY_MID, gap=2.4)
    if door["film"] == "opaque":
        B.label(c, D.M, y - 4 * MM, "WHAT OPAQUE CHANGES", 4.2, B.TEAL, "Inter-600", 1.8)
        y = y - 10 * MM
        y = D.bullets(c, D.M, y, opaque_notes(door), 168 * MM, 3.1, B.NAVY_MID, gap=2.4)
    B.label(c, D.M, y - 4 * MM, "ABOUT THE FILES IN THIS PACKAGE", 4.2, B.TEAL,
            "Inter-600", 1.8)
    y = y - 10 * MM
    D.para(c, D.M, y,
           "The PDFs are the artwork: true size, 10 mm bleed, 4 mm marks and a 20 mm slug, in "
           "CMYK with the fonts embedded. The placed photographs are desktop previews, roughly "
           "25–40 ppi at final size, so plot from the full-size originals recorded in the README "
           "rather than from this package — every frame has its Pexels ID and link listed. If BCM "
           "prefers its own team on the door, one morning with a phone on the same eight subjects "
           "beats any stock image, and the artwork takes new files without a single change.",
           168 * MM, 3.0, B.NAVY_MID)
    c.showPage()

    D.page_bg(c, f"BCM / {door['prefix']} / 02", "Rev B  ·  2026-10-29", 2, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, f"Installation — door {door['n']}", 8.0)
    D.bullets(c, D.M, y + 2 * MM, install_notes(door), 120 * MM, 3.0, B.NAVY_MID, gap=2.2)

    tx = D.M + 132 * MM
    tw = D.PW - tx - D.M
    B.label(c, tx, D.PH - 44 * MM, "OPEN ITEMS", 4.2, B.TEAL, "Inter-600", 1.8)
    D.bullets(c, tx, D.PH - 52 * MM, open_items(door), tw, 3.0, B.NAVY_MID, gap=2.2)
    c.showPage()
    c.save()
    return path


def film_notes(door):
    if door["film"] == "opaque":
        return [
            "Opaque white blockout self-adhesive vinyl, 100–140 µm plus liner, grey-backed so "
            "nothing shows through from either side — confirm with printer.",
            "No perforation, so no mesh limit: detail, gradients and type below 6 mm cap all "
            "hold. Treat it as a poster on glass, not as a mesh.",
            "Matte anti-glare face, UV or latex print, four colour plus white. White backing "
            "layer is still needed where the navy sits on clear glass at the edges.",
            "Eight pieces per door, cut from one roll run. The opaque door cannot be mixed with "
            "offcuts from the one-way doors — the substrate is different and the colour will "
            "read differently.",
            "Because the glass is now blocked, check the door's function: a solid pane hides the "
            "room behind it from outside and hides the street from inside. Confirm this is "
            "wanted on this particular door.",
        ]
    return [
        "Perforated one-way vision vinyl, white-backed, 140–160 µm plus liner — confirm with "
        "printer.",
        "1.6 mm holes on a 2.3 mm staggered pitch, ≈44 % open by geometry. The mesh, not the "
        "file, is the limit on detail.",
        "Matte anti-glare face, UV or latex print, four colour plus white backing layer.",
        "Eight pieces per door. Cut from one roll run so the navy matches across all eight.",
        "Doors 1 and 2 use the same film and should be printed in the same run if the schedule "
        "allows; door 3 is a different substrate and will not match it exactly.",
    ]


def opaque_notes(door):
    return [
        "Nothing shows through: not the room behind the glass, not the street from inside. The "
        "pane becomes a flat poster on both faces.",
        "Print at full detail. There is no mesh to break up fine type, gradients or skin, so the "
        "6 mm minimum on the perforated doors does not apply here.",
        "The navy will read slightly denser than on the one-way doors, because it is printed on "
        "solid white rather than over 44 % open holes. Judge it against door 1 before signing "
        "off, and expect a small difference rather than a match.",
        "Clean with a soft cloth and water only. Opaque vinyl on glass cannot be wiped with "
        "solvent, and a blade to remove it later will scratch the glass — plan the removal.",
    ]


def install_notes(door):
    common = [
        "Re-measure every pane with a tape, corner to corner, before plotting. Measured figures "
        "were supplied for these doors; the next one may not match.",
        "Number the panes on the back of each print in pencil as they are cut — eight pieces, "
        "two sizes, and they all look alike in a stack.",
        "Clean the glass and apply one pane as a control: the narrowest, most awkward one, low "
        "on the leaf, where mistakes are least visible.",
        "Trim inside the rebate, 2 mm clear of the glass edge. Clear 25 mm around handles, locks "
        "and hinges.",
        "Do not stretch the film to fit a pane. If a pane is out of square by more than 3 mm, "
        "re-cut the artwork to the measured diagonal — the design has room for it.",
        "Leave 24 hours before cleaning or closing the door against the film.",
    ]
    if door["film"] == "opaque":
        common.insert(3, "Opaque vinyl shows every air bubble and every speck of dust under a "
                         "flat colour: use a felt squeegee and wet or dry application exactly as "
                         "the printer specifies, and never a heat gun on the glass.")
    else:
        common.insert(3, "Keep the perforation grid square to the frame, not to the handle. On "
                         "two 900 mm rows stacked, a skewed grid reads as a crooked poster.")
    return common


def open_items(door):
    items = [
        "Confirm the column order on the leaf: 500 mm on the left as drawn, or mirrored?",
        "BACTIMED's own vector logo, to replace the recreated badge on all eight panes.",
        "Confirm the two help-line numbers (0771 240 104 / 0754 132 715) read off the premises boards — they now print on the foot of every pane.",
        "The printer's own film standard, to replace the flagged values.",
        "Print-resolution originals: the working files are desktop previews. Pull the full-size "
        "files from the recorded Pexels links, or shoot the real team.",
    ]
    if door["film"] == "opaque":
        items.insert(3, "Confirm the client wants a solid pane on this door — it blocks the view "
                        "in and out.")
    return items


def combined(door, paths):
    base = os.path.join(ROOT, "bcm", door["folder"])
    path = os.path.join(base, f"BCM-Door-{door['n']}-Panels.pdf")
    w = PdfWriter()
    for p in paths:
        for page in PdfReader(p).pages:
            w.add_page(page)
    with open(path, "wb") as fh:
        w.write(fh)
    return path


def web(door, panels_list):
    base = os.path.join(ROOT, "bcm", door["folder"])
    art_dir = os.path.join(base, "artwork")
    web_dir = os.path.join(base, "web")
    os.makedirs(web_dir, exist_ok=True)
    cards = []
    for p in panels_list:
        pdf = os.path.join(art_dir, f"{p['id']}.pdf")
        doc = pdfium.PdfDocument(pdf)
        page = doc[0]
        img = page.render(scale=760 / page.get_size()[0]).to_pil().convert("RGB")
        doc.close()
        img.save(os.path.join(web_dir, f"{p['id']}.jpg"), "JPEG", quality=88, optimize=True)
        photo = (P.PHOTOS[p["photo"]]["creator"] if p["photo"] else "No photograph")
        cards.append(f"""
    <figure class="card">
      <a href="artwork/{p['id']}.pdf"><img src="web/{p['id']}.jpg" alt="{p['service']} pane"></a>
      <figcaption><b>{p['id']}</b> · {p['service'].title()} · {p['w']}×{p['h']} mm<br>
      <span>{photo}</span></figcaption>
    </figure>""")
    retouched = [p["photo"] for p in panels_list if p["photo"] and
                 P.PHOTOS[p["photo"]].get("edit")]
    retouch = (" Four frames carry an AI colour retouch so the people reflect the community BCM "
               "serves; they are models, not staff." if retouched else "")
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BACTIMED — door {door['n']}</title>
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
.nav a{{margin-right:18px}}
</style></head><body>
<header>
  <div style="letter-spacing:.3em;font-size:11px;color:#2ba9e0">BACTIMED · COMMUNITY MEDICAL CENTRE · DOOR {door['n']} · {door['film_name']}</div>
  <h1>{door['web_head']}</h1>
  <p>{door['web_blurb']}</p>
  <p class="nav"><a href="BCM-Door-{door['n']}-Panels.pdf">All eight panes (PDF)</a>
     <a href="docs/BCM-Door-{door['n']}-Schedule.pdf">Schedule</a>
     <a href="docs/BCM-Door-{door['n']}-Specification.pdf">Specification</a></p>
</header>
<main class="grid">{''.join(cards)}</main>
<footer>Rev B — {door['film_name'].title()}. Photographs are Pexels Free licence, recorded pane by
pane in the README.{retouch} Working files are preview resolution; pull the full-size originals
from the recorded links before plotting.</footer>
</body></html>"""
    path = os.path.join(base, "index.html")
    open(path, "w").write(html)
    return path


def readme(door, panels_list):
    base = os.path.join(ROOT, "bcm", door["folder"])
    rows = ["| Pane | Service | Glass (H × W) | Photograph | Leaf · position |",
            "| --- | --- | --- | --- | --- |"]
    for p, (_s, _w, photo, pos) in zip(panels_list, door["spec"]):
        if photo:
            ph = P.PHOTOS[photo]
            label = f"{ph['asset']} {ph['title']}"
        else:
            label = "none — type only"
        rows.append(f"| {p['id']} | {pretty(p['service'])} | {p['h']} × {p['w']} | {label} "
                    f"| {pos[0].lower()} · {pos[1]} |")

    credits = ["| Asset | Pexels ID | Creator | Original | Edited |", "| --- | --- | --- | --- | --- |"]
    for p in panels_list:
        if not p["photo"]:
            continue
        ph = P.PHOTOS[p["photo"]]
        credits.append(f"| {ph['asset']} | {ph['id']} | {ph['creator']} | "
                       f"{ph['px'][0]} × {ph['px'][1]} px | "
                       f"{'yes — colour retouch' if ph.get('edit') else 'no'} |")

    film_line = ("Perforated one-way vision vinyl — you can see out through the print from inside."
                 if door["film"] == "one-way" else
                 "Opaque white blockout vinyl — nothing shows through, and the print carries full "
                 "detail because there is no mesh over it.")

    provisional_extra = ("- Opaque film blocks the view through the glass, in and out; confirm "
                         "that is wanted on this door.\n- The night elevation assumes the door is "
                         "lit from the street and the fascia: an opaque pane cannot be backlit." if door["film"] == "opaque" else
                         "- Doors 1 and 2 use the same perforated film; door 3 is opaque vinyl and "
                         "will not match it exactly.")
    text = f"""# BACTIMED Community Medical Centre — door {door['n']}

Eight panes on the {ordinal(door['n'])} doorway, built from the client's own measurement rather
than from a photograph: four panes at **900 × 500 mm** and four at **900 × 400 mm**, all 900 mm
high. The geometry is identical on all three doors; only the subject matter and the film change.

{film_line}

{chr(10).join(rows)}

Seven different photographs and one type-only directory. No image on this door appears on either
of the other two.

## Files

- `artwork/{door['prefix']}-P1…P8.pdf` — print files, pane + 10 mm bleed + 20 mm slug + crop marks
- `BCM-Door-{door['n']}-Panels.pdf` — all eight pages in one file
- `docs/BCM-Door-{door['n']}-Schedule.pdf` — schedule + measured layout diagram
- `docs/BCM-Door-{door['n']}-Specification.pdf` — film, artwork setup, installation, open items
- `lookbook/M-01-door-{door['n']}-day.png`, `M-02-door-{door['n']}-night.png` — elevations
- `index.html` — web preview

## Photography

All photographs are Pexels Free licence, checked 29 October 2026: free commercial use, no
attribution required, modification allowed. The ones carrying an AI colour retouch so the people
reflect the community BACTIMED serves are marked in the table below; the people in those frames are
models, never staff or patients, and no pane captions them as such.

{chr(10).join(credits)}

Working files are desktop previews, not print files. Pull the full-size original from the Pexels
link for each ID before plotting — the record of what was used, and where it came from, is the
point of the table.

## Provisional

- Column order is drawn as 500 mm left, 400 mm right on both leaves — confirm, or say if the
  second leaf is mirrored.
- The B monogram is a recreation, not BCM's official logo.
- The two help-line numbers (0771 240 104 / 0754 132 715) come off the clinic's own premises
  boards and print on the foot of every pane; confirm they are still current.
{provisional_extra}
Rebuild: `cd source && python3 bcm_doors.py {door['n']}`
"""
    path = os.path.join(base, "README.md")
    open(path, "w").write(text)
    return path


def pretty(service):
    out = service.title()
    return out.replace("Cbc", "CBC").replace("Hiv", "HIV")


def ordinal(n):
    return {1: "first", 2: "second", 3: "third"}.get(n, f"{n}th")


# ---------------------------------------------------------------------- main
def build(door):
    base = configure(door)
    art_dir = os.path.join(base, "artwork")
    os.makedirs(art_dir, exist_ok=True)
    plist = panels(door)
    paths = [ART.build(p, os.path.join(art_dir, f"{p['id']}.pdf")) for p in plist]
    print(f"door {door['n']}: artwork", len(paths))
    # the render cache is keyed by pane id only, so clear this door's entries
    for f in os.listdir(WORK) if os.path.isdir(WORK) else []:
        if f.startswith(f"{door['prefix']}-P"):
            os.remove(os.path.join(WORK, f))
    by_id = {p["id"]: p for p in plist}
    print(mockup(door, by_id, False))
    print(mockup(door, by_id, True))
    print(schedule(door, plist))
    print(spec(door))
    print(combined(door, paths))
    print(web(door, plist))
    print(readme(door, plist))


def main():
    want = [int(a) for a in sys.argv[1:] if a.isdigit()] or [1, 2, 3]
    # the photo cache is keyed by asset + size + focus, not by file, so a new retouch
    # would silently reuse the old crop
    cache = os.path.join(WORK, "bcm_d1_photos")
    if os.path.isdir(cache):
        for f in os.listdir(cache):
            os.remove(os.path.join(cache, f))
    for door in DOORS:
        if door["n"] in want:
            build(door)


if __name__ == "__main__":
    main()
