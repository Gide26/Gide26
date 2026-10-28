"""Produce true-size, print-intent PDFs per panel (bleed + slug + marks)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm as MM

import brand as B
import panels as PN
import render as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "one-way-vision-film", "artwork")


def build(panel, out_path):
    w, h = panel["w"], panel["h"]
    bl, slug = PN.BLEED_MM, PN.SLUG_MM
    pw, ph = w + bl * 2, h + bl * 2 + slug
    c = canvas.Canvas(out_path, pagesize=(pw * MM, ph * MM))
    c.setTitle(f"{panel['id']} {panel['dept']} — one-way vision artwork")
    c.setAuthor("GMC One-Way Vision Film Project")
    c.setSubject("Perforated one-way vision graphics — PROVISIONAL")

    # background covering the full page incl. slug, so nothing white shows
    c.saveState()
    c.setFillColor(B.NAVY)
    c.rect(0, 0, pw, ph, stroke=0, fill=1)
    c.restoreState()

    c.saveState()
    c.translate(bl, bl + slug)
    c.scale(MM, MM)
    R.draw_artwork(c, panel, bleed=bl, hardware_layer=False)
    c.restoreState()

    # marks (page space, points)
    c.saveState()
    c.translate(bl * MM, (bl + slug) * MM)
    c.scale(MM, MM)
    B.crop_marks(c, w, h, bl and bl, mark=7.0, offset=0)
    c.restoreState()
    for x in (bl + w / 2, ):
        B.registration_target(c, x * MM, (bl * 0.5) * MM)

    # slug strip
    B.slug(c, 0, 0, pw, slug,
           [(f"{panel['id']}  |  {panel['dept']}  |  {w:.0f} x {h:.0f} mm  |  {panel['orientation']}", 2.9, B.NAVY, "Inter-600"),
            (f"ONE-WAY VISION FILM — {PN.FILM}  |  BLEED {bl:.0f} mm  |  SAFE {PN.SAFE_MM:.0f} mm  |  {PN.REVISION}  {PN.ISSUE_DATE}", 2.4, B.NAVY, "Inter-500"),
            ("COMP: PHOTOGRAPH PLACED FROM WEB PREVIEW AT 110 ppi — RELINK ORIGINAL STOCK FILE BEFORE OUTPUT  |  PLACEHOLDER IDENTITY — REPLACE LOGO WITH CLIENT ARTWORK", 2.2, B.NAVY_MID, "Inter-500")])
    c.setFillColor(B.WHITE)
    B.label(c, pw - 2.5, 2.2, "HARDWARE NOT SHOWN", 2.4, B.GREY, "Inter-500", 0.5, "right")

    c.showPage()
    c.save()
    return out_path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for p in PN.PANELS:
        f = build(p, os.path.join(OUT, f"{p['id']}.pdf"))
        print("built", f, f"{os.path.getsize(f)/1024:.0f} KB")
