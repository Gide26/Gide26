# BCM Medical Centre — door 1

Eight panes on the first door, built from the client's own measurement rather than
from a photograph: four panes at **900 × 500 mm** and four at **900 × 400 mm**, all
900 mm high.

| Pane | Service | Glass (H × W) | Leaf · position |
| --- | --- | --- | --- |
| D1-P1 | Dental | 900 × 500 | left leaf · upper left |
| D1-P2 | Laboratory | 900 × 400 | left leaf · upper right |
| D1-P3 | Pharmacy | 900 × 500 | left leaf · lower left |
| D1-P4 | Physiotherapy | 900 × 400 | left leaf · lower right |
| D1-P5 | Reception | 900 × 500 | right leaf · upper left |
| D1-P6 | Paediatrics | 900 × 400 | right leaf · upper right |
| D1-P7 | Our Services | 900 × 500 | right leaf · lower left |
| D1-P8 | Antenatal | 900 × 400 | right leaf · lower right |

## Files

- `artwork/D1-P1…P8.pdf` — print files, pane + 10 mm bleed + 20 mm slug + crop marks
- `BCM-Door-1-Panels.pdf` — all eight pages in one file
- `docs/BCM-Door-1-Schedule.pdf` — schedule + measured layout diagram
- `docs/BCM-Door-1-Specification.pdf` — film, artwork setup, installation, open items
- `lookbook/M-01-door-1-day.png`, `M-02-door-1-night.png` — elevations
- `index.html` — web preview

## How the design adapts to the two widths

Every pane keeps one structure: white logo plate top-left, photograph full bleed,
navy caption band at the foot. Two things scale with the glass:

- **Service name** — cap height 13.5 % of pane width: 64 mm on the 500 mm panes,
  54 mm on the 400 mm panes. Same optical weight from the pavement.
- **Logo plate** — measured from its own type, then squeezed to fit, so the badge and
  wordmark land identically on all eight.

The slogan lives in the plate; at 400 mm wide there is no room for it twice.

## Provisional

- Column order is drawn as 500 mm left, 400 mm right on both leaves — confirm, or say
  if the second leaf is mirrored.
- The B monogram is a recreation.
- No telephone numbers appear — none supplied.
- Six photographs carry an AI colour retouch and are proof resolution only.

Rebuild: `cd source && python3 bcm_door1.py`
