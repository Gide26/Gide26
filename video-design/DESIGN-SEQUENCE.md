# **"UMURIRO W'URWANDA"** — *The Fire of Rwanda*
### A 60-second recreation + Kinyarwanda dance + nature-and-people film
### CapCut-native design sequence · Build v1.0

---

## 1. The one-line brief

> A stranger arrives for rest, and Rwanda answers with **movement** — mist on the hills,
> water on the lake, hands on the drum, feet in the air. Recreation becomes celebration,
> celebration becomes belonging.

**Logline:** *"Come to rest. Leave dancing."*

---

## 2. Core concept

| Pillar | What it means | Where it lives in the film |
|---|---|---|
| **Recreation** | Leisure as an *active*, communal, joyful thing — not passive rest. Hiking, cycling, paddling, canopy walking, drumming workshops, dancing with locals. | Act 3 (full), plus the closing block-party in Act 6 |
| **Kinyarwanda dance** | Two registers, in deliberate order: **Umushagiriro** (the cow dance — grace, arms like *inyambo* horns, slow and liquid) then **Intore / Umuhamirizo** (the warrior dance — leaps, spears, shields, ankle bells *amayugi*, stomp-driven). The order matters: elegance first, so the warrior energy lands as a *release*, not a shock. | Act 4 |
| **Beauty of nature** | Rwanda as "Land of a Thousand Hills": Virunga volcanoes, Nyungwe rainforest canopy, Akagera savanna, Lake Kivu shoreline, terraced tea at Gisakura/Mata, sunrise mist, silverback forest. | Acts 1, 5, 6 |
| **Beauty of people** | Faces and *hands* — not faces and bodies. Elders, children, drummers, weavers, dancers mid-breath. The rule: **every person is doing something, or looking at something.** No vacant posing. | Act 5 (full), threaded everywhere |

**Central device — the MATCH CUT SPINE.** The film is stitched by *shape echoes*:
a drum skin → a lake at dawn · an outstretched arm → a ridge line · a spinning ankle bell →
a spinning bike wheel · sisal mane flying → tea rows rippling in wind · a leap → a heron taking off.
Every act hands its last image to the next act as a shape. **This is the thing that makes it feel
designed rather than compiled.** In CapCut these are built with *Mask → Circle/Film* + *Camera Pull*
transitions and *Keyframe* scale matching (see the playbook).

**Colour philosophy:** three temperatures, one journey.
Cool blue-grey mist (Act 1) → warm earth green/amber (Acts 2–4) → deep golden hour (Acts 5–6).

**Rhythm philosophy:** the *ingoma* drum is the metronome. The film breathes with it —
slow wide shots on the intro chant, hard beat-locked cuts after the first drop,
a sustained slow-motion *exhale* in the middle, then a final sprint.

---

## 3. Delivery specs (master)

| Item | Master (hero) | Vertical social | Horizontal cut |
|---|---|---|---|
| Aspect ratio | **9:16** | 9:16 | 16:9 |
| Duration | **60.0 s** | 60 s | 60 s (+ optional 90 s) |
| Resolution | 1080×1920 min, **2160×3840 preferred** | 1080×1920 | 3840×2160 |
| Frame rate | **60 fps** (needed for clean slow-mo) | 60 fps | 30 or 60 fps |
| Codec | H.264, high bitrate | H.264 | H.264 / ProRes for cinema |
| Audio | −14 LUFS integrated, true peak −1 dB | −14 LUFS | −16 LUFS |
| Safe margins | 250 px bottom (UI), 180 px top | same | none |

**Shoot spec:** 4K, 60 fps, **shutter 1/120** for normal motion · 120–240 fps for the
Act 4 leaps and Act 6 confetti/petal moments · log or flat profile if the camera allows
(easier grade in CapCut's *Adjust* panel). Lock white balance manually — auto WB will
flicker across the golden-hour material and fight the grade.

**Naming convention (do this before you import — it saves hours):**
```
ACT{1-6}_{SHOT##}_{descriptor}_{fps}_{take}
ACT3_007_kivu-kayak-sunrise_120_t2.mp4
ACT4_011_intore-leap-front_240_t1.mp4
```

---

## 4. Audio architecture — build the bed FIRST

CapCut is a beat-driven editor. **Do not cut a single frame of picture until the music
track is on the timeline and its beats are marked.** Everything else is decoration on top.

**Layer stack (5 tracks):**

| # | Layer | Content | CapCut path | Level |
|---|---|---|---|---|
| A1 | **Music bed** | Contemporary Rwandan track fusing *ingoma* drums + *inanga* (zither) with a modern Afro-house/Afro-fusion groove. Needs: a chant intro, a clear first drop, a mid breakdown, a final drop. | `Audio → Sounds` (search *Afro percussion, Rwanda, drums*) or import your own licensed file | 0 dB ref |
| A2 | **Native ambience** | Real location sound: lake water, forest insects, crowd claps, wind in tea bushes. Extracted from your own clips. | `Audio → Extract` on the source clip, then drag to its own track | −12 to −18 dB |
| A3 | **Diegetic dance sound** | Drum hits, ankle bells (*amayugi*), spear-shield clack, feet stomping earth. **Left at near-full level during Act 4** — this is the emotional core. | `Extract` from performance footage; keep in sync with picture | −6 dB under music |
| A4 | **Design SFX** | Whooshes on transitions, sub-boom on the title card, risers into each drop, a vinyl-stop on the breakdown. | `Audio → Sound Effects` (search *whoosh, riser, boom, hit*) | −14 dB |
| A5 | **Voice (optional)** | An elder's *ibyivugo* (self-praise poetry) line, or a single spoken Kinyarwanda phrase at the top and bottom of the film. | `Audio → Voiceover` record, or `Text → Text-to-speech` | −8 dB, ducked music −6 dB |

**Ducking rule:** every time A3 or A5 speaks, drop A1 by 4–6 dB for the length of the phrase,
then bring it back. Use CapCut's `Audio → Fade In / Fade Out` per clip, or keyframe volume on desktop.

**Beat map (target ~104 BPM in the groove sections, free-time on the intro chant):**

```
00.0 ─ 05.0   FREE TIME   inanga + wind + single distant drum. No cuts on beat.
05.0          DROP 1      ─┐ hard cut. Everything from here is beat-locked.
05.0 ─ 14.0   GROOVE A    │  4-beat bars. Cut on beats 1 and 3.
14.0 ─ 24.0   GROOVE B    │  Add off-beat cuts (the "and" of 2 and 4) as energy rises.
24.0 ─ 27.0   BREAKDOWN   ─┘ Music pulls back to drums only / near-silence + one held breath.
27.0          DROP 2      ─┐ The warrior section. Fastest cutting of the film.
27.0 ─ 38.0   GROOVE C    │  Cut on every beat. Triples and doubles where the drum rolls.
38.0 ─ 41.0   EXHALE      ─┘ Sustained slow-motion, one shot, music swells underneath.
41.0 ─ 52.0   GROOVE D    ─┐ Warm, human, communal. Beats 1 and 3 again, wider shots.
52.0 ─ 60.0   OUTRO       ─┘ Last drum hit at 56.8, decay to ambience only, final frame 60.0.
```

> **CapCut how-to:** drop the music on the timeline → select it → `Audio → Beats →
> Auto-generate` (or `Add beat` manually). Zoom the timeline in until the yellow beat
> markers are clearly separated. **Cut every clip edge exactly on a marker.** Then, once
> picture is locked, mute the music track and watch the whole edit again — if it still
> *feels* rhythmic with no music, the cutting is right.

**Licensing note:** if this is for a brand, tourism board or any monetised channel, do **not**
use trending CapCut library audio. Use a licensed Rwandan artist track or a cleared
production-music Afro-percussion cue. Keep the licence PDF next to the project file.

---

## 5. THE DESIGN SEQUENCE — shot by shot

Legend for the *Cut* column: **B** = on a beat marker · **H** = hard cut on the drop ·
**X** = shape-match cross cut · **D** = dissolve · **S** = speed-ramp · **W** = whip/blur move.

---

### ACT 1 — "IMPUMURO" *(The First Breath)* · 00:00.0 → 00:05.0
**Function:** earn the viewer's attention with silence and scale. No beat yet.
**Mood:** cold, blue-grey, hushed. **Cutting rate:** very slow — one shot per 1.2–1.8 s.

| # | TC in | Dur | Shot | Frame | Motion | Cut | CapCut treatment |
|---|---|---|---|---|---|---|---|
| 1.01 | 00:00.0 | 1.8 | **Black.** A single deep *ingoma* hit blooms out of darkness into a wide of mist filling a valley at first light, Virunga silhouettes behind. | Extreme wide, 9:16 | Locked tripod, mist drifting | — | Fade in from black 12 frames. `Effects → Retro → Film Grain` at 15. `Adjust`: temp −10, highlights −15, fade 8. |
| 1.02 | 00:01.8 | 1.4 | Slow push across a **terraced tea hill**, Gisakura, rows vanishing into cloud. | Wide, low angle in the rows | Drone/gimbal push-in | D | Keyframe `Scale` 100→108 across the clip (2.5 s ease). `Effects → Lens → Soft Focus` at 10, only on the first 8 frames. |
| 1.03 | 00:03.2 | 1.0 | **Water, mirror-still**, Lake Kivu at dawn. A single fisher's boat, tiny, off-centre. | Wide, 9:16, boat in upper third | Static | D | `Adjust`: shadows +10, contrast −8 to flatten the water into glass. |
| 1.04 | 00:04.2 | 0.8 | **The title.** Text rises over the lake. | — | — | **H** on the riser | Text `UMURIRO W'URWANDA` · font: a clean serif or hand-brushed face · `Animation → In → Typewriter` **off** — use `In → Fade` + `Blur` (8 f), `Out → Fade`. Add `Effects → Light Effect → Light Leak` at 20 behind the type. Sub-boom SFX on the frame the text locks. |

**Act 1 subtitle (optional, bottom third, 60% opacity):** *"Igihugu cy'imisozi igihumbi"* — *Land of a thousand hills.*

---

### ACT 2 — "KWITEGURA" *(The Preparation)* · 00:05.0 → 00:14.0
**Function:** the drop lands and we meet **people** before we meet the dance. Hands, faces,
costume, craft. This is where the film says *"the beauty of people"* without saying it.
**Mood:** warm, amber, kinetic. **Cutting rate:** 0.7–1.2 s, on beats 1 and 3.

| # | TC in | Dur | Shot | Frame | Motion | Cut | CapCut treatment |
|---|---|---|---|---|---|---|---|
| 2.01 | 00:05.0 | 0.9 | **Hands** tightening the beaded *igikubwe* band on a dancer's forehead. | ECU, shallow DoF | Handheld, breathing | **H** (the drop) | Freeze the first 3 frames on the hit (`Freeze` tool) then release — a micro-stop that sells the drop. |
| 2.02 | 00:05.9 | 0.7 | Sisal **umugara** mane being combed out, fibres catching backlight. | CU, backlit | Slow lateral | B | `Adjust`: highlights +12, glow 15. Golden hour grade base. |
| 2.03 | 00:06.6 | 0.8 | **Beadwork** — *ibitako* shoulder ornaments, fingers threading beads. | Macro | Static, hands move | B | Speed 0.7× if the hands rush. |
| 2.04 | 00:07.4 | 0.7 | An elder's **face**, weathered, laughing at something off-frame. | MCU, eye-level | Handheld | B | **Do not** colour-correct the laugh out. Keep the eyes bright: `Adjust → HSL → Orange → Luminance +12`. |
| 2.05 | 00:08.1 | 0.8 | A **drummer's palm** strikes the *ingoma* skin. Dust jumps off the head. | ECU, 240 fps | — | B | **S** — Speed → Curve → `Bullet` centred on the strike, 0.3× for 6 frames then snap to 1×. Extract the drum hit to track A3 at full level. |
| 2.06 | 00:08.9 | 0.7 | Anklet of **bells** (*amayugi*) being tied. | CU, ground level | Static | B | SFX: bell jingle, −10 dB, in the gap between beats. |
| 2.07 | 00:09.6 | 0.9 | A **woman** adjusts her *umushanana* sash over one shoulder; fabric slides. | MS, backlit | Slow dolly | B | Speed 0.6× — let the fabric move like water. This is the visual seed for Act 4A. |
| 2.08 | 00:10.5 | 0.8 | **Spears and shields** stacked, leaning against a wall, morning light raking across. | Wide detail | Static | B | `Adjust`: contrast +10, shadows −8 for graphic hardness. |
| 2.09 | 00:11.3 | 0.9 | A child **peeks** through a gap in the crowd / a doorway at the dancers. | CU, child's POV height | Handheld | B | Hold one beat longer than feels right — the child is the audience surrogate. |
| 2.10 | 00:12.2 | 0.9 | Dancers **walking into frame** in a line, backs to camera, toward the performance ground. | Wide, symmetrical | Gimbal follow | B | Keyframe `Position` to nudge the frame with them (fake parallax). |
| 2.11 | 00:13.1 | 0.9 | **Reverse-angle**: the line stops, turns as one, faces us. | Wide | Locked | B → into X | Cut on the exact frame the heads finish turning. **Match cut** to 3.01 via the shared circular shape of a shield / a wheel. |

---

### ACT 3 — "KWIDAGADURA" *(Recreation — Play in the Land)* · 00:14.0 → 00:24.0
**Function:** the recreation pillar. Rwanda is not a museum, it's a playground. Ten seconds of
pure joy — water, wheels, rope, height, laughter. **Mood:** bright, saturated, alive.
**Cutting rate:** 0.6–1.0 s, now adding off-beat cuts as energy climbs.

| # | TC in | Dur | Shot | Frame | Motion | Cut | CapCut treatment |
|---|---|---|---|---|---|---|---|
| 3.01 | 00:14.0 | 0.9 | **Lake Kivu kayak / paddleboard** at sunrise, water sprayed by the paddle, rider grinning. | Wide→CU, 120 fps | Drone orbit | **X** from 2.11 | **S** — Curve `Hero`: 1.4× on the entry, 0.4× through the paddle splash, 1× on exit. Water droplets are the money frame. |
| 3.02 | 00:14.9 | 0.8 | **Cycling the Congo-Nile trail** — wheel spinning, red earth, green blur behind. | Low CU on the wheel | Tracking | B | **X** — the spinning wheel rhymes with the spinning ankle bell from 2.06. `Effects → Bling → Shake` at 8, synced to wheel rotation. |
| 3.03 | 00:15.7 | 0.7 | Rider's **POV** over the handlebars, hills dropping away. | POV, wide | Chest mount | B | `Adjust → Stabilize` **on** (Recommended level) — POV needs it. Slight `Effects → Bling → Zoom` at 6. |
| 3.04 | 00:16.4 | 0.8 | **Hiking the Virunga** — a hand grabs a root, pulls up, boots on wet rock. | ECU hands → tilt up | Handheld | B | Two shots in one: tilt-up reveals the volcano. Add a `whoosh` SFX on the tilt. |
| 3.05 | 00:17.2 | 0.9 | **Nyungwe canopy walk** — a person steps onto the swaying bridge, looks down, laughs nervously. | Wide, from below | Static, subject moves | B | Keep the nervous laugh in A2 at −14 dB. It is the most human sound in the film. |
| 3.06 | 00:18.1 | 0.7 | **Zipline / tree swing** through rainforest. | Wide, motion blur | — | B | Speed 0.8×, `Effects → Bling → Shake` 10 on the launch frame. |
| 3.07 | 00:18.8 | 0.8 | **Swimming / lake water** — someone breaks the surface, backlit spray. | CU, 240 fps | Under/surface | B | **S** — `Bullet` curve, 0.3× at the moment of breaking the surface. `Adjust`: highlights +15, saturation +8 on the water only via HSL Blue. |
| 3.08 | 00:19.6 | 0.9 | **Coffee / tea pickers at work**, laughing between rows, baskets on their heads. | MS, in the rows | Gimbal lateral | B | This is *labour as recreation* — don't romanticise it into silence. Keep the voices. |
| 3.09 | 00:20.5 | 0.8 | **A drumming workshop** — visitors and locals both hitting drums, badly and happily. | Wide, participatory | Handheld | B | The pivot shot: recreation → dance. A3 drum audio swells here. |
| 3.10 | 00:21.3 | 0.8 | **Imigongo** art being painted — geometric cow-dung-and-ochre patterns, a hand drawing a spiral. | Macro | Static | B | **X** — the spiral becomes the spin of Act 4's dancer. |
| 3.11 | 00:22.1 | 0.9 | **Akagera**: a herd, a giraffe's neck, tall grass bending in wind. | Wide, telephoto compress | Static | B | `Adjust`: temp +8, glow 12. |
| 3.12 | 00:23.0 | 1.0 | **A silverback**, in the bamboo, calmly chewing. Looks up. Direct eye contact with lens. | CU, 200 mm | Locked | B → into break | **The held frame.** Let the gorilla's look land. Then — |

**3.13 BREAKDOWN (00:24.0, 0.0 s):** on the gorilla's gaze the **music drops out completely**.
In CapCut: split A1 at 00:24.0, and on the second half apply `Fade In` of 12 frames starting at 00:27.0.
Fill 00:24.0–00:27.0 with **only** A2 ambience (wind) + A3 (one slow heartbeat drum) + a low riser.

---

### ACT 4 — "IMIBYINO" *(The Dance)* · 00:24.0 → 00:38.0
**Function:** the heart. Fourteen seconds. Split into three movements so the section has its own arc.
**Mood:** fire, sweat, earth, dust. **Cutting rate:** the fastest in the film — 0.4–0.8 s.

#### 4A — *Umushagiriro* — the cow dance, grace · 00:24.0 → 00:27.5
*(Performed during the breakdown. Slow, liquid, silent except for drums.)*

| # | TC in | Dur | Shot | Frame | Motion | Cut | CapCut treatment |
|---|---|---|---|---|---|---|---|
| 4.01 | 00:24.0 | 1.4 | A woman in **umushanana** begins *umushagiriro* — arms rising and curving outward like the horns of an *inyambo* cow. | Full body, 9:16, centred | Locked, 120 fps | D from the gorilla | Speed **0.4×** with `Smooth slow-mo → Optical Flow`. This must be butter. If Optical Flow artefacts on the fabric, back off to 0.6×. |
| 4.02 | 00:25.4 | 1.1 | **Her hands**, wrist turning, fingers extending. | ECU | Slow dolly | — | Same 0.4×. `Adjust → HSL → Orange`: skin luminance +10, saturation +4. Do not over-smooth. |
| 4.03 | 00:26.5 | 1.0 | **Fabric** of the umushanana sliding, sash trailing. | CU | Static | — | Speed 0.3×. `Effects → Lens → Soft Focus` 8. This is the breath before the storm. |

#### 4B — *Intore / Umuhamirizo* — the warrior dance, fire · 00:27.5 → 00:35.0
*(DROP 2 at 00:27.0. Hard cut. Every shot lands on a beat.)*

| # | TC in | Dur | Shot | Frame | Motion | Cut | CapCut treatment |
|---|---|---|---|---|---|---|---|
| 4.04 | 00:27.5 | 0.5 | **THE LEAP.** A full Intore line jumps simultaneously, sisal manes airborne, spears up. | Wide, low angle, 240 fps | Locked | **H** (drop) | Speed **0.5× → 1.0×** Curve `Bullet`, timed so they hang at the apex exactly on the downbeat. Sub-boom SFX + the real stomp audio at −3 dB. |
| 4.05 | 00:28.0 | 0.4 | **Landing** — feet hit earth, dust explodes upward. | Ground-level CU, 240 fps | Static | B | **S** — 0.2× for 5 frames on impact, then snap to 1.2×. Shake effect 12 for 4 frames only. This is the film's signature shot; get it right. |
| 4.06 | 00:28.4 | 0.4 | **Face** of a dancer mid-cry, teeth showing, sweat, mane across the eyes. | ECU | Handheld | B | Freeze 2 frames on the beat, release. `Adjust`: contrast +12, clarity +15. |
| 4.07 | 00:28.8 | 0.4 | **Spear** thrust forward into lens. | CU, foreground | — | B | `Effects → Bling → Zoom` 15 on the thrust frame. Hard whoosh. |
| 4.08 | 00:29.2 | 0.5 | **Shields** clashing in unison across the line. | Wide | Locked | B | A3 shield-clack at full level; duck A1 by 5 dB for 8 frames. |
| 4.09 | 00:29.7 | 0.5 | **Ankle bells** in a blur of stomp. | ECU, 240 fps | Static | B | Speed 0.35×. Bell audio isolated and pitched slightly up. |
| 4.10 | 00:30.2 | 0.5 | **Formation change** — the line collapses and reforms, top-down drone shot. | Top-down wide | Drone | B | Keyframe `Rotation` 0→8° over the clip for slow drift. |
| 4.11 | 00:30.7 | 0.4 | **A woman dancing *umuhamirizo*** — reclaiming the warrior dance. Leap, full commitment. | MS, 240 fps | Handheld pan | B | **Deliberate inclusion.** Hold her leap as long as the men's. 0.5× curve. |
| 4.12 | 00:31.1 | 0.4 | **Drummers** — full *umutagara* ensemble, sticks blurring. | Wide detail | Handheld | B | Speed 1.1× (slightly *over* real time reads as frenzy). |
| 4.13 | 00:31.5 | 0.5 | **A child mimics** the leap, badly, delighted, in the foreground; real dancers soft behind. | Two-plane MS | Static | B | `Adjust → Depth-of-field` / `Effects → Lens → Blur` 20 on the background plane. |
| 4.14 | 00:32.0 | 0.5 | **Ibyivugo** — a poet steps forward, reciting self-praise verse, arm outstretched. | MCU | Slow push | B | Keyframe `Scale` 100→106. If he speaks, duck A1 to −10 dB for the length of the line and let A5 carry it. |
| 4.15 | 00:32.5 | 0.4 | **Horn / amakondera** player, cheeks full, sound announcing the warriors. | CU | Static | B | The horn melody is the traditional "arrival" cue — put a real horn hit here in A3. |
| 4.16 | 00:32.9 | 0.5 | **Three leaps**, jump-cut in sequence, same framing, different dancers. | Wide, locked | — | B×3 | Three 5-frame cuts inside one beat cluster. Reads as a drum roll. |
| 4.17 | 00:33.4 | 0.5 | **The mane**, filling the frame, whipping sideways in slow motion. | ECU, 240 fps | — | B | Speed 0.3×. Glow 20, highlights +15. The single most beautiful texture in the film. |
| 4.18 | 00:33.9 | 0.6 | **The whole line, apex of a leap**, silhouetted against a low sun. | Wide, backlit | Locked | B | `Adjust`: exposure −15 to crush to silhouette, then highlights +20 to keep the rim. |
| 4.19 | 00:34.5 | 0.5 | **Crowd clapping**, hands in unison, faces lit. | Wide | Handheld | B | Crowd clap audio at −4 dB — this is the transition into Act 5. |

#### 4C — The Exhale · 00:38.0 → 00:41.0 *(see below; plays over the sustained moment)*

---

### ACT 4C / 5 — "ABANTU" *(The People, The Land)* · 00:38.0 → 00:48.0
**Function:** the sustained slow-motion **exhale** at 00:38–41, then a portrait montage of
Rwanda's land and faces. **Mood:** reverent, golden, warm. **Cutting rate:** drops sharply — 1.2–2.0 s.

| # | TC in | Dur | Shot | Frame | Motion | Cut | CapCut treatment |
|---|---|---|---|---|---|---|---|
| 5.01 | 00:38.0 | 3.0 | **THE EXHALE.** One shot, held. A dancer, chest heaving, sweat, a slow smile breaking across the face as the last drum fades. Or: the mane settling, dust hanging in the golden light, everything going quiet. | MCU, 240 fps | Locked | from 4.19 | **One continuous 3-second shot. Do not cut it.** Speed 0.35× + Optical Flow. Music sustains under. `Effects → Light Effect → Halo Blur` 12. This is the emotional peak — protect it from effects creep. |
| 5.02 | 00:41.0 | 1.5 | **A grandmother's hands** weaving *agaseke* (peace basket), intricate geometric coil. | Macro, 9:16 | Slow dolly | D | Keyframe `Scale` 100→104. Warm grade: temp +12, glow 10. |
| 5.03 | 00:42.5 | 1.2 | **An elder's face**, full frame, still. He looks into the lens and holds it. | ECU portrait | Locked | D | **Hold it.** No motion, no effect except grain 12 and a soft vignette 8. The stillness after 38 seconds of movement is the point. |
| 5.04 | 00:43.7 | 1.2 | **Children running** a dirt path between banana trees, laughing, toward camera. | MS, 120 fps | Gimbal, backing up | B | Speed 0.7×. Laughter in A2 at −10 dB. |
| 5.05 | 00:44.9 | 1.3 | **Rolling hills** at golden hour, terraced, mist beginning to return — the film comes full circle to Act 1. | Extreme wide, drone | Slow aerial pull-back | **X** | `Effects → Nature → Sunset` at 15, or manual: temp +14, highlights −10, shadows +8, glow 18. |
| 5.06 | 00:46.2 | 1.0 | **A face in the crowd**, watching the dancers, tears or laughter — ambiguous, alive. | CU | Handheld | D | `Adjust → HSL → Orange` luminance +10. Do not add any effect. Faces don't need help. |
| 5.07 | 00:47.2 | 0.8 | **Water again** — Lake Kivu, now gold instead of grey. Sun on the surface. | Wide | Static | D | Direct colour rhyme with shot 1.03. Same framing, opposite temperature. |

---

### ACT 6 — "UMUNSI MUSHYA" *(Together / The New Day)* · 00:48.0 → 01:00.0
**Function:** recreation and dance fuse. Everyone is dancing — visitors, children, elders, the
troupe. The film ends not with a landscape but with a **person**, then the land again, then black.
**Mood:** sunset to dusk, communal, warm, then hushed.

| # | TC in | Dur | Shot | Frame | Motion | Cut | CapCut treatment |
|---|---|---|---|---|---|---|---|
| 6.01 | 00:48.0 | 1.2 | **Everyone dancing** — a visitor, clumsy and joyful, pulled into the line by a dancer. Wide. | Wide, 9:16 | Gimbal orbit | B | Speed 0.8×. Crowd + drum audio full. This is the thesis shot: *recreation as belonging*. |
| 6.02 | 00:49.2 | 1.0 | **Hands clapping** across the circle, cut with **feet stomping** earth. | CU ×2 | Static | B×2 | 4-frame cuts. Pure rhythm. |
| 6.03 | 00:50.2 | 1.2 | **The full troupe + the crowd**, one frame, dancing together at golden hour. | Wide, drone rising | Drone pull-up | B | Keyframe `Scale` 100→90 while `Position` rises — a real drone-lift feel on a locked shot. |
| 6.04 | 00:51.4 | 1.0 | **A dancer's leap** against the setting sun, silhouette. | Wide, backlit | Locked | B | Crush exposure −18, rim highlights +22. |
| 6.05 | 00:52.4 | 1.4 | **Lake Kivu at dusk**, longhorn *inyambo* cattle silhouetted along the shore. | Wide | Slow dolly | D | `Effects → Light Effect → Sunset Rays` 18, intensity low. Temp +16. |
| 6.06 | 00:53.8 | 1.4 | **Night**: a fire, sparks rising, faces lit orange, drumming continuing off-frame. | MS, backlit by fire | Handheld | D | `Effects → Nature → Sparkle` or `Particles` at 12 for the embers. Firelight in A3. |
| 6.07 | 00:55.2 | 1.6 | **THE LAST FACE.** A dancer, close, catching breath, looks straight into the lens and smiles. Hold. | ECU | Locked | D | Speed 0.8×. **Hold this frame for the final drum hit at 00:56.8.** Music decays to ambience only. |
| 6.08 | 00:56.8 | 2.0 | **Wide of the hills at dusk**, mist returning. The same valley as shot 1.01. Full circle. | Extreme wide | Locked | D | Same grade as 1.01 but warmer — the film ends in the same place, changed. |
| 6.09 | 00:58.8 | 1.2 | **Closing card** over black or over 6.08. | — | — | Fade | Text block 1: `UMURIRO W'URWANDA` · Text block 2: `Come to rest. Leave dancing.` · Text block 3 (small): `Rwanda — Land of a Thousand Hills` · `Animation → In → Fade + Blur`, `Out → Fade`. Fade to black over the last 12 frames. |

---

## 6. Text & title copy (verified by a native speaker before delivery)

| Position | Kinyarwanda | English | Where |
|---|---|---|---|
| Opening sub | *Igihugu cy'imisozi igihumbi* | Land of a thousand hills | Act 1, shot 1.04 |
| Act 2 card | *Kwitegura* | The Preparation | 00:05.2, 1.0 s |
| Act 3 card | *Kwidagadura* | Play / Recreation | 00:14.2, 1.0 s |
| Act 4A card | *Umushagiriro* | The Dance of Grace | 00:24.2, 1.2 s |
| Act 4B card | *Intore — Umuhamirizo* | The Chosen Ones / Warrior Dance | 00:27.6, 1.0 s |
| Act 5 card | *Abantu n'igihugu* | The People and the Land | 00:41.2, 1.2 s |
| Closing | *Umuriro w'Urwanda* | The Fire of Rwanda | 00:58.8 |
| Tagline | — | *Come to rest. Leave dancing.* | 00:59.2 |

**Typography rules:** one display face + one body face, maximum. Display for act cards and the
title; body for the tagline and credits. White or a warm off-white (#F5EFE6) — never pure #FFF,
it reads as digital. Letter-spacing +2 to +6 for Kinyarwanda words so apostrophes don't crowd.
Always `Text → Animation → Out → Fade` at 8 frames; hard-disappearing titles feel unfinished.
Keep every title inside the bottom-250 px safe zone on 9:16 so platform UI never covers it.

---

## 7. Variant cutdowns

| Cut | Length | What changes |
|---|---|---|
| **Hero** | 60 s | As written above. |
| **Reels/TikTok/Shorts** | 30 s | Cut Act 2 to 4 shots, Act 3 to 4 shots, Act 4A to 1 shot, Act 4B to 6 shots, drop Act 5 to 2 shots, keep 6.01 + 6.07 + closing card. Front-load the leap to 00:03. |
| **Hook cut** | 15 s | Cold open on the leap (4.04), then 8 hard cuts of dance, then the closing face. No nature act. |
| **Horizontal / YouTube** | 60 s or 90 s | Reframe 9:16 → 16:9 with CapCut `Ratio → 16:9`; **re-shoot or re-crop** any shot where the subject was centred vertically. In the 90 s version, restore the full Act 5 portrait montage and add a second recreation block (Akagera boat + gorilla trek) after Act 3. |
| **Tourism-board version** | 60 s | Replace the tagline with the client's line, add a lower-third logo bug at 00:56, and swap Act 6 fire shots for the client's preferred property/destination. |

---

## 8. Pre-flight checklist

**Before shooting**
- [ ] Music track chosen, licensed, and its BPM/drop structure confirmed
- [ ] Native-speaker sign-off on all Kinyarwanda text and any spoken lines
- [ ] Permissions for filming people, children (guardian consent), and on protected land (RDB/park permits)
- [ ] Drummers and dancers briefed: we need **isolated sound** takes (30 s of drums alone, bells alone, crowd clap alone)
- [ ] Shoot list printed from `assets/shot-list.csv` and sorted by location, not by act order
- [ ] 240 fps capability confirmed on the primary camera; ND filters packed for 1/120 at f/2.8 in daylight

**Before editing**
- [ ] All footage renamed to the convention in §3
- [ ] Proxies or a clean folder structure — Act folders, not one flat dump
- [ ] Music bed laid on the timeline and beats marked **before any picture edit**
- [ ] A CapCut project saved at 60 fps and the correct ratio from frame one (changing later forces re-cropping)

**Before delivery**
- [ ] Watch the whole thing **muted** — does the cutting still feel rhythmic?
- [ ] Watch on a **phone at arm's length**, not on a desktop — that's where it will be seen
- [ ] Titles inside safe margins; nothing covered by platform UI
- [ ] No clip over 3 s except the deliberate holds (5.01, 5.03, 6.07)
- [ ] Audio peaks under −1 dB; no clipping on the drop
- [ ] Colour is consistent across acts — the three-temperature arc reads, not random per-clip looks
- [ ] Export at the spec in §3 and re-watch the **exported file**, not the timeline preview

---

## 9. Related documents

| File | What it is |
|---|---|
| `storyboard.html` | Visual storyboard + beat map + CapCut build order — open in a browser, print to PDF |
| `CAPCUT-PLAYBOOK.md` | Tool-by-tool CapCut workflow: every phase, with exact menu paths and settings |
| `assets/shot-list.csv` | The 60 shots as a sortable shooting/assembly list |
| `assets/beat-grid.csv` | Cut points mapped to the beat structure, for timeline marking |
| `assets/sequence.json` | Machine-readable sequence data, for re-use or scripting |
