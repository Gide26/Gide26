"""CarePoint production specification — what the printer needs to quote and run this job."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cp_docutil as D
import cp_brand as B


def use_brand(mod):
    """Swap the active identity module (CarePoint, BCM, …)."""
    global B
    B = mod
import cp_panels as PN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "carepoint")
MM = D.MM

PLACEMENT = {"CP-01": "Left inner leaf · upper", "CP-04": "Left inner leaf · lower",
             "CP-02": "Right inner leaf · upper", "CP-05": "Right inner leaf · lower",
             "CP-03": "Right outer leaf · upper", "CP-06": "Right outer leaf · lower",
             "CP-07": "Left outer leaf · upper", "CP-08": "Left outer leaf · lower"}

FILM_ROWS = [
    ["Substrate", "Perforated one-way vision vinyl, white-backed", "Industry standard",
     "Confirm brand"],
    ["Total thickness", "140–160 µm film plus liner", "Industry typical", "Confirm with printer"],
    ["Hole diameter", "1.6 mm", "Industry typical", "Confirm with printer"],
    ["Hole pitch", "2.3 mm centres, staggered", "Industry typical", "Confirm with printer"],
    ["Open area", "≈ 44 % by geometry", "1.6 mm hole on 2.3 mm staggered pitch", "Confirm with printer"],
    ["Finish", "Matte or satin anti-glare", "Recommended", "Confirm with printer"],
    ["Adhesive", "Clear removable acrylic, bubble-free", "Industry standard", "Confirm with printer"],
    ["Print", "UV or latex, 4-colour plus white backing layer", "Recommended", "Confirm with printer"],
]

SETUP_ROWS = [
    ["Trim size", "810 × 1120 mm (5 panes) / 810 × 1180 mm (3 panes)"],
    ["Bleed", "10 mm all round on every pane"],
    ["Live / safe area", "25 mm inside trim"],
    ["Crop marks", "Offset 4 mm from trim, 4 mm long, outside bleed"],
    ["Total artwork size", "830 × 1140 mm / 830 × 1200 mm including bleed"],
    ["Slug", "20 mm at foot, outside bleed — carries job, panel, size, revision"],
    ["Resolution", "Photographs: 75 ppi floor, 100 ppi target at final size in the placed "
     "crop. Vector and type: resolution-independent."],
    ["Colour space", "CMYK, coated profile supplied by printer"],
    ["Max ink", "300 % total"],
    ["Solid navy", "#16233F — specify as C98 M88 Y38 K42 equivalent, or use spot if offered"],
    ["Rich black", "Not used. Navy tints only."],
    ["Fonts", "Embedded subsets; Manrope + Inter, open licence (SIL OFL)"],
    ["Transparency", "Flattened — no live transparency or blend modes"],
    ["Overprint", "None. All elements knock out."],
]

INSTALL_STEPS = [
    "Site survey first: measure each glazed pane, corner to corner, and photograph the frames. "
    "The pane sizes in this set are scaled from the client's frontage photograph and must be "
    "confirmed before any film is cut.",
    "Select one leaf as a control. Clean the glass, apply one pane, view it from 3 m and 8 m in "
    "daylight and again at night with the interior lights on.",
    "Apply wet or dry following the film manufacturer's method — do not improvise with a method "
    "the supplier has not validated for this adhesive.",
    "Work top edge first, squeegee down and out from the centre. Keep the perforation pattern "
    "square to the frame, not to the handle.",
    "Trim inside the frame rebate, never over the edge of the glass. Leave 2 mm clearance so the "
    "film cannot lift when the leaf moves.",
    "Keep film 25 mm clear of handles, locks and hinges, and clear of any gasket or drainage "
    "channel.",
    "If the leaves are double-glazed, film only the interior face and check the unit's warranty "
    "before applying anything.",
    "Cure 24 hours before cleaning or closing the door against the film.",
]

CARE = [
    "Clean with water and a neutral detergent on a soft cloth; no solvents, no abrasive pads, no "
    "pressure washer.",
    "Never scrape ice or use a squeegee with a hard edge on the perforation.",
    "Check the leading edge of each opening leaf monthly — that is where lift always starts.",
    "Life expectancy for exterior-facing perforated vinyl on a sheltered entrance is typically "
    "3–5 years. Confirm the figure with the film supplier.",
]


def build():
    path = os.path.join(BASE, "docs", f"{B.DOC_CODE}-02-Production-Specification.pdf")
    c = D.new_doc(path, "CarePoint — one-way vision film production specification")

    # 1 · scope
    D.page_bg(c, f"{B.DOC_CODE} / OWV / 02", "Rev R2  ·  2026-10-28  ·  PROVISIONAL", 1,
              eyebrow="CAREPOINT MEDICAL CENTER  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Production specification", 8.2)
    y = D.para(c, D.M, y + 2 * MM,
               "Eight printed panes for the glass leaves of the CarePoint Medical Center frontage. "
               "This document states what the artwork requires and what the printer must confirm. "
               "Every value marked “confirm with printer” is an industry-typical figure used because "
               "the printer's own standard has not yet been supplied — it is a placeholder for a "
               "conversation, not a specification the printer has agreed to.",
               (D.PW - 2 * D.M) / MM, 3.4, B.NAVY_MID)
    y -= 2 * MM
    c.setFillColor(B.PAPER)
    c.rect(D.M, y - 26 * MM, D.PW - 2 * D.M, 26 * MM, stroke=0, fill=1)
    c.setFillColor(B.TEAL)
    c.rect(D.M, y - 26 * MM, 2.4 * MM, 26 * MM, stroke=0, fill=1)
    B.label(c, D.M + 8 * MM, y - 8 * MM, "THE ONE THING THAT MUST HAPPEN FIRST", 4.0, B.NAVY,
            "Inter-600", 1.6)
    D.para(c, D.M + 8 * MM, y - 15 * MM,
           "Measure the glazing. Pane sizes here were scaled from a photograph of the shopfront to a "
           "standard 900 mm leaf; a 20 mm error in a 1120 mm pane is invisible on screen and fatal "
           "on the glass. Re-issue every pane from measured dimensions before cutting film.",
           D.PW - 2 * D.M - 18 * MM, 3.2, B.NAVY_MID)
    y -= 33 * MM

    B.label(c, D.M, y, "FILM AND MATERIAL", 4.2, B.TEAL, "Inter-600", 1.8)
    y -= 6 * MM
    y = D.table(c, D.M, y, [("Property", 34, "left"), ("Specification", 92, "left"),
                            ("Basis", 34, "left"), ("Action", 34, "left")],
                FILM_ROWS, row_h=7.4 * MM, cap=2.9) - 6 * MM
    D.para(c, D.M, y,
           "One-way vision film is perforated so the inside of the building stays visible to staff. "
           "The printed face reads as a solid image from outside because the holes are below the "
           "eye's resolving limit at street distance; from inside, the same film reads as a dark "
           "tint. Nothing on these panes may depend on the viewer reading small type.",
           (D.PW - 2 * D.M) / MM, 3.0, B.NAVY_MID)

    # 2 · artwork setup
    c.showPage()
    D.page_bg(c, f"{B.DOC_CODE} / OWV / 02", "Rev R2  ·  2026-10-28  ·  PROVISIONAL", 2,
              eyebrow="CAREPOINT MEDICAL CENTER  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Artwork setup", 8.2)
    y = D.para(c, D.M, y + 2 * MM,
               "Supplied as eight single-page PDFs, one per pane, plus a combined eight-page file. "
               "Each page is the trim size plus bleed plus a 20 mm slug at the foot, with crop marks "
               "outside the bleed.",
               (D.PW - 2 * D.M) / MM, 3.3, B.NAVY_MID)
    y -= 2 * MM
    cols = [("Item", 44, "left"), ("Value", 150, "left")]
    y = D.table(c, D.M, y, cols, SETUP_ROWS, row_h=6.6 * MM, cap=2.9) - 7 * MM

    B.label(c, D.M, y, "LEGIBILITY THROUGH THE PERFORATION", 4.2, B.TEAL, "Inter-600", 1.8)
    y -= 6 * MM
    D.bullets(c, D.M, y, [
        "Service names are set at 54–66 mm cap height, Manrope 800. At 44 % open area the edges of "
        "the letterforms pick up the hole pattern, so thin weights and hairline serifs are out.",
        "Nothing live sits below 6 mm cap height. Reverse type on the navy block holds; type on "
        "photographs does not, so no caption is ever placed over a photograph.",
        "The navy caption block is a solid tint, not a photograph — it is the one area where type "
        "stays crisp through the film.",
        "Contrast on the caption block is white on #16233F: well beyond the 4.5:1 needed at these "
        "sizes even after the perforation softens the edges.",
    ], 168 * MM, 3.1, B.NAVY_MID)

    # 3 · installation
    c.showPage()
    D.page_bg(c, f"{B.DOC_CODE} / OWV / 02", "Rev R2  ·  2026-10-28  ·  PROVISIONAL", 3,
              eyebrow="CAREPOINT MEDICAL CENTER  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Installation", 8.2)
    y = D.bullets(c, D.M, y + 2 * MM, INSTALL_STEPS, 118 * MM, 3.1, B.NAVY_MID, gap=2.6)

    x2 = D.M + 130 * MM
    w2 = D.PW - x2 - D.M
    B.label(c, x2, D.PH - 44 * MM, "CARE AFTER INSTALLATION", 4.2, B.TEAL, "Inter-600", 1.8)
    cy = D.bullets(c, x2, D.PH - 52 * MM, CARE, w2, 3.0, B.NAVY_MID, gap=2.4)

    B.label(c, x2, cy - 6 * MM, "SIGNOFF CHECKLIST", 4.2, B.TEAL, "Inter-600", 1.8)
    D.bullets(c, x2, cy - 14 * MM, [
        "All eight panes measured on site and artwork re-issued to measured size.",
        "Client's vector logo supplied and substituted for the recreation.",
        "Original photographs relinked at full resolution and crops re-checked.",
        "Proof approved on the actual film, not on paper.",
        "One control pane installed and viewed from street and interior before the set is run.",
    ], w2, 3.0, B.NAVY_MID, gap=2.4)

    # perforation diagram + open items, foot of the installation page
    dy = 33 * MM
    c.setFillColor(B.NAVY)
    c.rect(D.M, dy, 78 * MM, 44 * MM, stroke=0, fill=1)
    step = 2.3 * MM
    r = 0.8 * MM
    row = 0
    yy = dy + 3 * MM
    while yy < dy + 41 * MM:
        xx = D.M + 3 * MM + (step / 2 if row % 2 else 0)
        while xx < D.M + 75 * MM:
            c.setFillColor(B.MIST)
            c.circle(xx, yy, r, stroke=0, fill=1)
            xx += step
        yy += step * 0.87
        row += 1
    B.label(c, D.M, dy - 6 * MM,
            "PERFORATION AT 1:1 — 1.6 MM HOLES, 2.3 MM STAGGERED PITCH, ≈44 % OPEN", 3.0,
            B.GREY, "Inter-500", 1.1)

    x3 = D.M + 92 * MM
    w3 = D.PW - x3 - D.M
    B.label(c, x3, dy + 40 * MM, "OPEN ITEMS — NEEDED BEFORE FILM IS CUT", 4.2, B.TEAL,
            "Inter-600", 1.8)
    D.bullets(c, x3, dy + 32 * MM, [
        "Measured glazing schedule, or a photograph of each leaf with a tape measure held against "
        "it. Everything in this set is scaled from one elevation.",
        "The client's vector logo — the cp mark here is a recreation drawn from the sign.",
        "Sign-off on the services list exactly as it will read on the directory pane.",
        "The printer's own film standard, so the flagged values above can be replaced with real ones.",
        "Confirmation of which leaves are opening leaves, so handles and locks can be masked out "
        "before output.",
    ], w3, 3.0, B.NAVY_MID, gap=2.6)

    # 4 · panel register
    c.showPage()
    D.page_bg(c, f"{B.DOC_CODE} / OWV / 02", "Rev R2  ·  2026-10-28  ·  PROVISIONAL", 4,
              eyebrow="CAREPOINT MEDICAL CENTER  ·  ONE-WAY VISION FILM")
    y = D.h1(c, D.PH - 34 * MM, "Panel register", 8.2)
    D.para(c, D.M, y + 2 * MM,
           "What each file contains, and where it goes on the frontage. Rev R2 is provisional: the "
           "panel sizes still rest on the photographic survey.",
           (D.PW - 2 * D.M) / MM, 3.2, B.NAVY_MID)
    placement = PLACEMENT
    rows = [[p["id"], p["service"], f"{p['w']} × {p['h']}",
             f"{p['w'] + 20} × {p['h'] + 20} bleed", placement[p["id"]],
             "no bleed colour — image runs to edge" if p["photo"] else "solid navy to edge"]
            for p in PN.PANELS]
    ty = D.table(c, D.M, D.PH - 58 * MM,
            [("File", 14, "left"), ("Service", 34, "left"), ("Trim mm", 24, "left"),
             ("Supplied size mm", 34, "left"), ("Position", 50, "left"),
             ("Edge", 60, "left")],
            rows, row_h=9.0 * MM, cap=2.9)

    B.label(c, D.M, ty - 8 * MM, "REVISION AND APPROVAL", 4.2, B.TEAL, "Inter-600", 1.8)
    D.table(c, D.M, ty - 16 * MM,
            [("Rev", 12, "left"), ("Date", 24, "left"), ("Change", 118, "left"),
             ("Status", 30, "left")],
            [["R1", "2026-10-27", "Placeholder-brand concept set", "Superseded"],
             ["R2", "2026-10-28", "Rebuilt on the client's own identity, measured shopfront "
              "geometry, verified photography, night mockup", "For client review"]],
            row_h=8.0 * MM, cap=2.9)
    c.save()
    return path


if __name__ == "__main__":
    print("built", build())
