# BCM Medical Centre — banner, 46 × 22 in

One banner in the sign post's own setting: **1168.4 × 558.8 mm (46 × 22 in,
3 ft 10 in × 1 ft 10 in)**, landscape, PVC on a fence.

Same measurement, same colours and the same band arrangement as the panel going into the
lighting board:

1. white band: `BCM`
2. navy band (`#16233F`): `MEDICAL CENTRE` in white
3. red block (`#ED1B24`), full width: `EDDWALIRO` knocked out in white
4. white row: an arrow at each end, `Open` and `24 Hrs` in red between them
5. navy foot strip: `TEL 0788 323 815 · 0754 132 715` left, `BUSSABALA` right

No motto, no photograph, no service list — the sign's message, on the fence.

What differs from the sign is only what the piece is: a banner carries a **25 mm
welded hem** and **eyelets at 300 mm centres**, so all the type stays
**45 mm clear of the trim** instead of running to the edge the way the panel does.

| File | What it is |
| --- | --- |
| `print/BCM-Banner-1168x559mm-EXACT.pdf` | **Exactly 46 × 22 in** — page = trim, no bleed. The file that measures the banner. |
| `print/BCM-Banner-1168x559mm-BLEED.pdf` | Trim + 10 mm bleed + 20 mm slug + crop marks — page 1188 × 599 mm, larger on purpose |
| `print/READ-ME-FIRST.txt` | The printer's note: sizes, hem, eyelets, colours |
| `BCM-Banner.pdf` | Two pages — the banner to scale with dimensions, then the eyelet and hem plan |
| `lookbook/M-01-banner-day.png` | The banner flat, with its eyelets |
| `lookbook/M-02-banner-dimensions.png` | The same, dimensioned |
| `index.html` | Web preview |
| `BCM-Banner-Package.zip` | Everything above in one zip |

## Production — confirm with the printer, none of this is a quotation

- PVC banner 510 g, matte, printed at 1 : 1. Plot at 100 %; do not scale.
- 25 mm welded hem all round; eyelets at 300 mm centres including
  every corner.
- Fix at every eyelet: a banner this size sails in wind if it is tied at every second hole.
- The red is the sign's `#ED1B24`; hold it to the same reference as the light box so the
  fence and the board match in daylight.

## Before plot

1. Check 46 × 22 in against the fence run it is going on.
2. Confirm the branch line reads **`BUSSABALA`** and the numbers are
   **0788 323 815 · 0754 132 715**.
3. Confirm the eyelet pitch with the installer — 300 mm is
   industry-typical, not measured.

Rebuild: `cd source && python3 bcm_banner_46.py`
