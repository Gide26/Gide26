"""BCM Medical Centre — the set on the premises.

Composes the real artwork — the 24 door panes, the three banners and the sign
post — onto a black-framed doorway and a rendered front, so the client can see
the whole scheme in place: three doorways in black frames, each banner sitting
on the wall directly above its door, and the sign post standing at the kerb.

Everything is drawn in millimetres and rendered at a chosen px/mm, so the
elevation is to scale and the panes come from the print files themselves.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from reportlab.lib.units import mm as MM

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bcm_brand as B
import cp_docutil as D
import bcm_doors as DOORS
import bcm_banners as BAN
import bcm_sign as SIGN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SET = os.path.join(ROOT, "bcm")
OUT = os.path.join(SET, "premises")
WORK = os.path.join(ROOT, "source", ".work", "bcm_premises")
REV = "Rev A  ·  2026-11-02"

B.register_fonts()
D.use_brand(B)

# ---------------------------------------------------------------- geometry, mm
FRAME = 60                       # stile / rail
PANE_H = 900
LEAF_W = FRAME + 500 + FRAME + 400 + FRAME      # 1080
LEAF_H = FRAME + PANE_H + FRAME + PANE_H + FRAME  # 1980
DOOR_W = LEAF_W * 2 + FRAME                      # 2220
DOOR_H = LEAF_H

BANNER_BOTTOM = 2560             # underside of each banner above ground
BANNER_H = 1000
WALL_TOP = 3900
CORNICE = 4020
SKY_TOP = 4700
PLINTH = 250

CENTRES = {1: 2100.0, 2: 6300.0, 3: 9700.0, 4: 13100.0}
SIGN_X = 16500.0                 # sign post centre, clear of the fourth doorway
SCENE_L, SCENE_R = -700.0, 17700.0


def banner_for(n):
    """The banner over a door, if it has one.

    Only three banners were specified, so doors 1-3 carry B-1, B-2 and B-3.
    Door 4 is drawn without a banner: it is new work and no banner is ordered
    for it yet.
    """
    return BAN.BANNERS[n - 1] if n <= len(BAN.BANNERS) else None

BLACK = (18, 20, 24)
BLACK_HI = (44, 47, 52)
INK = (10, 11, 13)

LEAF_OF = {1: "COL", 2: "COL", 3: "COL"}


def leaf_cols(leaf):
    return (500, 400) if leaf == 0 else (400, 500)


# ------------------------------------------------------------------- artwork
_pane_cache = {}


def pane_image(prefix, folder, i, px_h=520):
    """Trim-only render of pane i, straight from its print PDF."""
    key = (prefix, i, px_h)
    if key in _pane_cache:
        return _pane_cache[key]
    import pypdfium2 as pdfium
    src = os.path.join(SET, folder, "artwork", f"{prefix}-P{i}.pdf")
    doc = pdfium.PdfDocument(src)
    page = doc[0]
    pw, ph = page.get_size()
    im = page.render(scale=(px_h / (72 / 25.4)) / ((ph / 72 * 25.4) - 40)).to_pil()
    doc.close()
    im = im.convert("RGB")
    # the file is pane + 10 mm bleed all round + a 20 mm slug at the foot
    w_mm = pw / 72 * 25.4 - 20.0
    h_mm = ph / 72 * 25.4 - 40.0
    sx = im.width / (w_mm + 20.0)
    sy = im.height / (h_mm + 40.0)
    box = (round(10 * sx), round(20 * sy),
           round((10 + w_mm) * sx), round((20 + h_mm) * sy))
    im = im.crop(box)
    _pane_cache[key] = im
    return im


def banner_image(b, px_w=1800):
    return BAN.face_png(b, px_w)


def shade(im, k, add=0):
    a = np.asarray(im).astype(np.float32) * k + add
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ premisis
def wall_field(w, h, s, night=False):
    """Plaster wall, plinth, cornice and sky, in scene pixels."""
    if not night:
        top = np.array([0.955, 0.940, 0.912], np.float32)
        bot = np.array([0.885, 0.868, 0.836], np.float32)
        sky = np.linspace(np.array([0.686, 0.784, 0.878], np.float32),
                          np.array([0.906, 0.925, 0.930], np.float32),
                          max(2, int(SKY_TOP - CORNICE) * 2)).reshape(-1, 1, 3)
    else:
        top = np.array([0.20, 0.205, 0.225], np.float32)
        bot = np.array([0.13, 0.135, 0.155], np.float32)
        sky = np.linspace(np.array([0.02, 0.03, 0.06], np.float32),
                          np.array([0.08, 0.10, 0.16], np.float32),
                          max(2, int(SKY_TOP - CORNICE) * 2)).reshape(-1, 1, 3)

    img = Image.new("RGB", (w, h), (240, 238, 232))
    d = ImageDraw.Draw(img)

    def Y(mm):
        return int(round((SKY_TOP - mm) * s))

    # sky
    sky_im = Image.fromarray((np.repeat(sky, w, axis=1) * 255).astype(np.uint8))
    sky_im = sky_im.resize((w, max(1, Y(CORNICE))), Image.LANCZOS)
    img.paste(sky_im, (0, 0))

    # wall body: vertical gradient
    wall_h = Y(0) - Y(WALL_TOP)
    g = np.linspace(0, 1, wall_h).reshape(-1, 1, 1)
    field = np.repeat((top * (1 - g) + bot * g), w, axis=1)
    noise = np.random.default_rng(7).normal(0, 0.006, (wall_h, w, 1))
    field = np.clip(field + noise, 0, 1)
    img.paste(Image.fromarray((field * 255).astype(np.uint8)), (0, Y(WALL_TOP)))

    # plinth
    d.rectangle([0, Y(PLINTH), w, Y(0)], fill=(176, 170, 158) if not night else (26, 28, 33))
    d.line([0, Y(PLINTH), w, Y(PLINTH)],
           fill=(198, 193, 182) if not night else (38, 41, 47), width=2)

    # cornice
    d.rectangle([0, Y(CORNICE), w, Y(WALL_TOP)],
                fill=(214, 208, 196) if not night else (34, 36, 42))
    d.rectangle([0, Y(CORNICE), w, Y(CORNICE) + 3], fill=(120, 118, 112))
    d.line([0, Y(WALL_TOP), w, Y(WALL_TOP)],
           fill=(176, 171, 160) if not night else (24, 26, 31), width=2)

    # paving
    d.rectangle([0, Y(0), w, h], fill=(146, 142, 134) if not night else (22, 24, 28))
    d.rectangle([0, Y(0), w, Y(0) + 4],
                fill=(104, 102, 96) if not night else (16, 18, 22))
    for mm in range(-560, 0, 140):
        d.line([0, Y(mm), w, Y(mm)],
               fill=(154, 150, 142) if not night else (28, 30, 35), width=1)
    return img


def door_block(door, s, night=False):
    """One doorway in a black frame, panes from the print files."""
    prefix = door["prefix"]
    folder = door["folder"]
    w, h = int(DOOR_W * s), int(DOOR_H * s)
    img = Image.new("RGB", (w, h), BLACK)
    d = ImageDraw.Draw(img, "RGBA")

    # two leaves with a centre frame between them
    for leaf in range(2):
        lx = int(leaf * (LEAF_W + FRAME) * s)
        # the leaf itself: near-black, with a soft sheen down the stiles
        d.rectangle([lx, 0, lx + int(LEAF_W * s), h], fill=BLACK if not night else (14, 15, 18))
        for k in range(6):
            a = 26 - k * 5
            d.rectangle([lx + int(k * 2 * s), 0, lx + int(k * 2 * s) + 2, h],
                        fill=(255, 255, 255, max(a, 0)))

        widths = leaf_cols(leaf)
        for col, pw_mm in enumerate(widths):
            px = lx + int((FRAME + (0 if col == 0 else widths[0] + FRAME)) * s)
            # numbering runs down each leaf: leaf 0 holds P1–P4, leaf 1 holds P5–P8,
            # upper row first, outer pane first in leaf 0 and last in leaf 1
            for yy_mm, pid_suffix in ((FRAME + PANE_H + FRAME, 1),     # upper row
                                      (FRAME, 3)):                     # lower row
                pid = leaf * 4 + pid_suffix + col
                pw = int(pw_mm * s)
                ph = int(PANE_H * s)
                yy = int(yy_mm * s)
                art = pane_image(prefix, folder, pid, px_h=int(PANE_H * s)).resize(
                    (pw, ph), Image.LANCZOS)
                if night:
                    art = shade(art, 0.82, 18)
                img.paste(art, (px, h - yy - ph))
                # glazing bead: a hairline of light on the pane's edge
                d.rectangle([px, h - yy - ph, px + pw - 1, h - yy - ph + ph - 1],
                            outline=(255, 255, 255, 26), width=1)

        # handle: a vertical stainless pull beside the meeting stile
        if leaf == 0:
            hx = lx + int((LEAF_W - 52) * s)
        else:
            hx = lx + int(20 * s)
        d.rounded_rectangle([hx, h - int(1300 * s), hx + int(22 * s), h - int(760 * s)],
                            radius=max(2, int(9 * s)),
                            fill=(198, 202, 208) if not night else (86, 90, 96))
        d.rounded_rectangle([hx + int(3 * s), h - int(1290 * s),
                             hx + int(8 * s), h - int(770 * s)],
                            radius=max(1, int(3 * s)), fill=(236, 238, 242))

    # outer frame: a bevelled black band
    d.rectangle([0, 0, w - 1, h - 1], outline=(6, 6, 8), width=max(2, int(3 * s)))
    return img


def banner_block(b, s, night=False):
    img = banner_image(b, max(1200, int(b["w"] * s))).convert("RGB")
    if night:
        img = shade(img, 0.96, 6)
    img = img.resize((int(b["w"] * s), int(b["h"] * s)), Image.LANCZOS)
    return img


def sign_block(s, night=False):
    import pypdfium2 as pdfium
    os.makedirs(WORK, exist_ok=True)
    pdf = os.path.join(WORK, "sign_face.pdf")
    SIGN.face_pdf(pdf, "A")
    doc = pdfium.PdfDocument(pdf)
    page = doc[0]
    w_mm, h_mm = SIGN.W, SIGN.H
    im = page.render(scale=(int(w_mm * s)) / (w_mm / 25.4 * 72)).to_pil().convert("RGB")
    doc.close()
    im = im.resize((int(w_mm * s), int(h_mm * s)), Image.LANCZOS)
    return shade(im, 0.96, 6) if night else im


def facade(s=0.20, night=False):
    """The front: black doorways, a banner above the three that have one, sign post."""
    w = int((SCENE_R - SCENE_L) * s)
    h = int((SKY_TOP + 600) * s)
    img = wall_field(w, h, s, night).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")

    def X(mm):
        return int((mm - SCENE_L) * s)

    def Y(mm):
        return int((SKY_TOP - mm) * s)

    # ---- doorway recesses and the doors themselves
    for door in DOORS.DOORS:
        cx = CENTRES[door["n"]]
        dx = cx - DOOR_W / 2
        d.rectangle([X(dx - 40), Y(DOOR_H + 40), X(dx + DOOR_W + 40), Y(0)],
                    fill=INK)
        blk = door_block(door, s, night)
        img.paste(blk, (X(dx), Y(DOOR_H)))

    # ---- banners above their doors, where a banner is ordered
    for door in DOORS.DOORS:
        b = banner_for(door["n"])
        if b is None:
            continue
        cx = CENTRES[door["n"]]
        bx = cx - b["w"] / 2
        by = BANNER_BOTTOM
        # stand-off shadow
        d.rectangle([X(bx) + 6, Y(by + b["h"]) + 8, X(bx + b["w"]) + 8, Y(by) + 10],
                    fill=(0, 0, 0, 70))
        blk = banner_block(b, s, night)
        img.paste(blk, (X(bx), Y(by + b["h"])))
        d.rectangle([X(bx), Y(by + b["h"]), X(bx + b["w"]), Y(by)],
                    outline=(46, 50, 56), width=max(1, int(2 * s)))
        # four stand-off fixings
        for fx in (bx + 60, bx + b["w"] - 60):
            for fy in (by + 60, by + b["h"] - 60):
                r = max(2, int(14 * s))
                d.ellipse([X(fx) - r, Y(fy) - r, X(fx) + r, Y(fy) + r],
                          fill=(150, 154, 160) if not night else (70, 74, 80))

    # ---- downlights under the cornice, washing the banners
    for door in DOORS.DOORS:
        cx = CENTRES[door["n"]]
        for off in (-700, 700):
            x = cx + off
            d.rectangle([X(x - 90), Y(CORNICE - 20), X(x + 90), Y(CORNICE - 60)],
                        fill=(236, 238, 240) if not night else (120, 124, 130))
            if night:
                # a soft warm wash on the wall under each fitting
                gw, gh = int(760 * s), int(900 * s)
                yy, xx = np.mgrid[0:gh, 0:gw]
                r = np.sqrt(((xx - gw / 2) / (gw / 2)) ** 2 +
                            ((yy - gh * 0.18) / (gh * 0.62)) ** 2)
                fall = np.clip(1 - r, 0, 1) ** 2
                glow = np.zeros((gh, gw, 4), np.uint8)
                glow[..., 0], glow[..., 1], glow[..., 2] = 255, 228, 176
                glow[..., 3] = (fall * 88).astype(np.uint8)
                img.alpha_composite(Image.fromarray(glow, "RGBA"),
                                    (int(X(x) - gw / 2), int(Y(CORNICE - 40) - gh * 0.18)))

    # ---- the sign post, standing proud of the wall
    sb = sign_block(s, night)
    sw, sh = sb.width, sb.height
    post_w = max(2, int(76 * s))
    panel_cx = int(SIGN_X * s - SCENE_L * s)
    panel_y = Y(1500 + SIGN.H / 2)
    for off in (-520 / 2, 520 / 2):
        px = panel_cx + int(off * s)
        d.rectangle([px - post_w // 2, panel_y, px + post_w // 2, Y(0)],
                    fill=(58, 62, 68) if not night else (30, 33, 38))
    d.rectangle([panel_cx - sw // 2 + 8, panel_y + 10,
                 panel_cx + sw // 2 + 8, panel_y + sh + 10], fill=(0, 0, 0, 60))
    img.paste(sb, (panel_cx - sw // 2, panel_y))

    out = img.convert("RGB")
    # a touch of vignette, so the eye lands on the doors
    vig = Image.new("L", (out.width, out.height), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-out.width * 0.15, -out.height * 0.35,
                out.width * 1.15, out.height * 1.35], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(60))
    dark = Image.new("RGB", out.size, (0, 0, 0))
    out = Image.composite(out, Image.blend(out, dark, 0.22), vig)
    return out


def door_view(door, b, s=0.5, night=False):
    """One doorway with its banner above it — the close view, with ground below.

    b may be None: a doorway with no banner ordered still gets its close view,
    framed on the door itself.
    """
    pad = 300
    TOP_MM = CORNICE + pad           # top of the picture
    BOT_MM = -340                    # paving at the foot
    w_mm = max(b["w"] if b else DOOR_W, DOOR_W) + pad * 2
    w, h = int(w_mm * s), int((TOP_MM - BOT_MM) * s)

    img = Image.new("RGB", (w, h), (238, 236, 230))
    d = ImageDraw.Draw(img, "RGBA")

    def X(mm):
        return int((mm + w_mm / 2) * s)

    def Y(mm):
        return int((TOP_MM - mm) * s)

    # sky sliver above the parapet, then the wall
    sky_col = (198, 214, 230) if not night else (26, 34, 52)
    d.rectangle([0, 0, w, Y(CORNICE)], fill=sky_col)

    top = np.array([0.965, 0.950, 0.925] if not night else [0.20, 0.205, 0.225])
    bot = np.array([0.885, 0.868, 0.836] if not night else [0.13, 0.135, 0.155])
    wall_h = Y(0) - Y(CORNICE)
    g = np.linspace(0, 1, wall_h).reshape(-1, 1, 1)
    field = np.repeat(top * (1 - g) + bot * g, w, axis=1)
    img.paste(Image.fromarray((np.clip(field, 0, 1) * 255).astype(np.uint8)),
              (0, Y(CORNICE)))

    # parapet band, plinth and paving
    d.rectangle([0, Y(CORNICE), w, Y(WALL_TOP)],
                fill=(214, 208, 196) if not night else (34, 36, 42))
    d.rectangle([0, Y(CORNICE), w, Y(CORNICE) + max(2, int(3 * s))],
                fill=(150, 146, 138) if not night else (16, 18, 22))
    d.rectangle([0, Y(PLINTH), w, Y(0)],
                fill=(176, 170, 158) if not night else (26, 28, 33))
    d.line([0, Y(PLINTH), w, Y(PLINTH)], fill=(255, 255, 255, 60), width=2)
    d.rectangle([0, Y(0), w, h], fill=(150, 146, 138) if not night else (22, 24, 28))
    d.rectangle([0, Y(0), w, Y(0) + max(2, int(4 * s))], fill=(104, 102, 96))

    # door recess and shadow
    d.rectangle([X(-DOOR_W / 2 - 45), Y(DOOR_H + 45), X(DOOR_W / 2 + 45), Y(0)],
                fill=INK)
    d.ellipse([X(-DOOR_W / 2) - 10, Y(0) - int(26 * s),
               X(DOOR_W / 2) + 10, Y(0) + int(30 * s)], fill=(0, 0, 0, 55))
    blk = door_block(door, s, night)
    img.paste(blk, (X(-DOOR_W / 2), Y(DOOR_H)))
    d.rectangle([X(-DOOR_W / 2), Y(DOOR_H), X(DOOR_W / 2), Y(0)],
                outline=(8, 8, 10), width=max(1, int(2 * s)))

    # banner, its shadow and its four stand-off fixings (only where ordered)
    if b is not None:
        bx = -b["w"] / 2
        by = BANNER_BOTTOM
        d.rectangle([X(bx) + 7, Y(by + b["h"]) + 9, X(bx + b["w"]) + 9, Y(by) + 11],
                    fill=(0, 0, 0, 60))
        bimg = banner_block(b, s, night)
        img.paste(bimg, (X(bx), Y(by + b["h"])))
        d.rectangle([X(bx), Y(by + b["h"]), X(bx + b["w"]), Y(by)],
                    outline=(46, 50, 56), width=max(1, int(2 * s)))
        for fx in (bx + 70, bx + b["w"] - 70):
            for fy in (by + 70, by + b["h"] - 70):
                r = max(2, int(14 * s))
                d.ellipse([X(fx) - r, Y(fy) - r, X(fx) + r, Y(fy) + r],
                          fill=(152, 156, 162) if not night else (72, 76, 82))
                d.ellipse([X(fx) - r // 2, Y(fy) - r // 2, X(fx) + r // 2, Y(fy) + r // 2],
                          fill=(196, 200, 206) if not night else (96, 100, 108))

    # a wall-washer over the banner
    for x in ((-b["w"] / 2 + 400, b["w"] / 2 - 400) if b is not None else ()):
        d.rounded_rectangle([X(x) - int(90 * s), Y(WALL_TOP - 55),
                             X(x) + int(90 * s), Y(WALL_TOP - 95)],
                            radius=max(2, int(6 * s)),
                            fill=(236, 238, 240) if not night else (140, 144, 150))
    return img


def setout(s=0.12):
    """A dimensioned set-out drawing of the doorways and the banners."""
    from reportlab.pdfgen import canvas as rl_canvas

    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, "setout.pdf")
    pw, ph = 380 * MM, 150 * MM
    c = rl_canvas.Canvas(path, pagesize=(pw, ph))
    c.scale(MM, MM)
    c.setFillColor(B.WHITE)
    c.rect(0, 0, 380, 190, stroke=0, fill=1)

    # page scale is worked out from the scene, so a new doorway cannot run the
    # sign post off the right edge of the sheet
    ox, oy = 70.0, 46.0              # page origin for scene x=0, ground
    sc = (pw / MM - ox - 14.0) / (SIGN_X + 950.0)

    def PX(x):
        return ox + x * sc

    def PY(y):
        return oy + y * sc

    # ground and wall line
    c.setStrokeColor(B.NAVY_MID)
    c.setLineWidth(0.4)
    c.line(PX(-260), PY(0), PX(SIGN_X + 900), PY(0))
    c.setStrokeColor(B.MIST)
    c.line(PX(-260), PY(WALL_TOP), PX(SIGN_X + 900), PY(WALL_TOP))

    for door in DOORS.DOORS:
        cx = CENTRES[door["n"]]
        c.setFillColor(B.CP_NAVY)
        c.rect(PX(cx - DOOR_W / 2), PY(0), DOOR_W * sc, DOOR_H * sc, stroke=0, fill=1)
        c.setFillColor(B.CP_CYAN)
        c.setFillAlpha(0.9)
        c.rect(PX(cx - DOOR_W / 2), PY(DOOR_H), DOOR_W * sc, 3, stroke=0, fill=1)
        c.setFillAlpha(1)
        B.label(c, PX(cx), PY(0) - 7, f"DOOR {door['n']}", 3.0, B.CP_NAVY,
                "Inter-600", 1.0, "center")

        b = banner_for(door["n"])
        if b is None:
            continue
        c.setFillColor(B.CP_CYAN)
        c.setFillAlpha(0.35)
        c.rect(PX(cx - b["w"] / 2), PY(BANNER_BOTTOM), b["w"] * sc, BANNER_H * sc,
               stroke=1, fill=1)
        c.setFillAlpha(1)
        B.label(c, PX(cx), PY(BANNER_BOTTOM + BANNER_H / 2) - 1.2,
                f"{b['id']}  {b['w'] / 1000:.1f} m", 3.2, B.CP_NAVY, "Inter-600", 1.0,
                "center")

    # dimension strings
    def dim(x1, x2, y, label):
        c.setStrokeColor(B.TEAL)
        c.setLineWidth(0.3)
        c.line(PX(x1), PY(y), PX(x2), PY(y))
        for x in (x1, x2):
            c.line(PX(x), PY(y) - 1.6, PX(x), PY(y) + 1.6)
        B.label(c, PX((x1 + x2) / 2), PY(y) + 1.6, label, 3.0, B.TEAL, "Inter-500",
                0.6, "center")

    # door widths and the pier between doors, below the ground line
    dim(CENTRES[1] - DOOR_W / 2, CENTRES[1] + DOOR_W / 2, 170, "2220")
    dim(CENTRES[1] + DOOR_W / 2, CENTRES[2] - DOOR_W / 2, 170, "1980")
    dim(CENTRES[2] - DOOR_W / 2, CENTRES[2] + DOOR_W / 2, 170, "2220")
    dim(CENTRES[2] + DOOR_W / 2, CENTRES[3] - DOOR_W / 2, 170, "980")
    dim(CENTRES[3] - DOOR_W / 2, CENTRES[3] + DOOR_W / 2, 170, "2220")
    dim(CENTRES[3] + DOOR_W / 2, CENTRES[4] - DOOR_W / 2, 170, "1180")
    dim(CENTRES[4] - DOOR_W / 2, CENTRES[4] + DOOR_W / 2, 170, "2220")

    # door centres above the banners, banner widths in the band below them
    dim(CENTRES[1], CENTRES[2], 3790, "4200 door centres")
    dim(CENTRES[2], CENTRES[3], 3790, "3400 door centres")
    dim(CENTRES[3], CENTRES[4], 3790, "3400 door centres")

    c.setStrokeColor(B.TEAL)
    c.setLineWidth(0.2)
    c.setDash(1.2, 1.2)
    for n in (1, 2, 3):
        b = banner_for(n)
        cx = CENTRES[n]
        for x in (cx - b["w"] / 2, cx + b["w"] / 2):
            c.line(PX(x), PY(BANNER_BOTTOM), PX(x), PY(2190))
    c.setDash()
    dim(CENTRES[1] - 3800 / 2, CENTRES[1] + 3800 / 2, 2290, "3800")
    dim(CENTRES[2] - 3400 / 2, CENTRES[2] + 3400 / 2, 2290, "3400")
    dim(CENTRES[3] - 2400 / 2, CENTRES[3] + 2400 / 2, 2290, "2400")

    # heights, on the left
    c.setStrokeColor(B.TEAL)
    c.setLineWidth(0.3)
    xd = PX(-260)
    for y, lab in ((0, "0"), (DOOR_H, "1980 door head"),
                   (BANNER_BOTTOM, "2560 banner underside"),
                   (BANNER_BOTTOM + BANNER_H, "3560 banner head"),
                   (WALL_TOP, "3900 wall top")):
        c.line(xd, PY(y), xd + 6, PY(y))
        B.label(c, xd - 2.0, PY(y) - 1.1, lab, 2.9, B.GREY, "Inter-500", 0.4, "right")

    # the sign post — 4 ft × 2 ft, centre 1500 mm above finished ground
    hw, hh = SIGN.W / 2, SIGN.H / 2
    base = 1500 - hh
    c.setFillColor(B.CP_NAVY)
    c.rect(PX(SIGN_X - hw), PY(base), SIGN.W * sc, SIGN.H * sc, stroke=0, fill=1)
    c.setStrokeColor(B.NAVY_MID)
    c.setLineWidth(0.8)
    for off in (-260, 260):
        c.line(PX(SIGN_X + off), PY(0), PX(SIGN_X + off), PY(base))
    B.label(c, PX(SIGN_X), PY(0) - 7, "SIGN POST", 3.0, B.CP_NAVY, "Inter-600", 1.0,
            "center")

    B.label(c, 24, 16, "SET OUT — DOORS, BANNERS AND SIGN POST, ALL DIMENSIONS IN MM",
            3.2, B.TEAL, "Inter-600", 1.4)
    B.label(c, 24, 11, "Door centres are the proposal here; on site take them from the "
                       "existing openings.", 2.7, B.GREY, "Inter-400", 0.4)
    c.showPage()
    c.save()

    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(path)
    page = doc[0]
    im = page.render(scale=2600 / page.get_size()[0]).to_pil().convert("RGB")
    doc.close()
    return im


# ----------------------------------------------------------------------- proof
def _proof_copy(src, max_w=1700, q=84):
    """A JPEG copy for the proof PDF, so the proof stays light."""
    im = Image.open(src).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    out = os.path.join(WORK, "proof-" + os.path.basename(src).rsplit(".", 1)[0] + ".jpg")
    im.save(out, quality=q, optimize=True)
    return out


def proof(path, day, night, doors, setout_img):
    day, night = _proof_copy(day), _proof_copy(night)
    doors = [_proof_copy(d, 1200, 86) for d in doors]
    setout_img = _proof_copy(setout_img, 2200, 88)
    c = D.new_doc(path, "BCM Medical Centre — the set on the premises",
                  subject="Doors, banners and sign post in place")
    eyebrow = "BCM  ·  MEDICAL CENTRE  ·  ON THE PREMISES"

    # ---- page 1: the front, day
    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, D.PW, D.PH, stroke=0, fill=1)
    B.label(c, D.M, D.PH - 16 * MM, eyebrow, 3.4, B.CP_CYAN, "Inter-600", 1.8)
    B.caps(c, D.M, D.PH - 27 * MM, "The front, in place", 7.0, B.WHITE, "Manrope-800",
           0.4)
    B.label(c, D.M, D.PH - 33 * MM,
            "Four black doorways in film, a banner on the wall above each of the first "
            "three, and the sign post at the kerb. Drawn to scale from the print files.",
            2.9, B.CP_MIST, "Inter-400", 0.4)
    iw, ih = Image.open(day).size
    bw = D.PW                      # full bleed — the elevation runs edge to edge
    bh = bw * ih / iw
    c.drawImage(day, 0, 44 * MM, bw, bh, mask=None)
    B.label(c, D.M, 32 * MM,
            "DAY  ·  B-1 OVER DOOR 1, B-2 OVER DOOR 2, B-3 OVER DOOR 3  ·  "
            "SIGN POST AT THE KERB", 2.8, B.CP_MIST, "Inter-500", 1.0)

    # ---- page 2: the front, night
    c.showPage()
    c.setFillColor(B.CP_NAVY)
    c.rect(0, 0, D.PW, D.PH, stroke=0, fill=1)
    B.label(c, D.M, D.PH - 16 * MM, eyebrow, 3.4, B.CP_CYAN, "Inter-600", 1.8)
    B.caps(c, D.M, D.PH - 27 * MM, "The front, at night", 7.0, B.WHITE, "Manrope-800",
           0.4)
    B.label(c, D.M, D.PH - 33 * MM,
            "With the eaves downlights on: the banners are washed, the film stays legible "
            "and the doors read as lit panels.", 2.9, B.CP_MIST, "Inter-400", 0.4)
    iw, ih = Image.open(night).size
    bh = bw * ih / iw
    c.drawImage(night, 0, 44 * MM, bw, bh, mask=None)
    B.label(c, D.M, 32 * MM,
            "NIGHT  ·  IF THE EAVES DOWNLIGHTS ARE FITTED — CONFIRM WITH THE ELECTRICIAN",
            2.8, B.CP_MIST, "Inter-500", 1.0)

    # ---- pages 3-5: each doorway close up
    for i, (door, img) in enumerate(zip(DOORS.DOORS, doors), start=3):
        b = banner_for(door["n"])
        c.showPage()
        D.page_bg(c, f"DOOR {door['n']}", f"{REV}", i, eyebrow=eyebrow)
        y = D.h1(c, D.PH - 34 * MM,
                 f"Door {door['n']} — black frame" + (f", {b['id']} above" if b else ""),
                 7.4)
        D.para(c, D.M, y + 2 * MM,
               f"Eight panes of {'one-way vision film' if door['film'] == 'one-way' else 'opaque film'} "
               f"in a black-painted frame — 900 mm high, 500 mm panes on the outer edges "
               f"and 400 mm against the meeting stile. "
               + (f"{b['id']} sits on the wall above the door, centred, its underside at "
                  f"2560 mm." if b else
                  "No banner is ordered for this doorway yet, so the wall above it is "
                  "left clear."),
               (D.PW - 2 * D.M) / MM * 0.66, 3.2, B.NAVY_MID)

        iw, ih = Image.open(img).size
        bh2 = 126.0                       # fit the height, then take the width
        bw2 = bh2 * iw / ih
        c.drawImage(img, D.M, 40 * MM, bw2 * MM, bh2 * MM, mask=None)
        c.setStrokeColor(B.MIST)
        c.setLineWidth(0.4)
        c.rect(D.M, 40 * MM, bw2 * MM, bh2 * MM, stroke=1, fill=0)

        tx = D.M + (bw2 + 13) * MM
        tw = (D.PW - tx - D.M) / MM
        B.label(c, tx, 152 * MM, "ON THIS DOOR", 4.0, B.TEAL, "Inter-600", 1.6)
        rows = []
        for j, (service, w, photo, pos) in enumerate(door["spec"], start=1):
            rows.append(f"{door['prefix']}-P{j}  {service}  ·  900 × {w}")
        D.bullets(c, tx, 144 * MM, [
            f"Frame and leaves: black. Panes: {len(door['spec'])} per door, 900 mm high.",
            "Door head 1980 mm; banner underside 2560 mm; 580 mm of wall between.",
        ] + ([f"Banner: {b['w']:,.0f} × 1,000 mm, centred on the door."] if b else
             ["Banner: none ordered for this doorway."]) + rows, tw, 2.9, B.NAVY_MID)

        B.label(c, tx, 92 * MM, "CHECK ON SITE", 4.0, B.TEAL, "Inter-600", 1.6)
        D.bullets(c, tx, 84 * MM, [
            "Door centres here are a proposal — take them from the existing openings.",
            "If the wall above a door is shallower than 1,000 mm, the banner drops to the "
            "fascia band or moves to the fence.",
            "Banner fixing: four stand-offs through the face into wall plugs, or a "
            "channel frame; nothing drilled through the printed face.",
        ], tw, 2.9, B.NAVY_MID)

    # ---- page 6: set out
    c.showPage()
    D.page_bg(c, "SET OUT", f"{REV}", 6, eyebrow=eyebrow)
    y = D.h1(c, D.PH - 34 * MM, "How the doors sit together", 7.4)
    D.para(c, D.M, y + 2 * MM,
           "One elevation, all dimensions in millimetres. The banners are wider than the "
           "doors, so doors 1 to 3 are spaced to suit: 4.2 m, 3.4 m and 3.4 m between "
           "centres, which leaves 600 mm and 500 mm of wall between the banner ends. "
           "Door 4 carries no banner, so it sits a clear 1.18 m pier from door 3.",
           (D.PW - 2 * D.M) / MM * 0.8, 3.2, B.NAVY_MID)
    iw, ih = Image.open(setout_img).size
    bw3 = D.PW - 2 * D.M                     # points
    bh3 = min(bw3 * ih / iw, 110 * MM)
    bw3 = bh3 * iw / ih
    c.drawImage(setout_img, (D.PW - bw3) / 2, 58 * MM, bw3, bh3, mask=None)
    c.save()
    return path


def write_index(day, night, doors):
    cards = []
    for door, b, img in zip(DOORS.DOORS, BAN.BANNERS, doors):
        cards.append(f"""
    <figure class="card"><img src="lookbook/M-{10 + door['n']}-door-{door['n']}-black.png"
      alt="Door {door['n']} in a black frame with {b['id']} above">
      <figcaption><b>Door {door['n']} — black frame</b>
        <span>{b['id']} above · {b['w'] / 1000:.1f} m × 1.0 m</span></figcaption></figure>""")

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BCM Medical Centre — on the premises</title>
<style>
 body{{margin:0;background:#f4f7f9;color:#16233f;
   font:16px/1.6 Inter,Helvetica,Arial,sans-serif}}
 header{{background:#16233f;color:#fff;padding:48px 6vw 40px}}
 h1{{font-size:clamp(28px,4.6vw,50px);margin:.2em 0 .4em;line-height:1.03}}
 header p{{max-width:66ch;color:#cfd9e6}}
 .eyebrow{{letter-spacing:.3em;font-size:11px;color:#2ba9e0}}
 main{{padding:32px 6vw 72px}}
 figure.card{{margin:0 0 26px;background:#fff;border-radius:6px;overflow:hidden;
   box-shadow:0 2px 14px rgba(22,35,63,.08)}}
 figure.card img{{width:100%;display:block}}
 figcaption{{padding:12px 16px;font-size:13px;color:#4b5b73}}
 figcaption span{{display:block;font-size:12px;color:#8fa2b8}}
 .two{{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}}
 table{{width:100%;border-collapse:collapse;font-size:14px;background:#fff}}
 th,td{{text-align:left;padding:10px 14px;border-bottom:1px solid #e3eaf2}}
 th{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#8fa2b8}}
 a{{color:#1b87b8}}
 .note{{color:#4b5b73;font-size:13px;max-width:82ch}}
 nav{{padding:0 6vw 8px;font-size:13px}} nav a{{margin-right:18px}}
</style></head><body>
<header>
  <div class="eyebrow">BCM · MEDICAL CENTRE · ON THE PREMISES</div>
  <h1>The set, in place</h1>
  <p>Three black doorways in film, a banner on the wall above each, and the sign post at
     the kerb — drawn to scale from the same print files that go to the printer.</p>
</header>
<nav><a href="../index.html">All artwork</a>
     <a href="../door-1/index.html">Door 1</a>
     <a href="../door-2/index.html">Door 2</a>
     <a href="../door-3/index.html">Door 3</a>
     <a href="../sign/index.html">Sign post</a>
     <a href="../banners/index.html">Banners</a></nav>
<main>
  <div class="two">
    <figure class="card"><img src="lookbook/M-01-premises-day.png" alt="The front, day">
      <figcaption><b>The front — day</b><span>all three doors, three banners, sign post</span></figcaption></figure>
    <figure class="card"><img src="lookbook/M-02-premises-night.png" alt="The front, night">
      <figcaption><b>The front — night</b><span>with the eaves downlights on</span></figcaption></figure>
  </div>
  <h2 style="font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:#8fa2b8">
    Each doorway</h2>
  <div class="two">{"".join(cards)}</div>
  <figure class="card"><img src="lookbook/M-04-setout.png" alt="Set out drawing">
    <figcaption><b>Set out</b><span>door centres, banner height and widths, in mm</span></figcaption></figure>
  <table>
    <tr><th>File</th><th>What it is</th></tr>
    <tr><td><a href="BCM-Premises.pdf">BCM-Premises.pdf</a></td>
        <td>Six pages — the front day and night, each doorway, the set-out drawing</td></tr>
    <tr><td><a href="in-place.html">in-place.html</a></td>
        <td>One self-contained page — the images travel inside the file, so it opens
            anywhere, even where the folder is missing</td></tr>
    <tr><td><a href="BCM-Premises-Package.zip">BCM-Premises-Package.zip</a></td>
        <td>The elevations and the proof, as a zip</td></tr>
  </table>
  <p class="note">Door centres, wall heights and the 2560 mm banner underside are
     proposals drawn from the artwork's own dimensions — confirm them against the
     building. The artwork itself is unchanged: this page only shows it in place.</p>
</main></body></html>
"""
    open(os.path.join(OUT, "index.html"), "w").write(html)


def write_standalone():
    """A single self-contained page — every image inlined, so it opens anywhere.

    A plain HTML file with <img src="lookbook/..."> needs the folder beside it.
    Open that file from a viewer, a chat attachment or GitHub and the pictures
    break. This page carries its own images as data URIs and cannot miss.
    """
    import base64, io

    def data_uri(path, width):
        im = Image.open(path).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=84, optimize=True, progressive=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    def fig(name, title, sub, width):
        uri = data_uri(os.path.join(OUT, "lookbook", name), width)
        return (f'<figure class="card"><img alt="{title}" src="{uri}">'
                f'<figcaption><b>{title}</b><span>{sub}</span></figcaption></figure>')

    front = (fig("M-01-premises-day.png", "The front — day",
                 "four black doorways, three banners, the sign post at the kerb", 1600) +
             fig("M-02-premises-night.png", "The front — night",
                 "with the eaves downlights on", 1600))
    def door_sub(d):
        b = banner_for(d["n"])
        return (f"{b['id']} above · {b['w'] / 1000:.1f} m × 1.0 m" if b
                else "no banner ordered for this doorway")

    doors = "".join(
        fig(f"M-{10 + d['n']}-door-{d['n']}-black.png",
            f"Door {d['n']} — black frame", door_sub(d), 900)
        for d in DOORS.DOORS)
    so = fig("M-04-setout.png", "Set out",
             "door centres, banner height and widths, all in millimetres", 1500)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BCM Medical Centre — on the premises (single file)</title>
<style>
 body{{margin:0;background:#f4f7f9;color:#16233f;
   font:16px/1.6 Inter,Helvetica,Arial,sans-serif}}
 header{{background:#16233f;color:#fff;padding:48px 6vw 40px}}
 h1{{font-size:clamp(26px,4.4vw,46px);margin:.2em 0 .4em;line-height:1.05}}
 header p{{max-width:66ch;color:#cfd9e6;margin:0}}
 .eyebrow{{letter-spacing:.3em;font-size:11px;color:#2ba9e0}}
 main{{padding:26px 4vw 64px;max-width:1500px;margin:0 auto}}
 figure.card{{margin:0 0 22px;background:#fff;border-radius:6px;overflow:hidden;
   box-shadow:0 2px 14px rgba(22,35,63,.08)}}
 figure.card img{{width:100%;display:block;height:auto}}
 figcaption{{padding:12px 16px;font-size:13px;color:#4b5b73}}
 figcaption b{{color:#16233f}}
 figcaption span{{display:block;font-size:12px;color:#8fa2b8}}
 .two{{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}}
 h2{{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#8fa2b8;
   margin:34px 0 14px}}
 .note{{color:#4b5b73;font-size:13px;max-width:84ch}}
</style></head><body>
<header>
  <div class="eyebrow">BCM · MEDICAL CENTRE · ON THE PREMISES</div>
  <h1>The set, in place</h1>
  <p>Three black doorways in one-way vision film, a banner on the wall above each,
     and the sign post at the kerb — drawn to scale from the print files themselves.
     This page is self-contained: the images travel inside the file.</p>
</header>
<main>
  <div class="two">{front}</div>
  <h2>Each doorway</h2>
  <div class="two">{doors}</div>
  <h2>Set out</h2>
  {so}
  <p class="note">Door centres (4.2 m and 3.4 m) and the 2560 mm banner underside are
     proposals drawn from the artwork's own dimensions — confirm them, and the wall
     height above each door, against the building. The artwork itself is unchanged.</p>
</main></body></html>
"""
    path = os.path.join(OUT, "in-place.html")
    open(path, "w", encoding="utf-8").write(html)
    return path


# ------------------------------------------------------------------------ main
def main():
    os.makedirs(os.path.join(OUT, "lookbook"), exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    # the banners are drawn live, so point the photo registry at the retouched
    # files first — otherwise they render with the un-retouched originals
    BAN.configure()

    day = facade(s=0.20, night=False)
    night = facade(s=0.20, night=True)
    day.save(os.path.join(OUT, "lookbook", "M-01-premises-day.png"), "PNG", optimize=True)
    night.save(os.path.join(OUT, "lookbook", "M-02-premises-night.png"), "PNG", optimize=True)
    print("front: day, night")

    doors = []
    for door in DOORS.DOORS:
        img = door_view(door, banner_for(door["n"]), s=0.5)
        img.save(os.path.join(OUT, "lookbook",
                              f"M-{10 + door['n']}-door-{door['n']}-black.png"),
                 "PNG", optimize=True)
        doors.append(img)
    print("doorways:", len(doors))

    so = setout()
    so.save(os.path.join(OUT, "lookbook", "M-04-setout.png"), "PNG", optimize=True)
    print("set out")

    dp = os.path.join(OUT, "lookbook", "M-01-premises-day.png")
    np_ = os.path.join(OUT, "lookbook", "M-02-premises-night.png")
    door_paths = [os.path.join(OUT, "lookbook",
                               f"M-{10 + d['n']}-door-{d['n']}-black.png")
                  for d in DOORS.DOORS]
    so_path = os.path.join(OUT, "lookbook", "M-04-setout.png")
    standalone = write_standalone()
    print("single file:", os.path.basename(standalone))
    p = proof(os.path.join(OUT, "BCM-Premises.pdf"), dp, np_, door_paths, so_path)
    print("proof:", os.path.basename(p))

    write_index(day, night, doors)

    readme = f"""# BCM Medical Centre — on the premises

The set in place, drawn to scale from the same print files that go to the printer.

| File | What it is |
| --- | --- |
| `lookbook/M-01-premises-day.png` | The front by day — three black doorways, three banners, the sign post |
| `lookbook/M-02-premises-night.png` | The front at night, with the eaves downlights |
| `lookbook/M-1N-door-N-black.png` | Each doorway close up, banner above it |
| `lookbook/M-04-setout.png` | Set-out drawing, all dimensions in mm |
| `BCM-Premises.pdf` | Six pages — the same, for the meeting |
| `in-place.html` | One self-contained page, every image embedded — opens anywhere |

## What is drawn

- Doorways: 2220 mm wide overall, 1980 mm door head, two leaves, black frame and
  black leaves, eight panes of film each — 900 mm high, 500 mm outer, 400 mm at the
  meeting stile, exactly as scheduled on the door pages.
- Banners: B-1 (3.8 m) over door 1, B-2 (3.4 m) over door 2, B-3 (2.4 m) over door 3.
  Underside 2560 mm above the paving, 580 mm clear of the door head.
- Sign post at the kerb: 1219.2 × 609.6 mm panel (4 ft × 2 ft), centre 1500 mm
  above finished ground.

Door centres — 4.2 m and 3.4 m — and the 2560 mm banner height are proposals chosen so
the banners clear each other. Confirm them, and the wall height above each door, before
anything is fixed.

Rebuild: `cd source && python3 bcm_premises.py`
"""
    open(os.path.join(OUT, "README.md"), "w").write(readme)

    import zipfile
    z = os.path.join(OUT, "BCM-Premises-Package.zip")
    if os.path.exists(z):
        os.remove(z)
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for f in ("BCM-Premises.pdf", "index.html", "in-place.html", "README.md"):
            zf.write(os.path.join(OUT, f), os.path.join("BCM-Premises", f))
        for f in sorted(os.listdir(os.path.join(OUT, "lookbook"))):
            zf.write(os.path.join(OUT, "lookbook", f),
                     os.path.join("BCM-Premises", "lookbook", f))
    print("zip:", f"{os.path.getsize(z) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
