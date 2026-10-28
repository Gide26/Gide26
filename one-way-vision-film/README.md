# Medical Center — one-way vision film for glass doors

A complete, coordinated graphics package for the glazed door sections of a private
medical centre: **8 print panels across 5 services**, built for perforated one-way
vision film rather than opaque vinyl.

> **Status: Rev R1 — PROVISIONAL.**
> The client's door measurements, door photographs, logo and contact details have not
> yet been supplied, and the printer's technical sheet is outstanding. Every dimension
> here is a representative medical-centre module set, clearly marked as such in the
> artwork slugs, the schedule and the specification. The layout engine is parametric:
> real measurements are dropped into `source/panels.py` and the whole set re-flows —
> type re-fits, crops re-centre, nothing is stretched.

---

## What is in the package

| Path | Contents |
|---|---|
| `index.html` | **Client presentation** (open with any static server — see below) |
| `artwork/P-01…P-08.pdf` | True-size print artwork: 10 mm bleed, crop marks, registration target, technical slug **outside** the trim. No overlays. |
| `proofs/03-Technical-Proofs.pdf` | One A3 landscape sheet per panel: trim, safe zone, kick zone, handle position, dimensions, and the full spec block. This is the approval sheet. |
| `docs/01-Panel-Schedule.pdf` | Panel schedule (dimensions, orientation, hardware, coverage, photo asset) + panel detail cards + image source and licence log + resolution audit. |
| `docs/02-Production-Specification.pdf` | Material, colour and ink, one-way-vision constraints, installation schedule, printer RFQ, assumptions and sign-off. |
| `lookbook/GMC-One-Way-Vision-Lookbook.pdf` | 8-page design presentation: intent, palette, typography, panel suite, art direction, perforation handling, delivery. |
| `lookbook/mockups/*.png` | In-situ elevations (reception, consultation, imaging) composed from the actual artwork. |
| `source/` | The build system — brand primitives, panel data, renderer, documents. |
| `assets/photos/` | Web-resolution previews of the licensed photographs, used to build accurate comps. |

## Viewing the presentation

```bash
cd one-way-vision-film
python3 -m http.server 8000
# open http://localhost:8000
```

The page links directly to the artwork PDFs, the schedule, the proofs, the
specification and the lookbook.

## Rebuilding

```bash
cd source
python3 build_artwork.py     # true-size panel PDFs
python3 build_previews.py    # trimmed PNG previews (cached in .work)
python3 build_proofs.py      # A3 technical proof sheets
python3 build_schedule.py    # panel schedule + image log + resolution audit
python3 build_spec.py        # production specification + RFQ
python3 build_mockups.py     # in-situ elevations
python3 build_lookbook.py    # presentation PDF
python3 build_site.py        # presentation site
```

Requirements: `reportlab`, `pillow`, `pypdfium2`, `numpy`. Fonts (Manrope, Inter,
Cormorant) are in `source/fonts/` under the SIL Open Font License.

---

## Design decisions worth knowing

**Why the photograph sits at the head of each panel.** The lower 1.4 m of a glass
door is where hands, trolleys and mops live. Photography occupies 1250–2100 mm (the
eye-level band), and everything below is a quiet navy field that survives scuffing
without looking damaged.

**Why navy, not white.** On perforated film the darkest ink is the most transparent
zone — it hides the hole grid and gives the best outward view. A white or pale panel
would read as a mesh from both sides. Navy therefore carries both the brand and the
see-through performance.

**Why the headlines are 70–78 mm.** Perforation erodes edges by roughly one hole
diameter and lifts the apparent minimum type size. Nothing live is set below 4 mm
cap height; labels sit at 6–7 mm; headlines sit on solid navy, never over a
photograph, for maximum edge contrast.

**Why sidelights carry no photograph.** Two of the four glazed sections are narrow
fixed sidelights. Keeping them graphic-only prevents the scanner image repeating
across adjacent panels and preserves daylight into the corridor.

**Why the double door is one plot.** The imaging suite is 2 × 600 mm leaves. It is
designed as one artwork split at the centre line, with no type crossing the meeting
stile, so the scanner's symmetry survives the join.

---

## Imagery and licensing

All photographs are genuine, professionally shot stock images from **Pexels**. No
AI-generated imagery, synthetic people, or composited medical scenes are used
anywhere. Each panel states its asset number; the full record — creator, provider,
licence, original pixel size, and the resolution each panel achieves at final print
size — is in `docs/01-Panel-Schedule.pdf` (pages 3–4).

| Asset | Photograph | Creator | Original |
|---|---|---|---|
| A-01 | Receptionist assisting a patient at a modern desk | Cedric Fauntleroy | 5474 × 8211 |
| A-02 | Doctor sitting by a table with a patient | cottonbro studio | 4189 × 6284 |
| A-03 | Clinician discussing results with a patient | Thirdman | 4231 × 6346 |
| A-04 | Lab technician at a trinocular microscope | Pavel Danilyuk | 5192 × 3466 |
| A-05 | Pharmacists among medicine shelving | cottonbro studio | 6403 × 4269 |
| A-06 | MRI scanner in a hospital imaging room | MART PRODUCTION | 6000 × 4000 |

**Pexels Licence — checked 28 October 2026.** Permitted: free commercial and
non-commercial use including print marketing; modification and creative editing;
attribution not required (credited here as good practice). Not permitted: selling
unaltered copies; implying that depicted people or brands endorse the client; using
the imagery as part of a trade mark. These panels are environmental wayfinding and
must never caption a depicted person as named staff.

The previews in `assets/photos/` are web-resolution. Final output requires the
full-resolution originals downloaded from each asset page under the client's own
Pexels account, relinked at 150 ppi. The per-panel focus point is stored in
`source/panels.py`, so the crop reproduces exactly.

---

## Still outstanding

1. **Measurements.** Width and height in centimetres of every glass section, plus a
   photograph of each door with the hardware in frame. Use `CLIENT-INPUT.md`.
2. **Identity.** Client logo in vector form; approved department names, room numbers,
   contact details and any permitted claims. Everything currently reads
   "MEDICAL CENTER" with a placeholder monogram.
3. **Printer sheet.** Hole size and pitch, ink coverage limit, bleed and safe-zone
   allowance, maximum sheet/roll width. The RFQ on page 4 of the specification asks
   for exactly these.
4. **Sign-off path.** Do the client approve the design direction before the measured
   re-cut, or after? The system is built so either order works.
