# BCM Medical Centre — sign post panel

Name only. No service list, no photograph.

**EDDWALIRO** — Luganda for hospital — is set bold in cyan directly above MEDICAL CENTRE,
at the same cap height as the English name, so the panel reads in Luganda first and English
second. MEDICAL CENTRE keeps the widest line and the white ink, so it stays the headline.

**Trim: 944.9 × 643.1 mm — the client's 3.10 ft × 2.11 ft, landscape.**
Double-sided: both faces are in the one print PDF.

| File | What it is |
| --- | --- |
| `artwork/BCM-Sign-Name-Only.pdf` | Print file, option A (centred) — two faces, 1 : 1 in mm, 10 mm bleed, crop marks |
| `artwork/BCM-Sign-Name-Only-Option-B.pdf` | Print file, option B (badge-left lockup) |
| `BCM-Sign-Panel.pdf` | 4 pages — panel to scale with dimensions, the two options, on the post, specification |
| `lookbook/M-01-sign-day.png` | Day elevation, panel on two posts, to scale |
| `lookbook/M-02-sign-night.png` | Night elevation, if the panel is lit |
| `lookbook/M-03-sign-dimensions.png` | Dimensioned panel |
| `index.html` | Web preview |

## How the name is set

The badge, then `BCM` small in cyan, then **EDDWALIRO**, then **MEDICAL CENTRE** at the
largest size the panel will take — it spans the full measure of the panel, which is what
makes it pointable from across the road. The motto sits under the name and can be dropped.
EDDWALIRO is 592 mm wide at 12 mm tracking; MEDICAL CENTRE is 853 mm. Getting the Luganda
word bigger than the English one would mean shrinking the English name — say if you want
that, it is one number in `source/bcm_sign.py` (`ED_RATIO`).

## Measurements

- Trim 944.9 × 643.1 mm (3.10 ft × 2.11 ft at 304.8 mm to the foot)
- Bleed 10 mm all round → printed sheet 964.9 × 663.1 mm
- Safe area 25 mm in from trim
- Plot at 1 : 1. The file is drawn in millimetres; do not scale it.

## Production — confirm with the signwriter, none of this is a quotation

- 3 mm aluminium composite (ACM), matte white, direct-to-substrate UV print or cast vinyl
  plus matte anti-glare laminate. Gloss will mirror the sky and kill the navy.
- Double-sided: two faces bonded back to back on one ACM core, or two panels on a frame.
- Edges 3 mm radius, sealed; artwork is cut back to trim so no white edge shows.
- Fixing: two 76 mm galvanised posts at 520 mm centres, 600 mm into a concrete footing,
  panel centre 1500 mm above finished ground level. Stainless brackets behind the face —
  do not drill the printed face.

## Before plot

1. Check 3.10 × 2.11 ft against the panel the signwriter is actually making.
2. The B monogram is a recreation, not BCM's official logo — supply the vector and it is a
   one-line swap in `source/bcm_brand.py`.
3. Wording: the clinic's own board reads Community **Health** Centre; this sign reads
   **BCM Medical Centre** as instructed.
4. Confirm the spelling EDDWALIRO before plot.
5. The help-line numbers (0771 240 104 / 0754 132 715) are off the clinic's premises boards;
   they can be added at the foot on request.

Rebuild: `cd source && python3 bcm_sign.py`
