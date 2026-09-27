# Shoot Like a Pro With Your Phone

A free, picture-illustrated tutorial on taking better **photos and videos with a phone** — for complete beginners through to hobbyists.

Open `index.html` in any browser, or publish it with GitHub Pages (see below).

**Printable edition:** [`shoot-like-a-pro-with-your-phone.pdf`](shoot-like-a-pro-with-your-phone.pdf) (A4, ~36 pages) — the same content laid out for printing and sharing on WhatsApp/email.

**🇫🇷 En français :** [`fr/index.html`](fr/) (site) et [`fr/photographier-comme-un-pro-avec-votre-telephone.pdf`](fr/photographier-comme-un-pro-avec-votre-telephone.pdf) (PDF imprimable). Both pages link to each other through the **FR / EN** button in the top bar.

## What's inside

| # | Chapter | Covers |
|---|---------|--------|
| 01 | Know your camera | Cleaning the lens, the two-hand grip, tap-to-focus & exposure slider, AE/AF lock, grid, zoom vs. moving your feet, vertical vs. horizontal, what each camera mode is for |
| 02 | Light is everything | Golden hour (with Kampala sunrise/sunset times), light direction (front / side / back), harsh sun vs. open shade, window light, night |
| 03 | Composition | Rule of thirds (interactive grid toggle), leading lines, framing, symmetry, negative space, fill the frame, foreground/middle/background layers, cleaning up backgrounds |
| 04 | Camera angles | Eye level, low, high, bird's eye, worm's eye, Dutch tilt, over-the-shoulder, POV, macro, reflections, shooting through objects — each with a position diagram, effect, uses and how-to |
| 05 | Photographing people | Distance & lens choice, portrait mode, posing basics, groups, selfies |
| 06 | Video techniques | Resolution & frame-rate settings (incl. 25 fps for 50 Hz lighting), locking focus/exposure, the "ninja walk", shot sizes, the 3-shot rule, pan/tilt/push/truck/orbit/boom, in-camera transitions, audio, slow-mo/time-lapse/hyperlapse, lighting for video |
| 07 | Editing basics | Five-step edit with a before/after slider, apps, video editing habits |
| 08 | Cheat sheet | One-screen, printable summary |
| 09 | 7-day practice plan | A daily exercise for a week |

## Structure

```
docs/
├── index.html      # the whole tutorial (single page, inline SVG diagrams)
├── css/style.css   # styles, responsive layout, print stylesheet
├── js/main.js      # progress bar, table of contents, lightbox, grid toggle, before/after slider
├── images/         # photo illustrations (optimised JPEGs)
├── shoot-like-a-pro-with-your-phone.pdf   # print edition, generated from index.html
├── fr/index.html                          # French edition, generated from index.html + tools/i18n/fr.txt
├── fr/photographier-comme-un-pro-avec-votre-telephone.pdf
├── tools/build_pdf.py                     # regenerates a PDF from a page
├── tools/i18n.py                          # extracts / applies translations
└── tools/i18n/                            # en.txt (reference segments) and fr.txt (French strings)
```

## Translations

`index.html` is the single source of truth. The French page is generated from it, so a change to the
English text only needs a matching change in `tools/i18n/fr.txt`:

```bash
python3 docs/tools/i18n.py extract           # refresh docs/tools/i18n/en.txt (numbered English segments)
# edit docs/tools/i18n/fr.txt  (same @numbers, French text; HTML tags inside a segment are kept)
python3 docs/tools/i18n.py apply --lang fr   # -> docs/fr/index.html (reports untranslated / changed segments)
python3 docs/tools/build_pdf.py --html docs/fr/index.html   # -> the French PDF
```

Diagrams, layout, scripts and images are shared between languages; only the text differs.
Adding another language means adding an entry to `LANG` in `tools/i18n.py`, a `<lang>.txt`
file, and a strings block in `tools/build_pdf.py`.

## Rebuilding the PDF

The PDF is generated from `index.html`, so edit the web page and rebuild:

```bash
pip install reportlab beautifulsoup4 pillow resvg-py
python3 docs/tools/build_pdf.py
```

Fonts (Lato, DM Serif Display — both SIL Open Font Licence) are fetched once into `docs/tools/.fonts/` using the GitHub CLI; DejaVu Sans is used if they are unavailable. Example photos that are still placeholders are left out of the PDF automatically (pass `--keep-placeholders` to include them).

No build step and no dependencies — plain HTML, CSS and JavaScript.

## Publish with GitHub Pages

1. On GitHub open **Settings → Pages**.
2. Under *Build and deployment* choose **Deploy from a branch**.
3. Select the branch and the **`/docs`** folder, then save.

The tutorial will be live at `https://gide26.github.io/Gide26/` a minute or two later.

## Images

Photos in `images/` were generated specifically for this guide (no stock-photo licences to worry about). Some example photos are still placeholders (grey cards labelled *"example photo coming soon"*) and will be replaced as they are generated. To swap any image, keep the same file name and drop the new file into `images/`.

Diagrams are inline SVG in `index.html`, styled from `css/style.css`, so they stay crisp at any size and can be edited as text.
