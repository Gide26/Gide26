#!/usr/bin/env python3
"""
Build the printable PDF edition of "Shoot Like a Pro With Your Phone"
straight from docs/index.html, so the website stays the single source of truth.

    python3 docs/tools/build_pdf.py            # writes docs/shoot-like-a-pro-with-your-phone.pdf
    python3 docs/tools/build_pdf.py --keep-placeholders

Requirements (pip): reportlab beautifulsoup4 pillow resvg-py
Fonts: Lato + DM Serif Display are looked for in docs/tools/.fonts/ (downloaded
on demand from the google/fonts repository via `gh api`); DejaVu Sans is the
fallback for anything missing.
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image as PILImage, ImageDraw, ImageEnhance

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, Image, KeepTogether, ListFlowable, ListItem,
    NextPageTemplate, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

# --------------------------------------------------------------------------- paths / CLI
import argparse

DOCS = Path(__file__).resolve().parents[1]
_ap = argparse.ArgumentParser(description="Build the print edition (PDF) from the tutorial HTML.")
_ap.add_argument("--html", default=str(DOCS / "index.html"), help="source page (default: docs/index.html)")
_ap.add_argument("--out", default=None, help="output PDF (default: next to the source page)")
_ap.add_argument("--keep-placeholders", action="store_true", help="include placeholder example photos")
ARGS = _ap.parse_args()

HTML = Path(ARGS.html).resolve()
CSS = DOCS / "css" / "style.css"
IMG_DIR = DOCS / "images"
TOOLS = DOCS / "tools"
FONT_DIR = TOOLS / ".fonts"
BUILD = TOOLS / ".build"

# language-specific strings (everything else comes from the page itself)
_L10N = {
    "en": dict(
        pdf="shoot-like-a-pro-with-your-phone.pdf",
        url="https://gide26.github.io/Gide26/",
        running="Shoot Like a Pro With Your Phone",
        contents="Contents",
        kicker="FREE PICTURE-ILLUSTRATED TUTORIAL",
        web="Web version with interactive examples: ",
        credit="By Gide26 · Kampala, Uganda · Free to read, print, share and remix.",
    ),
    "fr": dict(
        pdf="photographier-comme-un-pro-avec-votre-telephone.pdf",
        url="https://gide26.github.io/Gide26/fr/",
        running="Photographiez comme un pro avec votre téléphone",
        contents="Sommaire",
        kicker="TUTORIEL GRATUIT ET ILLUSTRÉ",
        web="Version web avec exemples interactifs : ",
        credit="Par Gide26 · Kampala, Ouganda · Libre à lire, imprimer, partager et remixer.",
    ),
}
_lang_m = re.search(r'<html[^>]*\blang="([a-z]{2})', HTML.read_text(encoding="utf-8"))
LANG = _lang_m.group(1) if _lang_m and _lang_m.group(1) in _L10N else "en"
T = _L10N[LANG]
OUT = Path(ARGS.out).resolve() if ARGS.out else HTML.parent / T["pdf"]
SITE_URL = T["url"]
KEEP_PLACEHOLDERS = ARGS.keep_placeholders
PLACEHOLDER_MAX_BYTES = 25_000   # generated placeholder cards are ~12-17 KB; real photos are >100 KB

BUILD.mkdir(parents=True, exist_ok=True)
FONT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------- colours
INK = colors.HexColor("#1f1d1a")
INK_SOFT = colors.HexColor("#3e3933")
MUTED = colors.HexColor("#6b645b")
LINE = colors.HexColor("#e6dfd5")
BG_SOFT = colors.HexColor("#f2ede5")
ACCENT = colors.HexColor("#e0892a")
ACCENT_DEEP = colors.HexColor("#b9681a")
ACCENT_SOFT = colors.HexColor("#fdf0df")
TEAL = colors.HexColor("#1f8a8a")
TEAL_SOFT = colors.HexColor("#e3f3f3")
RED = colors.HexColor("#c94a3a")
RED_SOFT = colors.HexColor("#fbe7e3")
GREEN = colors.HexColor("#3f8f5a")
WHITE = colors.white

# --------------------------------------------------------------------------- fonts
GOOGLE_FONTS = {
    "Lato-Regular.ttf": "ofl/lato/Lato-Regular.ttf",
    "Lato-Bold.ttf": "ofl/lato/Lato-Bold.ttf",
    "Lato-Italic.ttf": "ofl/lato/Lato-Italic.ttf",
    "Lato-BoldItalic.ttf": "ofl/lato/Lato-BoldItalic.ttf",
    "DMSerifDisplay-Regular.ttf": "ofl/dmserifdisplay/DMSerifDisplay-Regular.ttf",
}
DEJAVU = Path("/usr/share/fonts/truetype/dejavu")


def fetch_fonts() -> None:
    """Download the open-licence fonts once (needs the GitHub CLI); silently skip on failure."""
    for name, repo_path in GOOGLE_FONTS.items():
        target = FONT_DIR / name
        if target.exists() and target.stat().st_size > 10_000:
            continue
        try:
            b64 = subprocess.run(
                ["gh", "api", f"repos/google/fonts/contents/{repo_path}", "--jq", ".content"],
                check=True, capture_output=True, text=True, timeout=60,
            ).stdout
            import base64
            target.write_bytes(base64.b64decode(b64))
        except Exception:
            pass


def register_fonts() -> dict:
    fetch_fonts()
    have_lato = all((FONT_DIR / n).exists() for n in GOOGLE_FONTS if n.startswith("Lato"))
    have_display = (FONT_DIR / "DMSerifDisplay-Regular.ttf").exists()
    if have_lato:
        pdfmetrics.registerFont(TTFont("Body", FONT_DIR / "Lato-Regular.ttf"))
        pdfmetrics.registerFont(TTFont("Body-Bold", FONT_DIR / "Lato-Bold.ttf"))
        pdfmetrics.registerFont(TTFont("Body-Italic", FONT_DIR / "Lato-Italic.ttf"))
        pdfmetrics.registerFont(TTFont("Body-BoldItalic", FONT_DIR / "Lato-BoldItalic.ttf"))
    else:
        pdfmetrics.registerFont(TTFont("Body", DEJAVU / "DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("Body-Bold", DEJAVU / "DejaVuSans-Bold.ttf"))
        pdfmetrics.registerFont(TTFont("Body-Italic", DEJAVU / "DejaVuSans-Oblique.ttf"))
        pdfmetrics.registerFont(TTFont("Body-BoldItalic", DEJAVU / "DejaVuSans-BoldOblique.ttf"))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-Italic", boldItalic="Body-BoldItalic")
    if have_display:
        pdfmetrics.registerFont(TTFont("Display", FONT_DIR / "DMSerifDisplay-Regular.ttf"))
    else:
        pdfmetrics.registerFont(TTFont("Display", DEJAVU / "DejaVuSerif-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Fallback", DEJAVU / "DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("Fallback-Bold", DEJAVU / "DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFontFamily("Fallback", normal="Fallback", bold="Fallback-Bold", italic="Fallback", boldItalic="Fallback-Bold")
    return {"lato": have_lato, "display": have_display}


FONT_INFO = register_fonts()


def _cmap(font_name: str) -> dict:
    return pdfmetrics.getFont(font_name).face.charToGlyph


CMAP_BODY = _cmap("Body")
CMAP_DISPLAY = _cmap("Display")


def with_fallback(markup: str, cmap: dict, fallback: str = "Fallback") -> str:
    """Wrap characters the font cannot draw in a <font> tag pointing at a font that can.
    Only touches text outside of tags."""
    def fix_text(text: str) -> str:
        out, run, bad = [], [], False
        for ch in text:
            ok = (ord(ch) in cmap) or ch in "\n\t &;<>" or ch.isspace()
            if ok != (not bad) and run:
                out.append("".join(run) if not bad else f'<font name="{fallback}">{"".join(run)}</font>')
                run = []
            bad = not ok
            run.append(ch)
        if run:
            out.append("".join(run) if not bad else f'<font name="{fallback}">{"".join(run)}</font>')
        return "".join(out)

    parts = re.split(r"(<[^>]+>|&[a-z#0-9]+;)", markup)
    return "".join(p if (p.startswith("<") or p.startswith("&")) else fix_text(p) for p in parts)


# --------------------------------------------------------------------------- styles
PAGE_W, PAGE_H = A4
MARGIN = 17 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

def ps(name, **kw):
    base = dict(fontName="Body", fontSize=10.5, leading=15, textColor=INK, spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(name, **base)

S = {
    "body": ps("body"),
    "intro": ps("intro", fontSize=11.5, leading=17, textColor=INK_SOFT, spaceAfter=8),
    "small": ps("small", fontSize=9, leading=12.5, textColor=MUTED, spaceAfter=3),
    "caption": ps("caption", fontSize=9, leading=12.5, textColor=MUTED, spaceBefore=4, spaceAfter=10),
    "label": ps("label", fontName="Body-Bold", fontSize=7.5, leading=9, textColor=WHITE),
    "h1": ps("h1", fontName="Display", fontSize=26, leading=30, spaceBefore=0, spaceAfter=4),
    "h1num": ps("h1num", fontName="Display", fontSize=44, leading=44, textColor=ACCENT, spaceAfter=0),
    "h1sub": ps("h1sub", fontSize=11.5, leading=16, textColor=MUTED, spaceAfter=14),
    "h2": ps("h2", fontName="Display", fontSize=15.5, leading=19, spaceBefore=14, spaceAfter=5, keepWithNext=1),
    "h3": ps("h3", fontName="Body-Bold", fontSize=11, leading=14, spaceBefore=8, spaceAfter=3, keepWithNext=1),
    "cell": ps("cell", fontSize=9, leading=12, spaceAfter=0),
    "cellhead": ps("cellhead", fontName="Body-Bold", fontSize=7.8, leading=10, textColor=MUTED, spaceAfter=0),
    "boxtitle": ps("boxtitle", fontName="Display", fontSize=12.5, leading=15, spaceAfter=3),
    "boxtitle-sm": ps("boxtitle-sm", fontName="Body-Bold", fontSize=10, leading=13, spaceAfter=2),
    "boxtext": ps("boxtext", fontSize=9.3, leading=12.8, textColor=INK_SOFT, spaceAfter=0),
    "callout-title": ps("callout-title", fontName="Body-Bold", fontSize=7.8, leading=10, spaceAfter=2),
    "dt": ps("dt", fontName="Body-Bold", fontSize=7.3, leading=10, textColor=ACCENT_DEEP, spaceAfter=0),
    "dd": ps("dd", fontSize=9.2, leading=12.5, textColor=INK_SOFT, spaceAfter=0),
    "cardtitle": ps("cardtitle", fontName="Display", fontSize=14, leading=17, spaceAfter=4),
    "toc0": ps("toc0", fontName="Body-Bold", fontSize=11.5, leading=16, spaceBefore=6),
    "toc1": ps("toc1", fontSize=9.5, leading=13, leftIndent=14, textColor=INK_SOFT),
    "cover-title": ps("cover-title", fontName="Display", fontSize=40, leading=44, textColor=INK),
    "cover-sub": ps("cover-sub", fontSize=12.5, leading=18, textColor=INK_SOFT),
    "cover-meta": ps("cover-meta", fontSize=9.5, leading=13, textColor=MUTED),
    "day": ps("day", fontName="Display", fontSize=9.5, leading=12, textColor=ACCENT, spaceAfter=1),
    "use": ps("use", fontName="Body-Bold", fontSize=8.2, leading=11, textColor=TEAL, spaceAfter=0),
}

# --------------------------------------------------------------------------- text helpers
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U0001F900-\U0001F9FF\uFE0F\u200D\u2B50\u2B06\u2194-\u21AA\u23F0-\u23FF\u2705\u274C\u2795\u2796\u2934\u2935\u25AA\u25AB\u25FB-\u25FE\u2600-\u26FF\u2702-\u27B0]"
)
KEEP_SYMBOLS = {"→", "←", "↑", "↓", "↔", "●"}


def strip_emoji(text: str) -> str:
    return "".join(ch for ch in text if ch in KEEP_SYMBOLS or not EMOJI_RE.match(ch))


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(node, drop_tags=True) -> str:
    """Convert inline HTML to reportlab paragraph markup."""
    if isinstance(node, NavigableString):
        return esc(strip_emoji(str(node)))
    if not isinstance(node, Tag):
        return ""
    name = node.name
    cls = node.get("class", [])
    if name in ("script", "style", "button", "svg", "input"):
        return ""
    if "ico" in cls or ("tag" in cls and drop_tags) or "visually-hidden" in cls:
        return ""
    inner = "".join(inline(c, drop_tags) for c in node.children)
    if name in ("strong", "b"):
        return f"<b>{inner}</b>"
    if name in ("em", "i"):
        return f"<i>{inner}</i>"
    if name == "kbd":
        return f"<b>{inner}</b>"
    if name == "code":
        return f'<font name="Courier">{inner}</font>'
    if name == "br":
        return "<br/>"
    if name == "a":
        href = node.get("href", "")
        if href.startswith("http"):
            return f'<a href="{href}" color="#b9681a">{inner}</a>'
        return inner
    return inner


def clean(markup: str) -> str:
    markup = re.sub(r"[ \t\r\n]+", " ", markup).strip()
    markup = markup.replace(" <br/> ", "<br/>")
    return markup


def P(markup: str, style="body", cmap=None) -> Paragraph:
    st = S[style] if isinstance(style, str) else style
    cm = cmap or (CMAP_DISPLAY if st.fontName == "Display" else CMAP_BODY)
    fb = "Body-Bold" if st.fontName == "Display" else "Fallback"
    return Paragraph(with_fallback(clean(markup), cm, fb), st)


def text_of(node) -> str:
    return clean(inline(node)) if node else ""


def tag_label(h) -> str:
    """The small 'photo + video' badge in headings."""
    span = h.find("span", class_="tag") if isinstance(h, Tag) else None
    if not span:
        return ""
    label = span.get_text(" ", strip=True).upper()
    color = "#1f8a8a" if "tag-video" in span.get("class", []) else ("#b9681a" if "tag-photo" in span.get("class", []) else "#6b645b")
    return f' <font name="Body-Bold" size="7" color="{color}">{esc(label)}</font>'


# --------------------------------------------------------------------------- images
def is_placeholder(path: Path) -> bool:
    return (not path.exists()) or (path.stat().st_size < PLACEHOLDER_MAX_BYTES and not KEEP_PLACEHOLDERS)


def img_path(src: str) -> Path:
    return (HTML.parent / src).resolve()


def image_size(path: Path):
    with PILImage.open(path) as im:
        return im.size


def fitted_image(path: Path, max_w: float, max_h: float) -> Image:
    w, h = image_size(path)
    scale = min(max_w / w, max_h / h)
    return Image(str(path), width=w * scale, height=h * scale)


def derived_before_image(path: Path) -> Path:
    """Simulate the flat 'before' look used on the website's before/after slider."""
    out = BUILD / f"before-{path.stem}.jpg"
    if not out.exists():
        im = PILImage.open(path).convert("RGB")
        im = ImageEnhance.Brightness(im).enhance(0.86)
        im = ImageEnhance.Contrast(im).enhance(0.82)
        im = ImageEnhance.Color(im).enhance(0.55)
        im.save(out, quality=86)
    return out


def derived_grid_image(path: Path) -> Path:
    """Draw the rule-of-thirds grid and power points onto the photo."""
    out = BUILD / f"grid-{path.stem}.jpg"
    if not out.exists():
        im = PILImage.open(path).convert("RGB")
        w, h = im.size
        d = ImageDraw.Draw(im, "RGBA")
        lw = max(2, w // 500)
        for x in (w / 3, 2 * w / 3):
            d.line([(x, 0), (x, h)], fill=(0, 0, 0, 90), width=lw + 2)
            d.line([(x, 0), (x, h)], fill=(255, 255, 255, 230), width=lw)
        for y in (h / 3, 2 * h / 3):
            d.line([(0, y), (w, y)], fill=(0, 0, 0, 90), width=lw + 2)
            d.line([(0, y), (w, y)], fill=(255, 255, 255, 230), width=lw)
        r = max(6, w // 110)
        for x in (w / 3, 2 * w / 3):
            for y in (h / 3, 2 * h / 3):
                d.ellipse([x - r, y - r, x + r, y + r], fill=(224, 137, 42, 255), outline=(255, 255, 255, 255), width=lw)
        im.save(out, quality=88)
    return out


# --------------------------------------------------------------------------- SVG diagrams
_css = CSS.read_text(encoding="utf-8")
_vars = dict(re.findall(r"--([a-z-]+):\s*([^;]+);", _css))


def _resolve(s: str) -> str:
    for _ in range(3):
        s = re.sub(r"var\(--([a-z-]+)\)", lambda m: _vars.get(m.group(1), "#000"), s)
    return s


DG_RULES = "\n".join(_resolve(m) for m in re.findall(r"\.dg[^{]*\{[^}]*\}", _css))
DG_RULES += "\n.t-w{fill:#fff}\n text{font-family:'Lato','DejaVu Sans',sans-serif;}"
_html_text = HTML.read_text(encoding="utf-8")
_defs_svg = re.search(r'<svg width="0" height="0".*?</svg>', _html_text, re.S).group(0)
DEFS_INNER = re.search(r"<defs>(.*?)</defs>", _defs_svg, re.S).group(1).replace('href="#', 'xlink:href="#')


def render_svg(svg_markup: str, scale: float, extra_css: str = "") -> Path:
    """Render an inline diagram to PNG with resvg; cached by content hash."""
    import resvg_py
    key = hashlib.sha1((svg_markup + extra_css + str(scale)).encode()).hexdigest()[:16]
    out = BUILD / f"dg-{key}.png"
    if out.exists():
        return out
    s = svg_markup.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"', 1)
    s = s.replace('href="#', 'xlink:href="#')
    open_end = s.index(">") + 1
    s = s[:open_end] + "<defs>" + DEFS_INNER + "</defs><style>" + DG_RULES + extra_css + "</style>" + s[open_end:]
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s)
    w = float(vb.group(1))
    png = resvg_py.svg_to_bytes(
        svg_string=s, width=int(w * scale), background="#ffffff",
        font_dirs=[str(FONT_DIR), str(DEJAVU)], font_family="Lato", sans_serif_family="Lato",
    )
    out.write_bytes(bytes(png))
    return out


RAW_SVGS = re.findall(r'<svg class="dg".*?</svg>', _html_text, re.S)
RAW_BY_NODE: dict = {}


def index_raw_svgs(soup: BeautifulSoup) -> None:
    """bs4's html.parser lowercases attribute and tag names (viewBox -> viewbox, clipPath -> clippath),
    which breaks SVG rendering, so diagrams are rendered from the untouched source text instead."""
    nodes = soup.select("svg.dg")
    if len(nodes) != len(RAW_SVGS):
        raise SystemExit(f"diagram count mismatch: {len(nodes)} nodes vs {len(RAW_SVGS)} raw <svg class=\"dg\"> blocks")
    for node, raw in zip(nodes, RAW_SVGS):
        RAW_BY_NODE[id(node)] = raw


def svg_image(svg_tag: Tag, max_w: float, max_h: float, scale: float = 2.2, extra_css: str = "") -> Image:
    raw = RAW_BY_NODE.get(id(svg_tag)) or str(svg_tag)
    path = render_svg(raw, scale, extra_css)
    return fitted_image(path, max_w, max_h)


# --------------------------------------------------------------------------- boxes
def box(flowables, bg=WHITE, border=LINE, pad=8, width=CONTENT_W, border_w=0.8) -> Table:
    t = Table([[flowables]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), border_w, border),
        ("LEFTPADDING", (0, 0), (-1, -1), pad), ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("TOPPADDING", (0, 0), (-1, -1), pad), ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def grid(cells, ncols: int, gap: float = 5, width: float = CONTENT_W, pad: float = 8, bg=WHITE, border=LINE) -> Table:
    """Lay boxes out in a grid of equal columns; each cell is a list of flowables."""
    col_w = (width - gap * (ncols - 1)) / ncols
    rows, row = [], []
    for c in cells:
        row.append(box(c, bg=bg, border=border, pad=pad, width=col_w))
        if len(row) == ncols:
            rows.append(row); row = []
    if row:
        row += [""] * (ncols - len(row)); rows.append(row)
    widths = []
    for i in range(ncols):
        widths.append(col_w)
    t = Table(rows, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), gap),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), gap),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def labelled(flow, label: str, color=INK) -> Table:
    """A small coloured label above a flowable (used for Avoid / Better / Wide …)."""
    lab = Table([[P(esc(label.upper()), "label")]], colWidths=[None])
    lab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    lab.hAlign = "LEFT"
    t = Table([[lab], [flow]], colWidths=[None])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    return t


LABEL_COLORS = {"avoid": RED, "better": GREEN}

# --------------------------------------------------------------------------- component converters
def conv_list(node: Tag, ordered=False, style="body", steps=False) -> ListFlowable:
    items = []
    for li in node.find_all("li", recursive=False):
        if steps:
            strong = li.find("strong")
            lead = text_of(strong) if strong else ""
            rest = "".join(inline(c) for c in li.children if c is not strong)
            markup = f"<b>{lead}</b> {clean(rest)}"
        else:
            markup = inline(li)
        items.append(ListItem(P(markup, style), leftIndent=16, value=None))
    kw = dict(leftIndent=16, bulletFontSize=9.5, spaceAfter=6, bulletColor=ACCENT_DEEP)
    if ordered:
        return ListFlowable(items, bulletType="1", bulletFormat="%s.", bulletFontName="Body-Bold", **kw)
    if "checklist" in node.get("class", []):
        return ListFlowable(items, bulletType="bullet", start="\u2610", bulletFontName="Fallback", **kw)
    return ListFlowable(items, bulletType="bullet", start="\u2022", bulletFontName="Body", **kw)


def conv_figure(fig: Tag) -> list:
    cls = fig.get("class", [])
    cap = fig.find("figcaption")
    cap_md = text_of(cap)
    out = []

    if "diagram" in cls:
        svg = fig.find("svg")
        img = svg_image(svg, CONTENT_W - 16, 150 * mm)
        img.hAlign = "CENTER"
        inner = [img]
        if cap_md:
            inner += [Spacer(1, 4), P(cap_md, "caption")]
        out.append(KeepTogether([box(inner, bg=WHITE, border=LINE, pad=8), Spacer(1, 10)]))
        return out

    demo = fig.find("div", class_="grid-demo")
    if demo:
        path = img_path(demo.find("img")["src"])
        if is_placeholder(path):
            return []
        gi = derived_grid_image(path)
        img = fitted_image(gi, CONTENT_W, 120 * mm); img.hAlign = "CENTER"
        cap_md = cap_md.replace("Toggle the grid", "The grid overlay shows").replace("<b>The grid overlay shows</b> to see", "<b>The grid overlay shows</b>")
        out.append(KeepTogether([img, P(cap_md, "caption")]))
        return out

    ba = fig.find("div", class_="ba")
    if ba:
        path = img_path(ba.find("img")["src"])
        if is_placeholder(path):
            return []
        before = derived_before_image(path)
        col_w = (CONTENT_W - 6) / 2
        a = labelled(fitted_image(before, col_w, 90 * mm), "Before", INK)
        b = labelled(fitted_image(path, col_w, 90 * mm), "After", GREEN)
        t = Table([[a, b]], colWidths=[col_w + 3, col_w + 3])
        t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (-1, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        cap_md = cap_md.replace("<b>Drag the handle.</b> Left", "Left")
        out.append(KeepTogether([t, P(cap_md, "caption")]))
        return out

    if "figure-pair" in cls or "figure-trio" in cls:
        items = fig.find_all("div", class_="item")
        cells = []
        n = 3 if "figure-trio" in cls else 2
        col_w = (CONTENT_W - 6 * (n - 1)) / n
        for it in items:
            im = it.find("img")
            path = img_path(im["src"])
            if is_placeholder(path):
                continue
            lab = it.find("span", class_="label")
            label = lab.get_text(strip=True) if lab else ""
            color = LABEL_COLORS.get(label.lower(), INK)
            flow = fitted_image(path, col_w, 110 * mm)
            cells.append(labelled(flow, label, color) if label else flow)
        if not cells:
            return []
        t = Table([cells], colWidths=[col_w + (6 if i < len(cells) - 1 else 0) for i in range(len(cells))], hAlign="LEFT")
        t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (-1, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        out.append(KeepTogether([t, P(cap_md, "caption")]))
        return out

    im = fig.find("img")
    if im:
        path = img_path(im["src"])
        if is_placeholder(path):
            return []
        w, h = image_size(path)
        max_h = 118 * mm if h > w else 125 * mm
        img = fitted_image(path, CONTENT_W, max_h); img.hAlign = "CENTER"
        out.append(KeepTogether([img, P(cap_md, "caption")]))
    return out


def conv_callout(node: Tag) -> list:
    cls = node.get("class", [])
    bg, border, color = ACCENT_SOFT, colors.HexColor("#f6d9b4"), ACCENT_DEEP
    if "note" in cls:
        bg, border, color = TEAL_SOFT, colors.HexColor("#bfe1e1"), TEAL
    if "warn" in cls:
        bg, border, color = RED_SOFT, colors.HexColor("#f3c6bf"), RED
    body = node.find("div")
    inner = []
    title = body.find("strong", class_="title") if body else None
    if title:
        st = ParagraphStyle("ct", parent=S["callout-title"], textColor=color)
        inner.append(P(esc(title.get_text(strip=True).upper()), st))
    for p in (body.find_all("p", recursive=False) if body else []):
        inner.append(P(inline(p), "boxtext"))
    return [box(inner, bg=bg, border=border, pad=9), Spacer(1, 10)]


def conv_exercise(node: Tag) -> list:
    inner = []
    h = node.find("h4")
    if h:
        title = text_of(h).replace("Try it", "Try it", 1)
        inner.append(P(title, ParagraphStyle("ex-t", parent=S["boxtitle"], textColor=ACCENT_DEEP)))
    for child in node.children:
        if not isinstance(child, Tag) or child.name == "h4":
            continue
        if child.name in ("ol", "ul"):
            inner.append(conv_list(child, ordered=(child.name == "ol"), style="boxtext"))
        elif child.name == "p":
            inner.append(P(inline(child), "boxtext"))
    return [KeepTogether([box(inner, bg=colors.HexColor("#fbf3e6"), border=ACCENT, pad=10, border_w=1.2)]), Spacer(1, 10)]


def conv_table(wrap: Tag) -> list:
    table = wrap.find("table")
    head = [text_of(th) for th in table.find("thead").find_all("th")] if table.find("thead") else []
    rows = [[text_of(td) for td in tr.find_all(["td", "th"])] for tr in table.find("tbody").find_all("tr")]
    ncols = max(len(r) for r in rows + [head])
    if ncols == 3:
        widths = [CONTENT_W * 0.24, CONTENT_W * 0.40, CONTENT_W * 0.36]
    elif ncols == 2:
        widths = [CONTENT_W * 0.3, CONTENT_W * 0.7]
    else:
        widths = [CONTENT_W / ncols] * ncols
    data = []
    if head:
        data.append([P(esc(strip_emoji(h)).upper(), "cellhead") for h in head])
    for r in rows:
        data.append([P(c, "cell") for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0, hAlign="LEFT")
    style = [
        ("BOX", (0, 0), (-1, -1), 0.8, LINE),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if head:
        style.append(("BACKGROUND", (0, 0), (-1, 0), BG_SOFT))
    t.setStyle(TableStyle(style))
    return [t, Spacer(1, 10)]


def conv_cards(node: Tag) -> list:
    out = []
    for card in node.find_all("article", class_="card"):
        im = card.find("img")
        path = img_path(im["src"]) if im else None
        has_photo = path is not None and not is_placeholder(path)
        title = text_of(card.find("h4"))
        mini = card.find("div", class_="mini")
        dl = card.find("dl")
        body = [P(title, "cardtitle")]
        if mini and mini.find("svg"):
            mini_img = svg_image(mini.find("svg"), 62 * mm, 30 * mm, scale=4, extra_css=" text{font-size:9px}")
            mini_img.hAlign = "LEFT"
            body += [mini_img, Spacer(1, 5)]
        if dl:
            rows = []
            dts, dds = dl.find_all("dt"), dl.find_all("dd")
            for dt, dd in zip(dts, dds):
                rows.append([P(esc(dt.get_text(strip=True).upper()), "dt"), P(inline(dd), "dd")])
            dlt = Table(rows, colWidths=[16 * mm, None], hAlign="LEFT")
            dlt.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            body.append(dlt)
        if has_photo:
            img_w = 58 * mm
            img = fitted_image(path, img_w, 80 * mm)
            row = Table([[img, body]], colWidths=[img_w + 6, CONTENT_W - img_w - 6 - 18])
            row.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, 0), 6), ("RIGHTPADDING", (1, 0), (1, 0), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            content = [row]
        else:
            content = body
        out.append(KeepTogether([box(content, pad=9), Spacer(1, 7)]))
    return out


def conv_mini_cards(node: Tag, ncols: int) -> list:
    cells = []
    for mc in node.find_all("div", class_="mini-card"):
        cell = []
        h = mc.find("h5")
        if h:
            cell.append(P(text_of(h), "boxtitle-sm"))
        for p in mc.find_all("p"):
            cell.append(P(inline(p), "boxtext"))
        cells.append(cell)
    if not cells:
        return []
    return [grid(cells, ncols), Spacer(1, 6)]


def conv_moves(node: Tag) -> list:
    cells = []
    for mv in node.find_all("div", class_="move"):
        cell = []
        svg = mv.find("svg")
        col_w = (CONTENT_W - 10) / 3 - 16
        if svg:
            im = svg_image(svg, col_w, 40 * mm, scale=4, extra_css=" text{font-size:10px}")
            im.hAlign = "LEFT"
            cell += [im, Spacer(1, 4)]
        h = mv.find("h5")
        if h:
            cell.append(P(text_of(h), "boxtitle-sm"))
        p = mv.find("p")
        if p:
            cell.append(P(inline(p), "boxtext"))
        use = mv.find("span", class_="use")
        if use:
            cell.append(P(text_of(use), "use"))
        cells.append(cell)
    return [grid(cells, 3, pad=7), Spacer(1, 6)]


def conv_cheat(node: Tag) -> list:
    cells = []
    for bx in node.find_all("div", class_="box"):
        cell = []
        h = bx.find("h4")
        if h:
            cell.append(P(text_of(h), "boxtitle"))
        ul = bx.find("ul")
        if ul:
            cell.append(conv_list(ul, style="boxtext"))
        cells.append(cell)
    return [grid(cells, 2), Spacer(1, 6)]


def conv_days(node: Tag) -> list:
    cells = []
    for d in node.find_all("div", class_="day"):
        cell = [P(text_of(d.find("div", class_="d")), "day"), P(text_of(d.find("h5")), "boxtitle-sm"), P(inline(d.find("p")), "boxtext")]
        cells.append(cell)
    return [grid(cells, 2), Spacer(1, 6)]


def conv_steps(node: Tag) -> list:
    return [conv_list(node, ordered=True, steps=True), Spacer(1, 4)]


# --------------------------------------------------------------------------- headings with TOC + bookmarks
class Heading(Paragraph):
    def __init__(self, markup, style, level, toc_text):
        super().__init__(markup, style)
        self.level = level
        self.toc_text = toc_text


class ChapterHead(Table):
    """Chapter opener (big number + title + subtitle) that also registers a TOC entry."""
    def __init__(self, data, colWidths, level, toc_text, anchor_key):
        super().__init__(data, colWidths=colWidths)
        self.level = level
        self.toc_text = toc_text
        self.anchor_key = anchor_key


_anchor_counter = [0]


def heading(markup: str, level: int, toc_text: str, style_name: str) -> Heading:
    st = S[style_name]
    cm = CMAP_DISPLAY if st.fontName == "Display" else CMAP_BODY
    fb = "Body-Bold" if st.fontName == "Display" else "Fallback"
    _anchor_counter[0] += 1
    key = f"h{_anchor_counter[0]}"
    h = Heading(with_fallback(clean(markup), cm, fb) + f'<a name="{key}"/>', st, level, toc_text)
    h.anchor_key = key
    return h


# --------------------------------------------------------------------------- document template
class GuideDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=20 * mm, bottomMargin=18 * mm,
                         title="Shoot Like a Pro With Your Phone", author="Gide26",
                         subject="A picture-illustrated guide to phone photography and video", **kw)
        self.current_chapter = ""
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_frame], onPage=lambda c, d: None),
            PageTemplate(id="Body", frames=[frame], onPageEnd=self._decorate),
        ])

    def handle_documentBegin(self):
        self.current_chapter = ""
        super().handle_documentBegin()

    def _decorate(self, canv, doc):
        canv.saveState()
        canv.setFont("Body", 8.2)
        canv.setFillColor(MUTED)
        canv.drawString(MARGIN, PAGE_H - 12 * mm, T["running"])
        if self.current_chapter:
            canv.drawRightString(PAGE_W - MARGIN, PAGE_H - 12 * mm, self.current_chapter)
        canv.setStrokeColor(LINE); canv.setLineWidth(0.6)
        canv.line(MARGIN, PAGE_H - 14 * mm, PAGE_W - MARGIN, PAGE_H - 14 * mm)
        canv.drawCentredString(PAGE_W / 2, 10 * mm, str(doc.page))
        canv.drawRightString(PAGE_W - MARGIN, 10 * mm, SITE_URL.replace("https://", ""))
        canv.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, (Heading, ChapterHead)):
            key = getattr(flowable, "anchor_key", None)
            if key:
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(flowable.toc_text, key, level=flowable.level, closed=False)
            self.notify("TOCEntry", (flowable.level, flowable.toc_text, self.page, key))
            if flowable.level == 0:
                self.current_chapter = flowable.toc_text


# --------------------------------------------------------------------------- cover page
class Cover(Flowable):
    def __init__(self, hero: Path, title: str, subtitle: str, chips: list[str]):
        super().__init__()
        self.hero, self.title, self.subtitle, self.chips = hero, title, subtitle, chips
        self.width, self.height = PAGE_W, PAGE_H

    def wrap(self, aw, ah):
        return PAGE_W, PAGE_H

    def draw(self):
        c = self.canv
        # hero image, cropped to the top 52% of the page
        img_h = PAGE_H * 0.52
        w, h = image_size(self.hero)
        scale = max(PAGE_W / w, img_h / h)
        dw, dh = w * scale, h * scale
        c.saveState()
        p = c.beginPath(); p.rect(0, PAGE_H - img_h, PAGE_W, img_h); c.clipPath(p, stroke=0)
        c.drawImage(str(self.hero), (PAGE_W - dw) / 2, PAGE_H - img_h - (dh - img_h) * 0.35, dw, dh)
        c.restoreState()
        # accent band
        c.setFillColor(ACCENT); c.rect(0, PAGE_H - img_h - 3, PAGE_W, 3, stroke=0, fill=1)
        # text block
        x = MARGIN; y = PAGE_H - img_h - 22 * mm
        c.setFillColor(ACCENT_DEEP); c.setFont("Body-Bold", 9)
        c.drawString(x, y + 10 * mm, T["kicker"])
        title_style = S["cover-title"]
        para = Paragraph(with_fallback(self.title, CMAP_DISPLAY, "Body-Bold"), title_style)
        tw, th = para.wrap(CONTENT_W, 200); para.drawOn(c, x, y - th)
        y = y - th - 8 * mm
        sub = Paragraph(self.subtitle, S["cover-sub"])
        tw, th = sub.wrap(CONTENT_W * 0.9, 200); sub.drawOn(c, x, y - th)
        y = y - th - 9 * mm
        # chips
        cx = x
        c.setFont("Body-Bold", 8.5)
        for chip in self.chips:
            tw = pdfmetrics.stringWidth(chip, "Body-Bold", 8.5) + 12
            c.setFillColor(BG_SOFT); c.setStrokeColor(LINE)
            c.roundRect(cx, y - 4, tw, 14, 7, stroke=1, fill=1)
            c.setFillColor(INK_SOFT); c.drawString(cx + 6, y, chip)
            cx += tw + 6
        # footer meta
        c.setFillColor(MUTED); c.setFont("Body", 9.5)
        c.drawString(x, 22 * mm, T["web"] + SITE_URL)
        c.drawString(x, 17 * mm, T["credit"])


# --------------------------------------------------------------------------- build story
def build_story(soup: BeautifulSoup) -> list:
    story = []
    hero = soup.find("section", class_="hero")
    title = strip_emoji(hero.find("h1").get_text(" ", strip=True))
    title = re.sub(r"\s+", " ", title)
    subtitle = text_of(hero.find("p", class_="lede"))
    chips = [strip_emoji(ch.get_text(strip=True)) for ch in hero.find_all("span", class_="chip")]
    story.append(Cover(IMG_DIR / "hero.jpg", title, subtitle, chips))
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    # table of contents
    toc = TableOfContents()
    toc.levelStyles = [S["toc0"], S["toc1"]]
    toc.dotsMinLevel = 0
    story += [P(T["contents"], "h1"), Spacer(1, 6), toc, PageBreak()]

    for section in soup.select("main section.chapter"):
        story += conv_section(section)
    return story


def glue_headings(flowables: list) -> list:
    """Keep every heading on the same page as whatever follows it (reportlab's keepWithNext
    does not pull a heading along with a following KeepTogether)."""
    out, i = [], 0
    while i < len(flowables):
        f = flowables[i]
        is_heading = isinstance(f, Heading) or (isinstance(f, Paragraph) and getattr(f.style, "name", "") == "h3")
        if is_heading and i + 1 < len(flowables) and not isinstance(flowables[i + 1], PageBreak):
            group = [f]
            j = i + 1
            # swallow spacers and consecutive headings, then the first real block
            while j < len(flowables) and (isinstance(flowables[j], Spacer) or isinstance(flowables[j], Heading)):
                group.append(flowables[j]); j += 1
            if j < len(flowables) and not isinstance(flowables[j], PageBreak):
                nxt = flowables[j]
                if isinstance(nxt, KeepTogether):
                    group += list(nxt._content)
                else:
                    group.append(nxt)
                j += 1
            for g in group:
                if isinstance(g, Paragraph):
                    g.style = ParagraphStyle(g.style.name + "-nk", parent=g.style, keepWithNext=0)
            out.append(KeepTogether(group))
            i = j
        else:
            out.append(f); i += 1
    return out


def conv_section(section: Tag) -> list:
    out = []
    head = section.find("div", class_="chapter-head")
    if head:
        num = head.find("div", class_="chapter-num").get_text(strip=True)
        h2 = head.find("h2")
        sub = head.find("p")
        title_txt = h2.get_text(" ", strip=True)
        for b in (sub.find_all("button") if sub else []):
            b.decompose()
        _anchor_counter[0] += 1
        key = f"h{_anchor_counter[0]}"
        header = ChapterHead([[P(num, "h1num"), [P(inline(h2), "h1"), P(inline(sub), "h1sub") if sub else Spacer(1, 1)]]],
                             colWidths=[22 * mm, CONTENT_W - 22 * mm], level=0, toc_text=f"{num}  {title_txt}", anchor_key=key)
        header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0), ("LINEBELOW", (0, 0), (-1, -1), 0.8, LINE)]))
        out += [header, Spacer(1, 12)]
        start_index = list(section.children).index(head) + 1
    else:
        h2 = section.find("h2")
        out += [heading(inline(h2), 0, h2.get_text(" ", strip=True), "h1"), Spacer(1, 6)]
        start_index = list(section.children).index(h2) + 1

    body = []
    for child in list(section.children)[start_index:]:
        if not isinstance(child, Tag):
            continue
        body += conv_block(child)
    out += glue_headings(body)
    out.append(PageBreak())
    return out


def conv_block(node: Tag) -> list:
    name = node.name
    cls = node.get("class", [])
    if name == "h3":
        txt = "".join(inline(c) for c in node.children) + tag_label(node)
        tag = node.find("span", class_="tag")
        plain = node.get_text(" ", strip=True)
        if tag:
            plain = plain.replace(tag.get_text(strip=True), "").strip()
        return [heading(txt, 1, plain, "h2")]
    if name == "h4":
        return [P(inline(node), "h3")]
    if name == "p":
        return [P(inline(node), "intro" if "intro" in cls else "body")]
    if name == "ol" and "steps" in cls:
        return conv_steps(node)
    if name in ("ul", "ol"):
        return [conv_list(node, ordered=(name == "ol")), Spacer(1, 2)]
    if name == "figure":
        return conv_figure(node)
    if name == "div":
        if "callout" in cls:
            return conv_callout(node)
        if "exercise" in cls:
            return conv_exercise(node)
        if "cards" in cls:
            return conv_cards(node)
        if "table-wrap" in cls:
            return conv_table(node)
        if "moves" in cls:
            return conv_moves(node)
        if "cheat" in cls:
            return conv_cheat(node)
        if "days" in cls:
            return conv_days(node)
        if "grid-3" in cls:
            return conv_mini_cards(node, 3)
        if "grid-2" in cls:
            return conv_mini_cards(node, 2)
    return []


# --------------------------------------------------------------------------- main
def main() -> None:
    soup = BeautifulSoup(HTML.read_text(encoding="utf-8"), "html.parser")
    index_raw_svgs(soup)
    story = build_story(soup)
    doc = GuideDoc(str(OUT))
    doc.multiBuild(story)
    size = OUT.stat().st_size / 1_048_576
    try:
        import pymupdf
        pages = pymupdf.open(str(OUT)).page_count
    except Exception:
        pages = "?"
    print(f"wrote {OUT.relative_to(DOCS.parent)}  ({pages} pages, {size:.1f} MB)  fonts: {FONT_INFO}")


if __name__ == "__main__":
    main()
