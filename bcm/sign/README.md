# BCM Medical Centre — sign post panel

Name only. No service list, no photograph.

**EDDWALIRO** — Luganda for hospital — heads the panel, above the badge: bold, cyan, at the
same cap height as the English name, so the panel reads in Luganda first and English second.
MEDICAL CENTRE keeps the widest line and the white ink, so it stays the headline.

**Trim: 1168.4 × 558.8 mm — the client's 46 in long × 22 in high, landscape.**
Revised on 2026-11-06 from 16 ft 7 in × 49 in, which itself replaced 4 ft × 2 ft
(1219.2 × 609.6 mm) and, before that, 3.10 × 2.11 ft. At 2.09 : 1 the approved lockup fills
the panel as it did on the 4 × 2 ft sample; the proportions, the type hierarchy and MEDICAL
CENTRE's widest line are unchanged.
Double-sided: both faces are in the one print PDF.

| File | What it is |
| --- | --- |
| `print/BCM-Sign-Post-BOTH-FACES-1168x559mm.pdf` | **Send this to the signwriter** — the sign post only, both faces, 1 : 1 in mm, 10 mm bleed, crop marks |
| `print/BCM-Sign-Post-FACE-A-1168x559mm.pdf` | Face A alone |
| `print/BCM-Sign-Post-FACE-B-1168x559mm.pdf` | Face B alone |
| `print/BCM-Sign-Post-OPTION-C-FASCIA-1168x559mm.pdf` | Spare: the fascia setting, one face |
| `print/READ-ME-FIRST.txt` | Trim, bleed, safe area, colour, plot-at-100 % note |
| `BCM-Sign-Post-Print-1168x559mm.zip` | All of the above in one zip |
| `artwork/BCM-Sign-Name-Only.pdf` | Print file, option A (centred stack) — two faces |
| `artwork/BCM-Sign-Name-Only-Option-C-Fascia.pdf` | Print file, option C (fascia setting) |
| `BCM-Sign-Panel.pdf` | 4 pages — panel to scale with dimensions, the two settings, on the post, specification |
| `lookbook/M-01-sign-day.png` | Day elevation, panel on two posts, to scale |
| `lookbook/M-02-sign-night.png` | Night elevation, if the panel is lit |
| `lookbook/M-03-sign-dimensions.png` | Dimensioned panel |
| `index.html` | Web preview |

## How the name is set

Reading down: **EDDWALIRO**, the badge, `BCM` small in cyan, then **MEDICAL CENTRE** at the
largest size the panel will take. The motto sits under the name and can be dropped.
EDDWALIRO is set bold and cyan so the Luganda word is read first; MEDICAL CENTRE is the
widest line.

At 16 ft 7 in (the previous size) the stacked lockup filled only about 41 % of the length —
its width is fixed by the name, its size by the height. At 46 × 22 in the panel is 2.09 : 1
again and the lockup fills it, so **option A is the face that ships**. Option C, the fascia
setting (badge left, name run beside it), is kept in the pack as a spare if the proportions
change again.

## Measurements

- Trim 1168.4 × 558.8 mm (46 in × 22 in at 25.4 mm to the inch; 3 ft 10 in × 1 ft 10 in)
- Bleed 10 mm all round → 1188.4 × 578.8 mm, plus a 22 mm slug at the foot → page 1188.4 × 600.8 mm
- Safe area 25 mm in from trim
- Both faces identical; print the two-page file once and turn the sheet
- Plot at 1 : 1. The file is drawn in millimetres; do not scale it, and leave the crop marks outside the bleed.

## Production — confirm with the signwriter, none of this is a quotation

- 3 mm aluminium composite (ACM), matte white, direct-to-substrate UV print or cast vinyl plus
  matte anti-glare laminate. Gloss will mirror the sky and kill the navy.
- Double-sided: two faces bonded back to back on one ACM core, or two panels on a frame.
- Edges cut back to trim and sealed, so no white edge shows.
- Fixing: proposal only — two 76 mm galvanised posts at 520 mm centres, set 600 mm into a
  concrete footing; panel centre 1500 mm above finished ground level. Stainless brackets
  behind the face — do not drill the printed face.

## Before plot

1. Check 46 × 22 in against the panel the signwriter is actually making.
2. The B monogram is a recreation, not BCM's official logo — supply the vector and it is a
   one-line swap in `source/bcm_brand.py`.
3. Wording: the clinic's own board reads Community **Health** Centre; this sign reads
   **BCM Medical Centre** as instructed.
4. Confirm the spelling EDDWALIRO before plot.
5. The help-line numbers (0771 240 104 / 0754 132 715) are off the clinic's premises boards;
   they can be added at the foot on request.

Rebuild: `cd source && python3 bcm_sign.py`
