# BCM Medical Centre — sign post panel, for a lighting board

Name only. No service list, no photograph, no monogram.

**The board lights the sign, so the words do the shouting.** The face is a plain white field
with every word in bright red `#ED1B24`, set as large as a 46 × 22 in panel will carry:
`EDDWALIRO` edge to edge, `BCM` between, `MEDICAL CENTRE` edge to edge, a short red rule, the
motto in the same red a shade deeper. No second colour, no dense field.

Why white and not a colour: a lit face reads evenly when there is little ink on it. White is
the field the tubes light most cleanly, so the panel glows quietly from end to end and the red
lettering is what carries — from across the road, lit or not.

Type sizes on the shipped face (1168.4 × 558.8 mm):

| Line | Cap height | How it is set |
| --- | --- | --- |
| EDDWALIRO | 128.7 mm | full measure, red, tight tracking |
| BCM | 35.8 mm | centred under it, red |
| MEDICAL CENTRE | 89.4 mm | full measure, red |
| motto | 12.1 mm | deep red, under a short rule |

**Trim: 1168.4 × 558.8 mm — the client's 46 in long × 22 in high, landscape.**
Revised on 2026-11-06 from 16 ft 7 in × 49 in, which itself replaced 4 ft × 2 ft
(1219.2 × 609.6 mm) and 3.10 × 2.11 ft. Double-sided: both faces are in the one print PDF and
are identical.

| File | What it is |
| --- | --- |
| `print/BCM-Sign-Post-RED-BOTH-FACES-1168x559mm.pdf` | **Send this to the signwriter** — the sign post only, both faces, 1 : 1 in mm, 10 mm bleed, crop marks |
| `print/BCM-Sign-Post-RED-FACE-A-1168x559mm.pdf` | Face A alone |
| `print/BCM-Sign-Post-RED-FACE-B-1168x559mm.pdf` | Face B alone |
| `print/BCM-Sign-Post-SPARE-CYAN-FIELD-1168x559mm.pdf` | The earlier cyan field at the same type size — spare |
| `print/READ-ME-FIRST.txt` | Trim, bleed, safe area, backlit media, the red-in-a-light-box note |
| `BCM-Sign-Post-Print-1168x559mm.zip` | All of the above in one zip |
| `artwork/BCM-Sign-Name-Only-Red.pdf` | Print file, red on white, both faces |
| `artwork/BCM-Sign-Name-Only-Spare-Cyan.pdf` | Print file, cyan field, spare |
| `BCM-Sign-Panel.pdf` | 4 pages — the face to scale with dimensions, the three faces side by side, on the post, specification |
| `lookbook/M-01-sign-day.png` | Day elevation, panel on two posts, to scale |
| `lookbook/M-02-sign-night.png` | Night elevation, lit — what it looks like after dark |
| `lookbook/M-03-sign-dimensions.png` | Dimensioned panel |
| `index.html` | Web preview |

## Measurements

- Trim 1168.4 × 558.8 mm (46 in × 22 in at 25.4 mm to the inch; 3 ft 10 in × 1 ft 10 in)
- Bleed 10 mm all round → 1188.4 × 578.8 mm, plus a 22 mm slug at the foot → page 1188.4 × 600.8 mm
- Safe area 25 mm in from trim
- Both faces identical; print the two-page file once and turn the sheet
- Plot at 1 : 1. The file is drawn in millimetres; do not scale it.

## Production — confirm with the signwriter, none of this is a quotation

- **Backlit-grade face.** Translucent diffusing acrylic or backlit film for the box's own
  face, or backlit banner media if the box takes a soft face. Not vinyl on opaque composite —
  that blocks the light.
- **Red is the colour to watch.** `#ED1B24` bleeds slightly into white when it is lit from
  behind: letter edges soften and the red can warm towards orange. Hold it as a flat spot
  colour if the process allows, keep the tube close behind the face and even, and check a lit
  sample before the full run.
- Print the white field as one solid, even coat — no gradient, no vignette.
- Double-sided: the artwork is identical on both faces, so the same file prints twice.
- **The face fits the box's aperture, not its outer frame.** The visible opening should be the
  trim size above, or the rebate will crop the lettering.
- Panel centre 1500 mm above finished ground level is a proposal — check it against the box and
  the kerb line.
- If it also stands on posts rather than in the box: two 76 mm galvanised posts at 520 mm
  centres, 600 mm into concrete, is the industry-typical proposal.

## Before plot

1. Check 46 × 22 in against the box's aperture.
2. Get a lit sample of the red before the full run.
3. Confirm the spelling EDDWALIRO before plot.
4. The help-line numbers (0771 240 104 / 0754 132 715) are off the clinic's premises boards;
   they can be added at the foot on request.

If the red is too loud, say so: the same layout can be set in the clinic's cyan `#2BA9E0` at
the same size, and the cyan field spare is already in the pack.

Rebuild: `cd source && python3 bcm_sign.py`
