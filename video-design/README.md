# Video Design Package — *Umuriro w'Urwanda*

A complete, CapCut-oriented design sequence for a 60-second film about **recreation**,
**Kinyarwanda dance**, the **beauty of nature** and the **beauty of people** in Rwanda.

**New to the project?** Open **[`START-HERE.md`](START-HERE.md)** — it is the session-by-session
guide to actually building this in CapCut, starting with a 30-minute proof-of-concept test you
should run before spending any money on footage.

Otherwise open `index.html` in a browser for the landing page, or go straight to `storyboard.html`.

**Sourcing mode: licensed stock libraries.** Read [`STOCK-SOURCING.md`](STOCK-SOURCING.md) before
you buy anything — 40 of the 63 shots are readily buyable, 23 need a substitution or an
in-editor build, and the dance act sits right in the middle of a licensing trap.

| File | What it is |
|---|---|
| [`START-HERE.md`](START-HERE.md) | **New here? Start with this.** Session-by-session CapCut build guide: setup, the music bed and beat grid, a 10-second proof-of-concept test before you buy footage, the assembly pass, the treatment pass, shortcuts, and the eight first-timer mistakes |
| [`STOCK-SOURCING.md`](STOCK-SOURCING.md) | **Read first.** Availability audit of every shot, the editorial-licence problem in Act 4, three sourcing strategies, library-by-library plan, frame-rate re-specs, match-cut fixes, licensing checklist, zero-budget path |
| [`storyboard.html`](storyboard.html) | Visual storyboard: beat map, 63 shot cards with timecodes, CapCut treatments and availability tiers, match-cut spine, grade table, build order, on-screen copy |
| [`DESIGN-SEQUENCE.md`](DESIGN-SEQUENCE.md) | Master treatment — concept, delivery specs, audio architecture, act-by-act shot sequence, title copy, variant cutdowns, pre-flight checklist |
| [`CAPCUT-PLAYBOOK.md`](CAPCUT-PLAYBOOK.md) | Tool-by-tool CapCut workflow, phases 0–11 plus stock ingestion, with exact menu paths, settings, a free-vs-Pro table and failure-mode fixes |
| [`assets/stock-shot-list.csv`](assets/stock-shot-list.csv) | **The working sourcing list** — availability tier, primary and alternate keywords, libraries, fps notes, licence cautions and a fallback per shot |
| [`assets/shot-list.csv`](assets/shot-list.csv) | 63 shots as a sortable assembly list (creative fields only) |
| [`assets/beat-grid.csv`](assets/beat-grid.csv) | Cut points mapped to the beat structure, for timeline marking |
| [`assets/sequence.json`](assets/sequence.json) | Machine-readable sequence data, including the per-shot `stock` object |

## Availability at a glance

| Tier | Meaning | Shots |
|---|---|---|
| **A** | Plentiful — buy immediately | 23 |
| **B** | Findable — allow real search time | 17 |
| **C** | Scarce — likely needs a substitution | 17 |
| **D** | Not available — crop, stitch or build it in CapCut | 6 |

Nature, recreation and people are well covered by the libraries. **The dance is the whole
risk** — so search Act 4 first, not last, and decide up front whether to license it directly
from a Rwandan troupe.

## At a glance

```
60.0 s · 9:16 · 60 fps · 4K H.264 · −14 LUFS · CapCut Desktop

ACT 1  00:00–00:05  Impumuro            The First Breath          free time      4 shots
ACT 2  00:05–00:14  Kwitegura           The Preparation           DROP 1        11 shots
ACT 3  00:14–00:24  Kwidagadura         Recreation                groove B      13 shots
       00:24–00:27                      BREAKDOWN — music out
ACT 4A 00:24–00:27  Umushagiriro        The Cow Dance (grace)     drums only     3 shots
ACT 4B 00:27–00:38  Intore              The Warrior Dance (fire)  DROP 2        16 shots
ACT 5  00:38–00:48  Abantu              The People and the Land   exhale → D     7 shots
ACT 6  00:48–01:00  Umunsi Mushya       Together / The New Day    groove D       9 shots
```

## Two rules that carry the whole film

1. **Build the audio bed and mark its beats before cutting a single frame of picture.**
   CapCut is a beat-driven editor; everything else is decoration on top of that grid.
2. **The match-cut spine.** Every act hands its last image to the next act as a *shape* —
   a drum skin → a lake at dawn, a spinning ankle bell → a spinning bike wheel, a painted
   spiral → a turning wrist, a flying sisal mane → wind in the tea terraces. This is what
   makes the film feel designed rather than compiled.

## Before delivery

- [ ] All Kinyarwanda text and any spoken line verified by a native speaker
- [ ] Music licensed **separately from the footage** — CapCut's built-in library audio is not cleared for commercial use
- [ ] Per-clip licence register complete: shot ID → library → licence type → model release → invoice
- [ ] No editorial-only clip in a commercial delivery; if one survives, the delivery is stated in writing as non-commercial only
- [ ] Every identifiable face has a model release
