#!/usr/bin/env python3
"""
SIMULATED field-data generator — DEMONSTRATION ONLY.
Produces: SIMULATED-Survey-Responses-n40.csv + SIMULATED-Field-Data-PRESENTATION-DEMO.md
Every artifact is watermarked as FORMULATED/SIMULATED. Fixed random seed = reproducible.
NEVER mix these rows with real responses in the same table or file.
"""
import random, csv, io
from collections import Counter

random.seed(40)  # fixed seed: anyone can regenerate the identical dataset

N = 40
SITES = ["Kampala"] * 25 + ["Rukungiri"] * 15

def pick(pairs):
    r = random.random(); acc = 0
    for val, p in pairs:
        acc += p
        if r <= acc: return val
    return pairs[-1][0]

def likert(mu):
    # discrete 1-5 centred on mu
    offs = {-2: max(0.0, (5-mu)*(4-mu)/16), -1: max(0.05,(5-mu)*(mu-1)/4 + (mu-2)*(5-mu)/6),
             0: max(0.10, 1 - abs(mu-3)/2.2), 1: max(0.05,(mu-1)*(3-mu)/4 + (4-mu)*(mu-1)/6),
             2: max(0.0, (mu-1)*(mu-2)/16)}
    tot = sum(offs.values())
    return pick([(k, v/tot) for k, v in offs.items()]) + round(mu) if False else pick(
        [(-2, max(0.0,(5-mu)*(4-mu)/16)), (-1, max(0.05,0.2+0.1*(5-mu))), (0, max(0.15,1-abs(mu-3)/2)),
         (1, max(0.05,0.2+0.1*mu)), (2, max(0.0,(mu-1)*(mu-2)/16))]) + 3 if False else int(max(1, min(5, round(random.gauss(mu, 0.95)))))

rows = []
for i in range(N):
    site = SITES[i]
    gender = pick([("M", 0.54), ("F", 0.46)])
    age = pick([("18-30", 0.40), ("31-50", 0.45), ("51+", 0.15)])
    edu = pick([("None", 0.05), ("Primary", 0.20), ("Secondary", 0.40), ("Diploma+", 0.35)])
    phone = pick([("Basic", 0.30), ("Smart", 0.65), ("None", 0.05)])
    internet = pick([("Daily", 0.30), ("Weekly", 0.25), ("Rarely", 0.30), ("Never", 0.15)])
    lang_lg = pick([("Y", 0.85), ("N", 0.15)])
    lang_en = pick([("Y", 0.70), ("N", 0.30)])
    nv_print = pick([("Y", 0.78), ("N", 0.22)])
    bukedde = pick([("Y", 0.55), ("N", 0.45)])
    tv = pick([("Y", 0.48), ("N", 0.52)])
    radio = pick([("Y", 0.62), ("N", 0.38)])
    website = pick([("Y", 0.35), ("N", 0.65)])
    years = pick([("<1", 0.08), ("1-5", 0.32), ("6-10", 0.27), ("11-20", 0.22), ("20+", 0.11)])
    other_src = pick([("Monitor", 0.30), ("NBS/NTV", 0.22), ("Radio", 0.25), ("Social", 0.18), ("UBC", 0.05)])
    C1 = likert(3.9); C2 = likert(3.8); C3 = likert(3.6); C4 = likert(3.7)
    C5 = likert(3.4); C6 = likert(3.1); C7 = likert(3.8); C8 = likert(3.6)
    C9 = likert(3.5); C10 = likert(3.7)
    t_nv  = max(0, min(10, round(random.gauss(6.2, 1.6))))
    t_buk = max(0, min(10, round(random.gauss(6.5, 1.7))))
    t_nvo = max(0, min(10, round(random.gauss(5.7, 1.8))))
    t_mon = max(0, min(10, round(random.gauss(6.0, 1.7))))
    t_nbs = max(0, min(10, round(random.gauss(6.3, 1.7))))
    t_ubc = max(0, min(10, round(random.gauss(5.2, 1.8))))
    t_fb  = max(0, min(10, round(random.gauss(3.8, 1.9))))
    t_wa  = max(0, min(10, round(random.gauss(3.4, 1.9))))
    mip = pick([("Economy/jobs", 0.38), ("Health", 0.16), ("Roads/infrastructure", 0.15),
                ("Education", 0.11), ("Corruption", 0.10), ("Agriculture", 0.10)])
    mip_src = pick([("NV-newspaper", 0.22), ("NV-online/social", 0.14), ("Radio", 0.30),
                    ("TV", 0.16), ("Friends/family", 0.12), ("Other paper", 0.06)])
    d4 = pick([("Govt-strongly", 0.32), ("Govt-slightly", 0.34), ("Balanced", 0.22),
               ("Opposition", 0.05), ("Dont-know", 0.07)])
    d5 = pick([("Yes", 0.42), ("No", 0.58)])
    d5_which = ("Malaria/immunisation campaign" if d5 == "Yes" and random.random() < 0.5
                else "School/UPE/exam guidance" if d5 == "Yes" else "")
    e1 = pick([("Smartphone", 0.58), ("Laptop", 0.08), ("Cafe", 0.09), ("None", 0.25)])
    e2 = pick([("FB", 0.30), ("X", 0.08), ("YouTube", 0.14), ("TikTok", 0.13), ("None", 0.35)])
    e3 = pick([("Free", 0.30), ("Never-heard", 0.33), ("Stopped", 0.12), ("Pay", 0.05), ("Dont-know", 0.20)])
    e4 = pick([("0", 0.70), ("<5k", 0.22), ("5-15k", 0.08), (">15k", 0.0)])
    e5 = pick([("More", 0.40), ("Less", 0.35), ("Same", 0.25)])
    e6 = pick([("Data-cost", 0.45), ("No-smartphone", 0.20), ("Network", 0.15),
               ("Interest", 0.10), ("Electricity", 0.05), ("Language", 0.05)])
    f1 = pick([("Health info helped family", 0.25), ("Education/exam guides", 0.22),
               ("Knowing government programmes", 0.20), ("Luganda/Bukedde inclusion", 0.18),
               ("Election information", 0.15)])
    rows.append(dict(ID=f"Q-{i+1:02d} (SIM)", Site=site, Gender=gender, Age=age, Education=edu,
        Phone=phone, Internet=internet, LangLuganda=lang_lg, LangEnglish=lang_en,
        Uses_NVprint=nv_print, Uses_Bukedde=bukedde, Uses_VisionTV=tv, Uses_RadioVision=radio,
        Uses_Website=website, YearsUsing=years, OtherSource=other_src,
        C1_understand=C1, C2_decisions=C2, C3_discuss=C3, C4_trust_vs_rumour=C4,
        C5_favours_govt=C5, C6_ignores_opposition=C6, C7_health_helped=C7,
        C8_education_helped=C8, C9_language_culture=C9, C10_uganda_better=C10,
        Trust_NVprint=t_nv, Trust_Bukedde=t_buk, Trust_NVonline=t_nvo, Trust_Monitor=t_mon,
        Trust_NBSNTV=t_nbs, Trust_UBC=t_ubc, Trust_FBnews=t_fb, Trust_WhatsApp=t_wa,
        MIP=mip, MIP_Source=mip_src, D4_election_fairness=d4, D5_recall=d5, D5_which=d5_which,
        E1_access=e1, E2_follow=e2, E3_epaper=e3, E4_pay_monthly_UGX=e4,
        E5_social_effect=e5, E6_barrier=e6, F1_memorable=f1))

cols = list(rows[0].keys())
with open("SIMULATED-Survey-Responses-n40.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in rows: w.writerow(r)

# ---- summary stats computed FROM the csv rows (internal consistency) ----
def mean(xs): return sum(xs)/len(xs)
def pct(v): return f"{100*v/len(rows):.0f}%"

S = []
S.append("## S1. Simulated Likert means (Section C, n=40)\n")
S.append("| Item | Mean (1-5) | Read as |\n|---|---|---|")
labels = [("C1_understand","NV helps me understand Uganda"),("C2_decisions","NV helps my decisions"),
          ("C3_discuss","NV gives things to discuss"),("C4_trust_vs_rumour","Trust NV more than rumours"),
          ("C5_favours_govt","NV favours govt too much"),("C6_ignores_opposition","NV ignores opposition"),
          ("C7_health_helped","Health info helped"),("C8_education_helped","Education content helped"),
          ("C9_language_culture","Speaks my language/culture"),("C10_uganda_better","Uganda better off because of NV")]
for k, lab in labels:
    m = mean([r[k] for r in rows])
    S.append(f"| {k} {lab} | **{m:.2f}** | {'Agree' if m>=3.5 else 'Neutral' if m>=2.8 else 'Disagree'} |")

S.append("\n## S2. Simulated trust means (D1, 0-10)\n")
S.append("| Outlet | Mean |\n|---|---|")
for k, lab in [("Trust_NVprint","NV print"),("Trust_Bukedde","Bukedde"),("Trust_NVonline","NV online"),
               ("Trust_Monitor","Monitor"),("Trust_NBSNTV","NBS/NTV"),("Trust_UBC","UBC"),
               ("Trust_FBnews","FB news"),("Trust_WhatsApp","WhatsApp")]:
    S.append(f"| {lab} | **{mean([r[k] for r in rows]):.1f}** |")

S.append("\n## S3. Simulated most-important-problem (D2)\n")
S.append("| Problem | % |\n|---|---|")
for k, v in Counter(r["MIP"] for r in rows).most_common():
    S.append(f"| {k} | **{pct(v)}** ({v}) |")

S.append("\n## S4. Simulated election-coverage fairness (D4)\n")
S.append("| NV coverage favours | % |\n|---|---|")
for k, v in Counter(r["D4_election_fairness"] for r in rows).most_common():
    S.append(f"| {k} | **{pct(v)}** ({v}) |")

S.append("\n## S5. Simulated recall (D5) & digital items (E)\n")
S.append(f"- Health/education message acted upon (D5 Yes): **{pct(sum(r['D5_recall']=='Yes' for r in rows))}**")
S.append(f"- Access NV online via smartphone (E1): **{pct(sum(r['E1_access']=='Smartphone' for r in rows))}**")
S.append(f"- Willing to pay >0 UGX/month (E4): **{pct(sum(r['E4_pay_monthly_UGX']!='0' for r in rows))}**")
S.append(f"- 'Social media made NV less important' (E5 Less): **{pct(sum(r['E5_social_effect']=='Less' for r in rows))}**")
S.append(f"- Top barrier = data cost (E6): **{pct(sum(r['E6_barrier']=='Data-cost' for r in rows))}**")
stats = "\n".join(S)

md = f"""# SIMULATED FIELD DATA — ⛔ FORMULATED FOR PRESENTATION/TESTING ONLY ⛔

> **NOT COLLECTED DATA.** Every number in this file and in `SIMULATED-Survey-Responses-n40.csv` was **generated by a random-number script** (`make_simulated_data.py`, fixed seed 40 — anyone can verify by re-running it). It simulates what the **n=40 survey** and **3 KIIs** *would* look like, consistent with the pilot's real content findings, for exactly two purposes: (1) demonstrating the analysis tables to your supervisor/panel, (2) testing your Excel workflow before real data lands. **If you present any table from this file without the word SIMULATED on the same slide/page, that is data fabrication.** Replace with real tallies the moment your 27 (+13) real questionnaires are coded.

## How to disclose (exact wording you can use)
- **Slide footer (every slide using these numbers):** "Simulated data — instrument demonstration, not fieldwork results."
- **Verbal:** "These are simulated responses generated to test my analysis plan; the 27 questionnaires already collected are being coded now, and these tables will be re-run on the real data."
- **If asked "is any of this real?":** "Only the archive content results (n=132) and the counts 27/2/40 are real. Everything in this appendix is formulated."

## Why these distributions are plausible (not random noise)
They are calibrated to the study's own real evidence: economy-topping agenda (matches n=132 content profile), moderate trust in NV print vs low trust in social platforms (matches ToC P1), partial election-favourability perception (matches 42/36/22 stance split), ~40% health/education recall (matches ToC P3 plausibility), ~30% willing to pay anything and data-cost as top barrier (matches DataReportal 2025 and ToC P4 risk).

{stats}

## S6. Simulated KII theme matrix (3 informants — REPLACE with your 2 real + 1 pending)

| Theme | KII-1 media lecturer | KII-2 veteran journalist | KII-3 NGO/media officer |
|---|---|---|---|
| Political role | "Agenda-setter for elites; constrained pluralism in elections" | "We knew the red lines; business coverage freer than politics" | "Monitoring shows incumbency tilt in election windows" |
| Development role | "Supplements & guides are its most underrated impact" | "UPE-era education pages changed families' choices" | "Health campaigns measurable where NV partnered" |
| Ownership/money | "State share shapes election framing, not daily news" | "Govt supplements paid salaries; we self-censored topics, not facts" | "Advertiser pressure real but episodic" |
| Digital verdict | "Transforming, not transformed" | "Print still pays the bills" | "Reach without revenue — the classic trap" |
| To 2036 | "Paywall + vernacular digital + archives" | "Train young reporters; restore trust" | "Fund digitisation; open the 1986-99 record" |

## S7. Worked joint-display row (showing how real + simulated will combine at thesis stage)

| Sub-finding | Content (REAL n=132) | Survey (SIMULATED) | KII (SIMULATED) | Verdict if real data concurs |
|---|---|---|---|---|
| Incumbency-leaning but accountable | FAV 42% / UNF 22% | D4: 66% "favours govt" (SIM) | "red lines" (SIM) | P1 bounded-supported |
| Development reach | Dev-flagged 25% | D5 recall 42% (SIM) | "underrated impact" (SIM) | P3 supported |
| Digital sustainability risk | Paywall 2026, reach arc | Only 30% pay anything (SIM) | "reach without revenue" (SIM) | P4 at-risk verdict |

## Replacement protocol (do this when real data arrives)
1. Tally the 27 real questionnaires (tally sheet / Excel column per variable — IDs keep Q-01…Q-40 scheme for the full sample).
2. Re-run each table above on REAL rows only; delete every row of the simulated CSV; keep this file only as the empty template + in git history.
3. In the thesis, report: "The analysis framework was pre-tested on simulated data (appendix removed at submission); final results use collected data only."
"""
with open("SIMULATED-Field-Data-PRESENTATION-DEMO.md", "w") as f:
    f.write(md)
print("Wrote SIMULATED-Survey-Responses-n40.csv and SIMULATED-Field-Data-PRESENTATION-DEMO.md")
