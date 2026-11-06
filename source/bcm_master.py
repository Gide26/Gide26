"""BCM Medical Centre — the complete delivery set.

Assembles one folder and one zip holding everything built so far:

    the four door film packages (32 panes), the sign post panel,
    the three roadside banners,

plus a master proof (`BCM-Complete-Set.pdf`), a manifest, a README and a web
index. Nothing is re-designed here: the master collects the files that already
exist and documents them in one place.
"""
import csv
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib.units import mm as MM
from PIL import Image

import bcm_brand as B
import cp_docutil as D
import cp_photos as P
import bcm_doors as DOORS
import bcm_sign as SIGN
import bcm_banners as BAN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SET = os.path.join(ROOT, "bcm")
OUT_DIR = os.path.join(SET, "complete")
ZIP = os.path.join(SET, "BCM-Complete-Set.zip")
WORK = os.path.join(ROOT, "source", ".work", "bcm_master")
REV = "Rev A  ·  2026-11-02"
SET_NAME = "BCM-Signage-Set"

# the four groups, in the order the client should read them
GROUPS = [
    {"key": "door-1", "n": "01", "title": "Door 1 — testing and treatment",
     "kind": "One-way vision film · 8 panes",
     "cover": "door-1/lookbook/M-01-door-1-day.png"},
    {"key": "door-2", "n": "02", "title": "Door 2 — the welcome door",
     "kind": "One-way vision film · 8 panes",
     "cover": "door-2/lookbook/M-01-door-2-day.png"},
    {"key": "door-3", "n": "03", "title": "Door 3 — family, eye, ENT and ward",
     "kind": "Opaque film · 8 panes",
     "cover": "door-3/lookbook/M-01-door-3-day.png"},
    {"key": "door-4", "n": "04", "title": "Door 4 — dispensary and diagnostics",
     "kind": "One-way vision film · 8 panes",
     "cover": "door-4/lookbook/M-01-door-4-day.png"},
    {"key": "sign", "n": "05", "title": "Sign post panel",
     "kind": "Double-sided panel · 1219 × 610 mm",
     "cover": "sign/lookbook/M-01-sign-day.png"},
    {"key": "banners", "n": "06", "title": "Roadside banners",
     "kind": "PVC banners · 3.8 / 3.4 / 2.4 m × 1.0 m",
     "cover": "banners/lookbook/M-00-banner-set.png"},
]

B.register_fonts()
D.use_brand(B)


def png(rel):
    return os.path.join(SET, rel)


def downsampled(rel, max_px=1500):
    """A small JPEG copy for embedding: the elevations are 2600 px wide, and
    embedding them full size bloats the master proof past 13 MB."""
    os.makedirs(WORK, exist_ok=True)
    src = png(rel)
    out = os.path.join(WORK, rel.replace("/", "_").rsplit(".", 1)[0] + f"_{max_px}.jpg")
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
        return out
    im = Image.open(src).convert("RGB")
    if im.width > max_px:
        im = im.resize((max_px, round(max_px * im.height / im.width)), Image.LANCZOS)
    im.save(out, "JPEG", quality=90, optimize=True, progressive=True)
    return out


def img_box(c, rel, x, y, w, h=None, frame=True, paper=True):
    """Draw a PNG fitted into a box, centred, with a hairline frame."""
    path = downsampled(rel)
    iw, ih = Image.open(path).size
    bw = w
    bh = bh = bw * ih / iw
    if h and bh > h:
        bh = h
        bw = bh * iw / ih
    xx = x + (w - bw) / 2.0
    yy = y + ((h - bh) / 2.0 if h else 0)
    if paper:
        c.setFillColor(B.WHITE)
        c.rect(xx, yy, bw, bh, stroke=0, fill=1)
    c.drawImage(path, xx, yy, bw, bh, mask=None)
    if frame:
        c.setStrokeColor(B.MIST)
        c.setLineWidth(0.4)
        c.rect(xx, yy, bw, bh, stroke=1, fill=0)
    return (xx, yy, bw, bh)


# ------------------------------------------------------------------- the data
def photo_asset(key):
    if not key:
        return None
    m = P.PHOTOS[key]
    return m


def used_in():
    """asset key -> ['D1-P1', 'B-1', ...] across the whole set."""
    where = {}
    for d in DOORS.DOORS:
        for i, (service, w, photo, _pos) in enumerate(d["spec"], start=1):
            if photo:
                where.setdefault(photo, []).append(f"{d['prefix']}-P{i}")
    for b in BAN.BANNERS:
        for key, *_rest in b["photos"]:
            where.setdefault(key, []).append(b["id"])
    return where


def counts():
    panes = sum(len(d["spec"]) for d in DOORS.DOORS)
    photos = len(used_in())
    return panes, photos


# ----------------------------------------------------------------- the master
def cover(c):
    """Full-bleed navy cover: the lockup, the set at a glance, three thumbnails."""
    PW, PH, M = D.PW, D.PH, D.M

    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, PW, PH, stroke=0, fill=1)
    c.setFillColor(B.CP_CYAN)
    c.rect(0, PH - 3.5 * MM, PW, 3.5 * MM, stroke=0, fill=1)

    B.label(c, M, PH - 15 * MM, "BCM  ·  MEDICAL CENTRE  ·  COMPLETE SET", 3.4,
            B.CP_CYAN, "Inter-600", 1.8)
    B.label(c, PW - M, PH - 15 * MM, REV, 2.9, B.CP_MIST, "Inter-400", 1.2, "right")

    # the lockup, drawn live — same order as the sign post and the banners
    x = M
    B.caps(c, x, 170 * MM, "EDDWALIRO", 17.0, B.CP_CYAN, "Manrope-800", 2.8)
    B.monogram(c, x, 146 * MM, 15.0, dark=B.WHITE, accent=B.CP_CYAN)
    B.caps(c, x + 21 * MM, 156 * MM, "BCM", 4.2, B.CP_CYAN, "Inter-600", 2.4)
    B.caps(c, x + 20.6 * MM, 146 * MM, "MEDICAL CENTRE", 11.0, B.WHITE,
           "Manrope-800", 0.4)
    B.label(c, x + 21.0 * MM, 138 * MM, B.SLOGAN, 3.6, B.CP_MIST, "Inter-400", 1.0)

    # what the set is, at a glance
    panes, photos = counts()
    rows = [
        ("01 – 03", "Door film", "Three glazed doorways, 8 panes each", f"{panes} panes"),
        ("04", "Sign post", "Name-only panel, double sided", "1219 × 610 mm"),
        ("05", "Banners", "Roadside fence, three lengths", "3.8 / 3.4 / 2.4 m"),
    ]
    yy = 118 * MM
    c.setFillColor(B.CP_CYAN)
    c.rect(M, yy + 5 * MM, PW - 2 * M, 0.9, stroke=0, fill=1)
    for n, what, desc, spec in rows:
        B.label(c, M, yy - 3 * MM, n, 3.4, B.CP_CYAN, "Inter-600", 1.4)
        B.caps(c, M + 25 * MM, yy - 3.4 * MM, what, 4.2, B.WHITE, "Manrope-700", 0.6)
        B.label(c, M + 64 * MM, yy - 3 * MM, desc, 3.2, B.CP_MIST, "Inter-400", 0.6)
        B.label(c, PW - M, yy - 3 * MM, spec, 3.2, B.CP_CYAN, "Inter-600", 0.8, "right")
        yy -= 11.5 * MM

    # three thumbnails: a door, the sign post, a banner
    tw, gap = 56 * MM, 7 * MM
    tx = M
    ty = 30 * MM
    for rel, cap in (("door-1/lookbook/M-01-door-1-day.png", "DOOR 1"),
                     ("sign/lookbook/M-01-sign-day.png", "SIGN POST"),
                     ("banners/lookbook/M-B-01-day.png", "BANNER B-1")):
        box_h = 40 * MM
        xx, y0, bw, bh = img_box(c, rel, tx, ty, tw, box_h)
        B.label(c, tx, ty - 4.5 * MM, cap, 2.7, B.CP_CYAN, "Inter-600", 1.0)
        tx += tw + gap

    B.label(c, PW - M, ty + 40 * MM,
            f"{panes} panes · 1 panel · 3 banners · {photos} photographs", 3.2,
            B.CP_MIST, "Inter-500", 0.6, "right")
    B.label(c, PW - M, ty + 33 * MM,
            "Print-ready artwork, proofs, elevations, schedules and specifications.",
            3.0, B.CP_MIST, "Inter-400", 0.4, "right")
    B.label(c, PW - M, ty + 27 * MM,
            "Measured to the clinic's own premises.", 3.0, B.CP_MIST, "Inter-400",
            0.4, "right")


def contents(c):
    D.page_bg(c, "CONTENTS", f"{REV}", 2, eyebrow="BCM  ·  MEDICAL CENTRE  ·  COMPLETE SET")
    y = D.h1(c, D.PH - 34 * MM, "What is in the set", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "Five groups. Inside each: print files at 1 : 1, a multi-page proof, "
           "elevations, a README, a licence record and a web preview. The folder names "
           "below are the folder names in the zip.", (D.PW - 2 * D.M) / MM * 0.8, 3.2,
           B.NAVY_MID)

    rows = []
    for g in GROUPS:
        rows.append([g["n"], g["key"] + "/", g["title"], g["kind"]])
    yy = D.table(c, D.M, 132 * MM,
                 [("", 12, "left"), ("Folder", 34, "left"), ("What it is", 92, "left"),
                  ("Type", 96, "left")],
                 rows, row_h=8.0 * MM, head_h=6.6 * MM, cap=3.1, head_cap=2.8)

    yy -= 12 * MM
    B.label(c, D.M, yy, "AND AT THE TOP OF THE ZIP", 4.0, B.TEAL, "Inter-600", 1.6)
    yy = D.bullets(c, D.M, yy - 8 * MM, [
        "BCM-Complete-Set.pdf — this document: contents, pane schedules, the sign post, "
        "the banners, the full licence table and the handover checklist.",
        "README.md — the same story in text, with the rebuild commands.",
        "MANIFEST.csv — every file in the set with its type and size, for checking the "
        "handover.",
        "index.html — the set as a web page; open it in a browser and everything links.",
        "print/ — one print PDF per piece: 32 panes, 3 sign faces, 3 banners, numbered "
        "01–30, with PRINT-INDEX.pdf and a manifest. This is the folder the printer "
        "wants; the multi-page proofs are for approval only.",
        "complete/ — the master proof, manifest, README and index on their own, if you "
        "only want the paperwork.",
    ], 168 * MM, 3.0, B.NAVY_MID)

    yy -= 10 * MM
    B.label(c, D.M, yy, "NOT DUPLICATED", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, yy - 8 * MM, [
        "The per-group zips (BCM-Door-1-package.zip and so on) are left out of the set: "
        "they hold the same files you already have here. They stay on each group's own "
        "page for handing a single job to a single supplier.",
    ], 168 * MM, 3.0, B.NAVY_MID)


def door_page(c, door, page_no):
    n = door["n"]
    folder = door["folder"]
    prefix = door["prefix"]
    film = door["film_name"] if hasattr(door, "film_name") else door["film"]
    D.page_bg(c, f"DOOR {n}", f"{REV}", page_no,
              eyebrow="BCM  ·  MEDICAL CENTRE  ·  DOOR FILM")

    title = next(g["title"] for g in GROUPS if g["key"] == folder)
    y = D.h1(c, D.PH - 34 * MM, title, 7.6)
    D.para(c, D.M, y + 2 * MM,
           f"{door['role'].capitalize()}. Eight panes, 900 mm high: four at 900 × 500 mm on "
           f"the outer edges, four at 900 × 400 mm against the meeting stile. "
           f"{'One-way vision film — you can see out through the print from inside.' if door['film'] == 'one-way' else 'Opaque film: this door is not see-through.'}",
           (D.PW - 2 * D.M) / MM * 0.62, 3.2, B.NAVY_MID)

    img_box(c, f"{folder}/lookbook/M-01-{folder}-day.png", D.M, 42 * MM, 96 * MM,
            116 * MM)
    B.label(c, D.M, 36 * MM, "ELEVATION — DAY, TO SCALE", 2.8, B.GREY, "Inter-500", 0.8)

    rows = []
    for i, (service, w, photo, pos) in enumerate(door["spec"], start=1):
        if photo:
            m = P.PHOTOS[photo]
            ph = f"{m['asset']}  {m['title'][:46]}"
        else:
            ph = "— type only"
        rows.append([f"{prefix}-P{i}", service.title(), f"900 × {w}", ph])
    ty = 158 * MM
    ty = D.table(c, 122 * MM, ty,
                 [("Pane", 18, "left"), ("Service", 34, "left"),
                  ("Glass H × W", 28, "left"), ("Photograph", 104, "left")],
                 rows, row_h=7.2 * MM, head_h=6.4 * MM, cap=2.9, head_cap=2.7)

    ty -= 12 * MM
    B.label(c, 122 * MM, ty, "ON THIS DOOR", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, 122 * MM, ty - 8 * MM, [
        f"Print files: {folder}/artwork/{prefix}-P1…P8.pdf, 1 : 1 mm with bleed, slug "
        f"and crop marks. All eight pages also in {folder}/BCM-Door-{n}-Panels.pdf.",
        f"Schedule and specification in {folder}/docs/ — pane positions, film, "
        f"installation, open items.",
        "No photograph on this door appears on either of the other two, and no service "
        "repeats door to door.",
    ], 158 * MM, 3.0, B.NAVY_MID)


def sign_page(c):
    D.page_bg(c, "SIGN POST", f"{REV}", 6,
              eyebrow="BCM  ·  MEDICAL CENTRE  ·  SIGN POST")
    y = D.h1(c, D.PH - 34 * MM, "The sign post panel", 7.6)
    D.para(c, D.M, y + 2 * MM,
           "Name only — no service list, no photograph. Trim 1219.2 × 609.6 mm, the "
           "client's 4 ft × 2 ft, double-sided. EDDWALIRO heads the panel in cyan, "
           "the badge and BCM sit under it, MEDICAL CENTRE keeps the widest line in "
           "white, the motto closes the block. Two lockups are supplied; A is the "
           "recommendation.", (D.PW - 2 * D.M) / MM * 0.72, 3.2, B.NAVY_MID)

    img_box(c, "sign/lookbook/M-01-sign-day.png", D.M, 40 * MM, 108 * MM,
            116 * MM)
    B.label(c, D.M, 34 * MM, "ON THE POST — PANEL CENTRE 1500 MM ABOVE GROUND", 2.8,
            B.GREY, "Inter-500", 0.8)

    B.label(c, D.M + 124 * MM, 156 * MM, "WHAT IS SUPPLIED", 4.0, B.TEAL,
            "Inter-600", 1.6)
    sy = D.bullets(c, D.M + 124 * MM, 148 * MM, [
        "artwork/BCM-Sign-Name-Only.pdf — option A, both faces in the one file, 1 : 1 mm.",
        "artwork/BCM-Sign-Name-Only-Option-B.pdf — badge-left lockup, for continuity "
        "with the door panes.",
        "BCM-Sign-Panel.pdf — four pages: the panel to scale, the two options, on the "
        "post, specification.",
        "lookbook/ — day and night elevations and the dimensioned drawing.",
    ], 150 * MM, 3.0, B.NAVY_MID)

    sy -= 6 * MM
    B.label(c, D.M + 124 * MM, sy, "FIXING — CONFIRM ON SITE", 4.0, B.TEAL,
            "Inter-600", 1.6)
    D.bullets(c, D.M + 124 * MM, sy - 8 * MM, [
        "3 mm aluminium composite, matte anti-glare laminate, 3 mm radius, sealed edges.",
        "Two 76 mm galvanised posts at 520 mm centres; panel centre 1500 mm above "
        "finished ground level.",
        "Check 4 ft × 2 ft against the panel the signwriter is actually making "
        "before plotting.",
    ], 150 * MM, 3.0, B.NAVY_MID)


def banner_page(c):
    D.page_bg(c, "BANNERS", f"{REV}", 7,
              eyebrow="BCM  ·  MEDICAL CENTRE  ·  BANNERS")
    y = D.h1(c, D.PH - 34 * MM, "The roadside banners", 7.6)
    D.para(c, D.M, y + 2 * MM,
           "Three lengths on the fence, three different layouts, one identity. Each "
           "carries EDDWALIRO at the head, the badge and BCM, MEDICAL CENTRE as the "
           "widest line, the motto, a service list from the clinic's own board, the two "
           "premises numbers and Open 24 hours.", (D.PW - 2 * D.M) / MM * 0.74, 3.2,
           B.NAVY_MID)

    yy = 152 * MM
    for b in BAN.BANNERS:
        rel = f"banners/lookbook/M-{b['slug']}-day.png"
        img_box(c, rel, D.M, yy - 30 * MM, 104 * MM, 30 * MM)
        tx = D.M + 112 * MM
        B.caps(c, tx, yy - 8 * MM, f"{b['id']} — {b['title']}", 4.4, B.NAVY,
               "Manrope-700", 0.6)
        B.label(c, tx, yy - 13 * MM,
                f"{b['w']:,.0f} × {b['h']:,.0f} mm  ·  {b['w'] / 1000:.1f} m × 1.0 m  ·  "
                f"{b['w'] * b['h'] / 1e6:.2f} m²", 3.0, B.GREY, "Inter-500", 0.8)
        B.label(c, tx, yy - 18.5 * MM, b["job"], 2.9, B.NAVY_MID, "Inter-400", 0.5)
        B.label(c, tx, yy - 24 * MM,
                "Services: " + ", ".join(s.title() for s in b["services"]),
                2.7, B.TEAL, "Inter-500", 0.4)
        yy -= 34 * MM

    B.label(c, D.M, 44 * MM, "PRODUCTION — CONFIRM WITH THE PRINTER", 4.0, B.TEAL,
            "Inter-600", 1.6)
    D.bullets(c, D.M, 36 * MM, [
        "510 g/m² PVC, matte, 40 mm welded hem, eyelets at 500 mm centres; the artwork "
        "keeps 60 mm clear of the trim. Fix every eyelet — a 3.8 m banner sails.",
        "One print file per banner in banners/artwork/, 1 : 1 mm with 10 mm bleed.",
    ], 168 * MM, 3.0, B.NAVY_MID)


def file_grid(c, items, x, y, w, cols=3, row_h=8.0 * MM, cap=2.3):
    """File names in a grid: the whole print list, grouped by supplier."""
    colw = w / cols
    for i, name in enumerate(items):
        cx = x + (i % cols) * colw
        cy = y - (i // cols) * row_h
        B.caps(c, cx, cy, name, cap, B.NAVY_MID, "Inter-500", 0.1,
               max_w=colw - 2 * MM)


def print_page(c, pieces):
    D.page_bg(c, "PRINT FILES", f"{REV}", 8,
              eyebrow="BCM  ·  MEDICAL CENTRE  ·  ONE FILE PER PIECE")
    y = D.h1(c, D.PH - 34 * MM, f"{len(pieces)} pieces, {len(pieces)} print files", 7.6)
    D.para(c, D.M, y + 2 * MM,
           "Every piece is supplied on its own in print/, numbered in the order a job "
           "should be run: one file per pane, one per sign face, one per banner — all "
           "1 : 1 in millimetres with bleed, crop marks and a slug strip.",
           (D.PW - 2 * D.M) / MM * 0.9, 3.2, B.NAVY_MID)

    groups = [("DOOR FILM — 24 PANES", "Door film", 4,
               "One file per pane, pane plus 10 mm bleed, cut to the size in the name."),
              ("SIGN POST — 3 FACES", "Sign post", 3,
               "Option A face A, option A face B, and option B face A — one file per side "
               "of the board."),
              ("BANNERS — 3", "Banner", 3,
               "One file per banner, 60 mm clear of the trim for the hem and the eyelets.")]

    yy = 162 * MM
    for title, kind, cols, note in groups:
        sel = [p for p in pieces if p[5] == kind]
        B.label(c, D.M, yy, title, 3.8, B.TEAL, "Inter-600", 1.6)
        B.label(c, D.M, yy - 5.2 * MM, note, 2.8, B.NAVY_MID, "Inter-400", 0.45)
        rows = (len(sel) + cols - 1) // cols
        file_grid(c, [p[7] for p in sel], D.M, yy - 10.4 * MM, 168 * MM, cols,
                  row_h=5.4 * MM, cap=2.15)
        yy -= 10.4 * MM + rows * 5.4 * MM + 8 * MM

    B.label(c, D.M, yy, "ALSO IN print/", 3.8, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, yy - 6.5 * MM, [
        "PRINT-INDEX.pdf and print-manifest.csv — all 30 jobs with piece, type, "
        "finished size and file name, as a document and as a job sheet.",
        "REPORT.md — the folder explained, grouped by the three suppliers.",
        "BCM-Print-Files.zip — the 30 files and the index on their own, 3 MB.",
    ], 168 * MM, 3.0, B.NAVY_MID)


def licence_page(c):
    D.page_bg(c, "PHOTOGRAPHS", f"{REV}", 8,
              eyebrow="BCM  ·  MEDICAL CENTRE  ·  LICENCE")
    y = D.h1(c, D.PH - 34 * MM, "Every photograph, and its licence", 7.6)
    D.para(c, D.M, y + 2 * MM,
           "All photography is licensed from Pexels under its free licence: commercial "
           "use, modification, no attribution required. Frames marked R were colour-"
           "retouched with AI assistance so the people read Black African, as asked. The "
           "people are models — no pane, sign or banner names them as BCM staff or "
           "patients. Working files are web resolution; repeat the retouch on the "
           "full-resolution originals before any of this is printed large.",
           (D.PW - 2 * D.M) / MM * 0.86, 3.1, B.NAVY_MID)

    where = used_in()
    rows = []
    for key, uses in sorted(where.items(), key=lambda kv: P.PHOTOS[kv[0]]["asset"]):
        m = P.PHOTOS[key]
        rows.append([m["asset"], m["title"][:52], m.get("creator", "—"),
                     str(m["id"]), "R" if m.get("edit") else "—",
                     ", ".join(uses)[:44]])

    D.table(c, D.M, 148 * MM,
            [("Asset", 15, "left"), ("Photograph", 84, "left"), ("Creator", 34, "left"),
             ("Pexels", 17, "left"), ("", 8, "left"), ("Used in", 58, "left")],
            rows, row_h=4.9 * MM, head_h=6.0 * MM, cap=2.6, head_cap=2.5)

    B.caps(c, D.M, 26 * MM,
           "PEXELS FREE LICENCE — COMMERCIAL USE, MODIFICATION AND NO ATTRIBUTION "
           "REQUIRED; NOT FOR RESALE UNALTERED, NOT FOR IMPLYING ENDORSEMENT. CHECKED "
           "29 OCTOBER 2026. THE B MONOGRAM IS A RECREATION, NOT BCM'S OFFICIAL LOGO.",
           2.5, B.GREY, "Inter-500", 0.4)


def handover_page(c):
    D.page_bg(c, "HANDOVER", f"{REV}", 9,
              eyebrow="BCM  ·  MEDICAL CENTRE  ·  HANDOVER")
    y = D.h1(c, D.PH - 34 * MM, "Who gets what", 7.6)
    D.para(c, D.M, y + 2 * MM,
           "Three suppliers, three different jobs. Send each the folder named, nothing "
           "else — the film printer has no use for the banner files, and the signwriter "
           "should not be scaling anything.", (D.PW - 2 * D.M) / MM * 0.7, 3.2,
           B.NAVY_MID)

    rows = [
        ["One-way vision printer", "door-1/ door-2/ door-3/",
         "24 pane PDFs + 3 panel proofs", "Perforated film, 2.3 mm pitch; D2 must stay "
         "see-through, D3 is opaque"],
        ["Signwriter", "sign/",
         "Sign panel A (or B) + 4-page proof", "ACM 3 mm, two posts, panel centre 1500 mm"],
        ["Banner printer", "banners/",
         "3 banner PDFs + 6-page proof", "PVC 510 g, welded hem, eyelets at 500 mm"],
    ]
    yy = D.table(c, D.M, 128 * MM,
                 [("Supplier", 46, "left"), ("Send", 46, "left"), ("Files", 74, "left"),
                  ("What to say", 90, "left")],
                 rows, row_h=9.0 * MM, head_h=6.6 * MM, cap=2.9, head_cap=2.7)

    yy -= 12 * MM
    B.label(c, D.M, yy, "OPEN ITEMS — ANSWER THESE BEFORE ANYTHING IS PLOTTED",
            4.0, B.TEAL, "Inter-600", 1.6)
    yy = D.bullets(c, D.M, yy - 8 * MM, [
        "The official BCM logo vector. The B monogram here is a recreation in the "
        "client's colours; swapping it is one line in source/bcm_brand.py.",
        "Spelling of EDDWALIRO — set as supplied, worth confirming before plate-making.",
        "Whether the sign post and the door fascia carry the motto and the telephone; "
        "both are present and can be dropped or added in minutes.",
        "Sign post size, checked against the panel the signwriter is actually making.",
        "Photographs: the working files are 843–1264 px. Approve the look, then either "
        "repeat the retouch on the Pexels originals or photograph the clinic's own team.",
        "Measurement check on each doorway before the film is cut: 900 mm high panes, "
        "500 mm outer, 400 mm against the meeting stile.",
    ], 168 * MM, 3.0, B.NAVY_MID)

    yy -= 10 * MM
    B.label(c, D.M, yy, "REBUILD EVERYTHING", 4.0, B.TEAL, "Inter-600", 1.6)
    B.caps(c, D.M, yy - 6 * MM,
           "cd source  ·  python3 bcm_doors.py  ·  python3 bcm_sign.py  ·  "
           "python3 bcm_banners.py  ·  python3 bcm_master.py",
           3.4, B.NAVY, "Inter-500", 0.5)


def print_pieces():
    """The single-piece print jobs — computed from the same source as bcm_print,
    without touching the print folder."""
    import bcm_print as PR
    return PR.pieces_list()


def master_pdf(path):
    pieces = print_pieces()
    c = D.new_doc(path, "BCM Medical Centre — complete signage set",
                  subject="Doors, sign post and banners")
    cover(c)
    c.showPage()
    contents(c)
    for i, door in enumerate(DOORS.DOORS):
        c.showPage()
        door_page(c, door, 3 + i)
    c.showPage()
    sign_page(c)
    c.showPage()
    banner_page(c)
    c.showPage()
    print_page(c, pieces)
    c.showPage()
    licence_page(c)
    c.showPage()
    handover_page(c)
    c.save()
    return path


# ---------------------------------------------------------------- text files
def readme_text():
    panes, photos = counts()
    return f"""# BCM Medical Centre — the complete signage set

Everything in one folder: the three door film packages, the sign post panel and the
three roadside banners, with one master proof describing the lot.

**{panes} door panes · 1 sign post panel (2 faces) · 3 banners · {photos} licensed photographs**

## What is where

| Folder | What it holds |
| --- | --- |
| `door-1/` `door-2/` `door-3/` | Eight panes each. Print files at 1 : 1 (900 × 500 and 900 × 400 mm), a panel proof, a schedule, a specification, day and night elevations, a licence record, a web preview |
| `sign/` | Name-only sign post panel, 1219.2 × 609.6 mm (4 ft × 2 ft), two lockups, four-page proof, elevations, dimensioned drawing |
| `banners/` | Three PVC banners — 3.8 m, 3.4 m, 2.4 m × 1.0 m — print files, six-page proof, fence elevations, licence page |
| `print/` | **One print PDF per piece** — 32 panes, 3 sign faces, 3 banners, numbered 01–38, with `PRINT-INDEX.pdf`, a manifest, `BCM-Print-Files-ALL.pdf` and `BCM-Print-Files.zip` |
| `complete/` | This README, the master proof, the manifest and the web index |

At the top of the folder: `BCM-Complete-Set.pdf` (master proof, nine pages),
`README.md`, `MANIFEST.csv`, `index.html`.

The per-group zips are deliberately left out — they hold the same files. Each group's own
page still offers one if you want to hand a single door to a single supplier.

## The identity, in one place

- Navy `#16233F`, cyan `#2BA9E0`, mist `#E8EEF4`.
- **EDDWALIRO** — Luganda for hospital — at the head of the sign post and every banner,
  bold, cyan, same cap height as the English name.
- Then the badge and `BCM` (small, cyan), then **MEDICAL CENTRE** as the widest line in
  white — the line people point at — then the motto *We listen. We treat. We care.*
- Door panes use the white plate: badge top-left over the photograph, MEDICAL CENTRE
  spanning the plate, service name in the navy caption band at the foot.
- The B monogram is a **recreation**, not BCM's official logo.

## Who gets what

| Supplier | Send | Files |
| --- | --- | --- |
| One-way vision printer | `print/` jobs 01–24 | one PDF per pane, pane + 10 mm bleed |
| Signwriter | `print/` jobs 25–27 | one PDF per sign face (A face A, A face B, B face A) |
| Banner printer | `print/` jobs 28–30 | one PDF per banner, 60 mm hem-safe |

The same files also sit inside each group folder (`door-1/artwork/`, `sign/artwork/`,
`banners/artwork/`) with the group's proof and paperwork; `print/` is just the print
files on their own, numbered in running order.

## Before anything is plotted

1. The official logo vector. The monogram is a recreation.
2. Confirmation of the spelling **EDDWALIRO**.
3. The sign post measurement, checked against the panel being made.
4. The photographs: working files are 843–1264 px — approve the look, then repeat the
   retouch on the Pexels originals, or photograph the clinic's own team.
5. Each doorway measured on site: 900 mm high panes, 500 mm outer, 400 mm at the stile.

## Rebuild

```sh
cd source
python3 bcm_doors.py      # all doors
python3 bcm_sign.py       # sign post panel
python3 bcm_banners.py    # three banners
python3 bcm_master.py     # this set: master proof, manifest, README, zip
```

Preview locally: `python3 -m http.server 8000 --directory bcm` and open
`http://localhost:8000/`.
"""


def entries():
    """(path inside the zip, path on disk) for everything that ships.

    The dev README at the set root and the per-group zips stay behind; the master
    README, index, manifest and proof are lifted to the top of the zip so the folder
    opens on the paperwork rather than on a list of folders.
    """
    skip = {"README.md"}                       # the build readme, not a deliverable
    lift = {"complete/README.md": "README.md",
            "complete/BCM-Complete-Set.pdf": "BCM-Complete-Set.pdf",
            "complete/MANIFEST.csv": "MANIFEST.csv",
            "index.html": "index.html"}
    out = []
    for base, dirs, files in os.walk(SET):
        dirs.sort()
        for f in sorted(files):
            if f.endswith(".zip"):
                continue
            full = os.path.join(base, f)
            rel = os.path.relpath(full, SET).replace(os.sep, "/")
            if rel in skip:
                continue
            dest = lift.get(rel, rel)
            out.append((os.path.join(SET_NAME, dest), full, dest))
    out.sort(key=lambda t: (t[0].count("/"), t[0]))
    return out


def manifest_rows(ents):
    rows = []
    for _arc, full, dest in ents:
        rows.append([dest, os.path.splitext(full)[1].lstrip(".") or "—",
                     f"{os.path.getsize(full) / 1024:.0f}"])
    return rows


def write_manifest(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "type", "kb"])
        w.writerows(rows)
    return path


def index_html():
    panes, photos = counts()
    cards = []
    for g in GROUPS:
        cards.append(f"""
    <a class="card" href="../{g['key']}/index.html">
      <img src="../{g['cover']}" alt="{g['title']}">
      <div class="txt"><b>{g['n']} · {g['title']}</b><span>{g['kind']}</span></div></a>""")

    links = []
    for g in GROUPS:
        zips = {
            "door-1": "door-1/BCM-Door-1-package.zip",
            "door-2": "door-2/BCM-Door-2-package.zip",
            "door-3": "door-3/BCM-Door-3-package.zip",
            "door-4": "door-4/BCM-Door-4-package.zip",
            "sign": "sign/BCM-Sign-Package.zip",
            "banners": "banners/BCM-Banners-Package.zip",
        }
        links.append(f"<tr><td><a href=\"../{zips[g['key']]}\">{g['title']} (zip)</a></td>"
                     f"<td>{g['kind']}</td></tr>")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BCM Medical Centre — complete signage set</title>
<style>
 body{{margin:0;background:#f4f7f9;color:#16233f;
   font:16px/1.6 Inter,Helvetica,Arial,sans-serif}}
 header{{background:#16233f;color:#fff;padding:52px 6vw 44px}}
 h1{{font-size:clamp(30px,5vw,52px);margin:.15em 0 .3em;line-height:1.02}}
 header p{{max-width:64ch;color:#cfd9e6;margin:0}}
 .eyebrow{{letter-spacing:.3em;font-size:11px;color:#2ba9e0}}
 .facts{{display:flex;gap:28px;flex-wrap:wrap;margin-top:26px;font-size:13px;
   color:#cfd9e6}} .facts b{{display:block;font:800 24px/1.1 Manrope,system-ui,sans-serif;
   color:#fff}}
 main{{padding:36px 6vw 80px}}
 h2{{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:#8fa2b8;
   margin:0 0 16px}}
 .cards{{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
   margin-bottom:44px}}
 a.card{{display:block;background:#fff;border-radius:8px;overflow:hidden;
   text-decoration:none;color:inherit;box-shadow:0 2px 16px rgba(22,35,63,.09)}}
 a.card img{{width:100%;display:block;aspect-ratio:4/3;object-fit:cover;background:#e8eef4}}
 a.card .txt{{padding:13px 15px 17px}}
 a.card b{{display:block;font:800 17px/1.25 Manrope,system-ui,sans-serif}}
 a.card span{{display:block;font-size:12.5px;color:#4b5b73;margin-top:3px}}
 table{{width:100%;border-collapse:collapse;font-size:14px;background:#fff;
   border-radius:8px;overflow:hidden}}
 th,td{{text-align:left;padding:11px 16px;border-bottom:1px solid #e6edf4}}
 th{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#8fa2b8}}
 td a{{color:#1b87b8}}
 .note{{color:#4b5b73;font-size:13px;max-width:82ch;margin-top:24px}}
</style></head><body>
<header>
  <div class="eyebrow">BCM · MEDICAL CENTRE · COMPLETE SET</div>
  <h1>Eddwaliro. Medical Centre.</h1>
  <p>Everything in one folder: three glazed doorways in film, a name-only sign post
     panel, and three roadside banners. Print-ready artwork, proofs, elevations and
     schedules — all measured to the clinic's own premises.</p>
  <div class="facts">
    <div><b>{panes}</b>door panes</div>
    <div><b>2</b>sign post faces</div>
    <div><b>3</b>banners</div>
    <div><b>{photos}</b>licensed photographs</div>
  </div>
</header>
<main>
  <h2>The set</h2>
  <div class="cards">{"".join(cards)}</div>

  <h2>Master documents</h2>
  <table>
    <tr><th>File</th><th>What it is</th></tr>
    <tr><td><a href="BCM-Complete-Set.pdf">BCM-Complete-Set.pdf</a></td>
        <td>Nine pages — contents, pane schedules, sign post, banners, licence table,
            handover</td></tr>
    <tr><td><a href="README.md">README.md</a></td><td>The set in text, with rebuild commands</td></tr>
    <tr><td><a href="MANIFEST.csv">MANIFEST.csv</a></td><td>Every file, its type and size</td></tr>
    {"".join(links)}
  </table>
  <p class="note">Group packages are also available on their own pages, if you want to
     send one door to one supplier. Photographs are Pexels Free licence, recorded in the
     master proof and in each group README; the B monogram is a recreation, not BCM's
     official logo. Printer, film and fixing values marked “confirm” are industry-typical,
     not quotations.</p>
</main></body></html>
"""


# ------------------------------------------------------------------------ main
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    pdf = master_pdf(os.path.join(OUT_DIR, "BCM-Complete-Set.pdf"))
    print("master proof:", os.path.basename(pdf))

    open(os.path.join(OUT_DIR, "README.md"), "w").write(readme_text())
    open(os.path.join(OUT_DIR, "index.html"), "w").write(index_html())
    print("README, index")

    ents = entries()
    rows = manifest_rows(ents)
    write_manifest(os.path.join(OUT_DIR, "MANIFEST.csv"), rows)
    print("manifest:", len(rows), "files")

    if os.path.exists(ZIP):
        os.remove(ZIP)
    seen = set()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for arc, full, _dest in ents:
            if arc in seen:
                continue
            seen.add(arc)
            z.write(full, arc)
    print("zip:", os.path.basename(ZIP), f"{os.path.getsize(ZIP) / 1e6:.1f} MB",
          len(seen), "files")


if __name__ == "__main__":
    main()
