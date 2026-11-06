# BCM Medical Centre — sign post panel

Name only. No service list, no photograph.

**EDDWALIRO** — Luganda for hospital — heads the panel, above the badge: bold, cyan, at the
same cap height as the English name, so the panel reads in Luganda first and English second.
MEDICAL CENTRE keeps the widest line and the white ink, so it stays the headline.

**Trim: 5054.6 × 1244.6 mm — the client's 16 ft 7 in long × 49 in high, landscape.**
Revised on 2026-11-06 from 4 ft × 2 ft (1219.2 × 609.6 mm), which itself replaced
3.10 × 2.11 ft. The approved lockup is still scaled proportionally, so the type hierarchy
and MEDICAL CENTRE's widest line are unchanged; at 4:1 the setting sits centred with wide
navy margins either side.
Double-sided: both faces are in the one print PDF.

| File | What it is |
| --- | --- |
| `print/BCM-Sign-Post-BOTH-FACES-5055x1245mm.pdf` | **Send this to the signwriter** — the sign post only, both faces, 1 : 1 in mm, 10 mm bleed, crop marks |
| `print/BCM-Sign-Post-FACE-A-5055x1245mm.pdf` | Face A alone |
| `print/BCM-Sign-Post-FACE-B-5055x1245mm.pdf` | Face B alone |
| `print/BCM-Sign-Post-OPTION-C-FASCIA-5055x1245mm.pdf` | Spare: the fascia setting, one face |
| `print/READ-ME-FIRST.txt` | Trim, bleed, safe area, colour, plot-at-100 % note |
| `BCM-Sign-Post-Print-5055x1245mm.zip` | All of the above in one zip (145 KB) |
| `artwork/BCM-Sign-Name-Only.pdf` | Print file, option A (centred stack) — two faces |
| `artwork/BCM-Sign-Name-Only-Option-C-Fascia.pdf` | Print file, option C (fascia setting) |
| `BCM-Sign-Panel.pdf` | 4 pages — panel to scale with dimensions, the three settings, on the post, specification |
| `lookbook/M-01-sign-day.png` | Day elevation, panel on four posts, to scale |
| `lookbook/M-02-sign-night.png` | Night elevation, if the panel is lit |
| `lookbook/M-03-sign-dimensions.png` | Dimensioned panel |
| `index.html` | Web preview |

## How the name is set

Reading down: **EDDWALIRO**, the badge, `BCM` small in cyan, then **MEDICAL CENTRE** at the
largest size the panel will take. The motto sits under the name and can be dropped.
EDDWALIRO is set bold and cyan so the Luganda word is read first; MEDICAL CENTRE is the
widest line.

At 16 ft 7 in the stacked lockup can only fill about 41 % of the length — its width is fixed
by the name, its size by the height. The panel is therefore mostly navy either side. That is
correct for this proportion and is what the print files carry. **Option C** is the
alternative if the client prefers the length used: the same elements turned on their side,
badge at the left, `EDDWALIRO` / `MEDICAL CENTRE` / motto run beside it, so the name is about
four times the size. It is supplied as a spare, not as the approved setting.

## Measurements

- Trim 5054.6 × 1244.6 mm (16 ft 7 in = 199 in long, 49 in high; 25.4 mm to the inch)
- Bleed 10 mm all round → 5074.6 × 1264.6 mm, plus a 22 mm slug at the foot → page 5074.6 × 1286.6 mm
- Safe area 25 mm in from trim
- Both faces identical; print the two-page file once and turn the sheet
- Plot at 1 : 1. The file is drawn in millimetres; do not scale it.

**The page is deliberately at full size and close to the PDF limit.** A PDF page cannot
exceed 5080 mm and this sheet is 5074.6 mm wide: there is no margin around the artwork to
add anything to, and the file must not be rescaled. If the plotter cannot take a 5.07 m
sheet, ask for a seamed or half-size version rather than scaling this one — a rescale changes
the stroke weights the type was set for.

## Production — confirm with the signwriter, none of this is a quotation

- The face is about 6.29 m². 3 mm aluminium composite (ACM) over a 5 m span is marginal:
  propose 4 mm ACM, or 3 mm ACM on a rail frame. Matte white core, direct-to-substrate UV
  print or cast vinyl plus matte anti-glare laminate. Gloss will mirror the sky and kill
  the navy.
- Double-sided: two faces bonded back to back on one frame, or two panels on a frame.
- Edges cut back to trim and sealed, so no white edge shows.
- Roughly 25 kg of 4 mm sheet before the frame.
- Fixing: proposal only — four galvanised posts, or a rail/cleat frame carrying the panel
  across four posts; panel centre 1500 mm above finished ground level. Stainless brackets
  behind the face — do not drill the printed face. 6.29 m² is a real sail: the footings,
  post gauge and brackets need the signwriter's own wind calculation for the site.

## Before plot

1. Check 16 ft 7 in × 49 in against the panel the signwriter is actually making.
2. The B monogram is a recreation, not BCM's official logo — supply the vector and it is a
   one-line swap in `source/bcm_brand.py`.
3. Wording: the clinic's own board reads Community **Health** Centre; this sign reads
   **BCM Medical Centre** as instructed.
4. Confirm the spelling EDDWALIRO before plot.
5. The help-line numbers (0771 240 104 / 0754 132 715) are off the clinic's premises boards;
   they can be added at the foot on request.

Rebuild: `cd source && python3 bcm_sign.py`
