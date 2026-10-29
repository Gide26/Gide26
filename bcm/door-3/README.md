# BACTIMED Community Medical Centre — door 3

Eight panes on the third doorway, built from the client's own measurement rather
than from a photograph: four panes at **900 × 500 mm** and four at **900 × 400 mm**, all 900 mm
high. The geometry is identical on all three doors; only the subject matter and the film change.

Opaque white blockout vinyl — nothing shows through, and the print carries full detail because there is no mesh over it.

| Pane | Service | Glass (H × W) | Photograph | Leaf · position |
| --- | --- | --- | --- | --- |
| D3-P1 | Antenatal & Postnatal | 900 × 500 | PH-26 OB-GYN beside the ultrasound machine, scan on the monitor | left leaf · upper left |
| D3-P2 | Eye Services | 900 × 400 | PH-29 Eye examination on a vision testing instrument | left leaf · upper right |
| D3-P3 | Paediatrics | 900 × 500 | PH-03 Paediatrician examining a child with a stethoscope | left leaf · lower left |
| D3-P4 | Ent | 900 × 400 | PH-30 Otoscope examination of an ear | left leaf · lower right |
| D3-P5 | Minor Surgery | 900 × 500 | PH-22 Surgical tools arranged on a sterile surface | right leaf · upper left |
| D3-P6 | Ultrasound | 900 × 400 | PH-25 Clinician operating an ultrasound scanner in a clinic room | right leaf · upper right |
| D3-P7 | Our Services | 900 × 500 | none — type only | right leaf · lower left |
| D3-P8 | Inpatient Care | 900 × 400 | PH-31 Inpatient beds in a hospital room | right leaf · lower right |

Seven different photographs and one type-only directory. No image on this door appears on either
of the other two.

## Files

- `artwork/D3-P1…P8.pdf` — print files, pane + 10 mm bleed + 20 mm slug + crop marks
- `BCM-Door-3-Panels.pdf` — all eight pages in one file
- `docs/BCM-Door-3-Schedule.pdf` — schedule + measured layout diagram
- `docs/BCM-Door-3-Specification.pdf` — film, artwork setup, installation, open items
- `lookbook/M-01-door-3-day.png`, `M-02-door-3-night.png` — elevations
- `index.html` — web preview

## Photography

All photographs are Pexels Free licence, checked 29 October 2026: free commercial use, no
attribution required, modification allowed. The ones carrying an AI colour retouch so the people
reflect the community BACTIMED serves are marked in the table below; the people in those frames are
models, never staff or patients, and no pane captions them as such.

| Asset | Pexels ID | Creator | Pexels original | Working file | Retouch |
| --- | --- | --- | --- | --- | --- |
| PH-26 | 7089394 | MART PRODUCTION | 3982 × 5973 px | 843 × 1264 px | yes — colour retouch |
| PH-29 | 6749698 | Antoni Shkraba | 5917 × 3945 px | 1264 × 842 px | yes — colour retouch |
| PH-03 | 5998457 | Pavel Danilyuk | 4016 × 6016 px | 844 × 1264 px | yes — colour retouch |
| PH-30 | 5206951 | Karola G | 6720 × 4480 px | 1264 × 842 px | yes — colour retouch |
| PH-22 | 7108125 | Pavel Danilyuk | 3654 × 5473 px | 500 × 749 px | no |
| PH-25 | 7089041 | MART PRODUCTION | 3949 × 5923 px | 843 × 1264 px | yes — colour retouch |
| PH-31 | 39128512 | Maxx Sas | 2510 × 4032 px | 500 × 803 px | no |

At final size these working crops land between 25 and 80 ppi, so the PDFs are proofs for approval, not files to plot.

Working files are desktop previews, not print files. Pull the full-size original from the Pexels
link for each ID before plotting — the record of what was used, and where it came from, is the
point of the table.

## Provisional

- Column order is drawn as 500 mm left, 400 mm right on both leaves — confirm, or say if the
  second leaf is mirrored.
- The B monogram is a recreation, not BCM's official logo.
- The two help-line numbers (0771 240 104 / 0754 132 715) come off the clinic's own premises
  boards and print on the foot of every pane; confirm they are still current.
- Opaque film blocks the view through the glass, in and out; confirm that is wanted on this door.
- The night elevation assumes the door is lit from the street and the fascia: an opaque pane cannot be backlit.
Rebuild: `cd source && python3 bcm_doors.py 3`
