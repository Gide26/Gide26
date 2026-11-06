# BCM Medical Centre — door 4

Eight panes on the 4th doorway, built from the client's own measurement rather
than from a photograph: four panes at **900 × 500 mm** and four at **900 × 400 mm**, all 900 mm
high. The geometry is identical on every door; only the subject matter and the film change.

Perforated one-way vision vinyl — you can see out through the print from inside.

| Pane | Service | Glass (H × W) | Photograph | Leaf · position |
| --- | --- | --- | --- | --- |
| D4-P1 | Pharmacy | 900 × 500 | PH-17 Pharmacist handing medicine across a dispensary counter | left leaf · upper outer |
| D4-P2 | Laboratory | 900 × 400 | PH-21 Scientist examining samples at a microscope | left leaf · upper middle |
| D4-P3 | CBC | 900 × 500 | PH-15 Blood sample tubes in a rack beside a centrifuge | left leaf · lower outer |
| D4-P4 | Ultrasound | 900 × 400 | PH-07 Ultrasound scanner and examination couch in a clinic scanning room | left leaf · lower middle |
| D4-P5 | Laboratory | 900 × 500 | PH-16 Scientist working at a microscope | right leaf · upper outer |
| D4-P6 | CBC | 900 × 400 | PH-23 Blood samples in a rack with a centrifuge | right leaf · upper middle |
| D4-P7 | Open 24 Hours | 900 × 400 | none — type only | right leaf · lower middle |
| D4-P8 | Our Services | 900 × 500 | none — type only | right leaf · lower outer |

Seven different photographs and one type-only directory. No image on this door appears on either
of the other two.

## Files

- `artwork/D4-P1…P8.pdf` — print files, pane + 10 mm bleed + 20 mm slug + crop marks
- `BCM-Door-4-Panels.pdf` — all eight pages in one file
- `docs/BCM-Door-4-Schedule.pdf` — schedule + measured layout diagram
- `docs/BCM-Door-4-Specification.pdf` — film, artwork setup, installation, open items
- `lookbook/M-01-door-4-day.png`, `M-02-door-4-night.png` — elevations
- `index.html` — web preview

## Photography

All photographs are Pexels Free licence, checked 29 October 2026: free commercial use, no
attribution required, modification allowed. The ones carrying an AI colour retouch so the people
reflect the community BCM serves are marked in the table below; the people in those frames are
models, never staff or patients, and no pane captions them as such.

| Asset | Pexels ID | Creator | Pexels original | Working file | Retouch |
| --- | --- | --- | --- | --- | --- |
| PH-17 | 8657358 | cottonbro studio | 6720 × 4480 px | 1264 × 842 px | yes — colour retouch |
| PH-21 | 8851548 | Mikhail Nilov | 7952 × 5304 px | 843 × 1264 px | yes — colour retouch |
| PH-15 | 6627696 | Karola G | 4480 × 6720 px | 500 × 750 px | no |
| PH-07 | 7089304 | MART PRODUCTION | 6123 × 4082 px | 1125 × 750 px | no |
| PH-16 | 9768447 | Ron Lach | 2987 × 4480 px | 843 × 1264 px | yes — colour retouch |
| PH-23 | 6627697 | Karola G | 6580 × 4387 px | 500 × 333 px | no |

At final size these working crops land between 25 and 71 ppi, so the PDFs are proofs for approval, not files to plot.

Working files are desktop previews, not print files. Pull the full-size original from the Pexels
link for each ID before plotting — the record of what was used, and where it came from, is the
point of the table.

## Provisional

- The 400 mm panes are drawn in the middle of the doorway, against the meeting stile, with the
  500 mm panes at the two outer edges — as the client described the door. Confirm against the
  real leaves before cutting.
- The B monogram is a recreation, not BCM's official logo.
- Telephone numbers on the foot of each pane: panes 1-18 (door 1, door 2, door 3 P1-P2)
  carry **0788 323 815** with 0754 132 715, changed at the client's instruction on
  2026-11-02. Panes 19-24 (door 3 P3-P8) keep 0771 240 104 with 0754 132 715 from the
  clinic's own boards, as do the sign post and the banners. Confirm all three lines are
  current before plotting.
- Doors 1 and 2 use the same perforated film; door 3 is opaque vinyl and will not match it exactly.
Rebuild: `cd source && python3 bcm_doors.py 4`
