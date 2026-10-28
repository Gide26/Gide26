"""Panel artwork renderer — parametric, true-scale (millimetres).

Vertical rhythm (portrait door, 2100 mm):
    1250 – 2100  photograph, full bleed to the head of the panel
    1250 –  700  breathing field: vertical service line + perforation texture
     660         full-width hairline
     620         teal accent rule
     200 –  520  department name (cap height 70–78 mm)
     140         department index label
     112         hairline
      40 –   74  identity lockup

Everything the client has not yet supplied is a named placeholder held in
panels.py, so a single edit re-flows the whole set.
"""
import os

import brand as B
import photos as P

MARGIN = 26.0          # outer margin for live content (inside SAFE_MM)
PHOTO_BLEED = 14.0     # horizontal bleed for the photograph
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".work")


def _fit_lines(c, text, weight, cap, max_w, tracking):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        c.setFont(weight, B.font_for(cap))
        width = c.stringWidth(trial, weight, B.font_for(cap)) + tracking * max(len(trial) - 1, 0)
        if width <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def fade(c, x, y, w, h, top_alpha=0.0, bottom_alpha=1.0):
    """Soft navy hold-down at the foot of a photograph (alpha PNG mask)."""
    grad = os.path.join(WORK, "gradient_navy.png")
    if os.path.exists(grad):
        c.drawImage(grad, x, y, w, h, mask="auto")


def perforation_texture(c, x, y, w, h, pitch=8.0, r=0.85, alpha=0.05, color=B.WHITE):
    c.saveState()
    p = c.beginPath()
    p.rect(x, y, w, h)
    c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(color)
    c.setFillAlpha(alpha)
    yy = y
    while yy < y + h:
        xx = x
        while xx < x + w:
            c.circle(xx, yy, r, stroke=0, fill=1)
            xx += pitch
        yy += pitch
    c.restoreState()


def _photo(c, p, y0, y1, bleed=PHOTO_BLEED):
    w = p["w"]
    path = P.prepare(p["photo"], w, y1 - y0, p["focus"], dpi=110)
    c.drawImage(path, -bleed, y0, w + bleed * 2, y1 - y0,
                preserveAspectRatio=False, mask=None)
    # hold the photograph down into the navy field
    fade(c, -bleed, y0, w + bleed * 2, 260)


def _ghost_number(c, p, x, y, cap, alpha=0.06):
    c.saveState()
    c.setFillColor(B.WHITE)
    c.setFillAlpha(alpha)
    c.setFont("Manrope-300", B.font_for(cap))
    c.drawRightString(x, y, p["id"][-2:])
    c.restoreState()


def _base_lockup(c, p):
    w = p["w"]
    B.logomark(c, MARGIN, 42, 40)
    B.caps(c, MARGIN + 56, 62, "MEDICAL CENTER", 9.2, B.WHITE, "Manrope-600",
           tracking_mm=1.35)
    B.label(c, MARGIN + 56, 45, "PREMIUM HEALTHCARE", 4.0, B.GREY, "Inter-500",
            tracking_mm=1.15)
    B.label(c, w - MARGIN, 50, p["id"], 5.0, B.GREY, "Inter-500",
            tracking_mm=1.0, align="right")
    B.hairline(c, MARGIN, 112, w - MARGIN, 112, B.WHITE, 0.3, 0.15)


def _vertical_text(c, x, y_bottom, text, cap, color=B.GREY, weight="Inter-500",
                   tracking=1.6, alpha=0.85):
    c.saveState()
    c.translate(x, y_bottom)
    c.rotate(90)
    c.setFillAlpha(alpha)
    B.label(c, 0, 0, text, cap, color, weight, tracking)
    c.restoreState()


def draw_single(c, p, bleed=12.0):
    w, h = p["w"], p["h"]
    pb = p["photo_bottom"]

    c.setFillColor(B.NAVY)
    c.rect(-bleed, -bleed, w + bleed * 2, pb + 2, stroke=0, fill=1)
    _photo(c, p, pb, h + bleed)

    # --- breathing field between photograph and title ---------------------
    perforation_texture(c, -bleed, 150, w + bleed * 2, pb - 760, 9.0, 1.0, 0.045)
    B.hairline(c, MARGIN, pd_cfg["band_y"], w - MARGIN, pd_cfg["band_y"],
               B.WHITE, 0.3, 0.13)
    _vertical_text(c, MARGIN + 3, pd_cfg["band_y"] + 26, p["sub"], 5.6,
                   B.GREY, "Inter-500", 2.6, 0.85)
    _ghost_number(c, p, w - MARGIN, pd_cfg["ghost_y"], pd_cfg["ghost_cap"], 0.05)

    # --- title block -------------------------------------------------------
    cap = p["title_cap"]
    max_w = (w / 2 - MARGIN - 26) if p["layout"] == "double" else (w - 2 * MARGIN)
    # a single unwrappable word must never reach the meeting stile: shrink the cap
    c.setFont("Manrope-800", B.font_for(cap))
    widest = max(c.stringWidth(word, "Manrope-800", B.font_for(cap)) for word in p["title"].split())
    if widest > max_w:
        cap = cap * max_w / widest * 0.995
    B.caps(c, MARGIN, pd_cfg["title_y"], p["title"], cap, B.WHITE, "Manrope-800",
           tracking_mm=cap * 0.03, max_width=max_w)

    B.label(c, MARGIN, pd_cfg["label_y"], p["label_text"], 6.4, B.TEAL_LT,
            "Inter-500", tracking_mm=1.9)
    B.accent_rule(c, MARGIN, pd_cfg["rule_y"], 92, 4.8, B.TEAL)
    B.hairline(c, MARGIN, pd_cfg["hair_y"], w - MARGIN, pd_cfg["hair_y"],
               B.WHITE, 0.3, 0.16)

    _base_lockup(c, p)


pd_cfg = {
    "band_y": 840,
    "ghost_y": 760,
    "ghost_cap": 330,
    "title_y": 372,
    "label_y": 286,
    "rule_y": 248,
    "hair_y": 214,
}


def draw_narrow(c, p, bleed=12.0):
    """Fixed sidelight: photograph head, vertical wordmark, mark at the foot."""
    w, h = p["w"], p["h"]
    pb = p["photo_bottom"]

    c.setFillColor(B.NAVY)
    c.rect(-bleed, -bleed, w + bleed * 2, pb + 2, stroke=0, fill=1)
    if p.get("photo"):
        _photo(c, p, pb, h + bleed)
    else:
        B.cross_motif(c, w * 0.5, pb - 420, 220, B.WHITE, 0.05)
    perforation_texture(c, -bleed, 110, w + bleed * 2, pb - 300)

    cap = p["title_cap"]
    avail = pb - 320
    txt_w = B.caps(c, 0, -1000, p["dept"], cap, B.WHITE, "Manrope-800",
                   tracking_mm=cap * 0.04)
    # centre the rotated wordmark in the field between the foot and the photo
    x_centre = w / 2 + cap * 0.36
    y_start = 300 + (avail - min(txt_w, avail)) / 2

    c.saveState()
    c.translate(x_centre, y_start)
    c.rotate(90)
    B.caps(c, 0, 0, p["dept"], cap, B.WHITE, "Manrope-800",
           tracking_mm=cap * 0.04, max_width=avail)
    c.restoreState()

    B.hairline(c, MARGIN, pb - 62, w - MARGIN, pb - 62, B.WHITE, 0.3, 0.16)
    B.label(c, MARGIN, pb - 104, p["label_text"], 6.0, B.TEAL_LT, "Inter-500", 1.8)
    B.accent_rule(c, MARGIN, pb - 146, 64, 4.2, B.TEAL)

    B.hairline(c, MARGIN, 96, w - MARGIN, 96, B.WHITE, 0.3, 0.15)
    B.logomark(c, (w - 44) / 2, 40, 44)
    B.label(c, w / 2, 24, p["id"], 4.4, B.GREY, "Inter-500", 1.0, "center")


def hardware(c, p, alpha=1.0):
    """Reference hardware on a separate layer: print the proofs WITH it, and the
    release files WITHOUT it. Never printed on the film itself."""
    hw = p.get("handle")
    if not hw:
        return
    side, inset = hw
    w = p["w"]
    c.saveState()
    if side == "right":
        hx = w - inset
    else:
        hx = inset
    y0, y1 = 900, 1220
    c.setStrokeColor(B.TEAL_LT)
    c.setFillColor(B.TEAL_LT)
    c.setStrokeAlpha(0.9 * alpha)
    c.setFillAlpha(0.14 * alpha)
    c.setLineWidth(1.4)
    c.roundRect(hx - 13, y0 - 70, 26, (y1 - y0) + 140, 13, stroke=0, fill=1)
    c.setFillAlpha(0.7 * alpha)
    c.roundRect(hx - 6, y0 - 62, 12, (y1 - y0) + 124, 6, stroke=0, fill=1)
    # fixing points
    for yy in (y0, y1):
        c.circle(hx, yy, 3.4, stroke=1, fill=0)
    # dimension annotation
    c.setStrokeAlpha(0.6 * alpha)
    c.setDash(3, 3)
    c.line(hx, 0, hx, 830)
    c.setDash()
    B.label(c, hx + (6 if side == "left" else -6), 700,
            f"HANDLE {900}–{1220}", 5.0, B.TEAL_LT, "Inter-500", 1.1,
            "left" if side == "left" else "right")
    c.restoreState()


def draw_artwork(c, p, bleed=12.0, hardware_layer=True):
    B.register_fonts()
    w, h = p["w"], p["h"]
    c.setFillColor(B.NAVY)
    c.rect(-bleed, -bleed, w + bleed * 2, h + bleed * 2, stroke=0, fill=1)

    if p["layout"] == "narrow":
        draw_narrow(c, p, bleed)
    else:
        draw_single(c, p, bleed)

    c.saveState()
    c.setStrokeColor(B.WHITE)
    c.setStrokeAlpha(0.09)
    c.setLineWidth(0.2)
    c.rect(-bleed + 1, -bleed + 1, w + bleed * 2 - 2, h + bleed * 2 - 2, stroke=1, fill=0)
    c.restoreState()
    if hardware_layer:
        hardware(c, p)
