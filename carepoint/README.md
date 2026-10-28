# CarePoint Medical Center — one-way vision film, Rev R2

Photographic service panels for the glazed entrance doors of CarePoint Medical Center,
Kampala. Eight panes across four 900 mm door leaves, printed on perforated one-way vision
film: the street reads a poster, the clinic still sees out.

**Provisional.** Pane sizes are scaled from a photograph of the client's own shopfront, and
the `cp` monogram is a vector recreation. Both must be replaced with measured dimensions and
the client's vector logo before anything is printed.

---

## What's here

| Path | What it is |
| --- | --- |
| `index.html` | Web preview — all eight panes, both elevations, licence table |
| `CarePoint-One-Way-Vision-R2.pdf` | All eight panes in one 8-page PDF, at print size |
| `artwork/CP-01…CP-08.pdf` | Individual print files: pane + 10 mm bleed + 20 mm slug with crop marks |
| `lookbook/CarePoint-One-Way-Vision-Lookbook.pdf` | 3-page lookbook — cover, the set, after dark + brand |
| `lookbook/mockups/` | Frontage elevations, day and night, at panel size |
| `docs/CP-01-Panel-Schedule.pdf` | 4 pages — schedule, pane detail, licence log, resolution audit |
| `docs/CP-02-Production-Specification.pdf` | 4 pages — film, artwork setup, installation, panel register |
| `web/` | Previews, mockup JPEGs, contact sheet, self-hosted fonts |

## The eight panes

| File | Service | Trim (mm) | Photograph | Position |
| --- | --- | --- | --- | --- |
| CP-01 | Dental | 810 × 1120 | PH-02 Andrea Piacquadio / Pexels 3952130 | Left inner leaf, upper |
| CP-02 | Paediatrics | 810 × 1120 | PH-03 Pavel Danilyuk / Pexels 5998457 | Right inner leaf, upper |
| CP-03 | Laboratory | 810 × 1120 | PH-05 Pavel Danilyuk / Pexels 8442574 | Right outer leaf, upper |
| CP-04 | Physiotherapy | 810 × 1180 | PH-04 Funkcinės Terapijos Centras / Pexels 20860597 | Left inner leaf, lower |
| CP-05 | Our services (directory) | 810 × 1180 | none — type only | Right inner leaf, lower |
| CP-06 | Pharmacy | 810 × 1120 | PH-06 cottonbro studio / Pexels 8657370 | Right outer leaf, lower |
| CP-07 | Antenatal | 810 × 1120 | PH-07 MART PRODUCTION / Pexels 7089304 | Left outer leaf, upper |
| CP-08 | Reception | 810 × 1120 | PH-01 Cedric Fauntleroy / Pexels 4269206 | Left outer leaf, lower |

Every image is Pexels Free licence — commercial use, modification and print permitted,
attribution not required (recorded anyway). All originals are 2667 px and up on the long
edge; effective ppi at final size is audited in the schedule — floor 75 ppi, target 100,
which is what perforated film can actually hold.

## Identity

Taken from the client's own fascia sign and existing boards — nothing invented:

- Navy `#16233F`, cyan `#2BA9E0`, mist `#E8EEF4`
- Slogan: *Your Health. Our Commitment.*
- TEL (+256) 078 474 7461 · 070 081 7054
- Services list transcribed from the client's directory board

Manrope (display) and Inter (text), both SIL Open Font Licence.

## Rebuilding

```sh
cd source
python3 cp_build_artwork.py   # carepoint/artwork/CP-01…08.pdf
python3 cp_mockup.py          # carepoint/lookbook/mockups/*.png
python3 cp_docs.py            # schedule + lookbook PDFs
python3 cp_spec.py            # production specification
python3 cp_site.py            # combined PDF, web previews, index.html
```

Palette and typography live in `cp_brand.py`, panels and copy in `cp_panels.py`, photograph
metadata and cropping in `cp_photos.py`, layout blocks in `cp_render.py`.

## Before release

1. Measure the glazing on site and re-issue every pane at measured size.
2. Substitute the client's vector logo for the recreation.
3. Relink the full-resolution originals and re-check each crop.
4. Replace the flagged printer values (1.6 mm hole / 2.3 mm pitch / ≈44 % open / 10 mm
   bleed) with the printer's own standard.
5. Proof on the actual film, not on paper.
