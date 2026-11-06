# BCM Medical Centre — the complete signage set

Everything in one folder: the three door film packages, the sign post panel and the
three roadside banners, with one master proof describing the lot.

**32 door panes · 1 sign post panel (2 faces) · 3 banners · 29 licensed photographs**

## What is where

| Folder | What it holds |
| --- | --- |
| `door-1/` `door-2/` `door-3/` | Eight panes each. Print files at 1 : 1 (900 × 500 and 900 × 400 mm), a panel proof, a schedule, a specification, day and night elevations, a licence record, a web preview |
| `sign/` | Name-only sign post panel, 1219.2 × 609.6 mm (4 ft × 2 ft), two lockups, four-page proof, elevations, dimensioned drawing |
| `banners/` | Three PVC banners — 3.8 m, 3.4 m, 2.4 m × 1.0 m — print files, six-page proof, fence elevations, licence page |
| `print/` | **One print PDF per piece** — 32 panes, 3 sign faces, 3 banners, numbered 01–38, with `PRINT-INDEX.pdf`, a manifest, `BCM-Print-Files-ALL.pdf` and `BCM-Print-Files.zip` |
| `complete/` | This README, the master proof, the manifest and the web index |

At the top of the folder: `BCM-Complete-Set.pdf` (master proof, nine pages),
`README.md`, `MANIFEST.csv`, `index.html`.

The per-group zips are deliberately left out — they hold the same files. Each group's own
page still offers one if you want to hand a single door to a single supplier.

## The identity, in one place

- Navy `#16233F`, cyan `#2BA9E0`, mist `#E8EEF4`.
- **EDDWALIRO** — Luganda for hospital — at the head of the sign post and every banner,
  bold, cyan, same cap height as the English name.
- Then the badge and `BCM` (small, cyan), then **MEDICAL CENTRE** as the widest line in
  white — the line people point at — then the motto *We listen. We treat. We care.*
- Door panes use the white plate: badge top-left over the photograph, MEDICAL CENTRE
  spanning the plate, service name in the navy caption band at the foot.
- The B monogram is a **recreation**, not BCM's official logo.

## Who gets what

| Supplier | Send | Files |
| --- | --- | --- |
| One-way vision printer | `print/` jobs 01–24 | one PDF per pane, pane + 10 mm bleed |
| Signwriter | `print/` jobs 25–27 | one PDF per sign face (A face A, A face B, B face A) |
| Banner printer | `print/` jobs 28–30 | one PDF per banner, 60 mm hem-safe |

The same files also sit inside each group folder (`door-1/artwork/`, `sign/artwork/`,
`banners/artwork/`) with the group's proof and paperwork; `print/` is just the print
files on their own, numbered in running order.

## Before anything is plotted

1. The official logo vector. The monogram is a recreation.
2. Confirmation of the spelling **EDDWALIRO**.
3. The sign post measurement, checked against the panel being made.
4. The photographs: working files are 843–1264 px — approve the look, then repeat the
   retouch on the Pexels originals, or photograph the clinic's own team.
5. Each doorway measured on site: 900 mm high panes, 500 mm outer, 400 mm at the stile.

## Rebuild

```sh
cd source
python3 bcm_doors.py      # all doors
python3 bcm_sign.py       # sign post panel
python3 bcm_banners.py    # three banners
python3 bcm_master.py     # this set: master proof, manifest, README, zip
```

Preview locally: `python3 -m http.server 8000 --directory bcm` and open
`http://localhost:8000/`.
