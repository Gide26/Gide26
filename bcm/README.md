# BCM Medical Centre — entrance door film set

Two things: photographic service panels for the glazed entrance doors of BCM Medical Centre, and a name-only sign post panel. Three doorways, eight panes each, printed on perforated one-way vision film on
doors 1 and 2 and on opaque white vinyl on door 3 — the street reads a poster, the clinic
still sees out of doors 1 and 2.

Built to the style of the door-sticker boards in the premises photographs: white logo plate
at the top-left, photograph full bleed, solid navy caption band at the foot with the service
name set large.

**Provisional.** The B monogram is a recreation, not the clinic's official logo. The doors
are drawn to the measured glazing supplied by the client; the plate and caption positions
should still be checked against the real leaves before the film is cut.

---

## The measured set

Every door is eight panes on four leaves: four panes at **900 × 500 mm** and four at
**900 × 400 mm**, all 900 mm high. The narrow 400 mm panes are the ones **in the middle of the
doorway, against the meeting stile**; the 500 mm panes sit at the two outer edges. So leaf A runs
wide then narrow and leaf B runs narrow then wide. The geometry is identical on all three doors;
only the subject matter and the film change.

| Door | Folder | Role | Film | Panes |
| --- | --- | --- | --- | --- |
| 1 | [`door-1/`](door-1/) | Testing and treatment — HIV care, pharmacy (tablets in hand), malaria, CBC, antenatal, laboratory, outpatient | One-way vision | 7 photographs + directory |
| 2 | [`door-2/`](door-2/) | The welcome door — WELCOME (open 24 hours), immunisation, general outpatient, obs & gyn, minor surgery, pharmacy (medicine handed over the counter), HIV care | One-way vision | 7 photographs + directory |
| 3 | [`door-3/`](door-3/) | Family, eye, ENT and ward care — antenatal & postnatal, eye services, paediatrics, ENT, minor surgery, ultrasound, inpatient care | Opaque, no see-through | 7 photographs + directory |

Twenty-one different photographs across the three doors — **no photograph is used twice**, and the
services are spread rather than repeated: pharmacy appears on doors 1 and 2 (a strip of tablets in
hand, and medicine handed across the counter), HIV care on doors 1 and 2, minor surgery on doors 2
and 3; every other service is pictured once. Every frame with people in it has been retouched so the
faces and hands read as Black African, matching the community BCM serves. Each door folder
carries its own artwork, schedule, specification, elevations, web preview, README and package zip.

## The sign post panel

A separate deliverable, name only: **3.10 ft × 2.11 ft** as the client measured it, landscape,
which is **944.9 × 643.1 mm**. No service list, no photograph — the badge, `BCM`, then
`MEDICAL CENTRE` set at the largest size the panel will take, so the name points from across the
road. Double-sided; both faces are in the one print PDF.

| Path | What it is |
| --- | --- |
| `sign/artwork/BCM-Sign-Name-Only.pdf` | Print file, option A (centred) — 1 : 1 mm, 10 mm bleed, crop marks, two faces |
| `sign/artwork/BCM-Sign-Name-Only-Option-B.pdf` | Print file, option B (badge-left lockup) |
| `sign/BCM-Sign-Panel.pdf` | 4 pages — panel to scale with dimensions, the two options, on the post, specification |
| `sign/lookbook/` | Day and night elevations, dimensioned panel |
| `sign/index.html` | Web preview |

Substrate (3 mm ACM, matte laminate), fixing (two 76 mm posts at 520 mm centres, panel centre
1500 mm above finished ground) and finish are industry-typical proposals flagged for the
signwriter; none of them is a quotation.

## What each door folder holds

| Path | What it is |
| --- | --- |
| `artwork/D{n}-P1…P8.pdf` | Individual print files — pane + 10 mm bleed + slug + crop marks |
| `BCM-Door-{n}-Panels.pdf` | All eight panes in one document at print size |
| `docs/` | Panel schedule (with door survey, pane notes, licence log) and production specification |
| `lookbook/` | Frontage elevations and mockups, day and night |
| `web/` | Preview JPEGs, contact sheet, self-hosted fonts |
| `index.html` | Web preview — all eight panes, both elevations, licence table |
| `README.md` | Door-specific record: panes, positions, photography, open questions |
| `BCM-Door-{n}-package.zip` | Everything above in one download |

## Services, from the clinic's own board

General outpatient, inpatient care, HIV care, immunisation, pharmacy, laboratory, ultrasound,
antenatal & postnatal, obs & gyn, paediatrics, minor surgery, family planning, ENT, eye
services, orthopaedics, travel medical exam — plus the two help-line numbers printed on the
foot of every pane, 0771 240 104 and 0754 132 715, taken from the premises boards. Nothing on
the artwork is invented: no address, no hours beyond the client's own 24-hour statement, no
accreditation, no clinical claim.

## Photography — read this before printing

The base photographs are licensed Pexels stock (free commercial use, no attribution,
modification permitted — terms checked 29 October 2026). The frames that carry people were
retouched with an AI image editor: skin tone only, so the people read as Black African.
Scenes, poses, clothing, equipment and lighting are the original photographs. Every retouch
is recorded in the table in each door's README, and in the licence log in its schedule.

Two consequences, stated in every door document:

- The people are **models, not BCM staff or patients.** No pane names them or presents
  them as staff.
- The working files are **proof-resolution only** (500–1264 px on the long edge). They are
  right for approval and for the mockups, not for a printed 900 mm pane; each door README
  states the ppi the crops actually resolve to. For production, the retouch is repeated on
  the full-resolution original from the Pexels link recorded against each asset, or the
  clinic's own team is photographed.

## Identity

- Navy `#16233F`, cyan `#2BA9E0`, mist `#E8EEF4`
- Motto on the plate: *We listen. We treat. We care.* — set under MEDICAL CENTRE at a
  size that never competes with the name, and held to the name's width
- **EDDWALIRO** — the Luganda word for hospital — heads the sign post panel, above the
  badge: bold, cyan, same cap height as the English name, so the panel reads to the road in
  Luganda first while MEDICAL CENTRE keeps the widest line, in white. It is not on the door
  panes: at 400 mm there is no room for a second language beside the name
- B monogram: cyan arc around a bold B, drawn in vector (recreation, swap for the real logo)
- Plate: monogram + `BCM` over `MEDICAL CENTRE`. The name carries the weight — MEDICAL CENTRE
  is set at 2.6 × the cap height of the initials, in the dark navy, spanning the full plate, so
  it is the thing a passer-by reads and points at. The initials sit above it in cyan as a
  kicker. Slogan appears on panes 470 mm wide and over, where it still reads through the
  perforation; the pane number sits in the plate's foot in grey
- Caption band: service name at 13.5 % of the pane width, subtitle and help line beneath

## Rebuilding

```sh
cd source
python3 bcm_doors.py          # all three doors — artwork, mockups, schedule, spec, web, zips
python3 bcm_doors.py 1        # one door
python3 bcm_sign.py           # the sign post panel — artwork, proof, elevations, web
```

Preview the whole set locally: `python3 -m http.server 8000 --directory bcm` and open
`http://localhost:8000/`. The hub at `bcm/index.html` links every door and the sign.

`bcm_brand.py` holds the identity and the white logo plate; `bcm_doors.py` the per-door
spec, crops and copy; `cp_photos.py` the licensed asset register; `cp_render.py`,
`cp_docs.py`, `cp_spec.py`, `cp_site.py` and `cp_mockup.py` are shared and switch identity
through `use_brand()`.

## Before release

1. Confirm the fascia wording — the board reads *Community Health Centre*, the artwork now uses
   *BCM Medical Centre* as instructed, with MEDICAL CENTRE as the dominant line.
2. Confirm the slogan — the board reads *Good Health is Your Responsibility*, the artwork
   reads *We listen. We treat. We care.*, the motto the client supplied.
3. Send the official logo file to replace the recreation. If the real logo already contains the
   name, the plate can be simplified to badge + name at a single size.
4. Confirm the help-line numbers and whether the email address should appear.
5. Re-run the retouch on the full-resolution originals, or photograph the real team.
6. Replace the flagged printer values (hole pitch, open area, bleed) with the printer's own
   standard, and proof on the actual film, not on paper.
