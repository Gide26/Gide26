"""
Panel schedule + art direction.

IMPORTANT: every dimension in this file is PROVISIONAL. The client's door
measurements and photographs have not yet been received, so this is a
representative medical-centre module set built to real-world glass door
practice. Each panel is an independent artwork and can be re-cut in minutes
once the measured schedule arrives — the layout engine is parametric.

Units: millimetres. Origin: bottom-left of the trimmed panel.
"""

# ---------------------------------------------------------------------------
# Fixed production constants (PROVISIONAL — replace with printer's own numbers)
# ---------------------------------------------------------------------------
BLEED_MM = 10.0          # image/graphic bleed beyond trim
SAFE_MM = 25.0           # keep live content this far inside trim
HANDLE_CLEAR_MM = 40.0   # extra clearance around hardware
KICK_CLEAR_MM = 120.0    # bottom zone kept free of fine detail
SLUG_MM = 20.0           # technical slug strip outside the bleed
REVISION = "R1 / PROVISIONAL"
ISSUE_DATE = "2026-10-28"

FILM = "Perforated one-way vision film (1.6 mm hole / 2.3 mm pitch, ~38% open area)"


PANELS = [
    {
        "id": "P-01",
        "dept": "RECEPTION",
        "title": "RECEPTION",
        "sub": "WELCOME & PATIENT SERVICES",
        "w": 1000, "h": 2100,
        "orientation": "PORTRAIT SINGLE SWING DOOR",
        "aspect": "1 : 2.10",
        "layout": "single",
        "photo": "reception",
        "focus": (0.50, 0.30),
        "photo_bottom": 1250,   # y0, y1 of the photographic window (mm from floor)
        "title_cap": 78,
        "label_text": "DEPARTMENT 01",
        "hardware": [
            "Left-hand hinge set: 3 no. butt hinges",
            "Right-hand lever/pull handle, 950–1120 mm",
            "Overhead door closer, top 240 mm",
            "Floor clearance 8 mm",
        ],
        "handle": ("right", 150),   # pull handle on the active leaf, inset from the meeting edge
        "kick_note": "Mop and trolley zone — no live content in the bottom 140 mm.",
        "print_notes": "Photograph must knock out to navy at the bottom edge, not float.",
    },
    {
        "id": "P-02",
        "dept": "RECEPTION",
        "title": "RECEPTION",
        "sub": "SIDELIGHT",
        "w": 450, "h": 2100,
        "orientation": "PORTRAIT FIXED SIDELIGHT",
        "aspect": "1 : 4.67",
        "layout": "narrow",
        "photo": None,
        "focus": None,
        "photo_bottom": 1450,
        "title_cap": 52,
        "label_text": "ENTRANCE",
        "hardware": [
            "Fixed glazing; no hardware",
            "Frame rebate 18 mm all round",
            "Silicone joint at floor",
        ],
        "handle": None,
        "kick_note": "Silicone joint at the floor; no print within 30 mm of the frame rebate.",
        "print_notes": "No joins through the vertical wordmark; single-piece plot required.",
    },
    {
        "id": "P-03",
        "dept": "CONSULTATION",
        "title": "CONSULTATION",
        "sub": "ROOM 01",
        "w": 900, "h": 2100,
        "orientation": "PORTRAIT SINGLE SWING DOOR",
        "aspect": "1 : 2.33",
        "layout": "single",
        "photo": "consult_01",
        "focus": (0.48, 0.34),
        "photo_bottom": 1250,
        "title_cap": 70,
        "label_text": "ROOM 01",
        "hardware": [
            "Right-hand hinge set",
            "Left-hand lever handle, 980–1150 mm",
            "Overhead closer",
        ],
        "handle": ('left', 120),
        "print_notes": "Doctor's face sits in the upper third; keep clear of the closer shadow.",
    },
    {
        "id": "P-04",
        "dept": "CONSULTATION",
        "title": "CONSULTATION",
        "sub": "ROOM 02",
        "w": 900, "h": 2100,
        "orientation": "PORTRAIT SINGLE SWING DOOR",
        "aspect": "1 : 2.33",
        "layout": "single",
        "photo": "consult_02",
        "focus": (0.45, 0.30),
        "photo_bottom": 1250,
        "title_cap": 70,
        "label_text": "ROOM 02",
        "hardware": [
            "Left-hand hinge set",
            "Right-hand lever handle, 980–1150 mm",
            "Overhead closer",
        ],
        "handle": ('right', 120),
        "print_notes": "Landscape source: crop keeps both figures inside the safe zone.",
    },
    {
        "id": "P-05",
        "dept": "LABORATORY",
        "title": "LABORATORY",
        "sub": "DIAGNOSTIC TESTING",
        "w": 900, "h": 2100,
        "orientation": "PORTRAIT SINGLE SWING DOOR",
        "aspect": "1 : 2.33",
        "layout": "single",
        "photo": "lab",
        "focus": (0.55, 0.40),
        "photo_bottom": 1250,
        "title_cap": 70,
        "label_text": "DEPARTMENT 03",
        "hardware": [
            "Right-hand hinge set",
            "Left-hand lever handle, 980–1150 mm",
            "Overhead closer",
        ],
        "handle": ('left', 120),
        "print_notes": "Lab-coat highlights must be held below 240 so they do not bloom under perforation.",
    },
    {
        "id": "P-06",
        "dept": "PHARMACY",
        "title": "PHARMACY",
        "sub": "DISPENSARY",
        "w": 1000, "h": 2100,
        "orientation": "PORTRAIT SINGLE SWING DOOR",
        "aspect": "1 : 2.10",
        "layout": "single",
        "photo": "pharmacy",
        "focus": (0.30, 0.32),
        "photo_bottom": 1250,
        "title_cap": 78,
        "label_text": "DEPARTMENT 04",
        "hardware": [
            "Left-hand hinge set",
            "Right-hand pull handle, 950–1120 mm",
            "Push plate to 1200 mm",
        ],
        "handle": ('right', 150),
        "print_notes": "Shelf repetition reads as texture through the perforation — crop keeps it soft.",
    },
    {
        "id": "P-07",
        "dept": "IMAGING",
        "title": "IMAGING",
        "sub": "SCAN SUITE",
        "w": 1200, "h": 2100,
        "orientation": "PORTRAIT DOUBLE DOOR, 2 × 600 LEAVES",
        "aspect": "1 : 1.75",
        "layout": "double",
        "photo": "imaging",
        "focus": (0.50, 0.52),
        "photo_bottom": 1250,
        "title_cap": 78,
        "label_text": "DEPARTMENT 05",
        "hardware": [
            "Meeting stile at centre (600 mm)",
            "Vertical pull handles both leaves, 900–1500 mm",
            "Overhead closers both leaves",
            "Seam allowance ±3 mm per leaf",
        ],
        "handle": ('right', 300),
        "print_notes": "One artwork plotted, split at centreline. No text across the meeting stile.",
    },
    {
        "id": "P-08",
        "dept": "IMAGING",
        "title": "IMAGING",
        "sub": "SIDELIGHT",
        "w": 450, "h": 2100,
        "orientation": "PORTRAIT FIXED SIDELIGHT",
        "aspect": "1 : 4.67",
        "layout": "narrow",
        "photo": None,
        "focus": None,
        "photo_bottom": 1450,
        "photo_band": None,
        "title_cap": 52,
        "label_text": "SCAN SUITE",
        "hardware": [
            "Fixed glazing; no hardware",
            "Frame rebate 18 mm all round",
        ],
        "handle": None,
        "print_notes": "Pairs with P-07 and deliberately carries no photograph — the scanner image "
                       "must not repeat across two adjacent panels.",
    },
]

DEPARTMENTS = [
    ("P-01 / P-02", "Reception", "Welcoming arrival; receptionist assisting a patient at a modern desk.",
     "Warm, human, immediately legible. Face placed high in the window, desk line used as a horizontal anchor."),
    ("P-03 / P-04", "Consultation Rooms", "Authentic doctor–patient consultations, seated, respectful distance.",
     "Calm and confidential. Subject centred, eye-line above the fold; no exposed or distressed patients."),
    ("P-05", "Laboratory", "Qualified technician at a microscope in a working laboratory.",
     "Precision. Cool highlights, shallow depth of field, equipment legible but never clinical-cold."),
    ("P-06", "Pharmacy", "Pharmacists among organised medicine shelving.",
     "Order and care. Shelf rhythm reads as texture; hands and faces stay sharp."),
    ("P-07 / P-08", "Medical Imaging", "Radiology suite and diagnostic imaging equipment.",
     "Technology with calm. Symmetry of the scanner echoed by the door's centreline."),
]
