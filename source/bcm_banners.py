"""BCM Medical Centre — three banner designs for the roadside fence.

Three different banners, three different jobs, one identity:

    B-1  4876.8 × 1244.6 mm  the road banner (16 ft × 49 in) — photo left, the name right
    B-2  4876.8 × 1244.6 mm  the services banner — type left, two photos right
    B-3  4876.8 × 1244.6 mm  the long banner — the name centred, one photograph right

All three are cut to the client's measurement of 2026-11-07 — 16 ft long × 49 in high,
4876.8 × 1244.6 mm — and each layout is drawn from the panel size, not from fixed
offsets, so the three read as one set and hold if the size is changed again.

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
import bcm_sign as SGN
import cp_docutil as D
import cp_photos as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "bcm", "banners")
ART_DIR = os.path.join(OUT_DIR, "artwork")
WORK = os.path.join(ROOT, "source", ".work", "bcm_banners")

BLEED, SLUG = 10.0, 20.0
SAFE = 60.0                    # hem + eyelet zone: nothing important goes here
REV = "Rev B  ·  2026-11-07"
NAME = "MEDICAL CENTRE"
WORD = "EDDWALIRO"
# the client's number, the same string the sign post face carries
PHONE = SGN.SIGN_TEL

# The banners keep the layout they were approved with. What changes here is only the
# colour, taken from the sign post the client already has on the road: white ground,
# the navy band (#16233F) with white type, the red block (#ED1B24) with white type,
# and that red again for the small accents. Nothing is moved, nothing is re-sized.
RED = SGN.LIT_RED
NAVY = B.CP_NAVY
GROUND = B.WHITE
BAND_HM = 1.19          # the sign post's own ratio: its band is 1.19 x the cap it carries
BAND_PAD = (BAND_HM - 1.0) / 2.0

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
        # the client's measurement, 2026-11-07: every banner 16 ft long x 49 in high
        "id": "B-1", "slug": "B-01",
        "w": 16 * 304.8, "h": 49 * 25.4,          # 4876.8 x 1244.6 mm
        "title": "The road banner", "sub": "16 ft × 49 in  (4.88 m × 1.24 m)",
        "job": "Read at speed, from the road. Photograph on the left, the name on the right.",
        "services": ["GENERAL OUTPATIENT", "LABORATORY", "PHARMACY",
                     "ULTRASOUND", "MINOR SURGERY", "HIV CARE"],
        "photos": [("pharmacy", 0.0, 0.0, 0.0, 0.0, (0.52, 0.42))],   # placed by the layout
        "layout": "road",
    },
    {
        "id": "B-2", "slug": "B-02",
        "w": 16 * 304.8, "h": 49 * 25.4,          # 4876.8 x 1244.6 mm
        "title": "The services banner", "sub": "16 ft × 49 in  (4.88 m × 1.24 m)",
        "job": "Read standing still, at the gate. The list does the work, two photographs carry it.",
        "services": ["PAEDIATRICS", "IMMUNISATION", "ANTENATAL & POSTNATAL",
                     "OBS & GYN", "FAMILY PLANNING", "EYE SERVICES"],
        "photos": [("lab", 0.0, 0.0, 0.0, 0.0, (0.50, 0.06)),          # placed by the layout
                   ("pharmacy_shelf", 0.0, 0.0, 0.0, 0.0, (0.62, 0.10))],
        "layout": "services",
    },
    {
        # the client's measurement, 2026-11-07: 16 ft long x 49 in high
        "id": "B-3", "slug": "B-03",
        "w": 16 * 304.8, "h": 49 * 25.4,          # 4876.8 x 1244.6 mm
        "title": "The long banner", "sub": "16 ft × 49 in  (4.88 m × 1.24 m)",
        "job": "The long run along the fence: the name set as large as it will go, one "
               "photograph at the right hand end, one line of services.",
        "services": ["INPATIENT CARE", "ENT", "ORTHOPAEDICS", "TRAVEL MEDICAL EXAM"],
        "photos": [("reception", 0.0, 0.0, 0.0, 0.0, (0.50, 0.55))],   # placed by the layout
        "layout": "compact",
    },
]

def _apply_photo_rects():
    """Give every banner its real photograph rectangles, from the panel size."""
    x, y, pw, ph = road_photo(BANNERS[0]["w"], BANNERS[0]["h"])
    BANNERS[0]["photos"] = [("pharmacy", x, y, pw, ph, (0.52, 0.42))]
    rects = []
    for (key, *_old), (rect, focus) in zip(BANNERS[1]["photos"],
                                           services_photos(BANNERS[1]["w"],
                                                           BANNERS[1]["h"])):
        rects.append((key, *rect, focus))
    BANNERS[1]["photos"] = rects
    x, y, pw, ph = compact_photo(BANNERS[2]["w"], BANNERS[2]["h"])
    BANNERS[2]["photos"] = [("reception", x, y, pw, ph, (0.50, 0.55))]


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
    return B.caps(c, x, y, WORD, cap, color or B.WHITE, "Manrope-800", track,
                  align=align, max_w=max_w)


def band(c, x, y, w, h, colour):
    """A solid band behind a line of type. y is the bottom edge."""
    c.setFillColor(colour)
    c.rect(x, y, w, h, stroke=0, fill=1)


def band_base(top, cap):
    """Baseline for a cap sitting in a band whose top edge is `top`."""
    return top - cap * BAND_PAD - cap


def bcm_line(c, x, w, y, cap, colour=None):
    """BCM alone, centred across the measure — no badge, as the client asked."""
    B.caps(c, x + w / 2.0, y, "BCM", cap, colour or NAVY, "Inter-600", cap * 0.22,
           align="center", max_w=w * 0.96)


def services_centre(c, items, xc, y, cols=3, av=3000.0, row=62.0, cap=32.0,
                    color=None, k=1.0, dash=None):
    """The service list centred: each row of `cols` set as one centred group.

    Same type and same rules as before, only the rows are centred instead of sitting on
    a left-hand grid, so the whole stack above them reads down one axis. If a row would
    not fit the measure, the type comes down a step rather than the gap closing up.
    """
    color = color or NAVY
    dash = dash or RED

    def measure(cap):
        d = 34.0 * (cap / 32.0)
        tw = {s: pdfmetrics.stringWidth(s, "Inter-600", B.font_for(cap, "Inter")) + 3.0
              for s in items}
        rows = [items[i:i + cols] for i in range(0, len(items), cols)]
        gap = cap * 2.4
        widest = max(sum(d * 1.6 + tw[s] for s in r) + gap * (len(r) - 1) for r in rows)
        return d, tw, rows, gap, widest

    d, tw, rows, gap, widest = measure(cap)
    for _ in range(6):
        if widest <= av:
            break
        cap *= av / widest * 0.98
        d, tw, rows, gap, widest = measure(cap)
    for j, r in enumerate(rows):
        cy = y - j * row
        total = sum(d * 1.6 + tw[s] for s in r) + gap * (len(r) - 1)
        cx = xc - total / 2.0
        for s in r:
            c.setFillColor(dash)
            c.rect(cx, cy + cap * 0.30, d, max(3.0, 4.0 * k), stroke=0, fill=1)
            B.caps(c, cx + d * 1.6, cy, s, cap, color, "Inter-600", 3.0)
            cx += d * 1.6 + tw[s] + gap


def services_block(c, items, x, y, cols=2, col_w=1120.0, row=62.0, cap=32.0,
                   color=None, k=1.0, dash=None):
    """Service list: a red rule then the name. `k` scales the rule."""
    color = color or NAVY
    dash = dash or NAVY
    d = 34.0 * k
    for i, s in enumerate(items):
        cx = x + (i % cols) * col_w
        # y is the first row's BASELINE and `row` is the pitch, so the ink starts at the
        # block's top edge and ends on its bottom edge — never into the gap below it
        cy = y - (i // cols) * row
        c.setFillColor(dash)
        c.rect(cx, cy + cap * 0.30, d * (cap / 32.0), max(3.0, 4.0 * k), stroke=0, fill=1)
        B.caps(c, cx + d * (cap / 32.0) * 1.6, cy, s, cap, color, "Inter-600", 3.0,
               max_w=col_w * 0.92)


def phone_line(c, x, y, cap=30.0, align="left", color=None):
    B.caps(c, x, y, f"TEL {PHONE}", cap, color or NAVY, "Inter-600", 3.0,
           align=align)


# ----------------------------------------------------------------------- faces
def layout_stack(h, m, elems, share=0.94):
    """Lay a column of type out on a banner face, top edge first.

    `elems` is the stack in order: `("block", name, coeff, fit)` — or
    `("block", name, coeff, fit, hm)` where the block is a coloured band `hm` times the
    cap it carries — and `("gap", coeff)`. Heights are multiples of one unit U, so the
    column is in proportion; U is chosen so blocks and gaps together take `share` of the
    clear height. Where a block is width-limited it comes out smaller than its share and
    the slack is handed back to the gaps, so nothing overlaps whatever the size.

    Returns (caps, tops, total).
    """
    def blk(e):
        return (e[1], e[2], e[3], e[4] if len(e) > 4 else 1.0)

    coeffs = sum(e[2] if e[0] == "block" else e[1] for e in elems)
    U = (h - 2 * m) * share / coeffs
    caps, heights, order = {}, {}, []
    for e in elems:
        if e[0] != "block":
            continue
        name, coeff, fit, hm = blk(e)
        cap = coeff * U / hm
        if fit is not None:
            cap = min(cap, fit())
        caps[name] = cap
        heights[name] = cap * hm
        order.append(e)
    fixed = sum(heights.values())
    gap_coeffs = sum(e[1] for e in elems if e[0] == "gap") or 1.0
    gap_total = max((h - 2 * m) * share - fixed, 0.0)
    tops = {}
    y = m + (h - 2 * m) / 2 + (fixed + gap_total) / 2
    for e in elems:
        if e[0] == "block":
            name = e[1]
            y -= heights[name]
            tops[name] = y
        else:
            y -= e[1] / gap_coeffs * gap_total
    return caps, tops, fixed + gap_total


def band_h(caps, name):
    """The height of a band around the cap of block `name`."""
    return caps[name] * BAND_HM


def road_photo(w, h):
    """B-1's photograph: a tall crop against the left edge, full clear height."""
    m = SAFE
    ph = h - 2 * m
    pw = min(ph * 0.80, w * 0.235)
    return (m, m, pw, ph)


def face_road(c, w, h):
    """B-1 — 16 ft x 49 in. Photograph left, the name right, the list under it.

    The design is untouched; it is only coloured the way the sign post is: white
    ground, EDDWALIRO white on the red block, MEDICAL CENTRE white on the navy band.
    """
    c.setFillColor(GROUND)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    m = SAFE
    k = h / 1244.6
    px, py, pw, ph = road_photo(w, h)
    photo(c, "pharmacy", px, py, pw, ph, (0.52, 0.42))
    keyline(c, px, py, pw, ph, NAVY, 0.22, max(1.8, h * 0.0022))

    gap = w * 0.030
    x0 = px + pw + gap
    col = w - m - x0

    # the stack: EDDWALIRO, BCM, MEDICAL CENTRE, the motto, the list, the numbers
    elems = [
        ("block", "word", 0.300, lambda: fit_cap(WORD, "Manrope-800", "Manrope",
                                                 col * 0.96, tracking=9.0), BAND_HM),
        ("gap", 0.040),
        ("block", "bcm", 0.165, None),
        ("gap", 0.026),
        ("block", "name", 0.205, lambda: fit_cap(NAME, "Manrope-800", "Manrope",
                                                 col * 0.96), BAND_HM),
        ("gap", 0.034),
        ("block", "motto", 0.030, None),
        ("gap", 0.030),
        ("block", "services", 0.128, None),        # two rows of three
        ("gap", 0.030),
        ("block", "tel", 0.034, None),
        ("gap", 0.014),
        ("block", "open", 0.029, None),
    ]
    caps, tops, total = layout_stack(h, m, elems)
    cap_sc = caps["services"] * 0.30
    row_sc = caps["services"] - cap_sc           # two rows fill the block exactly

    band(c, x0, tops["word"], col, band_h(caps, "word"), RED)
    word(c, x0 + col / 2.0, tops["word"] + caps["word"] * BAND_PAD, caps["word"],
         track=9.0, align="center", max_w=col - 28.0 * k)
    bcm_line(c, x0, col, tops["bcm"], caps["bcm"])
    band(c, x0, tops["name"], col, band_h(caps, "name"), NAVY)
    B.caps(c, x0 + col / 2.0, tops["name"] + caps["name"] * BAND_PAD, NAME,
           caps["name"], B.WHITE, "Manrope-800", 2.0, align="center",
           max_w=col - 28.0 * k)
    B.label(c, x0 + col / 2.0, tops["motto"], B.SLOGAN, caps["motto"], RED,
            "Inter-400", 4.0, align="center", max_w=col)
    # the stack reserves the block's TOP; the list draws down from its first baseline
    services_centre(c, BANNERS[0]["services"], x0 + col / 2.0,
                    tops["services"] + caps["services"] - cap_sc, cols=3,
                    av=col * 0.92, row=row_sc, cap=cap_sc, k=k)
    phone_line(c, x0 + col / 2.0, tops["tel"], caps["tel"], align="center")
    B.caps(c, x0 + col / 2.0, tops["open"], "OPEN 24 HOURS", caps["open"], RED,
           "Inter-600", 3.0, align="center")

    keyline(c, 32, 32, w - 64, h - 64, NAVY, 0.12, 2.0)


def services_photos(w, h):
    """B-2's two photographs, stacked against the right edge; ((x,y,w,h), focus)."""
    m = SAFE
    gap = h * 0.034
    ph = (h - 2 * m - gap) / 2
    pw = min(h * 0.86, w * 0.225)
    px = w - m - pw
    return [((px, h - m - ph, pw, ph), (0.50, 0.06)),          # top
            ((px, m, pw, ph), (0.62, 0.10))]                    # bottom


def face_services(c, w, h):
    """B-2 — 16 ft x 49 in. Type left, two photographs stacked right, a red foot rail."""
    c.setFillColor(GROUND)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    m = SAFE
    k = h / 1244.6
    rects = services_photos(w, h)
    for (rect, focus), (key, *_rest) in zip(rects, BANNERS[1]["photos"]):
        photo(c, key, *rect, focus)
        keyline(c, *rect, NAVY, 0.20, max(1.6, h * 0.0018))

    x0 = m
    col = rects[0][0][0] - w * 0.030 - x0

    elems = [
        ("block", "word", 0.300, lambda: fit_cap(WORD, "Manrope-800", "Manrope",
                                                 col * 0.96, tracking=8.0), BAND_HM),
        ("gap", 0.040),
        ("block", "bcm", 0.165, None),
        ("gap", 0.026),
        ("block", "name", 0.205, lambda: fit_cap(NAME, "Manrope-800", "Manrope",
                                                 col * 0.96), BAND_HM),
        ("gap", 0.032),
        ("block", "motto", 0.030, None),
        ("gap", 0.028),
        ("block", "services", 0.128, None),
        ("gap", 0.026),
        ("block", "rail", 0.006, None),
        ("gap", 0.024),
        ("block", "tel", 0.034, None),
        ("gap", 0.014),
        ("block", "open", 0.029, None),
    ]
    caps, tops, total = layout_stack(h, m, elems)
    cap_sc = caps["services"] * 0.30
    row_sc = caps["services"] - cap_sc

    band(c, x0, tops["word"], col, band_h(caps, "word"), RED)
    word(c, x0 + col / 2.0, tops["word"] + caps["word"] * BAND_PAD, caps["word"],
         track=8.0, align="center", max_w=col - 28.0 * k)
    bcm_line(c, x0, col, tops["bcm"], caps["bcm"])
    band(c, x0, tops["name"], col, band_h(caps, "name"), NAVY)
    B.caps(c, x0 + col / 2.0, tops["name"] + caps["name"] * BAND_PAD, NAME,
           caps["name"], B.WHITE, "Manrope-800", 1.8, align="center",
           max_w=col - 28.0 * k)
    B.label(c, x0 + col / 2.0, tops["motto"], B.SLOGAN, caps["motto"], RED,
            "Inter-400", 3.6, align="center", max_w=col)
    services_centre(c, BANNERS[1]["services"], x0 + col / 2.0,
                    tops["services"] + caps["services"] - cap_sc, cols=3,
                    av=col * 0.92, row=row_sc, cap=cap_sc, k=k)
    c.setFillColor(RED)
    c.rect(x0, tops["rail"], col, max(3.0, caps["rail"]), stroke=0, fill=1)
    phone_line(c, x0 + col / 2.0, tops["tel"], caps["tel"], align="center")
    B.caps(c, x0 + col / 2.0, tops["open"], "OPEN 24 HOURS", caps["open"], RED,
           "Inter-600", 3.0, align="center")

    keyline(c, 32, 32, w - 64, h - 64, NAVY, 0.12, 2.0)


def compact_photo(w, h):
    """Where B-3's photograph sits, as (x, y, w, h) — shared by the face and the proof."""
    m = SAFE
    ph = h - 2 * m
    pw = min(ph * 0.80, w * 0.255)
    return (w - m - pw, m, pw, ph)


def face_compact(c, w, h):
    """B-3 — 16 ft x 49 in. The name centred in its column, one photograph at the right.

    Same design as approved; only the colour is the sign post's — white ground,
    EDDWALIRO white on the red block, MEDICAL CENTRE white on the navy band.
    """
    c.setFillColor(GROUND)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    m = SAFE                                        # hem + eyelet zone
    px, py, pw, ph = compact_photo(w, h)
    photo(c, "reception", px, py, pw, ph, (0.50, 0.55))
    keyline(c, px, py, pw, ph, NAVY, 0.22, max(1.8, h * 0.0022))

    x0 = m
    col = px - x0 - w * 0.035                       # the type column, up to the photograph
    xc = x0 + col / 2.0

    # type: fitted to the column first, then capped against the height
    cap_e = min(fit_cap(WORD, "Manrope-800", "Manrope", col * 0.94, tracking=10.0),
                h * 0.280)
    cap_m = min(fit_cap(NAME, "Manrope-800", "Manrope", col * 0.94), h * 0.220)
    cap_rule = max(5.0, h * 0.006)
    cap_s = h * 0.024
    cap_r = h * 0.021
    cap_p = h * 0.027
    cap_o = h * 0.023
    clear = h - 2 * m

    # BCM is set large, but it must not squeeze the lines
    # under the name: back the two big lines off until the small type keeps its air
    for sc in (1.0, 0.97, 0.94, 0.91, 0.88, 0.85, 0.82, 0.79, 0.76, 0.73, 0.70,
               0.67, 0.64, 0.61, 0.58, 0.55):
        ce, cm = cap_e * sc, cap_m * sc
        cb = min(cm * 0.58, 240.0)
        msz = 0.0
        he, hm = ce * BAND_HM, cm * BAND_HM
        fixed = (he + msz + cb + hm + cap_rule + cap_s + cap_r + cap_p + cap_o)
        room = clear * 0.96 - fixed
        if room >= clear * 0.22:
            break
    cap_e, cap_m, cap_b, ms = ce, cm, cb, msz
    h_e, h_m = he, hm
    room = max(room, 0.0)
    wts = (0.055, 0.030, 0.055, 0.075, 0.050, 0.060, 0.075, 0.030)
    total_gap = sum(wts)
    g = [room * x / total_gap for x in wts]
    total = fixed + room
    top = m + (h - 2 * m) / 2 + total / 2           # the stack, centred in the clear area

    # the bands hug their line here, because this banner is a centred lockup: a
    # full-measure bar would sit proud of the type on both sides
    def _tw(txt, cap, track):
        return (pdfmetrics.stringWidth(txt, "Manrope-800", B.font_for(cap, "Manrope"))
                + track * (len(txt) - 1))

    bw_e = min(col, _tw(WORD, cap_e, 10.0) + 2 * cap_e * 0.14)
    bw_m = min(col, _tw(NAME, cap_m, 1.8) + 2 * cap_m * 0.14)

    y = top
    # EDDWALIRO heads it, white on the red block
    band(c, xc - bw_e / 2.0, y - h_e, bw_e, h_e, RED)
    B.caps(c, xc, band_base(y, cap_e), WORD, cap_e, B.WHITE, "Manrope-800", 10.0,
           align="center", max_w=col - 20.0)
    y -= h_e + g[0]

    # the initials, alone and centred
    y -= g[1]
    B.caps(c, xc, y - cap_b, "BCM", cap_b, NAVY, "Inter-600", cap_b * 0.22,
           align="center", max_w=col * 0.96)
    y -= cap_b + g[2]

    # the English name, the widest line on the banner, white on the navy band
    band(c, xc - bw_m / 2.0, y - h_m, bw_m, h_m, NAVY)
    B.caps(c, xc, band_base(y, cap_m), NAME, cap_m, B.WHITE, "Manrope-800", 1.8,
           align="center", max_w=col - 24.0)
    y -= h_m + g[3]

    # a short rule, then the motto
    rw = min(col * 0.16, 300.0)
    c.setFillColor(RED)
    c.rect(xc - rw / 2, y - cap_rule, rw, cap_rule, stroke=0, fill=1)
    y -= cap_rule + g[4]
    B.label(c, xc, y - cap_s, B.SLOGAN, cap_s, RED, "Inter-400", 3.4,
            align="center", max_w=col)
    y -= cap_s + g[5]

    # the rail of services, then the numbers and the hours
    rail = "   ·   ".join(BANNERS[2]["services"])
    B.caps(c, xc, y - cap_r, rail, cap_r, NAVY, "Inter-500", 1.6,
           align="center", max_w=col)
    y -= cap_r + g[6]
    phone_line(c, xc, y - cap_p, cap_p, align="center")
    y -= cap_p + g[7]
    B.caps(c, xc, y - cap_o, "OPEN 24 HOURS", cap_o, RED, "Inter-600", 4.0,
           align="center")

    keyline(c, 32, 32, w - 64, h - 64, NAVY, 0.12, 2.0)


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
    # one frame for all three, so they compare — sized for the longest banner (B-3 at
    # 16 ft) with air either side and above it
    width_mm = max(4200.0, max(x["w"] for x in BANNERS) + 1500.0)
    above = max(FENCE_TOP + SKY,
                LIFT + max(x["h"] for x in BANNERS) + 300.0)
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
           "at speed, B-2 is read standing at the gate, B-3 runs the long stretch of fence. "
           "The layouts are the ones approved, unchanged. What changed on 2026-11-07 is the "
           "colour, taken from the clinic's sign post: white ground, EDDWALIRO in white on "
           "the red block #ED1B24, MEDICAL CENTRE in white on the navy band #16233F, and "
           "that red again for the motto, the service rules and OPEN 24 HOURS.",
           (D.PW - 2 * D.M) / MM * 0.72, 3.2, B.NAVY_MID)

    yy = 126 * MM
    for b in BANNERS:
        png = os.path.join(WORK, f"{b['slug']}_mock.png")
        iw, ih = Image.open(png).size
        # the three mockups share one frame and one scale, so the banners inside them
        # read against each other: drawn at the same width or not at all
        bw = 72 * MM
        bh = bw * ih / iw
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
        rects = ([(k, *compact_photo(b["w"], b["h"])[0:1], *compact_photo(b["w"], b["h"])[1:])
                  for k, *_ in b["photos"]] if b["layout"] == "compact"
                 else [(k, x, y2, ww, hh) for k, x, y2, ww, hh, _f in b["photos"]])
        for key, _x, _y, ww, hh in rects:
            d, st = P.ppi(key, ww, hh)
            rows.append(f"{P.PHOTOS[key]['asset']} — {P.PHOTOS[key]['title']}, "
                        f"{ww:.0f} × {hh:.0f} mm at {d} ppi ({st}).")

        left = [f"Service list: {', '.join(x.lower() for x in b['services'])}.",
                f"Hem and eyelet zone: {SAFE:.0f} mm clear all round — no type, no faces.",
                f"Bleed {BLEED:.0f} mm, crop marks in the slug. Plot at 100 %, never scale."]
        B.label(c, D.M, ty, "HOW IT IS SET", 4.0, B.TEAL, "Inter-600", 1.6)
        D.bullets(c, D.M, ty - 8 * MM, left, 118 * MM, 3.0, B.NAVY_MID)

        notes = list(rows)
        if any("FAIL" in r for r in rows):
            notes.append("FAIL is measured on the working file. At this length the "
                         "photograph is placed large, so B-3 must be printed from the "
                         "full-resolution original, or the frame dropped — say which.")
        notes.append("Colour-retouched so the people read Black African; licence on page 6.")
        B.label(c, D.M + 130 * MM, ty, "PHOTOGRAPHS", 4.0, B.TEAL, "Inter-600", 1.6)
        D.bullets(c, D.M + 130 * MM, ty - 8 * MM, notes, 118 * MM, 3.0, B.NAVY_MID)


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
        "Fix at every eyelet, not every second one: a 4.9 m banner sails in wind and "
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
        "Confirm the size with the fence: all three banners are 16 ft × 49 in — 4876.8 × "
        "1244.6 mm — the client's measurement of 2026-11-07. Three of them need about "
        "15.6 m of fence with gaps.",
        "Confirm the spelling EDDWALIRO, and that BCM Medical Centre is the wording that "
        "goes on the fence.",
        "The service lists are split across the three banners so no service repeats. "
        "Tell us if any list must change.",
        "No monogram on the banners: the client asked for the badge off, so BCM "
        "stands alone — centred, and set large.",
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
  <p>All three at 16 ft × 49 in (4.88 m × 1.24 m). The layouts are the ones approved —
     EDDWALIRO at the head, MEDICAL CENTRE the widest line, the motto, a service list and
     a licensed photograph — now coloured from the clinic's sign post: white ground,
     EDDWALIRO white on the red block, MEDICAL CENTRE white on the navy band, red for
     the accents. Same red, same navy, so fence and light box read as one set.</p>
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
  <p class="note">Sizes are the client's: all three at 16 ft × 49 in. Substrate,
     hem and eyelets are industry-typical for a fence banner — confirm with the printer.
     No monogram on the banners: the badge came off at the client's request, so BCM
     stands alone, centred and set large.</p>
</main></body></html>
"""
    open(os.path.join(OUT_DIR, "index.html"), "w").write(html)


_apply_photo_rects()          # the panel size decides where the photographs sit


if __name__ == "__main__":
    main()
