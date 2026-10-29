# BACTIMED Community Medical Centre — one-way vision film, Rev R2

Photographic service panels for the glazed entrance doors of BCM Medical Centre.
Eight panes across four 900 mm door leaves, printed on perforated one-way vision film:
the street reads a poster, the clinic still sees out.

Built to the house style of the local door-sticker boards you supplied — white logo
plate at the top-left, photograph full bleed, solid caption band at the foot with the
service name set large.

**Provisional.** Pane sizes are scaled from the shopfront photograph, the B monogram is
a recreation, and no telephone numbers have been supplied yet, so none appear.

---

## Three doorways — the measured set

The clinic's own boards — the fascia sign listing general outpatient, inpatient, HIV care,
immunisation, pharmacy, laboratory, ultrasound, antenatal & postnatal, obs & gyn, paediatrics,
family planning, ENT, eye services, orthopaedics and travel medical examination — set the service
list. Dental is on the board and deliberately left out of the artwork at the client's instruction.
The two help-line numbers printed on the foot of every pane come off the same boards.

The R2 package above was scaled from a photograph. These three were built to the client's
measured glazing: every door is eight panes, four at **900 × 500 mm** and four at **900 × 400 mm**,
all 900 mm high. Doors 1 and 2 are perforated one-way vision; **door 3 is opaque white vinyl** and
is not see-through.

| Door | Folder | Role | Film | Panes |
| --- | --- | --- | --- | --- |
| 1 | [`door-1/`](door-1/) | Testing and treatment — HIV, pharmacy, malaria, CBC, antenatal, laboratory, consultation | One-way vision | 7 photographs + directory |
| 2 | [`door-2/`](door-2/) | The welcome door — WELCOME (open 24 hours), immunisation, general outpatient, laboratory, minor surgery, pharmacy, HIV care | One-way vision | 7 photographs + directory |
| 3 | [`door-3/`](door-3/) | Family care — antenatal & postnatal, laboratory, paediatrics, pharmacy, minor surgery, ultrasound, CBC | Opaque, no see-through | 7 photographs + directory |

Twenty-one different photographs across the three doors; no image is used twice, and every frame with people in it has been retouched so the faces and hands read as Black African, matching the community BACTIMED serves. Each door folder
carries its own artwork, schedule, specification, elevations, web preview, README and package zip.

---

## What's here

| Path | What it is |
| --- | --- |
| `index.html` | Web preview — all eight panes, both elevations, licence table |
| `BCM-Medical-Centre-One-Way-Vision-R2.pdf` | All eight panes in one 8-page PDF at print size |
| `artwork/BM-01…BM-08.pdf` | Individual print files: pane + 10 mm bleed + 20 mm slug + crop marks |
| `lookbook/BCM-Medical-Centre-…-Lookbook.pdf` | 3 pages — cover with the elevation, the set, after dark + identity |
| `lookbook/mockups/` | Frontage elevations, day and night |
| `docs/BCM-01-Panel-Schedule.pdf` | 4 pages — schedule, door survey, pane notes, licence log, resolution audit |
| `docs/BCM-02-Production-Specification.pdf` | 4 pages — film, artwork setup, installation, panel register |
| `web/` | Previews, mockup JPEGs, contact sheet, self-hosted fonts |

## The eight panes

| File | Service | Trim (mm) | Photograph | Position |
| --- | --- | --- | --- | --- |
| BM-01 | Dental | 810 × 1120 | PH-02 (Andrea Piacquadio / Pexels 3952130) | Left inner leaf, upper |
| BM-02 | Paediatrics | 810 × 1120 | PH-03 (Pavel Danilyuk / Pexels 5998457) | Right inner leaf, upper |
| BM-03 | Laboratory | 810 × 1120 | PH-05 (Pavel Danilyuk / Pexels 8442574) | Right outer leaf, upper |
| BM-04 | Physiotherapy | 810 × 1180 | PH-04 (Funkcinės Terapijos Centras / Pexels 20860597) | Left inner leaf, lower |
| BM-05 | Our Services | 810 × 1180 | none — type only | Right inner leaf, lower |
| BM-06 | Pharmacy | 810 × 1120 | PH-06 (cottonbro studio / Pexels 8657370) | Right outer leaf, lower |
| BM-07 | Antenatal | 810 × 1120 | PH-07 (MART PRODUCTION / Pexels 7089304) | Left outer leaf, upper |
| BM-08 | Reception | 810 × 1120 | PH-01 (Cedric Fauntleroy / Pexels 4269206) | Left outer leaf, lower |

## Photography — read this before printing

The base photographs are licensed Pexels stock (free commercial use, modification
permitted, checked 28 October 2026). Six of them were then retouched with an AI image
editor: the skin tone of the people was changed so the panels represent the community
BCM serves. Scenes, poses, clothing and equipment are the original photographs.

Two consequences, both stated in the documents:

- The people are **models, not BCM staff or patients.** No panel names them or presents
  them as staff. The retouch is declared in the schedule and on the web page.
- The retouched files are **proof-resolution only** (1264 px on the long edge). They are
  right for approval and for the mockups, not for a 3.5 m printed pane. For production,
  either re-do the retouch on the full-resolution originals or shoot the real team.

## Identity

- Navy `#16233F`, cyan `#2BA9E0`, mist `#E8EEF4` — carried over from the board language
- Slogan: *Your Health. Our Commitment.*
- B monogram: cyan arc around a bold B, drawn in vector (recreation, swap for the real logo)
- No telephone numbers, opening hours, accreditations or medical claims appear anywhere —
  none were supplied, and none have been invented

## Rebuilding

```sh
cd source
python3 bcm_build.py     # artwork, mockups, schedule, spec, lookbook, combined PDF, web preview
```

`bcm_brand.py` holds the BCM identity and the white logo plate; `cp_render.py`,
`cp_docs.py`, `cp_spec.py`, `cp_site.py` and `cp_mockup.py` are shared with the CarePoint
set and switch identity through `use_brand()`.

## Before release

1. Measure the glazing on site and re-issue every pane at measured size.
2. Send BCM's logo, tagline and telephone numbers; drop them into `bcm_brand.py`.
3. Re-run the retouch on full-resolution originals, or reshoot with the real team.
4. Replace the flagged printer values (1.6 mm hole / 2.3 mm pitch / ≈44 % open / 10 mm
   bleed) with the printer's own standard.
5. Proof on the actual film, not on paper.
