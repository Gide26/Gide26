"""Builds the Panel Schedule + Image Source & Licence Log."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import docutil as D
import brand as B
import panels as PN
import photos as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "one-way-vision-film", "docs")
MM = D.MM


def pct(a, b):
    return f"{a / float(b) * 100:.0f}%"


# ---------------------------------------------------------------------------
def build_schedule():
    path = os.path.join(DOCS, "01-Panel-Schedule.pdf")
    c = D.new_doc(path, "Panel schedule — one-way vision film")

    # ---- page 1: the schedule -------------------------------------------
    D.page_bg(c, "GMC / OWV / 01", "Rev R1  ·  2026-10-28  ·  PROVISIONAL", 1)
    y = D.h1(c, D.PH - 34 * MM, "Panel schedule — glass door sections", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "PROVISIONAL. Dimensions below are a representative medical-centre module set; "
               "they must be replaced by the measured door schedule and site photographs. "
               "Every panel is an independent print piece — the artwork engine is parametric, so "
               "changing a width or height re-flows type and crop automatically without distortion.",
               (D.PW - 2 * D.M) / MM, 3.4, B.NAVY_MID)
    y -= 3 * MM

    cols = [("Panel", 15, "left"), ("Department", 28, "left"), ("W x H (cm)", 21, "left"),
            ("Orientation / aspect", 42, "left"), ("Photo asset", 20, "left"),
            ("Coverage", 17, "left"), ("Handle / stile clearance", 40, "left"),
            ("Status", 22, "left")]
    rows = []
    for p in PN.PANELS:
        rows.append([
            p["id"], p["dept"], f"{p['w']/10:.0f} x {p['h']/10:.0f}",
            p["orientation"].title(), p["photo"] and P.PHOTOS[p["photo"]]["asset"] or "GRAPHIC",
            (f"{(p['h'] - p['photo_bottom'])/p['h']*100:.0f}% photo"
             if p["photo"] else "graphic only"),
            (p["hardware"][1] if len(p["hardware"]) > 1 else p["hardware"][0])[:46],
            "PROVISIONAL",
        ])
    y = D.table(c, D.M, y, cols, rows, row_h=10.2 * MM, cap=2.9) - 11 * MM

    B.label(c, D.M, y, "READING THE SCHEDULE", 4.0, B.TEAL, "Inter-600", 1.6)
    y -= 6 * MM
    D.para(c, D.M, y,
           "(1) Coverage = share of the panel given to photography. One-way vision film needs a "
           "substantial unprinted or dark field to preserve outward visibility; 36–46% photographic "
           "coverage is the working target for these doors.  (2) Clearance figures assume the handle "
           "and meeting-stile positions noted per panel and must be verified on site.  (3) All panels "
           "are portrait; no panel may be rotated or split to fit a stock sheet.",
           (D.PW - 2 * D.M) / MM, 3.3, B.NAVY_MID)
    c.showPage()

    # ---- page 2: per-panel detail cards ---------------------------------
    D.page_bg(c, "GMC / OWV / 01", "Rev R1  ·  2026-10-28  ·  PROVISIONAL", 2)
    y = D.h1(c, D.PH - 34 * MM, "Panel detail — obstructions, crop logic and production notes", 8.0)
    cards = PN.PANELS
    cw, ch = 88 * MM, 44 * MM
    gapx, gapy = 8 * MM, 7 * MM
    x0, y0 = D.M, D.PH - 44 * MM - ch
    for i, p in enumerate(cards):
        col, row = i % 3, i // 3
        x = x0 + col * (cw + gapx)
        cy = y0 - row * (ch + gapy)
        c.setFillColor(B.PAPER)
        c.rect(x, cy, cw, ch, stroke=0, fill=1)
        c.setFillColor(B.TEAL)
        c.rect(x, cy + ch - 1.6 * MM, cw, 1.6 * MM, stroke=0, fill=1)
        B.label(c, x + 4 * MM, cy + ch - 8 * MM, p["id"], 4.4, B.NAVY, "Inter-600", 1.0)
        B.caps(c, x + 20 * MM, cy + ch - 8.2 * MM, p["dept"], 3.9, B.NAVY, "Manrope-700",
               tracking_mm=0.4)
        B.label(c, x + 4 * MM, cy + ch - 14 * MM,
                f"{p['w']/10:.0f} x {p['h']/10:.0f} cm   ·   {p['aspect']}   ·   "
                f"photo bottom {p['photo_bottom']} mm", 2.9, B.GREY, "Inter-400", 0.4)
        yy = cy + ch - 21 * MM
        for line in p["hardware"]:
            yy = D.para(c, x + 4 * MM, yy, "—  " + line, cw - 8 * MM, 2.8,
                        B.NAVY_MID, 1.6)
        yy -= 1.0 * MM
        asset = p["photo"] and (P.PHOTOS[p["photo"]]["asset"] + "  " +
                                P.PHOTOS[p["photo"]]["creator"]) or "No photography (graphic panel)"
        D.para(c, x + 4 * MM, yy, "ASSET  " + asset, cw - 8 * MM, 2.8, B.TEAL, 1.6,
               "Inter-600")
        yy -= 4.6 * MM
        D.para(c, x + 4 * MM, yy, p["print_notes"], cw - 8 * MM, 2.8, B.NAVY_MID, 1.55)
    c.showPage()

    # ---- page 3: image source & licence log -----------------------------
    D.page_bg(c, "GMC / OWV / 01", "Rev R1  ·  2026-10-28", 3)
    y = D.h1(c, D.PH - 34 * MM, "Image source and licence log", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "Every photograph is a real, professionally shot stock image. No AI-generated imagery, "
               "synthetic people or composited medical scenes are used anywhere in this project. "
               "Licence status is recorded exactly as checked on the provider's page — see the terms "
               "note at the foot of this page and page 4 of the production specification.",
               (D.PW - 2 * D.M) / MM, 3.4, B.NAVY_MID)
    y -= 2 * MM

    cols = [("Asset", 16, "left"), ("Used on", 22, "left"), ("Photograph", 88, "left"),
            ("Creator / provider", 48, "left"), ("Licence", 33, "left"),
            ("Original px", 32, "left"), ("Checked", 24, "left")]
    rows = []
    usage = {}
    for p in PN.PANELS:
        if p["photo"]:
            usage.setdefault(p["photo"], []).append(p["id"])
    for key in ["reception", "consult_01", "consult_02", "lab", "pharmacy", "imaging"]:
        m = P.PHOTOS[key]
        rows.append([m["asset"], ", ".join(usage.get(key, ["—"])), m["title"],
                     f"{m['creator']} / Pexels", "Pexels Licence",
                     f"{m['original_px'][0]} x {m['original_px'][1]}", "2026-10-28"])
    D.table(c, D.M, y, cols, rows, row_h=10.0 * MM, cap=2.8)
    y -= 10.0 * MM * len(rows) + 9 * MM

    B.label(c, D.M, y, "LICENCE TERMS AS CHECKED (PEXELS, 2026-10-28)", 4.0, B.TEAL,
            "Inter-600", 1.6)
    y -= 6 * MM
    left_w = 128 * MM
    D.para(c, D.M, y,
           "Allowed: free use in commercial and non-commercial work, including print marketing "
           "material; modification and creative editing permitted; attribution not required "
           "(credited here as good practice).",
           left_w, 3.1, B.NAVY_MID)
    D.para(c, D.M + left_w + 10 * MM, y,
           "Not allowed — and directly relevant here: selling unaltered copies; implying that the "
           "people or brands depicted endorse the client; using imagery as part of a trade mark. "
           "These panels are environmental wayfinding and must not caption any depicted person as "
           "named staff.",
           (D.PW - 2 * D.M) - left_w - 10 * MM, 3.1, B.NAVY_MID)
    c.showPage()

    # ---- page 4: resolution audit ---------------------------------------
    D.page_bg(c, "GMC / OWV / 01", "Rev R1  ·  2026-10-28", 4)
    y = D.h1(c, D.PH - 34 * MM, "Resolution audit at final print size", 8.0)
    y = D.para(c, D.M, y + 2 * MM,
               "Effective resolution is calculated from the ORIGINAL file dimensions of each stock "
               "asset against the final crop window — not from the 110 ppi web previews used to build "
               "these comps. Minimum accepted for large-format work at 1.2 m viewing distance is "
               "120 ppi; 150 ppi is the preferred target. Files under the floor must be re-sourced "
               "or the crop tightened before output.",
               (D.PW - 2 * D.M) / MM, 3.4, B.NAVY_MID)
    y -= 2 * MM
    cols = [("Panel", 15, "left"), ("Asset", 16, "left"), ("Trim size (mm)", 28, "left"),
            ("Crop window px", 32, "left"), ("Needed @150 ppi", 30, "left"),
            ("Effective ppi", 24, "left"), ("Result", 26, "left")]
    rows = []
    for p in PN.PANELS:
        if not p["photo"]:
            rows.append([p["id"], "GRAPHIC", f"{p['w']} x {p['h']}", "vector", "vector", "—",
                         "PASS (vector)"])
            continue
        a = P.audit(p["photo"], p["w"], p["h"] - p["photo_bottom"], p["focus"])
        rows.append([p["id"], P.PHOTOS[p["photo"]]["asset"], f"{p['w']} x {p['h']}",
                     f"{a['crop_px'][0]} x {a['crop_px'][1]}",
                     f"{a['required_px_at_150'][0]} x {a['required_px_at_150'][1]}",
                     f"{a['effective_dpi']:.0f}", a["status"]])
    y = D.table(c, D.M, y, cols, rows, row_h=8.6 * MM, cap=3.0,
                col_colors={6: B.GREEN}) - 8 * MM
    D.para(c, D.M, y,
           "Downloaded originals must be the full-resolution file from each asset page "
           "(the 'Free download' original, not the resized preview). Relink in the production "
           "document, replace the placed preview, and re-check the crop — the focus point is stored "
           "per panel so the framing reproduces exactly.",
           (D.PW - 2 * D.M) / MM, 3.2, B.NAVY_MID)
    c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    os.makedirs(DOCS, exist_ok=True)
    print("built", build_schedule())
