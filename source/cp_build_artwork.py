import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm as MM
import cp_brand as B
import cp_panels as PN
import cp_render as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "carepoint", "artwork")


def build(p, path):
    w, h = p["w"], p["h"]
    bl, sl = PN.BLEED_MM, PN.SLUG_MM
    pw, ph = w + bl * 2, h + bl * 2 + sl
    c = canvas.Canvas(path, pagesize=(pw * MM, ph * MM))
    c.setTitle(f"{p['id']} {p['service']} — CarePoint one-way vision artwork")
    c.setAuthor("CarePoint Medical Center — one-way vision film project")
    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, pw, ph, stroke=0, fill=1)
    c.saveState()
    c.translate(bl, bl + sl)
    c.scale(MM, MM)
    R.draw(c, p, bleed=bl)
    c.restoreState()

    # crop marks
    c.saveState()
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.3)
    x0, y0 = bl * MM, (bl + sl) * MM
    x1, y1 = (bl + w) * MM, (bl + sl + h) * MM
    L = 7 * MM
    for (x, y) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        c.line(x - L, y, x - 2 * MM, y); c.line(x + 2 * MM, y, x + L, y)
        c.line(x, y - L, x, y - 2 * MM); c.line(x, y + 2 * MM, x, y + L)
    c.restoreState()

    # slug strip
    c.setFillColor(B.WHITE)
    c.rect(0, 0, pw, sl, stroke=0, fill=1)
    c.setStrokeColorRGB(0.6, 0.6, 0.6)
    c.setLineWidth(0.2)
    c.line(0, sl, pw, sl)
    B.caps(c, 3, sl - 6.4, f"{p['id']}  |  CAREPOINT  |  {p['service']}  |  {w} x {h} mm  |  {p['orientation']}",
           2.6, B.CP_NAVY, "Inter-600", 0.3)
    B.caps(c, 3, sl - 10.6, f"ONE-WAY VISION FILM — {PN.FILM}  |  BLEED {bl:.0f} mm  |  SAFE {PN.SAFE_MM:.0f} mm  |  {PN.REVISION}  {PN.ISSUE_DATE}",
           2.3, B.CP_NAVY, "Inter-500", 0.25)
    B.caps(c, 3, sl - 14.6, "COMP: WEB PREVIEW PHOTO AT 110 ppi — RELINK ORIGINAL STOCK FILE BEFORE OUTPUT  |  MONOGRAM IS A RECREATION — REPLACE WITH CLIENT VECTOR LOGO",
           2.1, B.CP_NAVY_MD, "Inter-500", 0.2)
    B.caps(c, pw - 3, 3.2, "HARDWARE NOT SHOWN", 2.2, B.CP_GREY, "Inter-500", 0.4, "right")
    c.showPage(); c.save()
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for p in PN.PANELS:
        f = build(p, os.path.join(OUT, p["id"] + ".pdf"))
        print("built", os.path.basename(f), f"{os.path.getsize(f)/1024:.0f} KB")
