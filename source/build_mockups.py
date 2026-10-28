"""In-situ door mockups: composed elevation renders of the glass door sets.

These are photomontages — the real panel artwork is composited onto a drawn
elevation of the door and frame (no AI-generated photography is used).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFilter
import numpy as np

import panels as PN
import build_previews as PV

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "one-way-vision-film", "lookbook", "mockups")
MM_PER_PX = 3          # drawing scale: 3 px per mm
PAD = 120


def _wall(w, h):
    """Neutral plaster wall with soft light falloff."""
    grad = np.linspace(0.92, 0.78, h).reshape(h, 1)
    arr = np.zeros((h, w, 3), dtype=np.float32)
    for i, base in enumerate((0.90, 0.895, 0.875)):
        arr[..., i] = grad * base
    yy, xx = np.mgrid[0:h, 0:w]
    vig = 1 - 0.16 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.4) / h) ** 2)
    arr *= np.clip(vig, 0.7, 1.05)[..., None]
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))


def _paste_panel(canvas, panel, x, y, w_mm, h_mm):
    src = Image.open(PV.preview(panel, 1600)).convert("RGB")
    target = (max(1, int(w_mm * MM_PER_PX)), max(1, int(h_mm * MM_PER_PX)))
    src = src.resize(target, Image.LANCZOS)
    canvas.paste(src, (int(x), int(y)))


def elevation(panels, width_mm, height_mm, floor_mm=0):
    w = int(width_mm * MM_PER_PX) + PAD * 2
    h = int(height_mm * MM_PER_PX) + PAD * 2
    img = _wall(w, h)
    d = ImageDraw.Draw(img, "RGBA")
    S = MM_PER_PX

    # floor band
    fy = PAD + int((height_mm - floor_mm) * S)
    d.rectangle([0, fy, w, h], fill=(196, 196, 194))
    d.rectangle([0, fy, w, fy + int(2 * S)], fill=(168, 168, 166))
    # skirting / frame reveal
    frame = int(60 * S)
    d.rectangle([PAD - frame, PAD - frame, w - PAD + frame, fy + frame],
                fill=(58, 62, 66))
    d.rectangle([PAD - int(14 * S), PAD - int(14 * S), w - PAD + int(14 * S),
                 fy + int(14 * S)], fill=(30, 34, 38))
    # glazing sits inside
    d.rectangle([PAD, PAD, w - PAD, fy], fill=(232, 236, 238))
    return img, d, S


def door_mockup(panel_ids, filename, handle_panel=0, handle_inset=120):
    panels = [next(p for p in PN.PANELS if p["id"] == pid) for pid in panel_ids]
    total_w = sum(p["w"] for p in panels) + 60 * (len(panels) - 1)
    H = max(p["h"] for p in panels)
    img, d, S = elevation(panels, total_w, H)
    w, h = img.size
    fx = PAD
    fy = w and PAD + H * S

    x = PAD
    for p in panels:
        _paste_panel(img, p, x, PAD, p["w"], p["h"])
        if p["layout"] == "double":
            mx = x + p["w"] * S / 2
            d.rectangle([mx - 6 * S, PAD, mx + 6 * S, PAD + p["h"] * S], fill=(26, 30, 34))
        x += p["w"] * S
        if p is not panels[-1]:
            d.rectangle([x, PAD, x + 60 * S, PAD + p["h"] * S], fill=(30, 34, 38))
            x += 60 * S

    d = ImageDraw.Draw(img, "RGBA")
    # shadow at the foot of the glass
    for i in range(int(18 * S)):
        a = int(60 * (1 - i / (18 * S)))
        d.rectangle([PAD, PAD + H * S - i, w - PAD, PAD + H * S - i], fill=(0, 0, 0, a))
    # reflection sheen
    sheen = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen)
    sd.polygon([(PAD + 40, PAD), (PAD + 40 + int(70 * S), PAD),
                (PAD + int(20 * S), PAD + H * S), (PAD - int(10 * S), PAD + H * S)],
               fill=(255, 255, 255, 26))
    img = Image.alpha_composite(img.convert("RGBA"), sheen.filter(
        ImageFilter.GaussianBlur(radius=6 * S))).convert("RGB")

    # hardware: pull handle / lever
    d = ImageDraw.Draw(img, "RGBA")
    # hardware sits on the active leaf, inset from its meeting edge
    leaf = panels[handle_panel]
    leaf_left = sum(q["w"] for q in panels[:handle_panel]) + 60 * handle_panel
    hx = PAD + (leaf_left + leaf["w"] - handle_inset) * S
    d.rounded_rectangle([hx, PAD + (1050 - 300) * S, hx + 26 * S, PAD + (1050 + 300) * S],
                        radius=13 * S, fill=(198, 202, 206))
    d.rounded_rectangle([hx + 4 * S, PAD + (1050 - 296) * S,
                         hx + 22 * S, PAD + (1050 + 296) * S], radius=9 * S,
                        fill=(228, 231, 234))
    for yy in (1050 - 250, 1050 + 250):
        d.rectangle([hx - 6 * S, PAD + yy * S - 4 * S, hx + 10 * S, PAD + yy * S + 4 * S],
                    fill=(176, 180, 184))
    # closer, confined to the active leaf
    leaf_l = PAD + (leaf_left + 70) * S
    leaf_r = PAD + (leaf_left + leaf["w"] - 70) * S
    d.rounded_rectangle([leaf_l, PAD + 26 * S, min(leaf_l + 340 * S, leaf_r),
                         PAD + 62 * S], radius=18 * S, fill=(186, 190, 194))
    d.rounded_rectangle([leaf_l, PAD + 26 * S, min(leaf_l + 340 * S, leaf_r),
                         PAD + 50 * S], radius=12 * S, fill=(214, 217, 220))

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, filename)
    img.save(path, "PNG")
    return path


def detail_crop(path, out_name, box=None):
    im = Image.open(path)
    w, h = im.size
    box = box or (int(w * 0.18), int(h * 0.18), int(w * 0.78), int(h * 0.66))
    im.crop(box).save(os.path.join(OUT, out_name), "PNG")
    return os.path.join(OUT, out_name)


if __name__ == "__main__":
    a = door_mockup(["P-02", "P-01"], "M-01-reception.png", handle_panel=1, handle_inset=150)
    b = door_mockup(["P-03"], "M-02-consultation.png", handle_panel=0, handle_inset=120)
    c = door_mockup(["P-07", "P-08"], "M-03-imaging.png", handle_panel=0, handle_inset=300)
    print(a, b, c)
