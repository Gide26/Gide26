"""Render trim-only panel previews (PNG) for the lookbook and mockups."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pypdfium2 as pdfium
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm as MM

import panels as PN
import render as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "source", ".work", "previews")


def preview(panel, px_height=1400):
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, f"{panel['id']}_{px_height}.png")
    if os.path.exists(out):
        return out
    tmp = os.path.join(CACHE, f"_{panel['id']}.pdf")
    c = canvas.Canvas(tmp, pagesize=(panel["w"] * MM, panel["h"] * MM))
    c.scale(MM, MM)
    R.draw_artwork(c, panel, bleed=0, hardware_layer=False)
    c.showPage()
    c.save()
    doc = pdfium.PdfDocument(tmp)
    page = doc[0]
    img = page.render(scale=px_height / page.get_size()[1]).to_pil()
    img.save(out, "PNG")
    doc.close()
    os.remove(tmp)
    return out


if __name__ == "__main__":
    for p in PN.PANELS:
        print(preview(p))
