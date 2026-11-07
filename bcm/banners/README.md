# BCM Medical Centre — roadside banners

Three banners, three different layouts, one identity. On a fence, PVC with eyelets.

**All three were re-measured on 2026-11-07 to 16 ft × 49 in (4876.8 × 1244.6 mm)**, as the
client gave them. Each layout is derived from the panel rather than from fixed offsets: the
photographs take their crops from the clear height, and the type takes the rest, so the same code
holds at any size and the three read as one set. At 4.88 m each banner is more than twice a
doorway wide, so on the premises they run as one band above the shopfront rather than one per
door.

| ID | Size | Trim | Job | Layout |
| --- | --- | --- | --- | --- |
| **B-1** | 16 ft × 49 in | 4876.8 × 1244.6 mm | Read at speed, from the road | Photograph left, the name and list right |
| **B-2** | 16 ft × 49 in | 4876.8 × 1244.6 mm | Read standing at the gate | Type left, two photographs stacked right |
| **B-3** | 16 ft × 49 in | 4876.8 × 1244.6 mm | The long run along the fence | The name centred in its column and as large as it will go, one photograph at the right hand end |

Every banner carries, in this order: **EDDWALIRO** (cyan, bold, at the head) → the badge and
`BCM` → **MEDICAL CENTRE** (the widest line, in white) → the motto → a service list from the
clinic's own board → the two premises numbers → *Open 24 hours*.

## Files

| File | What it is |
| --- | --- |
| `artwork/BCM-Banner-B-1.pdf` | Print file, 1 : 1 mm, 10 mm bleed, crop marks, 60 mm hem/eyelet safe |
| `artwork/BCM-Banner-B-2.pdf` | Print file, same setup |
| `artwork/BCM-Banner-B-3.pdf` | Print file, same setup |
| `BCM-Banners.pdf` | Six pages — the set, each banner to scale with its photograph resolutions, production spec with a sizes table, photographs and licence |
| `lookbook/M-00-banner-set.png` | All three on a fence, one frame width, to compare |
| `lookbook/M-B-0N-day.png` / `-night.png` | Each banner on the fence, day and night |
| `index.html` | Web preview |

## Production — proposals, confirm with the printer

- 510 g/m² PVC, matte, 720–1440 dpi.
- 40 mm welded hem all round, eyelets at 500 mm centres; the artwork keeps 60 mm clear of
  the trim so nothing is hemmed or eyeletted away.
- Fix **every** eyelet. A 4.9 m banner sails in wind; four tie-off points will tear the corners.
- Bottom edge on the fence set at 1150 mm above ground in the elevations — check it against
  the actual fence.

## Photographs

Four licensed Pexels frames, all colour-retouched so the people read Black African, all
recorded with asset, creator and licence on page 6 of the proof. The people are models, not
BCM staff or patients. Working files are web resolution (843–1264 px): right for approval
and for the elevations, not for a 4.9 m print. Before print either repeat the retouch on the
full-resolution originals (Pexels links on page 6) or photograph the clinic's own team.

No photograph repeats across the three banners, and no service appears on two banners.

## Rebuild

```sh
cd source
python3 bcm_banners.py     # three print files, proof, elevations, web page
```
