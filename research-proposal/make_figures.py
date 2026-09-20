#!/usr/bin/env python3
"""REAL figures from the pilot dataset (n=132): issue shares by decade + stance trend."""
import csv
from collections import Counter, defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["DejaVu Serif"]

rows = list(csv.DictReader(open("Dataset-NewVision-Editions-PILOT.csv")))
DECADES = ["1996-2005", "2006-2015", "2016-2026"]
COLORS = ["#1A56A8", "#1B7A3D", "#B36B00"]

def decade(d):
    y = int(d[:4])
    return "1996-2005" if y <= 2005 else ("2006-2015" if y <= 2015 else "2016-2026")

dec_n = Counter(decade(r["date_decoded"]) for r in rows)

# ---------- Figure 4.1: issue shares by decade (REAL, n=132) ----------
groups = [("Politics+Elections", {"POL","ELE"}), ("Economy+Agriculture", {"ECO","AGR"}),
          ("Health+Education", {"HEA","EDU"}), ("Sport", {"SPO"}), ("Security/Crime", {"SEC"}),
          ("International", {"INTL"}), ("General/Editorial", {"GEN"}),
          ("Other (tour/env/ent)", {"TOUR","ENV","ENT"})]
shares = {d: [] for d in DECADES}
for gname, codes in groups:
    for d in DECADES:
        cnt = sum(1 for r in rows if decade(r["date_decoded"]) == d and r["issue_code"] in codes)
        shares[d].append(100*cnt/dec_n[d])

fig, ax = plt.subplots(figsize=(12.5, 5.6), dpi=300)
x = np.arange(len(groups)); w = 0.26
for i, d in enumerate(DECADES):
    bars = ax.bar(x + (i-1)*w, shares[d], w, label=f"{d}  (n={dec_n[d]})", color=COLORS[i], edgecolor="white")
    for b, v in zip(bars, shares[d]):
        if v > 0:
            ax.text(b.get_x()+b.get_width()/2, v+0.6, f"{v:.0f}", ha="center", fontsize=8, color="#333333")
ax.set_xticks(x); ax.set_xticklabels([g[0] for g in groups], fontsize=9)
ax.set_ylabel("Share of coded items (%)")
ax.set_title("Figure 4.1: Issue shares by decade — REAL pilot data (14 editions, n=132 items)", fontsize=12, fontweight="bold")
ax.legend(frameon=False); ax.spines[["top","right"]].set_visible(False)
ax.set_ylim(0, 34)
fig.tight_layout(); fig.savefig("Figure-4.1-Issue-Shares-REAL.png", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------- Figure 4.2: stance trend by decade (REAL, n=36 classifiable) ----------
st = defaultdict(Counter)
for r in rows:
    if r["stance"] in ("FAV", "NEU", "UNF"):
        st[decade(r["date_decoded"])][r["stance"]] += 1
series = {"FAV": [], "NEU": [], "UNF": []}
ns = []
for d in DECADES:
    c = st[d]; tot = sum(c.values()); ns.append(tot)
    for k in series: series[k].append(100*c[k]/tot)

fig, ax = plt.subplots(figsize=(9.5, 5.4), dpi=300)
mk = {"FAV": ("o", "#1B7A3D"), "NEU": ("s", "#1A56A8"), "UNF": ("^", "#B3282D")}
for k, (m, col) in mk.items():
    ax.plot(range(3), series[k], marker=m, lw=2.2, ms=9, color=col, label=k)
    for i, v in enumerate(series[k]):
        if k == "FAV" and i < 2: dx, dy = 0, -17   # below the point
        elif k == "UNF" and i < 2: dx, dy = 0, 10  # above the point
        elif v == 0: dx, dy = 0, 10
        else: dx, dy = 0, 10
        ax.annotate(f"{v:.0f}%", (i, v), textcoords="offset points", xytext=(dx, dy),
                    ha="center", fontsize=9, color=col, fontweight="bold")
ax.set_xticks(range(3))
ax.set_xticklabels([f"{d}\n(classifiable n={ns[i]})" for i, d in enumerate(DECADES)], fontsize=9.5)
ax.set_ylabel("Share of classifiable political items (%)")
ax.set_ylim(-5, 105)
ax.set_title("Figure 4.2: Stance toward state actors by decade — REAL pilot data (n=36)", fontsize=12, fontweight="bold")
ax.legend(frameon=False, loc="center right")
ax.spines[["top","right"]].set_visible(False)
ax.set_ylim(-8, 105)
fig.tight_layout()
fig.text(0.5, -0.045,
         "Caveat: 3 of 4 recent editions are ceremonial year-end editions (presidential-address genre); "
         "the 2012\u20132014 archive gap removes mid-decade coverage. FAV = favourable, NEU = neutral, UNF = unfavourable to state actors.",
         ha="center", fontsize=8.2, style="italic", color="#555555", wrap=True)
fig.savefig("Figure-4.2-Stance-Trend-REAL.png", bbox_inches="tight", facecolor="white")
print("saved Figure-4.1-Issue-Shares-REAL.png and Figure-4.2-Stance-Trend-REAL.png")
