#!/usr/bin/env python3
"""
Build a single PDF from the course markdown.

    pip install markdown pygments xhtml2pdf matplotlib pypdf
    python tools/build_pdf.py

Output: generative-ai-course.pdf  (next to this file's parent directory)

Why matplotlib? It ships the DejaVu TTF fonts, which give us full
Unicode coverage (box drawing, arrows, ticks, warning signs) without
needing any system font packages.
"""

import html as html_mod
import pathlib
import re
import sys

import markdown
from pygments.formatters import HtmlFormatter
from xhtml2pdf import pisa
from xhtml2pdf.config.resources import ResourceAccessPolicy

# ------------------------------------------------------------------- paths
HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parent
OUT = COURSE / "generative-ai-course.pdf"

# --------------------------------------------------------------- font setup
try:
    import matplotlib

    FONT_DIR = pathlib.Path(matplotlib.get_data_path()) / "fonts" / "ttf"
except Exception:  # pragma: no cover
    FONT_DIR = pathlib.Path("/usr/share/fonts/truetype/dejavu")

# The renderer refuses to read files outside the document's directory;
# name the font directory as an extra root so @font-face can load them.
POLICY = ResourceAccessPolicy(base_dir=COURSE, extra_roots=[FONT_DIR])

# ------------------------------------------------------------------ content
# (kind, value, title)  kind: "part" divider | "doc" markdown file | "code" appendix
STRUCTURE = [
    ("part", "Part 1", "Foundations",
     "Understand it, prompt it, verify it. No code required."),
    ("doc", "00-before-you-start.md", "lesson-00"),
    ("doc", "01-what-is-generative-ai.md", "lesson-01"),
    ("doc", "02-your-first-conversation.md", "lesson-02"),
    ("doc", "03-anatomy-of-a-prompt.md", "lesson-03"),
    ("doc", "04-iteration.md", "lesson-04"),
    ("doc", "05-when-ai-lies.md", "lesson-05"),
    ("doc", "06-choosing-tools.md", "lesson-06"),

    ("part", "Part 2", "Creative Work",
     "Text, images, video, audio, and data. Still no code required."),
    ("doc", "07-writing-and-research.md", "lesson-07"),
    ("doc", "08-images.md", "lesson-08"),
    ("doc", "09-video-audio-music.md", "lesson-09"),
    ("doc", "10-data-analysis.md", "lesson-10"),

    ("part", "Part 3", "Building with Code",
     "APIs, structured output, and real applications."),
    ("doc", "11-setup-python-and-api-keys.md", "lesson-11"),
    ("doc", "12-first-api-call.md", "lesson-12"),
    ("doc", "13-system-prompts-and-roles.md", "lesson-13"),
    ("doc", "14-structured-output.md", "lesson-14"),
    ("doc", "15-cli-assistant.md", "lesson-15"),
    ("doc", "16-rag-your-documents.md", "lesson-16"),

    ("part", "Part 4", "Projects", "Four capstone builds."),
    ("doc", "17-projects.md", "lesson-17"),

    ("part", "Reference", "", "Cheat sheet, glossary, and resources."),
    ("doc", "cheat-sheet.md", "ref-cheat"),
    ("doc", "glossary.md", "ref-glossary"),
    ("doc", "resources.md", "ref-resources"),

    ("part", "Appendix", "Code Listings",
     "The complete runnable scripts, in full."),
    ("code", "code/01_hello_ai.py", "api"),
    ("code", "code/02_conversation.py", "api"),
    ("code", "code/03_structured.py", "api"),
    ("code", "code/04_cli_assistant.py", "api"),
    ("code", "code/05_rag_documents.py", "api"),
]

TITLES = {
    "00-before-you-start.md": "Before You Start",
    "01-what-is-generative-ai.md": "What Is Generative AI?",
    "02-your-first-conversation.md": "Your First Real Conversation",
    "03-anatomy-of-a-prompt.md": "The Anatomy of a Great Prompt",
    "04-iteration.md": "Iteration: The Real Skill",
    "05-when-ai-lies.md": "When AI Is Wrong",
    "06-choosing-tools.md": "Choosing Your Tools",
    "07-writing-and-research.md": "Writing, Research & Ideas",
    "08-images.md": "Generating Images",
    "09-video-audio-music.md": "Video, Voice & Music",
    "10-data-analysis.md": "Analysing Data with AI",
    "11-setup-python-and-api-keys.md": "Setup: Python & API Keys",
    "12-first-api-call.md": "Your First API Call",
    "13-system-prompts-and-roles.md": "System Prompts & Roles",
    "14-structured-output.md": "Structured Output (JSON)",
    "15-cli-assistant.md": "Build a CLI Assistant",
    "16-rag-your-documents.md": "Chat With Your Documents",
    "17-projects.md": "Four Capstone Projects",
    "cheat-sheet.md": "Cheat Sheet",
    "glossary.md": "Glossary",
    "resources.md": "Resources",
    "code/01_hello_ai.py": "Listing 1 — Hello AI: your first API call",
    "code/02_conversation.py": "Listing 2 — Conversation: keeping history",
    "code/03_structured.py": "Listing 3 — Structured output: get JSON, not prose",
    "code/04_cli_assistant.py": "Listing 4 — A command-line AI assistant",
    "code/05_rag_documents.py": "Listing 5 — RAG: chat with your documents",
}

# Emoji the DejaVu fonts cannot render, mapped to glyphs they can.
EMOJI_SUB = {
    "✅": "✔", "❌": "✗", "🔴": "●", "⭐": "★", "✨": "",
    "🌱": "", "👀": "", "👋": "", "💞": "", "📚": "", "📫": "", "😄": "",
    "\ufe0f": "",  # variation selector — safe to drop
}

# filename -> anchor, so cross-file links become in-document links
ANCHOR = {name: anchor for kind, name, anchor, *_ in STRUCTURE if kind == "doc"}
ANCHOR["README.md"] = "contents"


# ------------------------------------------------------------- preprocessing
def sub_emoji(text: str) -> str:
    for k, v in EMOJI_SUB.items():
        text = text.replace(k, v)
    return text


def convert_details(text: str) -> str:
    """<details>/<summary> are interactive; render them as a static box."""
    text = re.sub(r"<details>\s*", '<div class="dropbox">\n', text)
    text = re.sub(r"\s*</details>", "\n</div>", text)

    def summary(m):
        inner = re.sub(r"</?b>", "", m.group(1)).strip()
        return f'<p class="dropsum">{inner}</p>\n'

    text = re.sub(r"<summary>(.*?)</summary>", summary, text, flags=re.DOTALL)
    return text


def rewrite_links(text: str) -> str:
    """Turn links to other lesson files into in-document anchors."""

    def repl(m):
        label, target = m.group(1), m.group(2)
        base = target.split("#")[0].lstrip("./")
        if base in ANCHOR:
            return f"[{label}](#{ANCHOR[base]})"
        if target.startswith("http"):
            return f"[{label}]({target})"
        # code files and anything else: keep the label, drop the link
        return label

    return re.sub(r"\[([^\]]*)\]\(([^)]+)\)", repl, text)


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!---.*?--->", "", text, flags=re.DOTALL)


def task_lists(text: str) -> str:
    text = text.replace("- [ ]", "- ☐ ").replace("- [X]", "- ☐ ")
    return text.replace("- [x]", "- ☐ ")


MD = markdown.Markdown(
    extensions=["tables", "fenced_code", "attr_list", "sane_lists",
                "md_in_html", "codehilite", "footnotes"],
    extension_configs={
        # guess_lang=False keeps plain ``` fences (ASCII diagrams, prompt
        # templates) unhighlighted instead of being parsed as Python.
        "codehilite": {"noclasses": True, "pygments_style": "default",
                       "linenums": False, "guess_lang": False},
    },
)


_WS_SPAN = re.compile(r"<span[^>]*>(\s+)</span>", re.DOTALL)
_EMPTY_SPAN = re.compile(r"<span[^>]*></span>")


def clean_spans(html_text: str) -> str:
    """
    Pygments wraps whitespace-only runs in <span> tags. Reportlab builds an
    empty text fragment from those and then indexes into it, which blows up
    with IndexError. Unwrapping them keeps the colours and drops the crash.
    """
    for _ in range(6):
        before = html_text
        html_text = _EMPTY_SPAN.sub("", html_text)
        html_text = _WS_SPAN.sub(r"\1", html_text)
        if html_text == before:
            break
    return html_text


def md_to_html(text: str) -> str:
    MD.reset()
    return clean_spans(MD.convert(text))


def render_doc(name: str, anchor: str, eyebrow: str) -> str:
    raw = (COURSE / name).read_text(encoding="utf-8")
    raw = strip_html_comments(raw)
    raw = sub_emoji(raw)
    raw = convert_details(raw)
    raw = task_lists(raw)
    raw = rewrite_links(raw)

    body = md_to_html(raw)

    # The lesson's own H1 is the title. Wrap it with the part eyebrow above
    # and an anchor below, so cross-references can link to it, rather than
    # adding a second heading of our own.
    body = re.sub(
        r"<h1>",
        f'<div class="lessonhead"><div class="eyebrow">{eyebrow}</div>'
        f'<h1><a name="{anchor}">',
        body,
        count=1,
    )
    body = re.sub(r"</h1>", "</a></h1></div>", body, count=1)
    return body


def render_code(path_str: str) -> str:
    src = (COURSE / path_str).read_text(encoding="utf-8")
    MD.reset()
    highlighted = MD.convert("```python\n" + src + "\n```")
    return (
        f'<h2 class="listing">{TITLES.get(path_str, path_str)}</h2>\n'
        f'<div class="listing-src">{highlighted}</div>'
    )


# ------------------------------------------------------------------ the CSS
CSS = """
@font-face { font-family: 'DJV'; src: url('__FONTDIR__/DejaVuSans.ttf'); }
@font-face { font-family: 'DJVB'; src: url('__FONTDIR__/DejaVuSans-Bold.ttf'); }
@font-face { font-family: 'DJVI'; src: url('__FONTDIR__/DejaVuSans-Oblique.ttf'); }
@font-face { font-family: 'DJVM'; src: url('__FONTDIR__/DejaVuSansMono.ttf'); }
@font-face { font-family: 'DJVS'; src: url('__FONTDIR__/DejaVuSerif.ttf'); }

@page {
  size: A4;
  margin: 2.0cm 1.75cm 2.0cm 1.75cm;
  @frame footer {
    -pdf-frame-content: footerContent;
    left: 1.75cm; right: 1.75cm; bottom: 0.75cm; height: 0.7cm;
  }
}

#footerContent {
  font-family: 'DJV'; font-size: 8pt; color: #7a7a7a;
  text-align: center;
}

body {
  font-family: 'DJV'; font-size: 9.6pt; line-height: 1.52;
  color: #1d2530;
}

/* ---------- headings ---------- */
h1 {
  font-family: 'DJVB'; font-size: 19pt; color: #123c56;
  margin: 0 0 4pt 0; padding-bottom: 6pt;
  border-bottom: 1.6pt solid #123c56;
  page-break-before: always; page-break-after: avoid;
}
h2 {
  font-family: 'DJVB'; font-size: 12.6pt; color: #123c56;
  margin: 16pt 0 5pt 0; page-break-after: avoid;
  -pdf-outline: false;
}
h3 {
  font-family: 'DJVB'; font-size: 10.6pt; color: #1d5b7d;
  margin: 12pt 0 4pt 0; page-break-after: avoid;
  -pdf-outline: false;
}
h4 {
  font-family: 'DJVB'; font-size: 9.8pt; color: #34495e;
  margin: 9pt 0 3pt 0; page-break-after: avoid;
  -pdf-outline: false;
}

.lessonhead {
  margin-bottom: 10pt;
  page-break-before: always; page-break-after: avoid;
}
.lessonhead h1 { page-break-before: avoid; page-break-after: avoid; }
.eyebrow {
  font-family: 'DJVB'; font-size: 8pt; color: #0b6e99;
  letter-spacing: 0.9pt; margin-bottom: 3pt;
  page-break-after: avoid;
}

/* ---------- text ---------- */
p { margin: 0 0 7pt 0; text-align: justify; }
strong { font-family: 'DJVB'; }
em { font-family: 'DJVI'; }
a { color: #0b6e99; text-decoration: none; }
ul, ol { margin: 0 0 8pt 0; padding-left: 16pt; }
li { margin-bottom: 3pt; }
hr { border: none; border-top: 0.6pt solid #c8d2da; margin: 14pt 0; }

code {
  font-family: 'DJVM'; font-size: 8.2pt;
  background: #eef2f5; padding: 0 2pt; color: #a03a3a;
}

pre, .codehilite pre {
  font-family: 'DJVM'; font-size: 7.9pt; line-height: 1.42;
  background: #f4f7f9; border-left: 2.4pt solid #0b6e99;
  padding: 7pt 8pt; margin: 0 0 9pt 0;
  white-space: pre;
}
.codehilite { margin: 0 0 9pt 0; }

/* ---------- tables ---------- */
table { width: 100%; margin: 0 0 10pt 0; }
th {
  font-family: 'DJVB'; font-size: 8.2pt; background: #e6eef4;
  color: #123c56; border: 0.5pt solid #9fb3c2; padding: 3.6pt 4pt;
  text-align: left;
}
td {
  font-size: 8.3pt; border: 0.5pt solid #c2cfd9; padding: 3.4pt 4pt;
  vertical-align: top;
}

/* ---------- callouts ---------- */
blockquote {
  border-left: 2.6pt solid #0b6e99; background: #f2f8fb;
  margin: 0 0 10pt 0; padding: 7pt 9pt;
}
blockquote p { margin: 0 0 5pt 0; }
blockquote p:last-child { margin-bottom: 0; }

.dropbox {
  border: 0.7pt dashed #7fa3b8; background: #fafcfd;
  padding: 7pt 9pt; margin: 0 0 10pt 0;
}
.dropsum {
  font-family: 'DJVB'; font-size: 9pt; color: #0b6e99;
  margin: 0 0 5pt 0;
}

/* ---------- cover ---------- */
.cover { text-align: center; padding-top: 3.2cm; }
.cover .kicker {
  font-family: 'DJVB'; font-size: 9.5pt; color: #0b6e99;
  letter-spacing: 2.2pt; margin-bottom: 26pt;
}
.cover .title {
  font-family: 'DJVB'; font-size: 30pt; color: #123c56;
  line-height: 1.18; margin-bottom: 6pt;
}
.cover .subtitle {
  font-family: 'DJVI'; font-size: 13pt; color: #4a6274;
  margin-bottom: 30pt;
}
.cover .rule { border-top: 2pt solid #123c56; width: 42%;
  margin: 0 auto 26pt auto; }
.cover .blurb {
  font-size: 10.5pt; color: #33475b; line-height: 1.62;
  width: 82%; margin: 0 auto 30pt auto; text-align: center;
}
.cover .meta { font-size: 9.5pt; color: #61748a; line-height: 1.7; }

/* ---------- contents ---------- */
.toc-part {
  font-family: 'DJVB'; font-size: 10.4pt; color: #123c56;
  margin: 15pt 0 5pt 0; padding-bottom: 3pt;
  border-bottom: 0.8pt solid #c2cfd9;
}
.toc-row { margin: 0 0 3.5pt 0; font-size: 9.4pt; }
.toc-num { color: #0b6e99; font-family: 'DJVB'; }

/* ---------- part dividers ---------- */
.partdiv { text-align: center; padding-top: 6.5cm; }
.partdiv .pnum {
  font-family: 'DJVB'; font-size: 27pt; color: #0b6e99;
  letter-spacing: 3pt; margin-bottom: 8pt;
}
.partdiv .pname {
  font-family: 'DJVB'; font-size: 23pt; color: #123c56; margin-bottom: 14pt;
}
.partdiv .pdesc {
  font-family: 'DJVI'; font-size: 11pt; color: #54697d;
  width: 70%; margin: 0 auto;
}

/* ---------- appendix listings ---------- */
h2.listing {
  font-size: 11.4pt; color: #123c56; margin: 18pt 0 5pt 0;
  border-bottom: 0.6pt solid #c2cfd9; padding-bottom: 3pt;
  page-break-after: avoid;
}
.listing-src pre { font-size: 7.2pt; line-height: 1.38; }

.intro-note {
  background: #f2f8fb; border: 0.7pt solid #c2d9e6;
  padding: 9pt 11pt; margin: 0 0 12pt 0; font-size: 9.3pt;
}
"""

PYGMENTS_EXTRA = HtmlFormatter(style="default").get_style_defs(".codehilite")


# ---------------------------------------------------------------- assembly
def build_html() -> str:
    css = CSS.replace("__FONTDIR__", str(FONT_DIR))
    parts = [
        "<html><head><meta charset='utf-8'><style>",
        css,
        PYGMENTS_EXTRA,
        "</style></head><body>",
        '<div id="footerContent">'
        "Generative AI: From First Prompt to First App"
        " &nbsp;·&nbsp; Page <pdf:pagenumber/> of <pdf:pagecount/>"
        "</div>",
    ]

    # ---------- cover ----------
    parts.append(f"""
    <div class="cover">
      <div class="kicker">A BEGINNER-FRIENDLY COURSE</div>
      <div class="title">Generative AI</div>
      <div class="subtitle">From First Prompt to First App</div>
      <div class="rule"></div>
      <div class="blurb">
        Eighteen lessons taking you from your first conversation with an AI
        assistant to building real applications with the API.<br/><br/>
        Parts 1 and 2 need nothing but a web browser.<br/>
        Part 3 is where you start writing code.<br/>
        Part 4 is where you build something of your own.
      </div>
      <div class="meta">
        By Gide &nbsp;·&nbsp; {COURSE_DATE}<br/>
        Free to use and share
      </div>
    </div>
    """)

    # ---------- how to use ----------
    parts.append(f"""
    <h1><a name="howto">How to Use This Book</a></h1>

    <div class="intro-note">
      This PDF collects the whole course in reading order. Every lesson is
      self-contained, so you can skip around — but Parts 1 and 2 assume no
      prior experience, and Part 3 assumes you have worked through them.
    </div>

    <h2>What you need</h2>
    <ul>
      <li>A phone or computer with an internet connection.</li>
      <li>For Parts 1 and 2: a free account with any major AI assistant.
          Nothing else.</li>
      <li>For Part 3: Python 3.9 or newer, and about one US dollar of API
          credit. Module 11 walks through the setup, including setting a
          spending cap before you spend anything.</li>
    </ul>

    <h2>How the lessons work</h2>
    <p>
      Each lesson explains one idea, then asks you to try it. The exercises
      are short — usually ten to fifteen minutes — and they are where the
      skill actually forms. Reading without doing teaches very little here.
    </p>

    <h2>Three rules</h2>
    <ul>
      <li><strong>Do the exercises.</strong> The skill is in your hands,
          not your head.</li>
      <li><strong>Never ship unchecked output.</strong> AI is confidently,
          fluently wrong surprisingly often. Module 5 is the module that
          keeps you out of trouble.</li>
      <li><strong>Build something you actually want.</strong> The projects
          in Part 4 are templates. Change them to solve a problem you
          have.</li>
    </ul>

    <h2>A note on how fast this field moves</h2>
    <p>
      Model names, prices, and features change every few months. This book
      was compiled in {COURSE_DATE}. Where a specific model name or price
      appears, treat it as <em>this was true when written</em> — every such
      claim links to the official source so you can confirm it. The durable
      ideas — how to specify what you want, how to iterate, how to verify —
      do not change.
    </p>
    """)

    # ---------- contents ----------
    parts.append('<h1><a name="contents">Contents</a></h1>')

    # group the lesson rows under their part heading
    rows_by_part = {}
    current = None
    for item in STRUCTURE:
        if item[0] == "part":
            current = f"{item[1]} · {item[2]}" if item[2] else item[1]
            rows_by_part[current] = []
        else:
            fname, anchor = item[1], item[2]
            title = TITLES.get(fname, fname)
            num = re.match(r"(\d+)", fname)
            num = f"{num.group(1)} · " if num else ""
            rows_by_part[current].append(
                f'<div class="toc-row"><span class="toc-num">{num}</span>'
                f'<a href="#{anchor}">{title}</a></div>'
            )
    for part, rows in rows_by_part.items():
        parts.append(f'<div class="toc-part">{part}</div>')
        parts.extend(rows)

    # ---------- body ----------
    eyebrow = ""
    for item in STRUCTURE:
        if item[0] == "part":
            _, pnum, pname, pdesc = item
            eyebrow = f"{pnum} · {pname}" if pname else pnum
            parts.append(
                f'<div class="partdiv"><div class="pnum">{pnum}</div>'
                f'<div class="pname">{pname}</div>'
                f'<div class="pdesc">{pdesc}</div></div>'
            )
        elif item[0] == "doc":
            _, fname, anchor = item
            parts.append(render_doc(fname, anchor, eyebrow))
        elif item[0] == "code":
            _, path_str, _ = item
            parts.append(render_code(path_str))

    parts.append("</body></html>")
    return "\n".join(parts)


def main() -> int:
    global COURSE_DATE
    COURSE_DATE = "September 2026"

    document = build_html()

    with open(OUT, "wb") as fh:
        result = pisa.CreatePDF(document, dest=fh, resource_policy=POLICY)

    if result.err:
        print("PDF generation reported errors:")
        for msg in result.err.splitlines()[:40]:
            print("  ", msg)
        return 1

    size_mb = OUT.stat().st_size / 1_048_576
    print(f"Wrote {OUT}")
    print(f"  {size_mb:.2f} MB")
    return 0


COURSE_DATE = "September 2026"

if __name__ == "__main__":
    sys.exit(main())
