"""Shared document furniture for the A4 landscape reports."""
import os

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm as MM

import cp_brand as B


def use_brand(mod):
    global B
    B = mod

PAGE = landscape(A4)
PW, PH = PAGE
M = 16 * MM
DOC_NAVY = B.NAVY


def _t(s):
    """Identity translation: prose written for the CarePoint set, re-branded."""
    if not isinstance(s, str):
        return s
    out = s
    for a, b in (("CarePoint Medical Center", getattr(B, "CLIENT_FULL", "").title()),
                 ("CarePoint", getattr(B, "CLIENT_TITLE", "CarePoint")),
                 ("CAREPOINT", getattr(B, "CLIENT", "CAREPOINT"))):
        out = out.replace(a, b)
    return out


def new_doc(path, title, subject="GMC one-way vision film"):
    B.register_fonts()
    c = canvas.Canvas(path, pagesize=PAGE)
    c.setTitle(title)
    c.setAuthor("GMC One-Way Vision Film Project")
    c.setSubject(subject)
    return c


def page_bg(c, header, footer_left, page_no, total=None, eyebrow="MEDICAL CENTER  ·  ONE-WAY VISION FILM"):
    c.setFillColor(B.WHITE)
    c.rect(0, 0, PW, PH, stroke=0, fill=1)
    # header
    c.setFillColor(B.NAVY)
    c.rect(0, PH - 22 * MM, PW, 22 * MM, stroke=0, fill=1)
    B.label(c, M, PH - 13.5 * MM, _t(eyebrow), 4.0, B.TEAL_LT, "Inter-500", 1.6)
    B.caps(c, PW - M, PH - 14.0 * MM, _t(header), 5.6, B.WHITE, "Manrope-700",
           tracking_mm=0.6, align="right")
    # footer
    c.setStrokeColor(B.MIST)
    c.setLineWidth(0.3)
    c.line(M, 12 * MM, PW - M, 12 * MM)
    B.label(c, M, 8 * MM, _t(footer_left), 3.6, B.GREY, "Inter-400", 1.2)
    pg = f"{page_no}" if total is None else f"{page_no} / {total}"
    B.label(c, PW - M, 8 * MM, pg, 3.6, B.GREY, "Inter-500", 1.2, "right")


def h1(c, y, text, cap=8.4, color=B.NAVY):
    text = _t(text)
    B.caps(c, M, y, text, cap, color, "Manrope-800", tracking_mm=0.35)
    return y - cap * 1.9


def h2(c, y, text, cap=4.6, color=B.TEAL):
    text = _t(text)
    B.label(c, M, y, text, cap, color, "Inter-600", 1.8)
    return y - cap * 2.0


def para(c, x, y, text, width, cap=3.5, color=B.NAVY_MID, leading=1.72,
         weight="Inter-400"):
    """Simple word-wrapped paragraph in mm units."""
    words = _t(text).split()
    line, lines = "", []
    c.setFont(weight, B.font_for(cap))
    for w in words:
        trial = (line + " " + w).strip()
        if c.stringWidth(trial, weight, B.font_for(cap)) <= width:
            line = trial
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    for ln in lines:
        c.setFillColor(color)
        c.setFont(weight, B.font_for(cap))
        c.drawString(x, y, ln)
        y -= cap * leading
    return y


def bullets(c, x, y, items, width, cap=3.5, color=B.NAVY_MID, gap=1.9):
    for it in items:
        it = _t(it)
        c.setFillColor(B.TEAL)
        c.circle(x + 1.0 * MM, y + cap * 0.34, 0.55 * MM, stroke=0, fill=1)
        y = para(c, x + 4.0 * MM, y, it, width - 4 * MM, cap, color)
        y -= gap * MM
    return y


def table(c, x, y, cols, rows, row_h=7.0 * MM, head_h=7.5 * MM,
          cap=3.1, head_cap=3.0, zebra=True, col_colors=None):
    """cols = [(label, width_mm, align)]; rows = list of list of str."""
    total_w = sum(w for _, w, _ in cols)
    # header
    c.setFillColor(B.NAVY)
    c.rect(x, y - head_h, total_w * MM, head_h, stroke=0, fill=1)
    cx = x
    for label, wdt, align in cols:
        label = _t(label)
        if align == "right":
            B.label(c, cx + (wdt - 2) * MM, y - head_h + 2.6 * MM, label, head_cap,
                    B.WHITE, "Inter-600", 0.9, "right")
        else:
            B.label(c, cx + 2 * MM, y - head_h + 2.6 * MM, label, head_cap,
                    B.WHITE, "Inter-600", 0.9)
        cx += wdt * MM
    yy = y - head_h
    for i, row in enumerate(rows):
        rh = row_h
        if zebra and i % 2 == 1:
            c.setFillColor(B.PAPER)
            c.rect(x, yy - rh, total_w * MM, rh, stroke=0, fill=1)
        cx = x
        for j, (cell, (label, wdt, align)) in enumerate(zip(row, cols)):
            colour = B.NAVY
            if col_colors and j in col_colors:
                colour = col_colors[j]
            cell = _t(str(cell))
            cy = yy - rh + 2.4 * MM
            if align == "right":
                B.label(c, cx + (wdt - 2) * MM, cy, str(cell), cap, colour, "Inter-500",
                        0.2, "right")
            else:
                B.label(c, cx + 2 * MM, cy, str(cell), cap, colour, "Inter-500", 0.2)
            cx += wdt * MM
        c.setStrokeColor(B.MIST)
        c.setLineWidth(0.2)
        c.line(x, yy - rh, x + total_w * MM, yy - rh)
        yy -= rh
    return yy
