"""Production specification, installation schedule and printer RFQ."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import docutil as D
import brand as B
import panels as PN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "one-way-vision-film", "docs")
MM = D.MM


def pg(c, n, footer="GMC / OWV / 02  ·  Rev R1  ·  2026-10-28"):
    D.page_bg(c, "GMC / OWV / 02", footer + "  ·  PROVISIONAL", n)


def build():
    path = os.path.join(DOCS, "02-Production-Specification.pdf")
    c = D.new_doc(path, "Production specification — one-way vision film")

    # ------------------------------------------------------------ page 1
    pg(c, 1, "GMC / OWV / 02  ·  Rev R1  ·  2026-10-28")
    y = D.h1(c, D.PH - 34 * MM, "Production specification", 8.4)
    D.para(c, D.M, y + 2 * MM,
           "This document states how the eight panels are to be produced, applied and inspected. "
           "Everything marked PROVISIONAL is an industry-typical value used because the printer's "
           "own sheet has not yet been issued; each such value is repeated in the RFQ on page 6 and "
           "must be replaced by the printer's figure before release. Nothing in this document should "
           "be read as a printer-approved specification.",
           (D.PW - 2 * D.M) / MM, 3.4, B.NAVY_MID)

    left_w = (D.PW - 2 * D.M) / MM / 2 - 8
    y2 = D.PH - 74 * MM
    B.label(c, D.M, y2, "1  MATERIAL", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, y2 - 8 * MM, [
        "Perforated one-way vision film, white gloss face, grey-back adhesive. PROVISIONAL hole "
        "geometry 1.6 mm on a 2.3 mm pitch (~38% open area).",
        "No laminated over-laminate unless requested — a matte over-laminate reduces the "
        "see-through performance and increases the drop in outside contrast.",
        "Film must be supplied in a width that covers the tallest dimension in one piece "
        "(2100 mm panels) so no horizontal join crosses a headline.",
        "Warranty: minimum 5 years vertical exterior/interior glazing, manufacturer-backed.",
    ], left_w * MM, 3.3, B.NAVY_MID)

    B.label(c, D.M + (left_w + 16) * MM, y2, "2  COLOUR & INK", 4.0, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M + (left_w + 16) * MM, y2 - 8 * MM, [
        "Print CMYK, colour-managed to the printer's ICC profile for the specified film; "
        "solvent, UV or latex as the printer recommends. No RGB files released.",
        "Target values: navy #0A2642 → C100 M88 Y40 K38; teal #0F8C8C → C78 M22 Y48 K2; "
        "medical green #2E7A5F → C80 M30 Y65 K20. Treat as starting points for a proof, not as "
        "absolute conversion.",
        "Total ink coverage: hold the deep navy field at or below the film maker's stated maximum. "
        "Heavy coverage on perforated film causes blocking and slows drying — confirm the limit.",
        "White ink underbase: NOT used. The design relies on the film's own white face; adding a "
        "white layer would kill the one-way effect.",
        "Provide a colour-managed proof at 100% on the actual film before the production run.",
    ], left_w * MM, 3.3, B.NAVY_MID)

    y3 = 92 * MM
    B.label(c, D.M, y3, "3  ARTWORK CONSTRUCTION", 4.0, B.TEAL, "Inter-600", 1.6)
    cols = [("PARAMETER", 70, "left"), ("VALUE USED HERE", 62, "left"),
            ("STATUS", 34, "left"), ("NOTE", 96, "left")]
    rows = [
        ["Bleed", f"{PN.BLEED_MM:.0f} mm all round", "PROVISIONAL",
         "Applied to graphics and photography; trimmed before mounting"],
        ["Safe zone", f"{PN.SAFE_MM:.0f} mm inside trim", "PROVISIONAL",
         "Live type, logo and faces kept inside this line"],
        ["Hardware clearance", f"{PN.HANDLE_CLEAR_MM:.0f} mm around fittings", "PROVISIONAL",
         "Handles, closers, hinges and meeting stiles"],
        ["Kick zone", f"{PN.KICK_CLEAR_MM:.0f} mm from floor", "PROVISIONAL",
         "No live content; scuff and mop damage area"],
        ["Resolution", "150 ppi target / 110 ppi floor at final size", "AGREED",
         "See resolution audit in the panel schedule"],
        ["Colour space", "CMYK, printer ICC profile", "PROVISIONAL",
         "Confirm profile name before output"],
        ["File format", "PDF/X-4 preferred; PDF 1.6 acceptable", "PROVISIONAL",
         "Fonts embedded, images linked then flattened by the printer"],
        ["Slug strip", f"{PN.SLUG_MM:.0f} mm outside the bleed", "PROJECT RULE",
         "Panel ID, size, orientation, revision — trimmed off"],
    ]
    D.table(c, D.M, y3 - 3 * MM, cols, rows, row_h=8.6 * MM, cap=2.9)
    c.showPage()

    # ------------------------------------------------------------ page 2
    pg(c, 2)
    y = D.h1(c, D.PH - 34 * MM, "One-way vision specific requirements", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "These are the constraints that separate a one-way vision job from an ordinary vinyl "
           "print. They govern the design as much as the production.",
           (D.PW - 2 * D.M) / MM, 3.4, B.NAVY_MID)

    items = [
        ("IMAGE DENSITY", "Dark, saturated areas hide the perforation best; pale, busy photographs "
                          "read as a mesh. Every photograph in this set is graded down towards navy in "
                          "shadow, and no panel places light type or light detail over a mid-tone."),
        ("VISIBILITY BALANCE", "The client must be able to see out. Photography covers 40–45% of a "
                               "door; sidelights carry none. The remainder is a solid navy field which, "
                               "being dark, is the most transparent zone on the panel."),
        ("EDGE CONTRAST", "Perforation erodes edges by roughly one hole diameter. Type is set in "
                          "600–800 weights at 70–78 mm cap height; hairline rules are decorative and "
                          "carry no information."),
        ("NO FINE PATTERNS", "No fine stripes, small maps, dot screens or thin iconography anywhere "
                             "in the artwork. The ghost numerals are set at 6% tint purely as a "
                             "large-scale texture and are not intended to be read."),
        ("INSIDE APPEARANCE", "From inside, the panel reads as a dark grey field with a faint "
                              "photographic ghost. Plan interior lighting accordingly; the panels "
                              "should not be relied on for privacy after dark."),
        ("CLEANING", "Perforated film traps dust in the holes. Specify a non-abrasive, "
                     "solvent-free cleaner and a soft cloth; no squeegee pressure over type."),
    ]
    col_w = (D.PW - 2 * D.M) / 3 - 12 * MM
    for i, (head, body) in enumerate(items):
        col, row = i % 3, i // 3
        x = D.M + col * (col_w + 18 * MM)
        yy = D.PH - 70 * MM - row * 36 * MM
        c.setFillColor(B.TEAL)
        c.rect(x, yy + 3 * MM, 22, 1.4 * MM, stroke=0, fill=1)
        B.label(c, x, yy - 4 * MM, head, 3.8, B.NAVY, "Inter-600", 1.5)
        D.para(c, x, yy - 11 * MM, body, col_w, 3.2, B.NAVY_MID, 1.6)

    # ink coverage bar
    By = 50 * MM
    B.label(c, D.M, By + 16 * MM, "INK COVERAGE BY PANEL TYPE (TARGET)", 3.8, B.TEAL,
            "Inter-600", 1.6)
    for i, (name, pct, note) in enumerate([("Navy field", 92, "highest coverage zone"),
                                           ("Photographic band", 78, "graded, not flat"),
                                           ("Type and rules", 100, "small area, high density")]):
        yy = By - i * 9 * MM
        B.label(c, D.M, yy, name, 3.2, B.NAVY_MID, "Inter-500", 1.0)
        c.setFillColor(B.MIST)
        c.rect(D.M + 42 * MM, yy - 0.6 * MM, 96 * MM, 4.2 * MM, stroke=0, fill=1)
        c.setFillColor(B.TEAL if i < 2 else B.NAVY)
        c.rect(D.M + 42 * MM, yy - 0.6 * MM, 96 * MM * pct / 100.0, 4.2 * MM, stroke=0, fill=1)
        B.label(c, D.M + 142 * MM, yy, f"{pct}%", 3.2, B.NAVY, "Inter-600", 0.6)
        B.label(c, D.M + 160 * MM, yy, note, 3.0, B.GREY, "Inter-400", 0.6)
    B.label(c, D.M, By - 28 * MM,
            "Percentage figures are the designed intention on a 100% K-out basis, not measured "
            "values. The printer's limit governs what is released.", 3.0, B.GREY, "Inter-400", 0.8)
    c.showPage()

    # ------------------------------------------------------------ page 3
    pg(c, 3)
    y = D.h1(c, D.PH - 34 * MM, "Installation schedule", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "Sequence assumes the glazing is complete, clean and within tolerance. Each panel is an "
           "independent plot; the site is measured twice — once for the schedule and once after "
           "glazing — before release.",
           (D.PW - 2 * D.M) / MM, 3.4, B.NAVY_MID)

    cols = [("PANEL", 16, "left"), ("LOCATION", 54, "left"), ("TRIM (CM)", 24, "left"),
            ("PLOT SIZE INCL. BLEED (MM)", 44, "left"), ("PIECES", 18, "left"),
            ("FIXING", 54, "left"), ("SEQUENCE", 44, "left")]
    rows = []
    order = ["1", "2", "3", "4", "5", "6", "7", "8"]
    locs = {"P-01": "Reception entrance, active leaf", "P-02": "Reception entrance, sidelight",
            "P-03": "Consultation room 01", "P-04": "Consultation room 02",
            "P-05": "Laboratory entrance", "P-06": "Pharmacy entrance",
            "P-07": "Imaging suite, double leaf", "P-08": "Imaging suite, sidelight"}
    for p, seq in zip(PN.PANELS, order):
        pieces = "2 (split)" if p["layout"] == "double" else "1"
        rows.append([p["id"], locs[p["id"]], f"{p['w']/10:.0f} × {p['h']/10:.0f}",
                     f"{p['w']+2*PN.BLEED_MM:.0f} × {p['h']+2*PN.BLEED_MM:.0f}",
                     pieces,
                     "Wet apply, squeegee, trimmed in situ" if p["layout"] != "double"
                     else "Dry apply per leaf, trimmed at stile",
                     f"Step {seq}"])
    D.table(c, D.M, y - 2 * MM, cols, rows, row_h=10.0 * MM, cap=2.8)

    yb = 74 * MM
    B.label(c, D.M, yb, "SITE PREPARATION AND SIGN-OFF", 3.8, B.TEAL, "Inter-600", 1.6)
    D.bullets(c, D.M, yb - 8 * MM, [
        "Glass cleaned with a two-stage method (detergent, then pure water) and fully dry; "
        "surface temperature between 10 °C and 30 °C.",
        "Ambient conditions recorded on the day: temperature, humidity, and whether the space is "
        "dust-controlled. Wet application only in a dust-free interior.",
        "Hardware removed and refitted by the door contractor, not the film installer, where the "
        "film must pass behind a closer or hinge cover.",
        "Each panel inspected at 1 m under raking light: no bubbles over 1 mm, no lifted edges, no "
        "trim deviation greater than 1 mm from the frame line.",
        "Client walk-through and written acceptance; retain one A4 offcut per panel for future "
        "colour matching.",
    ], 168 * MM, 3.3, B.NAVY_MID)
    c.showPage()

    # ------------------------------------------------------------ page 4
    pg(c, 4)
    y = D.h1(c, D.PH - 34 * MM, "Printer RFQ — questions to settle before release", 8.0)
    D.para(c, D.M, y + 2 * MM,
           "Send this page with the artwork. The answers replace every PROVISIONAL value in this "
           "specification and in the panel schedule; the artwork is then re-issued at the same "
           "revision number with the confirmed figures.",
           (D.PW - 2 * D.M) / MM, 3.4, B.NAVY_MID)

    qs = [
        ("FILM", "Exact product, hole diameter, pitch and open-area percentage. Roll width and "
                 "whether 2100 mm panels can be produced in one piece without a join."),
        ("ADHESIVE", "Grey-back or clear adhesive? Is a removable or bubble-free adhesive available "
                     "for glass doors that may need re-glazing?"),
        ("INK LIMIT", "Maximum total ink coverage for this film, and any restriction on large solid "
                      "dark fields."),
        ("WHITE INK", "Confirm no white underbase is applied. If it is mandatory for durability, "
                      "state the effect on the one-way performance."),
        ("BLEED", "Required bleed and safe-zone allowance, and whether artwork should be supplied "
                  "with marks and slug or trimmed to a fixed sheet size."),
        ("COLOUR", "ICC profile name, proofing route (contract proof on film or soft proof), and "
                   "who signs off colour."),
        ("FILE SPEC", "Preferred PDF standard, maximum file size, and whether the printer imposes "
                      "its own imposition."),
        ("PROOF", "Cost and lead time for a 1:1 proof of one panel on the specified film."),
        ("INSTALL", "Who installs, what surface tolerance is accepted, and what the warranty covers "
                    "— material only or material and labour?"),
        ("LEAD TIME", "Production and installation lead time for eight panels, and any minimum "
                      "order or sheet waste charge."),
    ]
    col_w = (D.PW - 2 * D.M) / 2 - 9 * MM
    for i, (head, body) in enumerate(qs):
        col, row = i % 2, i // 2
        x = D.M + col * (col_w + 18 * MM)
        yy = D.PH - 76 * MM - row * 26 * MM
        B.label(c, x, yy, f"{i+1:02d}   {head}", 3.6, B.NAVY, "Inter-600", 1.6)
        D.para(c, x, yy - 6 * MM, body, col_w, 3.1, B.NAVY_MID, 1.6)
    c.showPage()

    # ------------------------------------------------------------ page 5
    pg(c, 5)
    y = D.h1(c, D.PH - 34 * MM, "Approval record and assumptions", 8.0)
    B.label(c, D.M, D.PH - 58 * MM, "REVISION HISTORY", 3.8, B.TEAL, "Inter-600", 1.6)
    cols = [("REV", 16, "left"), ("DATE", 30, "left"), ("ISSUE", 90, "left"),
            ("CHANGE", 120, "left"), ("BY", 40, "left")]
    rows = [["R1", "2026-10-28", "Client review — provisional module set",
             "First issue: 8 panels, system, schedule, spec", "Design"],
            ["", "", "", "", ""],
            ["", "", "", "", ""]]
    D.table(c, D.M, D.PH - 62 * MM, cols, rows, row_h=9.0 * MM, cap=2.9)

    B.label(c, D.M, 132 * MM, "ASSUMPTIONS ON WHICH THIS ISSUE RESTS", 3.8, B.TEAL,
            "Inter-600", 1.6)
    D.bullets(c, D.M, 124 * MM, [
        "Doors are glazed with clear float or low-iron glass; no tinted, frosted, wired or "
        "Low-E coating that would change the appearance of the film.",
        "Each glass section is flat, vertical and within ±3 mm of the stated dimensions.",
        "Film is applied to the outside face of the glass unless the printer advises otherwise; "
        "the design is orientation-independent apart from the photographic crop.",
        "No internal signage, manifestation strips or privacy band is required on the same glass. "
        "If a manifestation band is required for safety glazing compliance, it must be designed "
        "with the panel, not applied over it.",
        "Department names, room numbers and the identity lockup are placeholders pending the "
        "client's own brand assets.",
        "Photographs are licensed stock imagery, not portraits of staff or patients of the centre. "
        "They may not be captioned or implied to depict named individuals.",
    ], 176 * MM, 3.2, B.NAVY_MID)

    by = 44 * MM
    B.label(c, D.M, by, "SIGN-OFF", 3.8, B.TEAL, "Inter-600", 1.6)
    for i, (role, _) in enumerate([("CLIENT", ""), ("DESIGN", ""), ("PRINTER", "")]):
        x = D.M + i * 88 * MM
        c.setStrokeColor(B.MIST)
        c.setLineWidth(0.3)
        c.line(x, by - 14 * MM, x + 70 * MM, by - 14 * MM)
        B.label(c, x, by - 19 * MM, role, 3.0, B.GREY, "Inter-500", 1.4)
        B.label(c, x, by - 24 * MM, "name / date", 2.8, B.GREY, "Inter-400", 0.8)
    c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    os.makedirs(DOCS, exist_ok=True)
    print("built", build())
