"""Web preview + combined PDF for the CarePoint set."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
import pypdfium2 as pdfium
from pypdf import PdfWriter, PdfReader

import cp_brand as B
import cp_panels as PN
import cp_photos as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "carepoint")
ART = os.path.join(BASE, "artwork")
WEB = os.path.join(BASE, "web")

PLACEMENT = {"CP-01": "Left inner leaf · upper", "CP-04": "Left inner leaf · lower",
             "CP-02": "Right inner leaf · upper", "CP-05": "Right inner leaf · lower",
             "CP-03": "Right outer leaf · upper", "CP-06": "Right outer leaf · lower",
             "CP-07": "Left outer leaf · upper", "CP-08": "Left outer leaf · lower"}
ROLE = {"CP-01": "Dental suite", "CP-02": "Children's clinic", "CP-03": "Laboratory",
        "CP-04": "Physiotherapy", "CP-05": "Directory", "CP-06": "Pharmacy",
        "CP-07": "Antenatal", "CP-08": "Reception"}


def previews():
    os.makedirs(WEB, exist_ok=True)
    out = []
    for p in PN.PANELS:
        pdf = os.path.join(ART, f"{p['id']}.pdf")
        doc = pdfium.PdfDocument(pdf)
        page = doc[0]
        w_pt, h_pt = page.get_size()
        scale = 1000 / w_pt
        img = page.render(scale=scale).to_pil().convert("RGB")
        thumb = os.path.join(WEB, f"{p['id']}.jpg")
        img.save(thumb, "JPEG", quality=88, optimize=True)
        out.append(thumb)
        doc.close()
    # contact sheet
    cols, cell_w = 4, 360
    ratio = PN.UPPER_H / PN.UPPER_W if hasattr(PN, "UPPER_W") else 1120 / 810
    cell_h = int(cell_w * 1.45)
    sheet = Image.new("RGB", (cols * cell_w + 60, 2 * cell_h + 90), (244, 247, 249))
    for i, p in enumerate(PN.PANELS):
        im = Image.open(os.path.join(WEB, f"{p['id']}.jpg"))
        im.thumbnail((cell_w - 20, cell_h - 20), Image.LANCZOS)
        x = 20 + (i % cols) * cell_w + (cell_w - 20 - im.width) // 2
        y = 20 + (i // cols) * cell_h + (cell_h - 20 - im.height) // 2
        sheet.paste(im, (x, y))
    sheet.save(os.path.join(WEB, "contact-sheet.jpg"), "JPEG", quality=90)
    return out


def combined():
    path = os.path.join(BASE, "CarePoint-One-Way-Vision-R2.pdf")
    w = PdfWriter()
    for p in PN.PANELS:
        r = PdfReader(os.path.join(ART, f"{p['id']}.pdf"))
        for pg in r.pages:
            w.add_page(pg)
    with open(path, "wb") as fh:
        w.write(fh)
    return path


def html():
    cards = []
    for p in PN.PANELS:
        ph = P.PHOTOS[p["photo"]] if p["photo"] else None
        credit = (f'{ph["asset"]} · {ph["creator"]} / Pexels · {ph["px"][0]:,}×{ph["px"][1]:,}px'
                  if ph else "No photograph — typographic pane")
        cards.append(f"""
      <article class="card">
        <a class="shot" href="artwork/{p['id']}.pdf">
          <img src="web/{p['id']}.jpg" alt="{p['service']} panel, CarePoint one-way vision film"
               loading="lazy">
        </a>
        <div class="meta">
          <div class="row"><span class="id">{p['id']}</span><span class="pos">{PLACEMENT[p['id']]}</span></div>
          <h3>{p['service']}</h3>
          <p class="sub">{p['sub']}</p>
          <p class="dim">{p['w']} × {p['h']} mm &nbsp;·&nbsp; {p['aspect']}</p>
          <p class="credit">{credit}</p>
        </div>
      </article>""")

    lic_rows = []
    usage = {}
    for p in PN.PANELS:
        if p["photo"]:
            usage.setdefault(p["photo"], []).append(p["id"])
    for key, m in P.PHOTOS.items():
        lic_rows.append(f"""        <tr>
          <td class="mono">{m['asset']}</td>
          <td>{', '.join(usage.get(key, ['—']))}</td>
          <td>{m['title']}</td>
          <td>{m['creator']}</td>
          <td><a href="{m['url']}">Pexels {m['id']}</a></td>
          <td class="mono">{m['px'][0]:,} × {m['px'][1]:,}</td>
          <td>Free licence, checked 28 Oct 2026</td>
        </tr>""")

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CarePoint Medical Center — one-way vision film, Rev R2</title>
<link rel="stylesheet" href="web/style.css">
</head>
<body>
<header class="hero">
  <div class="lockup">
    <img src="web/logo.png" alt="CarePoint monogram" width="52" height="52">
    <div>
      <div class="wordmark">CAREPOINT</div>
      <div class="tagline">MEDICAL CENTER</div>
    </div>
  </div>
  <p class="kicker">GLASS DOOR GRAPHICS · ONE-WAY VISION FILM · REV R2</p>
  <h1>Eight panes,<br>one frontage.</h1>
  <p class="lede">Photographic service panels for the four glazed leaves of the CarePoint
  frontage — dental, paediatrics, laboratory, physiotherapy, pharmacy, antenatal, reception
  and a services directory — printed on perforated film so the clinic stays visible from
  inside and the street reads the poster from outside.</p>
  <div class="cta">
    <a class="btn" href="CarePoint-One-Way-Vision-R2.pdf">All eight panes (PDF, 8 pp)</a>
    <a class="btn ghost" href="lookbook/CarePoint-One-Way-Vision-Lookbook.pdf">Lookbook</a>
    <a class="btn ghost" href="docs/CP-01-Panel-Schedule.pdf">Panel schedule</a>
    <a class="btn ghost" href="docs/CP-02-Production-Specification.pdf">Production spec</a>
  </div>
  <p class="disclaimer">Provisional — Rev R2. Pane sizes are scaled from the client's own
  shopfront photograph and must be confirmed on site. The monogram is a vector recreation
  of the client's sign; the client's vector logo replaces it before release.</p>
</header>

<section class="elevation">
  <img src="web/mockup-day.jpg" alt="Frontage elevation with all eight panels in place, daytime">
  <img src="web/mockup-night.jpg" alt="The same frontage at night with interior lighting behind the film">
  <div class="cap">
    <span>Rebuilt to the measured leaf geometry: four 900 mm leaves, timber frames, two panes per
    leaf.</span>
    <span>After dark the interior lights turn every pane into a lit, translucent screen.</span>
  </div>
</section>

<section class="grid">
{''.join(cards)}
</section>

<section class="sheet">
  <img src="web/contact-sheet.jpg" alt="Contact sheet of the eight panels">
</section>

<section class="specs">
  <h2>Production notes</h2>
  <div class="cols">
    <div>
      <h3>Film</h3>
      <ul>
        <li>Perforated one-way vision vinyl, white-backed, 140–160 µm plus liner.</li>
        <li>1.6 mm holes on a 2.3 mm staggered pitch — about 44 % open by geometry.</li>
        <li>Matte anti-glare face; UV or latex print, four colour plus white backing.</li>
        <li>Every figure here is industry-typical and flagged <em>confirm with printer</em>.</li>
      </ul>
    </div>
    <div>
      <h3>Artwork</h3>
      <ul>
        <li>Trim 810 × 1120 mm (five panes) and 810 × 1180 mm (three panes).</li>
        <li>10 mm bleed, 25 mm live margin, 20 mm slug, crop marks outside bleed.</li>
        <li>Service names at 54–66 mm cap height — sized to survive a 44 % perforation.</li>
        <li>Nothing live below 6 mm; no caption ever sits on a photograph.</li>
        <li>Photographs audited in the placed crop: 77–172 ppi, all above the 75 ppi floor —
        on perforated film the 2.3 mm hole pitch is the real limit.</li>
      </ul>
    </div>
    <div>
      <h3>Identity</h3>
      <ul>
        <li>Colours sampled from the client's fascia sign: navy #16233F, cyan #2BA9E0.</li>
        <li>Slogan and both telephone numbers transcribed from the client's own board.</li>
        <li>Manrope display / Inter text, both open licence.</li>
        <li>No invented services, hours, accreditations or claims.</li>
      </ul>
    </div>
  </div>
</section>

<section class="licence">
  <h2>Photography &amp; licence</h2>
  <p class="note">Real, professionally shot stock photography. No AI-generated imagery, no
  synthetic patients, no images lifted from competitors' boards. Licence terms read on Pexels'
  licence page, 28 October 2026: free for commercial use including print, editing and cropping
  permitted, attribution not required. The people shown are models, not CarePoint staff or
  patients — no panel names a person or presents them as staff.</p>
  <div class="tablewrap">
    <table>
      <thead><tr><th>Asset</th><th>Pane</th><th>Subject</th><th>Creator</th><th>Source</th>
      <th>Original</th><th>Licence</th></tr></thead>
      <tbody>
{chr(10).join(lic_rows)}
      </tbody>
    </table>
  </div>
</section>

<footer>
  <div>
    <strong>CarePoint Medical Center</strong> · Your Health. Our Commitment.<br>
    TEL (+256) 078 474 7461 · 070 081 7054
  </div>
  <div class="right">Rev R2 · 2026-10-28 · provisional<br>Artwork, schedule and spec in this folder</div>
</footer>
</body>
</html>
"""
    path = os.path.join(BASE, "index.html")
    open(path, "w").write(page)
    return path


def mockup_jpgs():
    out = []
    for src, dst in [("M-01-shopfront-day.png", "mockup-day.jpg"),
                     ("M-02-shopfront-night.png", "mockup-night.jpg")]:
        p = os.path.join(BASE, "lookbook", "mockups", src)
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGB")
        im.thumbnail((1900, 1900), Image.LANCZOS)
        t = os.path.join(WEB, dst)
        im.save(t, "JPEG", quality=88, optimize=True)
        out.append(t)
    # logo for the page header
    logo = os.path.join(ROOT, "source", ".work", "logo.png")
    if not os.path.exists(logo):
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.units import mm as MM
        c = rl_canvas.Canvas(logo.replace(".png", ".pdf"), pagesize=(120 * MM, 120 * MM))
        B.register_fonts()
        c.setFillColor(B.CP_NAVY)
        c.rect(0, 0, 120 * MM, 120 * MM, stroke=0, fill=1)
        c.scale(MM, MM)
        B.monogram(c, 34, 34, 52, dark=B.WHITE, accent=B.CP_CYAN)
        c.showPage()
        c.save()
        doc = pdfium.PdfDocument(logo.replace(".png", ".pdf"))
        page = doc[0]
        page.render(scale=240 / page.get_size()[0]).to_pil().save(logo)
        doc.close()
    if os.path.exists(logo):
        t = os.path.join(WEB, "logo.png")
        Image.open(logo).convert("RGB").save(t)
        out.append(t)
    return out


if __name__ == "__main__":
    os.makedirs(WEB, exist_ok=True)
    print("previews:", len(previews()))
    print("mockups:", len(mockup_jpgs()))
    print("combined", combined())
    print("html", html())
