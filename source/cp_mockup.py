"""CarePoint shopfront elevations — day and night, composed from the real artwork.

The door block is drawn to the measured proportions of the client's photograph:
four 900 mm leaves, 60 mm timber frames, two glass panes per leaf.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import pypdfium2 as pdfium
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.units import mm as MM

import cp_brand as B
import cp_panels as PN
import cp_render as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "carepoint", "lookbook", "mockups")
WORK = os.path.join(ROOT, "source", ".work")
S = 1.15                    # px per mm

FRAME = 60
LEAVES = 4
LEAF_W = 900
MULLION = 60
UPPER_H, LOWER_H = PN.UPPER_H, PN.LOWER_H
DOOR_H = FRAME + LOWER_H + FRAME + UPPER_H + FRAME

SIGN_H = 620
WALL_PAD = 260


def panel_png(panel, px_h=1500):
    os.makedirs(WORK, exist_ok=True)
    out = os.path.join(WORK, f"{panel['id']}_{px_h}.png")
    if os.path.exists(out):
        return out
    tmp = os.path.join(WORK, f"_{panel['id']}.pdf")
    c = rl_canvas.Canvas(tmp, pagesize=(panel["w"] * MM, panel["h"] * MM))
    c.scale(MM, MM)
    R.draw(c, panel, bleed=0)
    c.showPage()
    c.save()
    doc = pdfium.PdfDocument(tmp)
    page = doc[0]
    page.render(scale=px_h / page.get_size()[1]).to_pil().save(out)
    doc.close()
    os.remove(tmp)
    return out


def sign_png(night=False):
    """Recreated fascia sign, matching the client's existing board."""
    w_mm = LEAVES * LEAF_W + (LEAVES + 1) * MULLION
    path = os.path.join(WORK, f"sign_{'n' if night else 'd'}.png")
    c = rl_canvas.Canvas(path, pagesize=(w_mm * MM, SIGN_H * MM))
    B.register_fonts()
    c.scale(MM, MM)
    left = 300
    c.setFillColor(B.CP_MIST)
    c.rect(0, 0, left, SIGN_H, stroke=0, fill=1)
    c.setFillColor(B.CP_NAVY)
    c.rect(left, 0, w_mm - left, SIGN_H, stroke=0, fill=1)
    # monogram, centred in the white block
    B.monogram(c, (left - 190) / 2, (SIGN_H - 190) / 2, 190, dark=B.CP_NAVY,
               accent=B.CP_CYAN)
    x = left + 70
    B.caps(c, x, SIGN_H - 190, "CAREPOINT", 108, B.WHITE, "Manrope-800", 4.0,
           max_w=w_mm - x - 80)
    B.caps(c, x, SIGN_H - 292, "MEDICAL CENTER", 72, B.CP_CYAN, "Manrope-600", 9.0,
           max_w=w_mm - x - 80)
    B.label(c, x, SIGN_H - 366, B.SLOGAN, 40, B.CP_MIST, "Inter-400", 0.6)
    B.label(c, x, SIGN_H - 470, "TEL: " + B.TEL_FULL, 38, B.WHITE, "Inter-600", 0.8)
    c.showPage()
    c.save()
    doc = pdfium.PdfDocument(path)
    page = doc[0]
    img = page.render(scale=(w_mm * S) / page.get_size()[0]).to_pil()
    doc.close()
    if night:
        a = np.asarray(img).astype(np.float32)
        a = np.clip(a * 0.78 + 18, 0, 255)
        img = Image.fromarray(a.astype(np.uint8))
    return img


def wall(w, h, night=False):
    g = np.linspace(0.90, 0.76, h).reshape(h, 1)
    base = np.array([0.93, 0.91, 0.86]) if not night else np.array([0.16, 0.19, 0.26])
    arr = g[..., None] * base[None, None, :]
    yy, xx = np.mgrid[0:h, 0:w]
    vig = 1 - 0.18 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.4) / h) ** 2)
    arr = arr * np.clip(vig, 0.65, 1.06)[..., None]
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))


def build(night=False, name="M-01-front-day.png"):
    total_w = LEAVES * LEAF_W + (LEAVES + 1) * MULLION
    w = int((total_w + WALL_PAD * 2) * S)
    h = int((DOOR_H + SIGN_H + 380 + 260) * S)
    img = wall(w, h, night)
    d = ImageDraw.Draw(img, "RGBA")
    ox = int(WALL_PAD * S)
    floor_y = h - int(150 * S)

    # ground / step
    d.rectangle([0, floor_y, w, h], fill=(150, 146, 140) if not night else (26, 28, 34))
    d.rectangle([0, floor_y, w, floor_y + int(10 * S)], fill=(120, 116, 110)
                if not night else (18, 20, 26))
    if night:
        for i in range(int(60 * S)):
            a = int(46 * (1 - i / (60.0 * S)))
            d.rectangle([ox - int(40 * S), floor_y - i, w - ox + int(40 * S),
                         floor_y - i], fill=(255, 236, 200, a))

    # fascia sign
    sign = sign_png(night)
    sign_h = int(SIGN_H * S)
    img.paste(sign.resize((int(total_w * S) + int(2 * MULLION * S), sign_h),
                          Image.LANCZOS), (ox - int(MULLION * S), int(70 * S)))

    # opening reveal
    top_y = 70 + sign_h + int(40 * S)
    d.rectangle([ox - int(MULLION * S), top_y,
                 ox + int(total_w * S) + int(MULLION * S), floor_y],
                fill=(38, 40, 44) if not night else (12, 14, 18))

    # leaves
    frames = {"CP-08": 0, "CP-01": 1, "CP-02": 2, "CP-06": 3}
    assignment = {"CP-08": ["CP-07", "CP-08"], "CP-01": ["CP-01", "CP-04"],
                  "CP-02": ["CP-02", "CP-05"], "CP-06": ["CP-06", "CP-03"]}
    order = ["CP-08", "CP-01", "CP-02", "CP-06"]

    for i, key in enumerate(order):
        lx = ox + int((MULLION + i * (LEAF_W + MULLION)) * S)
        ly = top_y
        lw, lh = int(LEAF_W * S), floor_y - top_y
        # timber frame
        d.rectangle([lx, ly, lx + lw, ly + lh], fill=(196, 152, 74))
        d.rectangle([lx, ly, lx + lw, ly + int(5 * S)], fill=(214, 172, 96))
        # panes
        inner_x = lx + int(FRAME * S)
        pw = int((LEAF_W - 2 * FRAME) * S)
        lower_y = ly + lh - int(FRAME * S) - int(LOWER_H * S)
        upper_y = lower_y - int(FRAME * S) - int(UPPER_H * S)
        for pane_id, (py, ph) in zip(assignment[key],
                                     [(upper_y, int(UPPER_H * S)),
                                      (lower_y, int(LOWER_H * S))]):
            if pane_id is None:
                d.rectangle([inner_x, py, inner_x + pw, py + ph],
                            fill=(120, 132, 142) if not night else (10, 12, 16))
                continue
            panel = next(p for p in PN.PANELS if p["id"] == pane_id)
            art = Image.open(panel_png(panel)).convert("RGB").resize((pw, ph), Image.LANCZOS)
            if night:
                # interior lights on: the print reads as a lit translucent screen
                a = np.asarray(art).astype(np.float32) * 0.80 + 26
                art = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
            img.paste(art, (inner_x, py))

        # louvred transom above the panes
        if upper_y is not None:
            band_top = ly + int(6 * S)
            band_bot = upper_y
            if band_bot - band_top > int(20 * S):
                yy = band_top + int(8 * S)
                while yy < band_bot - int(6 * S):
                    d.rectangle([lx + int(8 * S), yy, lx + lw - int(8 * S),
                                 yy + int(3.2 * S)], fill=(168, 126, 58))
                    yy += int(11 * S)

        # handle on the opening leaves
        if key in ("CP-01", "CP-02"):
            hx = lx + lw - int(70 * S) if key == "CP-01" else lx + int(46 * S)
            d.rounded_rectangle([hx, ly + int(760 * S), hx + int(26 * S),
                                 ly + int(1360 * S)], radius=int(13 * S),
                                fill=(206, 210, 214))

    # reflection sheen over the whole opening
    sheen = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    sd.polygon([(ox, top_y), (ox + int(240 * S), top_y),
                (ox - int(120 * S), floor_y), (ox - int(360 * S), floor_y)],
               fill=(255, 255, 255, 26 if not night else 10))
    img = Image.alpha_composite(img.convert("RGBA"),
                                sheen.filter(ImageFilter.GaussianBlur(radius=14))).convert("RGB")

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    if img.width > 2600:
        img = img.resize((2600, round(img.height * 2600 / img.width)), Image.LANCZOS)
    img.save(path, "PNG", optimize=True)
    return path


if __name__ == "__main__":
    print(build(False, "M-01-shopfront-day.png"))
    print(build(True, "M-02-shopfront-night.png"))
