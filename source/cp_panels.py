"""CarePoint panel schedule — rebuilt from the client's door photograph.

GEOMETRY IS PROVISIONAL. The client's photograph shows four door leaves, each
with two stacked glass panes. Pixel proportions were measured off that image and
scaled to a standard 900 mm leaf; confirm every figure on site before release.

Door survey (from the supplied photograph, 2026-10-28):
  leaf width  ≈ 900 mm, 4 leaves, yellow-timber frames
  each leaf carries an upper and a lower glass pane
  upper pane  ≈ 810 × 1120 mm      lower pane ≈ 810 × 1180 mm
  main opening: two centre leaves; outer leaves fixed / one inward-opening
"""

BLEED_MM = 10.0
SAFE_MM = 25.0
SLUG_MM = 20.0
REVISION = "R2 / CAREPOINT / PROVISIONAL"
ISSUE_DATE = "2026-10-28"
FILM = "Perforated one-way vision film — 1.6 mm hole / 2.3 mm staggered pitch (~44% open)"

# shared grid, so every pane in the block lines up
UPPER_H, LOWER_H, PANE_W = 1120, 1180, 810


def _panel(pid, service, sub, h, photo, focus, accent, list_items=None, note="",
           zoom=1.0):
    return {
        "id": pid, "service": service, "sub": sub,
        "w": PANE_W, "h": h, "photo": photo, "focus": focus, "zoom": zoom,
        "accent": accent, "list_items": list_items,
        "orientation": "PORTRAIT — GLAZED DOOR PANE",
        "aspect": f"1 : {h / PANE_W:.2f}",
        "title_cap": 66 if len(service) <= 12 else 54,
        "note": note,
    }


PANELS = [
    _panel("CP-01", "DENTAL", "SERVICES", UPPER_H, "dental", (0.50, 0.34), "cyan",
           note="Treatment in progress, faces small — crop keeps the clinician's hands and the chair light."),
    _panel("CP-02", "PAEDIATRICS", "CHILD HEALTH", UPPER_H, "paeds", (0.46, 0.28), "cyan",
           note="Warm, calm, no distress. Child's face held in the upper third, clear of the safe line."),
    _panel("CP-03", "LABORATORY", "SERVICES", UPPER_H, "lab", (0.52, 0.34), "cyan",
           note="Bench and microscope read as capability rather than decoration."),
    _panel("CP-04", "PHYSIOTHERAPY", "REHABILITATION", LOWER_H, "physio", (0.48, 0.34), "cyan",
           note="Hands-on treatment, modest framing. No exposed skin beyond the treated limb."),
    _panel("CP-05", "OUR SERVICES", "DEPARTMENT DIRECTORY", LOWER_H, None, None, "cyan",
           list_items=["Paediatrics", "General medicine", "Minor surgery", "Immunisation",
                       "Laboratory", "Pharmacy", "Dentistry", "Antenatal services",
                       "Physiotherapy"],
           note="Directory pane: no photograph, so the type does the work at corridor distance."),
    _panel("CP-06", "PHARMACY", "DISPENSARY", UPPER_H, "pharmacy", (0.70, 0.46), "cyan",
           note="Shelving gives depth; faces stay sharp. Crop avoids the dark cabinet edge.",
           zoom=1.25),
    _panel("CP-07", "ANTENATAL", "ULTRASOUND & CARE", UPPER_H, "ultrasound", (0.50, 0.40), "cyan",
           note="Equipment only: no patient is depicted, which avoids implying a real person's scan."),
    _panel("CP-08", "RECEPTION", "GENERAL MEDICINE", UPPER_H, "reception", (0.50, 0.50), "cyan",
           note="The welcome panel — used on the entrance leaf, where it is seen first."),
]

# services the client states on their own board, all covered by a pane
SERVICES_BOARD = ["Paediatrics", "General medicine", "Minor surgery", "Immunisation",
                  "Laboratory", "Pharmacy", "Dentistry", "Antenatal services",
                  "Physiotherapy"]
