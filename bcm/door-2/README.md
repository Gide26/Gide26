# BACTIMED Community Medical Centre — door 2

Eight panes on the second doorway, built from the client's own measurement rather
than from a photograph: four panes at **900 × 500 mm** and four at **900 × 400 mm**, all 900 mm
high. The geometry is identical on all three doors; only the subject matter and the film change.

Perforated one-way vision vinyl — you can see out through the print from inside.

| Pane | Service | Glass (H × W) | Photograph | Leaf · position |
| --- | --- | --- | --- | --- |
| D2-P1 | Welcome | 900 × 500 | PH-01 Receptionist assisting a patient at a modern reception desk | left leaf · upper left |
| D2-P2 | Minor Surgery | 900 × 400 | PH-14 Surgical instruments laid out on a sterile table | left leaf · upper right |
| D2-P3 | Obs & Gyn | 900 × 500 | PH-19 Doctor consulting a pregnant patient | left leaf · lower left |
| D2-P4 | General Outpatient | 900 × 400 | PH-12 Nurse taking a blood pressure reading with a digital monitor | left leaf · lower right |
| D2-P5 | Immunisation | 900 × 500 | PH-32 A child receiving a vaccination shot, held by a parent | right leaf · upper left |
| D2-P6 | Pharmacy | 900 × 400 | PH-27 Pharmacist handing dispensed medicine across the counter | right leaf · upper right |
| D2-P7 | Our Services | 900 × 500 | none — type only | right leaf · lower left |
| D2-P8 | HIV Care | 900 × 400 | PH-18 Hands preparing a rapid test kit on a white table | right leaf · lower right |

Seven different photographs and one type-only directory. No image on this door appears on either
of the other two.

## Files

- `artwork/D2-P1…P8.pdf` — print files, pane + 10 mm bleed + 20 mm slug + crop marks
- `BCM-Door-2-Panels.pdf` — all eight pages in one file
- `docs/BCM-Door-2-Schedule.pdf` — schedule + measured layout diagram
- `docs/BCM-Door-2-Specification.pdf` — film, artwork setup, installation, open items
- `lookbook/M-01-door-2-day.png`, `M-02-door-2-night.png` — elevations
- `index.html` — web preview

## Photography

All photographs are Pexels Free licence, checked 29 October 2026: free commercial use, no
attribution required, modification allowed. The ones carrying an AI colour retouch so the people
reflect the community BACTIMED serves are marked in the table below; the people in those frames are
models, never staff or patients, and no pane captions them as such.

| Asset | Pexels ID | Creator | Pexels original | Working file | Retouch |
| --- | --- | --- | --- | --- | --- |
| PH-01 | 4269206 | Cedric Fauntleroy | 5474 × 8211 px | 843 × 1264 px | yes — colour retouch |
| PH-14 | 6291179 | Anna Shvets | 3835 × 5752 px | 500 × 750 px | no |
| PH-19 | 7089401 | MART PRODUCTION | 6000 × 4000 px | 1264 × 842 px | yes — colour retouch |
| PH-12 | 5721672 | cottonbro studio | 4132 × 6198 px | 500 × 750 px | no |
| PH-32 | 20471645 | CP Khanal | 4000 × 3000 px | 1195 × 896 px | yes — colour retouch |
| PH-27 | 8657359 | cottonbro studio | 6091 × 4061 px | 1264 × 842 px | yes — colour retouch |
| PH-18 | 5712679 | cottonbro studio | 5929 × 3953 px | 1264 × 842 px | yes — colour retouch |

At final size these working crops land between 31 and 80 ppi, so the PDFs are proofs for approval, not files to plot.

Working files are desktop previews, not print files. Pull the full-size original from the Pexels
link for each ID before plotting — the record of what was used, and where it came from, is the
point of the table.

## Provisional

- Column order is drawn as 500 mm left, 400 mm right on both leaves — confirm, or say if the
  second leaf is mirrored.
- The B monogram is a recreation, not BCM's official logo.
- The two help-line numbers (0771 240 104 / 0754 132 715) come off the clinic's own premises
  boards and print on the foot of every pane; confirm they are still current.
- Doors 1 and 2 use the same perforated film; door 3 is opaque vinyl and will not match it exactly.
Rebuild: `cd source && python3 bcm_doors.py 2`
