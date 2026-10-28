"""Technical proofs: one A3 landscape page per panel, with trim / safe / hardware
overlays, dimensions and a coverage summary. This is the sheet the client signs
and the printer sets against — the release files carry no overlays."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.units import mm as MM
from PIL import Image

import brand as B
import panels as PN
import photos as P
import render as R
import docutil as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "one-way-vision-film", "proofs")
WORK = os.path.join(ROOT, "source", ".work")
A3L = landscape(A3)


def panel_pdf(panel, path):
    c = rl_canvas.Canvas(path, pagesize=(panel["w"] * MM, panel["h"] * MM))
    c.scale(MM, MM)
    R.draw_artwork(c, panel, bleed=12, hardware_layer=False)
    c.showPage()
    c.save()


def build():
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "03-Technical-Proofs.pdf")
    c = rl_canvas.Canvas(path, pagesize=A3L)
    c.setTitle("Technical proofs — one-way vision film")

    import pypdfium2 as pdfium

    W, H = A3L
    total = len(PN.PANELS)
    for n, p in enumerate(PN.PANELS, start=1):
        B.register_fonts()
        c.setFillColor(B.WHITE)
        c.rect(0, 0, W, H, stroke=0, fill=1)
        # frame / header
        c.setFillColor(B.NAVY)
        c.rect(0, H - 26 * MM, W, 26 * MM, stroke=0, fill=1)
        B.label(c, 18 * MM, H - 16 * MM, "TECHNICAL PROOF  ·  NOT FOR PRODUCTION COLOUR",
                4.2, B.TEAL_LT, "Inter-600", 1.7)
        B.caps(c, W - 18 * MM, H - 17 * MM,
               f"{p['id']}   {p['dept']}", 6.4, B.WHITE, "Manrope-700", 0.6, "right")
        B.label(c, 18 * MM, 12 * MM,
                f"GMC / OWV / 03  ·  Rev R1  ·  2026-10-28  ·  PROVISIONAL  ·  sheet {n} of {total}",
                3.6, B.GREY, "Inter-400", 1.2)

        # artwork at 1:10 (A3 height allows ~210 mm at 1:10 for 2100 mm)
        scale = (H - 90 * MM) / (p["h"] * MM)
        pw = p["w"] * MM * scale
        ph = p["h"] * MM * scale
        ax, ay = 34 * MM, 50 * MM

        # render the panel to an image at adequate px, then place
        tmp_pdf = os.path.join(WORK, f"proof_{p['id']}.pdf")
        panel_pdf(p, tmp_pdf)
        doc = pdfium.PdfDocument(tmp_pdf)
        page = doc[0]
        px_h = 2400
        im = page.render(scale=px_h / page.get_size()[1]).to_pil()
        png = os.path.join(WORK, f"proof_{p['id']}.png")
        im.save(png)
        doc.close()

        c.drawImage(png, ax, ay, pw, ph, mask=None)
        # trim line + safe zone + hardware overlay
        c.setStrokeColor(B.NAVY)
        c.setLineWidth(0.3)
        c.rect(ax, ay, pw, ph, stroke=1, fill=0)
        c.setStrokeColor(B.TEAL)
        c.setDash(3, 2.2)
        c.setLineWidth(0.35)
        safe = PN.SAFE_MM * MM * scale
        c.rect(ax + safe, ay + safe, pw - 2 * safe, ph - 2 * safe, stroke=1, fill=0)
        # kick zone
        kick = PN.KICK_CLEAR_MM * MM * scale
        c.setStrokeColor(B.GREEN)
        c.line(ax, ay + kick, ax + pw, ay + kick)
        # hardware
        hw = p.get("handle")
        if hw:
            side, inset = hw
            hx = ax + (pw - inset * MM * scale) if side == "right" else ax + inset * MM * scale
            c.setStrokeColor(B.TEAL_LT)
            c.setLineWidth(0.8)
            c.line(hx, ay + 900 * MM * scale, hx, ay + 1220 * MM * scale)
            c.setFillColor(B.TEAL_LT)
            for yy in (900, 1220):
                c.circle(hx, ay + yy * MM * scale, 2.0, stroke=0, fill=1)
        c.setDash()

        if p["layout"] == "double":
            c.setStrokeColor(B.GREY)
            c.setDash(4, 3)
            c.line(ax + pw / 2, ay - 3 * MM, ax + pw / 2, ay + ph + 3 * MM)
            c.setDash()
            B.label(c, ax + pw / 2 + 2 * MM, ay + ph + 4 * MM, "MEETING STILE", 2.6, B.GREY,
                    "Inter-600", 0.7)

        # dimensions
        c.setStrokeColor(B.NAVY_MID)
        c.setLineWidth(0.25)
        dim_y = ay - 8 * MM
        c.line(ax, dim_y, ax + pw, dim_y)
        for xx in (ax, ax + pw):
            c.line(xx, dim_y - 2 * MM, xx, dim_y + 2 * MM)
        B.label(c, ax + pw / 2, dim_y - 6 * MM, f"{p['w']} mm", 3.4, B.NAVY, "Inter-500", 0.8,
                "center")
        dim_x = ax + pw + 10 * MM
        c.line(dim_x, ay, dim_x, ay + ph)
        for yy in (ay, ay + ph):
            c.line(dim_x - 2 * MM, yy, dim_x + 2 * MM, yy)
        c.saveState()
        c.translate(dim_x + 6 * MM, ay + ph / 2)
        c.rotate(90)
        B.label(c, 0, 0, f"{p['h']} mm", 3.4, B.NAVY, "Inter-500", 0.8, "center")
        c.restoreState()

        # legend, below the artwork
        items = [("TRIM", B.NAVY), ("SAFE ZONE 25 mm", B.TEAL), ("KICK ZONE 120 mm", B.GREEN),
                 ("HANDLE POSITION", B.TEAL_LT)]
        for i, (txt, col) in enumerate(items):
            xx = ax + i * 34 * MM
            c.setFillColor(col)
            c.rect(xx, ay - 26 * MM, 6 * MM, 1.2 * MM, stroke=0, fill=1)
            B.label(c, xx + 8 * MM, ay - 26.5 * MM, txt, 2.6, B.GREY, "Inter-600", 0.7)

        # right column: spec block
        cx = ax + pw + 26 * MM
        cw = W - cx - 18 * MM
        y = H - 44 * MM
        B.label(c, cx, y, "PANEL", 3.6, B.TEAL, "Inter-600", 1.6)
        y -= 9 * MM
        B.caps(c, cx, y, p["dept"], 8.0, B.NAVY, "Manrope-800", 0.4, max_width=cw)
        y -= 9 * MM
        B.label(c, cx, y, f"{p['sub']}  ·  {p['orientation']}", 3.2, B.GREY, "Inter-400", 0.5)
        y -= 12 * MM

        rows = [("Trim size", f"{p['w']} × {p['h']} mm  ({p['w']/10:.0f} × {p['h']/10:.0f} cm)"),
                ("Aspect ratio", p["aspect"]),
                ("Bleed", f"{PN.BLEED_MM:.0f} mm all round — plot {p['w']+2*PN.BLEED_MM:.0f} × "
                          f"{p['h']+2*PN.BLEED_MM:.0f} mm"),
                ("Safe zone", f"{PN.SAFE_MM:.0f} mm inside trim"),
                ("Headline cap height", f"{p['title_cap']} mm"),
                ("Photograph", (P.PHOTOS[p['photo']]["asset"] + " — " +
                                P.PHOTOS[p['photo']]["creator"]) if p["photo"] else "None (graphic panel)"),
                ("Photo coverage", (f"{(p['h']-p['photo_bottom'])/p['h']*100:.0f}% of panel area "
                                    if p["photo"] else "0%")),
                ("Hardware", (f"{hw[0].title()} lever/pull, {hw[1]} mm from the meeting edge"
                              if hw else "None — fixed glazing")),
                ("Resolution", (P.audit(p["photo"], p["w"], p["h"] - p["photo_bottom"],
                                        p["focus"])["status"] if p["photo"] else "vector"))]
        for k, v in rows:
            B.label(c, cx, y, k, 2.9, B.GREY, "Inter-500", 1.1)
            B.label(c, cx + 44 * MM, y, str(v), 3.0, B.NAVY, "Inter-500", 0.3,
                    max_width=cw - 44 * MM)
            c.setStrokeColor(B.MIST)
            c.setLineWidth(0.2)
            c.line(cx, y - 2.6 * MM, cx + cw, y - 2.6 * MM)
            y -= 7.2 * MM

        y -= 4 * MM
        B.label(c, cx, y, "OBSTRUCTIONS TO RESPECT", 3.4, B.TEAL, "Inter-600", 1.5)
        y -= 6 * MM
        y = D.bullets(c, cx, y, p["hardware"], cw, 3.0, B.NAVY_MID, 1.4)

        y -= 3 * MM
        B.label(c, cx, y, "PRODUCTION NOTE", 3.4, B.TEAL, "Inter-600", 1.5)
        y -= 6 * MM
        y = D.para(c, cx, y, p["print_notes"], cw, 3.0, B.NAVY_MID, 1.55)
        y -= 3 * MM
        D.para(c, cx, y, p.get("kick_note", ""), cw, 3.0, B.GREY, 1.55)

        c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    print("built", build())
