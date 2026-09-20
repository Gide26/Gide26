#!/usr/bin/env python3
"""Assemble the pilot research proposal (markdown files) into a single .docx."""
import re
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

PARTS = [
    ("TITLE", None),
    ("00-Front-Matter-UCU-KIU.md", "FRONT MATTER (Template)"),
    ("Chapter-1-Introduction-DRAFT.md", None),
    ("Chapter-2-Literature-Review.md", None),
    ("Chapter-3-Research-Methodology-PILOT.md", None),
    ("Chapter-4-PILOT-Findings.md", None),
    ("Chapter-5-Summary-Conclusions-Framework.md", None),
    ("References.md", None),
    ("Pilot-Instruments-Print-Ready.md", "APPENDIX A: PILOT RESEARCH INSTRUMENTS"),
    ("Theory-of-Change.md", "APPENDIX B: THEORY OF CHANGE"),
    ("Gathered-Editions-Log.md", "APPENDIX C: GATHERED EDITIONS LOG"),
]

TITLE_BLOCK = """ASSESSING THE IMPACTS OF NEW VISION OVER THE PAST 40 YEARS OF ITS EXISTENCE (1986-2026)

A PILOT RESEARCH PROPOSAL

[YOUR FULL NAME]
[REG. NO.]

A Research Proposal Submitted to [Department, School, University] in Partial Fulfilment of the Requirements for the Award of [Degree]

[Month, Year]

WORKING DRAFT - assembled automatically on 20 September 2026. Status banners inside chapters show what is draft vs final. Chapter Two full prose to be pasted from the researcher's approved draft."""

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.5
for i in (1, 2, 3):
    hs = doc.styles[f"Heading {i}"]
    hs.font.name = "Times New Roman"
    hs.font.color.rgb = RGBColor(0, 0, 0)

def add_runs(para, text):
    # inline **bold**, *italic*, `code`, ☐ for [ ]
    text = text.replace("[ ]", "\u2610").replace("[x]", "\u2611").replace("[X]", "\u2611")
    token = re.split(r"(\*\*.+?\*\*|\*[^*]+?\*|`.+?`)", text)
    for t in token:
        if not t:
            continue
        if t.startswith("**") and t.endswith("**") and len(t) > 4:
            r = para.add_run(t[2:-2]); r.bold = True
        elif t.startswith("*") and t.endswith("*") and len(t) > 2:
            r = para.add_run(t[1:-1]); r.italic = True
        elif t.startswith("`") and t.endswith("`") and len(t) > 2:
            r = para.add_run(t[1:-1]); r.font.name = "Courier New"; r.font.size = Pt(10)
        else:
            # strip links [text](url) -> text (url)
            t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", t)
            para.add_run(t)

def add_table(lines):
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    tbl = doc.add_table(rows=len(rows), cols=ncols)
    tbl.style = "Table Grid"
    for i, r in enumerate(rows):
        for j in range(ncols):
            cell = tbl.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            txt = r[j] if j < len(r) else ""
            add_runs(p, txt)
            for run in p.runs:
                run.font.size = Pt(10)
            if i == 0:
                for run in p.runs:
                    run.bold = True
    doc.add_paragraph()

def process_md(path, override_title=None):
    with open(path) as f:
        lines = f.read().splitlines()
    if override_title:
        doc.add_heading(override_title, level=1)
    i, buf_table = 0, []
    def flush_table():
        if buf_table:
            add_table(buf_table); buf_table.clear()
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("|") and "|" in s[1:]:
            buf_table.append(ln); i += 1; continue
        flush_table()
        if not s:
            i += 1; continue
        if s.startswith("```"):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                p = doc.add_paragraph(); r = p.add_run(lines[i]); r.font.name = "Courier New"; r.font.size = Pt(10)
                i += 1
            i += 1; continue
        if s in ("---", "***"):
            i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)", s)
        if m:
            doc.add_heading(re.sub(r"\*\*(.*?)\*\*", r"\1", m.group(2)), level=min(len(m.group(1)), 3)); i += 1; continue
        if s.startswith(">"):
            p = doc.add_paragraph(); p.paragraph_format.left_indent = Pt(24)
            add_runs(p, s.lstrip("> ").strip())
            for r in p.runs: r.italic = True
            i += 1; continue
        m = re.match(r"^(\s*)[-*]\s+(.*)", ln)
        if m:
            p = doc.add_paragraph(style="List Bullet"); add_runs(p, m.group(2)); i += 1; continue
        m = re.match(r"^(\s*)\d+[.)]\s+(.*)", ln)
        if m:
            p = doc.add_paragraph(style="List Number"); add_runs(p, m.group(2)); i += 1; continue
        p = doc.add_paragraph(); add_runs(p, s); i += 1
    flush_table()

for fname, title in PARTS:
    if fname == "TITLE":
        for j, block in enumerate(TITLE_BLOCK.split("\n\n")):
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(block); r.bold = (j == 0)
            r.font.size = Pt(16) if j == 0 else Pt(13)
        doc.add_page_break(); continue
    process_md(fname, title)
    doc.add_page_break()

out = "New-Vision-40-Years-PILOT-Proposal.docx"
doc.save(out)
print("saved", out)
