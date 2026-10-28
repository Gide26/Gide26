"""Client-facing presentation site (static, self-contained)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image

import panels as PN
import photos as P
import build_previews as PV

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "one-way-vision-film")
WEB = os.path.join(BASE, "web")
MOCK = os.path.join(BASE, "lookbook", "mockups")

PALETTE = [
    ("Navy", "#0A2642", "Ground field — 60% of every panel"),
    ("Navy Deep", "#06182A", "Lockup ground, shadows"),
    ("Teal", "#0C8C8C", "Accent rules and labels"),
    ("Medical Green", "#2E7A5F", "Secondary accent, used sparingly"),
    ("Mist", "#DCE6EC", "Body text on navy"),
    ("White", "#FFFFFF", "Headlines"),
]

STEPS = [
    ("01", "Receive", "Measured schedule, door photographs, logo, printer technical sheet."),
    ("02", "Re-cut", "The parametric engine re-flows type and crop to the real dimensions."),
    ("03", "Proof", "Colour-managed proof on the specified film, signed off."),
    ("04", "Output", "Release PDFs: trimmed artwork, no overlays, printer's profile applied."),
    ("05", "Install", "Application, 1 m inspection, acceptance and one offcut per panel."),
]


def web_img(src, name, width):
    os.makedirs(WEB, exist_ok=True)
    out = os.path.join(WEB, name)
    im = Image.open(src).convert("RGB")
    h = int(im.height * width / im.width)
    im.resize((width, h), Image.LANCZOS).save(out, "JPEG", quality=84, optimize=True,
                                              progressive=True)
    return f"web/{name}"


def build():
    cards = []
    for p in PN.PANELS:
        src = PV.preview(p, 1500)
        img = web_img(src, f"{p['id']}.jpg", 620)
        asset = P.PHOTOS[p["photo"]] if p["photo"] else None
        cards.append({
            "p": p, "img": img, "asset": asset,
            "coverage": f"{(p['h']-p['photo_bottom'])/p['h']*100:.0f}%" if p["photo"] else "0%",
        })

    mockups = []
    for f, title, note in [
        ("M-01-reception.png", "Reception entrance",
         "Single active leaf with fixed sidelight. Handle sits 150 mm in from the meeting edge."),
        ("M-02-consultation.png", "Consultation room",
         "Single leaf. Headline baseline clears the handle zone and the door closer."),
        ("M-03-imaging.png", "Imaging suite",
         "Double leaf, 2 × 600 mm, with a 450 mm sidelight. No type crosses the meeting stile."),
    ]:
        src = os.path.join(MOCK, f)
        img = web_img(src, f.replace(".png", ".jpg"), 900)
        mockups.append({"img": img, "title": title, "note": note})

    over = "web/detail.jpg"
    web_img(os.path.join(PV.CACHE, "detail_title_1to1.png"), "detail.jpg", 900)

    rows = []
    usage = {}
    for p in PN.PANELS:
        if p["photo"]:
            usage.setdefault(p["photo"], []).append(p["id"])
    for key, m in P.PHOTOS.items():
        rows.append({
            "asset": m["asset"], "id": m["pexels_id"], "creator": m["creator"],
            "title": m["title"], "url": m["url"],
            "used": ", ".join(usage.get(key, [])),
            "px": f"{m['original_px'][0]:,} × {m['original_px'][1]:,}",
        })

    html = [HEAD]
    # ---------------------------------------------------------------- hero
    html.append(f"""
<header class="hero">
  <div class="wrap">
    <div class="eyebrow">Premium healthcare · glass door graphics · rev R1 · 2026-10-28</div>
    <h1>One-way vision<br>film system</h1>
    <div class="rule"></div>
    <p class="lede">A coordinated set of perforated window graphics for the reception, consultation
    rooms, laboratory, pharmacy and imaging suite of a private medical centre. Real photography,
    quiet colour, and type that survives perforation.</p>
    <div class="flags">
      <span class="flag">8 panels</span>
      <span class="flag">5 services</span>
      <span class="flag warn">Provisional dimensions</span>
    </div>
  </div>
</header>
""")

    # ------------------------------------------------------------ mockups
    html.append('<section id="mockups"><div class="wrap"><div class="sechead">'
                '<span class="num">01</span><h2>In situ</h2>'
                '<p>Elevations composed at true scale from the actual panel artwork. Hardware is '
                'drawn to position so clearances can be judged.</p></div><div class="mocks">')
    for m in mockups:
        html.append(f"""<figure><img src="{m['img']}" alt="{m['title']}" loading="lazy">
        <figcaption><strong>{m['title']}</strong><span>{m['note']}</span></figcaption></figure>""")
    html.append("</div></div></section>")

    # ------------------------------------------------------------- the set
    html.append('<section id="panels" class="alt"><div class="wrap"><div class="sechead">'
                '<span class="num">02</span><h2>The panel suite</h2>'
                '<p>Eight independent print panels. Fixed elements — photographic band, headline '
                'baseline, accent rule, lockup — sit at identical heights, so a corridor reads as '
                'one institution.</p></div><div class="grid">')
    for c in cards:
        p = c["p"]
        credit = (f"{c['asset']['asset']} · {c['asset']['creator']} / Pexels"
                  if c["asset"] else "Graphic panel — no photograph")
        html.append(f"""<article class="card">
  <a class="shot" href="artwork/{p['id']}.pdf" target="_blank" rel="noopener">
    <img src="{c['img']}" alt="{p['dept']} panel {p['id']}" loading="lazy">
    <span class="open">Open artwork PDF</span>
  </a>
  <div class="meta">
    <div class="row"><span class="pid">{p['id']}</span><span class="dept">{p['dept']}</span></div>
    <div class="spec">{p['w']/10:.0f} × {p['h']/10:.0f} cm · {p['aspect']} · photo {c['coverage']}</div>
    <div class="credit">{credit}</div>
  </div>
</article>""")
    html.append("</div></div></section>")

    # ------------------------------------------------------------- system
    swatches = "".join(
        f'<li><span class="chip" style="background:{hexv}"></span>'
        f'<strong>{name}</strong><code>{hexv}</code><em>{use}</em></li>'
        for name, hexv, use in PALETTE)
    html.append(f"""
<section id="system"><div class="wrap"><div class="sechead"><span class="num">03</span>
<h2>The system</h2><p>One palette, two typefaces, one grid. Everything else is photography.</p></div>
<div class="cols">
  <div>
    <h3>Palette</h3>
    <ul class="palette">{swatches}</ul>
  </div>
  <div>
    <h3>Typography</h3>
    <div class="type">
      <div><span class="tf">Manrope</span><p>Department names, 600–800. Geometric with open
      apertures — holds at 70–78 mm cap height and still reads through a 38% perforation.</p></div>
      <div><span class="tf light">Inter</span><p>Labels, indices and technical text, 400–600 with
      0.15–0.25 em tracking. Never below 4 mm cap height anywhere on a panel.</p></div>
    </div>
    <h3>Grid</h3>
    <ul class="rules">
      <li><b>1250–2100 mm</b> photographic band, full bleed to the head of the panel</li>
      <li><b>660–640 mm</b> accent rule and department label</li>
      <li><b>372 mm</b> headline baseline — identical on every panel</li>
      <li><b>140 mm</b> kick zone: no live content below the lockup</li>
      <li><b>25 mm</b> safe zone, <b>10 mm</b> bleed (printer to confirm)</li>
    </ul>
  </div>
</div></div></section>
""")

    # ------------------------------------------------------- perforation
    html.append(f"""
<section id="film" class="alt"><div class="wrap"><div class="sechead"><span class="num">04</span>
<h2>Designed for perforation</h2><p>Drag the slider to see the film's 1.6 mm holes at true scale over
the headline. This is what the patient actually sees from a metre away.</p></div>
<div class="sim">
  <div class="simframe" id="simframe">
    <img src="{over}" alt="Headline detail">
    <div class="dots" id="dots"></div>
  </div>
  <div class="simctl">
    <label for="pitch">Hole size / pitch</label>
    <input id="pitch" type="range" min="0" max="100" value="60">
    <div class="simval"><span id="pv">1.6 mm / 2.3 mm</span><span id="ov">38% open area</span></div>
    <ul class="rules tight">
      <li>Headlines never sit over photography — solid navy gives maximum edge contrast.</li>
      <li>No stroke thinner than 0.3 mm; hairline rules carry no information.</li>
      <li>Photography covers 40–45% of a door; sidelights carry none at all, preserving daylight.</li>
      <li>The darkest zone is the most transparent: navy is the "window" of the panel.</li>
      <li>From inside, the panel reads as a dark field — do not rely on it for privacy after dark.</li>
    </ul>
  </div>
</div></div></section>
""")

    # -------------------------------------------------------------- sources
    source_rows = "".join(f"""<tr>
  <td class="mono">{r['asset']}</td>
  <td>{r['used']}</td>
  <td><a href="{r['url']}" target="_blank" rel="noopener">{r['title']}</a></td>
  <td>{r['creator']}</td>
  <td class="mono">{r['px']}</td>
  <td><span class="pill ok">Pexels Licence</span></td>
</tr>""" for r in rows)

    html.append(f"""
<section id="sources"><div class="wrap"><div class="sechead"><span class="num">05</span>
<h2>Image sources &amp; licensing</h2><p>Every photograph is a real, professionally shot stock image —
no AI-generated imagery, no synthetic people, no composited scenes. Terms checked on Pexels'
licence page, 28 October 2026.</p></div>
<table class="tbl"><thead><tr><th>Asset</th><th>Used on</th><th>Photograph</th><th>Creator</th>
<th>Original size</th><th>Licence</th></tr></thead><tbody>{source_rows}</tbody></table>
<div class="notes">
  <div><h4>Permitted</h4><p>Free commercial and non-commercial use including print marketing;
  modification and creative editing; attribution not required, credited here as good practice.</p></div>
  <div><h4>Restricted</h4><p>No selling unaltered copies; no implying that the people or brands
  depicted endorse the centre; no use as part of a trade mark. These panels are wayfinding and must
  never caption a depicted person as named staff.</p></div>
</div></div></section>
""")

    # ------------------------------------------------------------ documents
    docs = [("artwork/P-01.pdf", "Panel artwork", "True-size PDF with bleed, marks and slug",
             "all 8 panels in <code>artwork/</code>"),
            ("docs/01-Panel-Schedule.pdf", "Panel schedule", "Dimensions, hardware, crop logic",
             "4 pages"),
            ("proofs/03-Technical-Proofs.pdf", "Technical proofs", "One A3 sheet per panel with overlays",
             "8 pages"),
            ("docs/02-Production-Specification.pdf", "Production specification",
             "Material, ink, installation, RFQ", "5 pages"),
            ("lookbook/GMC-One-Way-Vision-Lookbook.pdf", "Design lookbook",
             "The presentation document", "8 pages")]
    dcards = "".join(f"""<a class="doc" href="{href}" target="_blank" rel="noopener">
  <span class="dname">{name}</span><span class="ddesc">{desc}</span><span class="dmeta">{meta}</span>
</a>""" for href, name, desc, meta in docs)

    html.append(f"""
<section id="next" class="alt"><div class="wrap"><div class="sechead"><span class="num">06</span>
<h2>Where this stands</h2><p>The design is complete and the production system is built. What is
outstanding is measurement, identity and the printer's technical sheet.</p></div>
<div class="cols">
  <div class="panelbox">
    <h3>Ready</h3>
    <ul class="rules">
      <li>Eight true-size artwork files with bleed, marks and per-panel slug</li>
      <li>Panel schedule with hardware, crop logic and coverage</li>
      <li>Image log with creator, licence and original pixel size</li>
      <li>Resolution audit at final print size</li>
      <li>Production spec, install schedule and printer RFQ</li>
    </ul>
  </div>
  <div class="panelbox warnbox">
    <h3>Needed before release</h3>
    <ul class="rules">
      <li>Every glass section measured in centimetres, with door photographs</li>
      <li>Exact department names, room numbers and any second language</li>
      <li>Client logo in vector form, plus approved contact details and claims</li>
      <li>Film maker's hole geometry, ink limit, bleed and sheet width</li>
      <li>Full-resolution stock downloads, relinked at 150 ppi</li>
    </ul>
  </div>
</div>
<h3 class="mt">Sequence</h3>
<ol class="steps">{"".join(f'<li><span class="n">{n}</span><strong>{h}</strong><p>{d}</p></li>' for n, h, d in STEPS)}</ol>
<h3 class="mt">Documents</h3>
<div class="docs">{dcards}</div>
</div></section>
<footer><div class="wrap"><span>GMC / OWV · Rev R1 · 2026-10-28 · provisional</span>
<span>Identity and dimensions are placeholders pending client assets.</span></div></footer>
""")

    html.append(SCRIPT)
    os.makedirs(BASE, exist_ok=True)
    with open(os.path.join(BASE, "index.html"), "w") as fh:
        fh.write("".join(html))
    return os.path.join(BASE, "index.html")


HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>One-way vision film — Medical Center glass door graphics</title>
<meta name="description" content="Premium one-way vision window graphics system for a medical centre: reception, consultation, laboratory, pharmacy and imaging.">
<style>
:root{--navy:#0A2642;--navy-deep:#06182A;--teal:#0C8C8C;--teal-lt:#4FB3AE;--green:#2E7A5F;
--mist:#DCE6EC;--grey:#8FA3B4;--paper:#F4F7F8;--line:#DCE6EC}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:#fff;color:var(--navy);font-family:Inter,"Helvetica Neue",Arial,sans-serif;
font-size:16px;line-height:1.65;-webkit-font-smoothing:antialiased}
.wrap{max-width:1240px;margin:0 auto;padding:0 32px}
h1,h2,h3,h4{font-family:Manrope,"Helvetica Neue",Arial,sans-serif;letter-spacing:-.015em;margin:0}
a{color:inherit}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.82em}
.hero{background:var(--navy);color:#fff;padding:120px 0 96px;position:relative;overflow:hidden}
.hero::after{content:"";position:absolute;inset:auto -80px -120px auto;width:620px;height:620px;
background-image:radial-gradient(circle,#fff 1.4px,transparent 1.5px);background-size:22px 22px;
opacity:.05;transform:rotate(-8deg);pointer-events:none}
.eyebrow{font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--teal-lt);
font-weight:600;margin-bottom:36px}
.hero h1{font-size:clamp(44px,7vw,92px);line-height:.98;font-weight:800;letter-spacing:-.03em}
.rule{width:86px;height:4px;background:var(--teal);margin:36px 0 30px;border-radius:2px}
.lede{max-width:660px;font-size:19px;line-height:1.7;color:#D7E3EA;margin:0}
.flags{display:flex;gap:10px;flex-wrap:wrap;margin-top:44px}
.flag{font-size:12px;letter-spacing:.14em;text-transform:uppercase;padding:9px 15px;border-radius:999px;
border:1px solid rgba(255,255,255,.22);color:#EAF1F5;font-weight:600}
.flag.warn{border-color:var(--teal);color:var(--teal-lt)}
section{padding:96px 0}
section.alt{background:var(--paper)}
.sechead{max-width:760px;margin-bottom:56px}
.num{font-family:Manrope,sans-serif;font-weight:700;font-size:13px;letter-spacing:.2em;color:var(--teal)}
.sechead h2{font-size:clamp(30px,3.6vw,44px);font-weight:800;margin:12px 0 14px;letter-spacing:-.02em}
.sechead p{margin:0;color:#40546A;font-size:16.5px}
.mocks{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}
.mocks figure{margin:0}
.mocks img{width:100%;display:block;border-radius:4px;box-shadow:0 18px 50px rgba(6,24,42,.18)}
figcaption{margin-top:16px;font-size:13.5px;color:#54697E}
figcaption strong{display:block;color:var(--navy);font-family:Manrope;font-size:15px;margin-bottom:4px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:34px 24px}
.card .shot{position:relative;display:block;border-radius:3px;overflow:hidden;
box-shadow:0 10px 30px rgba(6,24,42,.13);transition:transform .35s ease,box-shadow .35s ease}
.card .shot:hover{transform:translateY(-5px);box-shadow:0 18px 44px rgba(6,24,42,.2)}
.card img{width:100%;display:block}
.open{position:absolute;left:0;right:0;bottom:0;background:rgba(6,24,42,.9);color:#fff;font-size:11px;
letter-spacing:.16em;text-transform:uppercase;text-align:center;padding:10px 6px;opacity:0;
transition:opacity .3s ease;font-weight:600}
.shot:hover .open{opacity:1}
.meta{padding-top:14px}
.row{display:flex;align-items:baseline;gap:10px}
.pid{font-family:Manrope;font-weight:700;font-size:12px;letter-spacing:.1em;color:var(--teal)}
.dept{font-family:Manrope;font-weight:700;font-size:14px;letter-spacing:.04em}
.spec{font-size:12.5px;color:#54697E;margin-top:3px}
.credit{font-size:11.5px;color:var(--grey);margin-top:2px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:64px}
h3{font-size:14px;letter-spacing:.18em;text-transform:uppercase;color:var(--teal);font-weight:700;
margin-bottom:22px}
h3.mt{margin-top:64px}
.palette{list-style:none;padding:0;margin:0;display:grid;gap:14px}
.palette li{display:grid;grid-template-columns:46px 1fr auto;gap:14px;align-items:center;
padding-bottom:13px;border-bottom:1px solid var(--line)}
.chip{width:46px;height:34px;border-radius:3px;display:block;border:1px solid rgba(10,38,66,.12)}
.palette strong{font-family:Manrope;font-size:14.5px}
.palette code{color:var(--grey);font-size:12px;justify-self:end}
.palette em{grid-column:2/4;font-style:normal;font-size:12.5px;color:#54697E;margin-top:-6px}
.type>div{padding:18px 0;border-bottom:1px solid var(--line)}
.tf{font-family:Manrope;font-weight:800;font-size:26px;letter-spacing:-.02em}
.tf.light{font-weight:500;letter-spacing:.02em}
.type p{margin:8px 0 0;font-size:14.5px;color:#40546A}
.rules{list-style:none;padding:0;margin:0;font-size:14.5px;color:#40546A}
.rules li{padding:11px 0 11px 20px;border-bottom:1px solid var(--line);position:relative}
.rules li::before{content:"";position:absolute;left:0;top:19px;width:6px;height:6px;border-radius:50%;
background:var(--teal)}
.rules b{color:var(--navy);font-weight:600}
.sim{display:grid;grid-template-columns:1.25fr .95fr;gap:48px;align-items:start}
.simframe{position:relative;border-radius:4px;overflow:hidden;background:var(--navy);
box-shadow:0 20px 50px rgba(6,24,42,.22)}
.simframe img{width:100%;display:block}
.dots{position:absolute;inset:0;pointer-events:none;
background-image:radial-gradient(circle,var(--navy) 1.05px,transparent 1.15px);
background-size:2.55px 2.55px;opacity:.92}
.simctl label{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--teal);
font-weight:700}
input[type=range]{width:100%;margin:18px 0 8px;accent-color:var(--teal)}
.simval{display:flex;justify-content:space-between;font-family:ui-monospace,monospace;
font-size:12.5px;color:#54697E;margin-bottom:26px}
.rules.tight li{font-size:13.5px;padding:9px 0 9px 18px}
.tbl{width:100%;border-collapse:collapse;font-size:13.5px}
.tbl th{text-align:left;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#fff;
background:var(--navy);padding:12px 14px;font-weight:600}
.tbl td{padding:13px 14px;border-bottom:1px solid var(--line);vertical-align:top}
.tbl tr:nth-child(even) td{background:#fff}
.tbl a{text-decoration:none;border-bottom:1px solid var(--line)}
.tbl a:hover{border-color:var(--teal);color:var(--teal)}
.mono{font-family:ui-monospace,monospace;font-size:12px;color:var(--grey)}
.pill{font-size:11px;padding:4px 9px;border-radius:999px;white-space:nowrap;font-weight:600}
.pill.ok{background:#E7F2EC;color:var(--green)}
.notes{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:34px}
.notes h4{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:var(--teal);
margin-bottom:8px}
.notes p{margin:0;font-size:14px;color:#40546A}
.panelbox{background:#fff;padding:28px;border-radius:5px;border:1px solid var(--line)}
.panelbox.warnbox{border-color:#E7C9A8;background:#FFFBF6}
.panelbox h3{margin-bottom:14px}
.steps{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(5,1fr);gap:20px}
.steps li{border-top:2px solid var(--teal);padding-top:16px}
.steps .n{font-family:Manrope;font-weight:800;font-size:26px;color:var(--teal);display:block;
margin-bottom:6px}
.steps strong{font-family:Manrope;font-size:14px;letter-spacing:.1em;text-transform:uppercase}
.steps p{font-size:13px;color:#54697E;margin:6px 0 0}
.docs{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.doc{display:block;padding:22px;border:1px solid var(--line);border-radius:5px;background:#fff;
text-decoration:none;transition:border-color .25s ease,transform .25s ease}
.doc:hover{border-color:var(--teal);transform:translateY(-3px)}
.dname{font-family:Manrope;font-weight:700;font-size:15px;display:block;margin-bottom:5px}
.ddesc{font-size:13px;color:#54697E;display:block}
.dmeta{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--teal);
display:block;margin-top:12px;font-weight:600}
footer{background:var(--navy-deep);color:var(--grey);font-size:12px;padding:34px 0}
footer .wrap{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}
@media(max-width:1000px){
.grid{grid-template-columns:repeat(2,1fr)}
.mocks,.cols,.notes,.docs,.steps{grid-template-columns:1fr 1fr}
.sim{grid-template-columns:1fr}
section{padding:72px 0}
}
@media(max-width:640px){
.wrap{padding:0 20px}
.grid,.mocks,.cols,.notes,.docs,.steps{grid-template-columns:1fr}
.hero{padding:80px 0 64px}
}
</style></head><body>
"""

SCRIPT = """
<script>
(function(){
  const r = document.getElementById('pitch');
  const dots = document.getElementById('dots');
  const pv = document.getElementById('pv');
  const ov = document.getElementById('ov');
  if(!r) return;
  function upd(){
    const t = r.value/100;                 // 0 = no film, 1 = coarse film
    const size = 2.2 + t*4.2;              // background tile in px
    const r1 = 0.75 + t*1.5;               // dot radius
    dots.style.backgroundSize = size+'px '+size+'px';
    dots.style.backgroundImage =
      'radial-gradient(circle, var(--navy) '+r1+'px, transparent '+(r1+0.1)+'px)';
    const pitch = (2.3 + t*2.9);
    const open = Math.round((1 - Math.PI*Math.pow((1.6+t*1.2)/2,2)/(pitch*pitch/ (4/Math.PI)))*100);
    pv.textContent = (1.6+t*1.2).toFixed(1)+' mm / '+pitch.toFixed(1)+' mm';
    ov.textContent = Math.max(8,Math.min(62,open))+'% open area';
  }
  r.addEventListener('input', upd); upd();
})();
</script>
</body></html>
"""

if __name__ == "__main__":
    print("built", build())
