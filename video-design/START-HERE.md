# START HERE — your first CapCut session
### How to actually begin editing *Umuriro w'Urwanda*

The other documents tell you **what** to build. This one tells you **what to do first**,
in order, with the exact clicks. Read it once, then keep it open in a second window
while you edit.

**Realistic total build time: 6–9 hours across three sessions.** Do not attempt it in one
sitting — you will make bad decisions in hour five and then have to undo them in hour six.

---

## Session 1 (about 2 hours) — setup, music, and the 10-second test

### Step 1 · Get CapCut Desktop, not the mobile app

Download CapCut for **Windows or macOS**. The mobile app cannot do what this film needs:
it caps you at 4 tracks, and you need 5 video tracks and 5 audio tracks.

The **free tier is enough to build the entire film at 1080p**. You only need Pro
(~US$19.99/month) at the very end for 4K export, auto captions, motion tracking and noise
reduction. Do not subscribe yet — build it free, then decide.

### Step 2 · Make the folders first, on your computer

Do this before opening CapCut. It takes two minutes and it is the difference between an
organised project and a pile.

```
URWANDA/
  00_MUSIC/          the track, plus any isolated drum/bell takes
  00_LICENSES/       licence PDF or invoice for every clip, same name as the clip
  01_ACT1_BREATH/
  02_ACT2_PREP/
  03_ACT3_RECREATION/
  04_ACT4_DANCE/
  05_ACT5_PEOPLE/
  06_ACT6_TOGETHER/
  99_REJECTS/
```

### Step 3 · New project, and set the ratio BEFORE you import anything

> ⚠️ **This is the most common first mistake.** CapCut sizes the canvas to your **first
> imported clip**. If you drop in a 16:9 landscape clip first, your project becomes 16:9,
> and every 9:16 clip you add afterwards gets letterboxed or cropped badly.

1. `New project` (or `Ctrl/Cmd + N`)
2. Top-left of the timeline area → **`Ratio` → `9:16`** ← do this first
3. Top-right export panel → confirm **60 fps**
4. `Ctrl/Cmd + I` → import `00_MUSIC/` only. Not the footage yet.

### Step 4 · Get one music track on the timeline

Everything else is decoration on top of this. Do not cut a single frame of picture until
the music is down and its beats are marked.

**For practising tonight:** `Audio → Sounds` and search *afro percussion*, *tribal drums*,
*african drums cinematic*. You need a track with **four things**: a quiet chant intro,
a clear first drop, a mid breakdown, and a final drop.

**For any real delivery:** CapCut's built-in library audio is **not cleared for commercial
use**, even on Pro. License separately — Artlist, Epidemic Sound, Musicbed, or directly
from a Rwandan artist. Put the licence PDF in `00_LICENSES/`.

Then:
1. Drag the track to the timeline. It lands on the audio track.
2. Trim it to exactly **60.0 s**, positioned so its **first drop sits at 00:05.0**.
3. Select the audio clip → **`Audio → Beats → Auto-generate`**. Pick **Beat II** if the
   percussion is fast and dense, **Beat I** if it is sparse.
4. `Ctrl/Cmd + =` a few times to zoom right in. Check the yellow markers against the
   waveform — auto-detect misses drum rolls and ghost notes. Fix with `Add beat`, or
   right-click a marker → `Delete beat`.
5. Press **`M`** to add manual markers at these seven points:

   ```
   00:05.0   DROP 1
   00:24.0   BREAKDOWN START
   00:27.0   DROP 2
   00:38.0   EXHALE START
   00:41.0   EXHALE END
   00:56.8   FINAL DRUM HIT
   01:00.0   END
   ```
   Jump between markers with `Shift + M` (next) and `Alt/Option + Shift + M` (previous).
6. Split the music at 00:24.0 and 00:27.0, select the middle piece, set `Volume` to
   **−14 dB** with 0.4 s fades in and out. That is your breakdown.
7. Split again at 00:56.8 and put a **3.0 s fade out** on the tail.
8. Right-click the music track → **`Lock`**. You never want to move it again by accident.

**Checkpoint — you are done with Step 4 when:** you can play the track and hear a clear
drop at 5 seconds, near-silence from 24 to 27, a second drop at 27, and the music fading
away after 56.8.

---

### Step 5 · The 10-second proof of concept — do this before you spend any money

**Do not buy 63 clips yet.** The single highest-risk thing in this film is Act 4B, the
warrior dance, and it is also the hardest footage to license. Test it first with five clips.

Buy or download **five** clips only:

| Shot | What to search | Why this one |
|---|---|---|
| **4.04** | `Intore dance jump warriors Rwanda` · alt: `African warrior dance leaps spears` | The leap. If this clip is weak, the film is weak. |
| **4.05** | `feet stomp dust slow motion` · alt: `dust explosion ground impact slo-mo` | The landing. Needs native slow motion. |
| **4.12** | `African drummers ensemble` · alt: `ingoma drumming group` | The engine of the section. |
| **4.18** | `dancers silhouette sunset jump` | Tests whether you can crush to silhouette cleanly. |
| **4.19** | `crowd clapping hands joyful` | Tests the handoff out of the act. |

Search **Pond5, Getty/iStock and Shutterstock**, and — this is the trick that works —
search in **Kinyarwanda**: `Intore`, `umuhamirizo`, `ingoma`, `amayugi`. Rwandan
contributors tag in their own language and Western searchers never find those clips.
When you find one good Rwandan clip, **open that contributor's whole portfolio** — one
cameraman who shot a performance probably shot 40 usable angles of it, all matching.

> **Before you fall in love with any clip, check two fields:** `Usage` and `Model Released`.
> If it says *Editorial* and you are making anything commercial, put it back.

Then build just **2.5 seconds** of the film:

1. Drop 4.04 on the timeline so its **first frame lands exactly on the 00:27.0 marker**.
2. Select it → `Speed → Curve → Customized`. Drag the curve so it runs 1× → **0.5× at the
   apex of the jump** → 1× on landing. The slowest point must sit **on** the beat marker.
3. Drop 4.05 right after, 0.4 s long. `Speed → Curve → Customized`: 1× → **0.2× for about
   5 frames** → 1.2×. Add `Effects → Bling → Shake` at 12 for **4 frames only**.
4. `Effects → Retro → Film Grain` at 15 on an adjustment clip over both.
5. Play it.

**Read the result:**

| What you see | What it means |
|---|---|
| The leap hangs in the air on the beat and the dust landing hits hard | ✅ Your sourcing route works. Buy the rest and build the film. |
| The leap smears, ghosts or warps around the sisal fibres | ❌ You are ramping 30 fps footage too far. Either buy native slow motion, or soften to no lower than 0.5×, or switch `Smooth slow-mo` to **Frame blending**. |
| You cannot find an Intore leap at all | ❌ Switch route. Contact a Rwandan troupe directly — Inganzo Ngari, Urukerereza, Ingoma Nshya, the Rwanda Cultural Heritage Academy, or RDB. See `STOCK-SOURCING.md` §2. |

**This 30-minute test decides whether you spend money on 63 clips or change plan.** That
is why it comes first.

---

## Session 2 (about 3 hours) — the assembly, no effects

Buy or download the remaining clips, renamed as you go:

```
ACT4_004_intore-group-leap_pond5_30.mp4
ACT3_012_silverback-eye-contact_filmsupply_60.mp4
```

Then assemble **all 63 shots** following `assets/stock-shot-list.csv`, act by act.

For every shot:
1. Drag the clip to the main video track.
2. Playhead on the beat marker → click the clip → **`Ctrl/Cmd + B`** to split → `Delete`
   the excess on both sides.
3. Trim to the duration in the shot list, ±3 frames.
4. Check the **`target_fps_designed`** column. If the shot needs to go below 0.5× and your
   clip is 30 fps, re-spec it now (`STOCK-SOURCING.md` §5) rather than discovering the
   smear later.

**Rules for this session:**
- ❌ **No transitions.** No effects. No filters. No text. No colour.
- ✅ Auto-snapping on (**`N`** toggles it) so clip edges magnet to the beat markers.
- ✅ Work act by act, in order. Don't jump around.
- ✅ `Ctrl/Cmd + S` often. CapCut autosaves, but save anyway.

**Checkpoint — the most important test in the whole build:**

> **Mute the music track and watch the entire assembly.**
>
> If the picture still cuts in a way that *feels* rhythmic with no sound, your cutting is
> right and every effect you add from here is a gain. If it does not, fix the cutting now —
> no amount of glow, grain or transitions will rescue it later.

---

## Session 3 (about 3 hours) — make it a film

Now, and only now, the treatments. In this order, because each step depends on the last:

| # | Phase | Do this | Time |
|---|---|---|---|
| 1 | **Speed** | The five signature curves: 2.05, 3.01, 3.07, 4.04, 4.05. `Speed → Curve → Customized`. | 30 min |
| 2 | **Match cuts** | The eight shape echoes. `Mask → Circle` reveals and `Scale` keyframe matching. | 45 min |
| 3 | **Keyframes** | Slow push-ins (`Scale` 100→108), the drone lift on 6.03, drift rotate on 4.10. | 30 min |
| 4 | **Colour** | **One adjustment clip per act on a track above**, graded once each. Never grade 63 clips individually. Use the table in `storyboard.html` §04. | 40 min |
| 5 | **Effects** | Film grain 12–18 globally on an overlay track. Light leak in Acts 1 and 6 only. Shake/Zoom for 4–6 frames only. | 30 min |
| 6 | **Transitions** | **Maximum 12 in the whole film.** Hard cuts everywhere in Act 4. | 15 min |
| 7 | **Titles** | One display face + one body face. Colour `#F5EFE6`, letter-spacing +4, shadow on, `Animation → In → Fade + Blur`, `Out → Fade`. Copy in `storyboard.html` §06. | 30 min |
| 8 | **Audio mix** | Duck the music 4–6 dB under every drum and voice moment. Loudest point in the film = 4.05. Add 6-frame fades to every audio clip. | 20 min |
| 9 | **Export** | `Ctrl/Cmd + E`. 1080p on free, 4K on Pro. 60 fps. H.264. Bit rate `Higher`. | 5 min |

Then the two QC passes that everybody skips and everybody regrets:
1. **Watch the exported file**, not the timeline preview. CapCut's preview drops frames on
   effect-heavy sections; the export is the truth.
2. **Watch it on your phone** at arm's length. That is where 95% of people will see it.
   Fix anything that only worked on the desktop.

---

## Shortcuts worth learning for this film

| Keys | Action | Why it matters here |
|---|---|---|
| `Ctrl/Cmd + B` | Split the **selected** clip at the playhead | 63 shots = a lot of splitting. Click the clip first, or nothing happens. |
| `B` | Switch to **split mode** — every click cuts | ⚠️ Beginners hit `B`, wander off, and shred their timeline. Press **`A`** to get back to select mode. |
| `N` | Toggle **auto snapping** | Keep it ON. It is what makes clip edges magnet to your beat markers. |
| `M` / `Shift + M` | Add marker / go to next marker | Jump between your seven structural markers instantly. |
| `←` / `→` | Step one frame | Beat-sync is a frame-accurate job. This is how you fix "it almost hits". |
| `Q` / `W` | Delete everything left / right of the playhead | Fast trims when you know exactly where the cut is. |
| `Ctrl/Cmd + =` / `Ctrl/Cmd + -` | Zoom timeline in / out | Zoom right in to place a cut on a beat. |
| `Shift + Z` | Fit the whole timeline | Zoom out to see the rhythm of the whole act at once. |
| `Ctrl/Cmd + R` | Open the **Speed** panel | You will live in this panel in Session 3. |
| `Shift + B` | Switch to **curve speed** | The speed-ramp tool — the film's signature move. |
| `Alt/Option + K` | Show/hide the **keyframe** panel | For the push-ins and the drone lift. |
| `Ctrl/Cmd + Shift + S` | Extract audio from a clip | How you build the ambience and dance-sound tracks. |
| `Ctrl/Cmd + E` | Export | — |

`Up` / `Down` arrow jumps between cut points — useful for checking that every cut in Act 4B
is exactly 0.4–0.5 s.

---

## The eight first-timer mistakes, in the order people make them

1. **Importing footage before setting `Ratio → 9:16`.** The canvas takes the first clip's
   shape. Set the ratio first, always.
2. **Adding effects during the assembly.** Build all 63 shots plain, watch it muted, then
   decorate. Effects-first is why amateur edits feel cluttered.
3. **Cutting 2–4 frames off the beat.** Zoom in to maximum and nudge with the arrow keys.
   This is the answer to "why doesn't my edit feel good" about 90% of the time.
4. **Slow-motion from 30 fps stock.** Optical Flow invents ~80% of the frames and it fails
   on sisal fibres, water and beadwork. Buy native slow motion for 3.07, 4.04, 4.05, 4.17
   and 5.01, or never go below 0.5×.
5. **Using an editorial-only clip in a commercial video.** Check `Usage` and `Model Released`
   before you fall in love with a shot, not after.
6. **Grading all 63 clips individually.** You will end up with 63 different looks. One
   adjustment clip per act.
7. **Too many transitions.** Twelve maximum in sixty seconds. Act 4 is hard cuts only — a
   transition inside the warrior section kills the impact.
8. **Judging it on the desktop preview.** Export, then watch on a phone.

---

## If you only have 20 minutes tonight

1. Install CapCut Desktop.
2. Make the folders.
3. `New project` → **`Ratio → 9:16`** → confirm 60 fps.
4. `Audio → Sounds`, search *afro percussion*, drag a track in, trim to 60 s.
5. `Audio → Beats → Auto-generate`.
6. Press `M` at 00:05.0 and 00:27.0.
7. Search Pond5 for **`Intore dance Rwanda`**, filter to free or cheap, grab anything with
   a jump in it.
8. Drop it on the 00:27.0 marker, `Ctrl/Cmd + R` → `Curve` → `Bullet`.

You have just done the two things that decide whether this film works: **a beat-locked
timeline** and **a ramped dance shot**. Everything after that is repetition.

---

## Where to go next

| You want to… | Open |
|---|---|
| See the whole film as pictures, with every shot's treatment | `storyboard.html` |
| Look up one shot's keywords, libraries and fallback | `assets/stock-shot-list.csv` |
| Understand the exact CapCut setting for a technique | `CAPCUT-PLAYBOOK.md` |
| Decide how to source Act 4 | `STOCK-SOURCING.md` §2 |
| Check the colour values for an act | `storyboard.html` §04 |
| Re-read why the film is structured this way | `DESIGN-SEQUENCE.md` §2 |
