# BCM Medical Centre — door 1

Eight panes on the first doorway, built from the client's own measurement rather
than from a photograph: four panes at **900 × 500 mm** and four at **900 × 400 mm**, all 900 mm
high. The geometry is identical on all three doors; only the subject matter and the film change.

Perforated one-way vision vinyl — you can see out through the print from inside.

| Pane | Service | Glass (H × W) | Photograph | Leaf · position |
| --- | --- | --- | --- | --- |
| D1-P1 | HIV Care | 900 × 500 | PH-09 Gloved hand holding two blood sample tubes for testing | left leaf · upper outer |
| D1-P2 | Pharmacy | 900 × 400 | PH-28 Hands holding a strip of tablets | left leaf · upper middle |
| D1-P3 | Malaria | 900 × 500 | PH-11 Macro photograph of a mosquito on skin, taken in Kaduna, Nigeria | left leaf · lower outer |
| D1-P4 | CBC | 900 × 400 | PH-10 Gloved hands handling a purple-top blood tube over a vacutainer rack | left leaf · lower middle |
| D1-P5 | Laboratory | 900 × 400 | PH-05 Laboratory technician at a trinocular microscope | right leaf · upper middle |
| D1-P6 | Antenatal | 900 × 500 | PH-24 Ultrasound examination of a pregnant patient | right leaf · upper outer |
| D1-P7 | Outpatient | 900 × 400 | PH-08 Doctor consulting a patient across a desk | right leaf · lower middle |
| D1-P8 | Our Services | 900 × 500 | none — type only | right leaf · lower outer |

Seven different photographs and one type-only directory. No image on this door appears on either
of the other two.

## Files

- `artwork/D1-P1…P8.pdf` — print files, pane + 10 mm bleed + 20 mm slug + crop marks
- `BCM-Door-1-Panels.pdf` — all eight pages in one file
- `docs/BCM-Door-1-Schedule.pdf` — schedule + measured layout diagram
- `docs/BCM-Door-1-Specification.pdf` — film, artwork setup, installation, open items
- `lookbook/M-01-door-1-day.png`, `M-02-door-1-night.png` — elevations
- `index.html` — web preview

## Photography

All photographs are Pexels Free licence, checked 29 October 2026: free commercial use, no
attribution required, modification allowed. The ones carrying an AI colour retouch so the people
reflect the community BCM serves are marked in the table below; the people in those frames are
models, never staff or patients, and no pane captions them as such.

| Asset | Pexels ID | Creator | Pexels original | Working file | Retouch |
| --- | --- | --- | --- | --- | --- |
| PH-09 | 6074931 | Alena Shekhovtcova | 4160 × 6240 px | 500 × 750 px | no |
| PH-28 | 3923159 | cottonbro studio | 4000 × 6000 px | 843 × 1264 px | yes — colour retouch |
| PH-11 | 32946369 | Saeed Saeed | 2795 × 4466 px | 500 × 799 px | no |
| PH-10 | 8460340 | Los Muertos Crew | 6000 × 4000 px | 1125 × 750 px | no |
| PH-05 | 8442574 | Pavel Danilyuk | 5192 × 3466 px | 1264 × 844 px | yes — colour retouch |
| PH-24 | 7088826 | MART PRODUCTION | 5625 × 3750 px | 1264 × 842 px | yes — colour retouch |
| PH-08 | 7580254 | cottonbro studio | 4189 × 6284 px | 843 × 1264 px | yes — colour retouch |

At final size these working crops land between 25 and 80 ppi, so the PDFs are proofs for approval, not files to plot.

Working files are desktop previews, not print files. Pull the full-size original from the Pexels
link for each ID before plotting — the record of what was used, and where it came from, is the
point of the table.

## Provisional

- The 400 mm panes are drawn in the middle of the doorway, against the meeting stile, with the
  500 mm panes at the two outer edges — as the client described the door. Confirm against the
  real leaves before cutting.
- The B monogram is a recreation, not BCM's official logo.
- The two help-line numbers (0771 240 104 / 0754 132 715) come off the clinic's own premises
  boards and print on the foot of every pane; confirm they are still current.
- Doors 1 and 2 use the same perforated film; door 3 is opaque vinyl and will not match it exactly.
Rebuild: `cd source && python3 bcm_doors.py 1`
