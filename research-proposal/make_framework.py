#!/usr/bin/env python3
"""Render the study's conceptual framework (IV -> DV with moderators) as a print-quality PNG."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["DejaVu Serif"]

NAVY = "#1A56A8"; NAVY_BG = "#E8F0FE"
GREEN = "#1B7A3D"; GREEN_BG = "#E9F5EC"
AMBER = "#B36B00"; AMBER_BG = "#FFF4E0"
GREY = "#333333"

fig, ax = plt.subplots(figsize=(15.5, 10.2), dpi=300)
ax.set_xlim(0, 100); ax.set_ylim(0, 66)
ax.axis("off")

def box(x, y, w, h, fc, ec, lw=1.6, ls="-", r=0.9):
    b = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                       fc=fc, ec=ec, lw=lw, linestyle=ls, zorder=2)
    ax.add_patch(b); return b

def band(x, y, w, h, fc, label, fs=11.5):
    band_box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.9",
                              fc=fc, ec="none", zorder=3)
    ax.add_patch(band_box)
    ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=fs,
            fontweight="bold", color="white", zorder=4)

def txt(x, y, s, fs=9.2, ha="left", va="top", color=GREY, weight="normal", zorder=5, lh=1.32, style="normal"):
    ax.text(x, y, s, fontsize=fs, ha=ha, va=va, color=color, fontweight=weight,
            zorder=zorder, linespacing=lh, style=style)

# ============ TITLE ============
txt(50, 65.0, "CONCEPTUAL FRAMEWORK: THE NEW VISION AND ITS IMPACTS, 1986\u20132026",
    fs=13.5, ha="center", va="top", color="#111111", weight="bold")

# ============ IV BOX (LEFT) ============
ivx, ivy, ivw, ivh = 2.0, 12.5, 38.0, 48.0
box(ivx, ivy, ivw, ivh, NAVY_BG, NAVY, lw=2.0)
band(ivx, ivy + ivh - 3.6, ivw, 3.6, NAVY, "INDEPENDENT VARIABLE")
txt(ivx + ivw/2, ivy + ivh - 4.6, "New Vision as Institution", fs=12.5, ha="center", weight="bold", color=NAVY)

items = [
    ("1.  Editorial content & agenda-setting",
     "\u2022  What issues get covered (issue salience)\n\u2022  Whose voices appear (sources, diversity)\n\u2022  What frames dominate (stability, progress,\n     accountability, prestige)"),
    ("2.  Business & ownership model",
     "\u2022  State-majority ownership (53.3%) + USE listing\n\u2022  Advertising-dependent revenue\n\u2022  Diversification: printing, broadcast, expos"),
    ("3.  Outreach & language strategy",
     "\u2022  Multilingual titles (Bukedde, Orumuri,\n     Rupiny, Etop)\n\u2022  Regional distribution & national footprint\n\u2022  Expos (Harvest Money, Bride & Groom) and CSR"),
    ("4.  Digital adaptation",
     "\u2022  Website, e-paper, mobile apps\n\u2022  Social media & forums (2002\u2013present)\n\u2022  Premium paywall & multilingual toggle (2026)"),
]
y = ivy + ivh - 8.2
for head, body in items:
    txt(ivx + 2.0, y, head, fs=10.2, weight="bold", color="#0F3B78")
    txt(ivx + 3.2, y - 1.55, body, fs=8.8)
    y -= 10.1

# ============ DV BOX (RIGHT) ============
dvx, dvy, dvw, dvh = 60.0, 12.5, 38.0, 48.0
box(dvx, dvy, dvw, dvh, GREEN_BG, GREEN, lw=2.0)
band(dvx, dvy + dvh - 3.6, dvw, 3.6, GREEN, "DEPENDENT VARIABLE")
txt(dvx + dvw/2, dvy + dvh - 4.6, "Impacts (1986\u20132026)", fs=12.5, ha="center", weight="bold", color=GREEN)

dv_items = [
    ("1.  POLITICAL impact",
     "\u2022  Governance quality (watchdog role)\n\u2022  Electoral knowledge & participation\n\u2022  Discourse diversity & issue agenda"),
    ("2.  ECONOMIC impact",
     "\u2022  Employment & talent pipeline\n\u2022  Advertising market development\n\u2022  Printing sector & allied industries"),
    ("3.  SOCIAL / DEVELOPMENT impact",
     "\u2022  Health knowledge & behaviour\n\u2022  Education & literacy promotion\n\u2022  National unity & multilingual inclusion"),
    ("4.  DIGITAL / SUSTAINABILITY impact",
     "\u2022  Online reach & engagement\n\u2022  Digital revenue & viability\n\u2022  Survival of print-era roles online"),
]
y = dvy + dvh - 8.2
for head, body in dv_items:
    txt(dvx + 2.0, y, head, fs=10.2, weight="bold", color="#14522A")
    txt(dvx + 3.2, y - 1.55, body, fs=8.8)
    y -= 10.1

# ============ CENTRAL ARROW ============
arrow = FancyArrowPatch((ivx + ivw + 0.7, 36.5), (dvx - 0.7, 36.5),
                        arrowstyle="simple,head_length=1.8,head_width=1.1,tail_width=0.65",
                        fc=GREY, ec=GREY, mutation_scale=18, zorder=3)
ax.add_patch(arrow)
txt(50, 40.6, "40-year influence", fs=11.5, ha="center", weight="bold", color="#111111")
txt(50, 38.9, "(content \u2192 audience \u2192 society)", fs=9.0, ha="center", color="#555555", style="italic")

# ============ MODERATING / INTERVENING BAND (BOTTOM) ============
mx, my, mw, mh = 2.0, 1.2, 96.0, 9.2
box(mx, my, mw, mh, AMBER_BG, AMBER, lw=1.8, ls="--")
band(mx, my + mh - 3.2, mw, 3.2, AMBER, "MODERATING / INTERVENING VARIABLES", fs=10.5)

mods = [
    ("Political & regulatory", "Press freedom, media laws, electoral cycles"),
    ("Economic environment", "GDP, advertising spend, competition"),
    ("Technological environment", "Literacy, electrification,\ninternet/smartphone penetration"),
    ("Audience agency (U&G)", "Selective exposure, interpretation,\nalternative sources"),
]
cw = (mw - 2.0) / 4
for i, (head, body) in enumerate(mods):
    cx = mx + 1.0 + i * cw
    txt(cx + cw/2, my + mh - 4.1, head, fs=9.2, ha="center", weight="bold", color="#7A4A00")
    txt(cx + cw/2, my + mh - 5.7, body, fs=8.2, ha="center", color="#6B5230", lh=1.25)

# dashed arrows: short stubs up into IV / DV box bottoms + one long one up the centre gap
for (x0, y0, x1, y1) in [(21.0, 10.7, 21.0, 12.1), (79.0, 10.7, 79.0, 12.1), (50.0, 10.7, 50.0, 33.2)]:
    a = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=16,
                        lw=1.7, fc=AMBER, ec=AMBER, linestyle="--", zorder=2)
    ax.add_patch(a)
txt(51.8, 34.9, "condition the strength /\ndirection of the relationship", fs=8.0, ha="left",
    color="#7A4A00", style="italic", lh=1.25)

fig.savefig("Conceptual-Framework.png", bbox_inches="tight", facecolor="white")
print("saved Conceptual-Framework.png")
