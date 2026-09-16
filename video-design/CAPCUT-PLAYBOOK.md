# CapCut Build Playbook
### For *Umuriro w'Urwanda* — how to actually construct the sequence in CapCut

Everything here is written for **CapCut Desktop** (the most capable version: unlimited
multi-track timeline, full keyframe set, Optical Flow smooth slow-mo, chroma key, advanced
stabilisation). Mobile notes are flagged where the UI differs. Menu paths are given as
`Panel → Option → Setting`.

---

## Phase 0 — Project setup (5 min, do not skip)

1. `New project` → top-left `Ratio` → **9:16**.
2. Top-right export panel → confirm the project **frame rate is 60 fps**.
   > ⚠️ CapCut does not let you cleanly change the base frame rate after you've cut.
   > Setting it wrong here means your 240 fps slow-motion clips will be interpreted badly.
3. `Settings → Project` → turn **off** any auto-watermark / auto-template behaviour.
4. Create the folder structure on disk *before* importing:
   ```
   URWANDA/
     00_MUSIC/        (licensed track, isolated drum takes, SFX)
     01_ACT1_BREATH/
     02_ACT2_PREP/
     03_ACT3_RECREATION/
     04_ACT4_DANCE/
     05_ACT5_PEOPLE/
     06_ACT6_TOGETHER/
     07_TITLES/
     99_OUTTAKES/
   ```
5. Import by folder, not by dumping everything into one bin.

**Timeline track map (keep it this way for the whole build):**

| Track | Content |
|---|---|
| V1 | Main picture — every shot |
| V2 | Overlays: dust, light leaks, lens flare, particles |
| V3 | Matte / mask layers for match cuts and split-screens |
| V4 | Titles and act cards |
| V5 | Adjustment clips (`Adjust` applied to a whole act at once) |
| A1 | Music bed |
| A2 | Location ambience |
| A3 | Diegetic dance sound (drums, bells, stomps, crowd) |
| A4 | Design SFX (whooshes, risers, booms) |
| A5 | Voice / ibyivugo |

---

## Phase 1 — Music bed and beat grid (20 min) · *do this before picture*

1. Drag the licensed track to **A1**. Trim to exactly **60.0 s** — align the track's
   first drop with **00:05.0** in the timeline. Use `Split` + nudge, not by dragging blindly.
2. Select A1 → `Audio → Beats` → **`Auto-generate`**. Choose **Beat II** (denser markers)
   if the track has fast percussion; **Beat I** if it's sparse.
3. Zoom the timeline to maximum. Inspect every marker against the waveform:
   the auto-detect will miss some ingoma rolls and ghost-notes. Add or delete manually
   with `Add beat` / right-click → `Delete beat`.
4. **Add manual markers** (desktop: press `M`) at these structural points regardless of beat:
   ```
   00:05.000  DROP 1
   00:24.000  BREAKDOWN START
   00:27.000  DROP 2
   00:38.000  EXHALE START
   00:41.000  EXHALE END
   00:56.800  FINAL DRUM HIT
   01:00.000  END
   ```
   These come from `assets/beat-grid.csv`.
5. Split A1 at **00:24.0** and at **00:27.0**. On the middle section (the breakdown),
   apply `Volume → -14 dB` and `Fade In → 0.4 s` / `Fade Out → 0.4 s` so the groove
   steps back and only drums and ambience carry those three seconds.
6. At **00:56.8**, split A1 again and `Fade Out → 3.0 s` on the tail, so the music decays
   into pure ambience for the closing card.
7. Lock A1 (right-click → `Lock`) so you never accidentally move it again.

**Ambience and design layers:**
- `Audio → Extract` on your best nature clips to pull lake/forest sound onto **A2**.
  Set them to **`Loop`** off, `Volume` −15 dB, and `Fade In/Out` 1 s at each edge.
- `Audio → Sounds`, search: `whoosh`, `deep boom`, `riser`, `vinyl stop`, `bell`, `crowd clap`.
  Place them on **A4** strictly on cut points — never floating between them.
- `Audio → Sound Effects → Reduce Noise` on A2 if the location audio is windy.
  (Noise reduction is a **Pro** feature. On free, use `Volume` automation instead.)

---

## Phase 2 — Assembly pass (60–90 min) · *structure only, no effects*

Work act by act from `assets/shot-list.csv`. For each shot:

1. Drag the clip to **V1**, `Split` at the in-point, `Split` at the out-point, delete the excess.
2. Snap the clip's **first frame** exactly onto a beat marker. Use the yellow marker line
   as a magnet — CapCut's timeline snapping is on by default; keep it on.
3. Set the clip length to the duration given in the design sequence, ± 3 frames.
4. **Do not** add a transition, effect, filter or piece of text yet. Just build all 60 shots
   and watch it end to end against the music.

> **Why this order:** effects-first editing is the #1 reason amateur cuts feel cluttered.
> If the assembly is rhythmic with nothing on it, every effect you add later is a gain.
> If the assembly is not rhythmic, no amount of glow will save it.

**Checkpoint:** play the assembly **muted**. If the picture still cuts in a way that feels
like music, continue. If not, fix the cutting before you go on.

---

## Phase 3 — Speed work (30 min)

Two tools, used deliberately:

### `Speed → Normal` (flat)
For anything that simply needs to run slower or faster than reality:
| Use | Setting |
|---|---|
| Grace material (4.01–4.03, 5.01, 6.07) | 0.35×–0.4×, **`Smooth slow-mo → Optical Flow` ON** |
| Fabric / mane detail (2.07, 4.17) | 0.3×, Optical Flow ON |
| Drummer frenzy (4.12) | **1.1×** — slightly over real time reads as intensity |
| Wide establishing shots | 0.8×–0.9× for a dreamy drift |

> ⚠️ **Optical Flow artefacts** on fast-moving sisal fibres, splashing water and patterned
> beadwork. When you see smearing or ghosting, back off: raise the speed to 0.6×, or switch
> `Smooth slow-mo` to `Frame blending`. Frame blending is safer on busy textures; Optical
> Flow is prettier on clean silhouettes. Test both on 4.04 before committing.

### `Speed → Curve` (ramping) — the film's signature
`Select clip → Speed → Curve → Customized` and drag the curve points.

| Shot | Preset starting point | Curve shape | Purpose |
|---|---|---|---|
| 2.05 drum strike | `Bullet` | 1× → 0.3× for 6 frames → 1× | The hit lands with weight |
| 3.01 kayak splash | `Hero` | 1.4× → 0.4× → 1× | Rush in, hang on the spray |
| 3.07 breaking the surface | `Bullet` | apex at the surface break, 0.3× | Water in the air |
| 4.04 **the leap** | `Customized` | 1× → 0.5× at the apex → 1× on landing | The apex sits **on** the downbeat |
| 4.05 **the landing** | `Customized` | 1× → 0.2× for 5 frames → 1.2× | Dust explosion reads as an impact |

**Rule for 4.04 / 4.05:** place the curve's slowest point exactly on the beat marker, then
let the clip accelerate *out* of the beat. Ramping *into* a beat feels mushy; ramping *off*
a beat feels powerful.

---

## Phase 4 — Match-cut spine (45 min) · *the thing that makes this film designed*

These are the shape echoes from §2 of the design sequence. Build each one the same way:

### Method A — the mask reveal
1. Put outgoing clip on **V1**, incoming clip on **V3** directly above, aligned so the
   match frame of both sits at the same timeline position.
2. Select V3 → `Mask → Circle` (or `Film` for a rectangle).
3. Keyframe the mask's **size** from 0% → 100% over 12 frames, centred on the shared shape
   (shield → wheel → drum skin → lake).
4. Add `Mask → Feather` 8–15 to hide the edge.
5. On the last frame, `Split` V3 and delete it, so the incoming clip takes over V1.

### Method B — the scale match
Where two shots share a **size** rather than a shape (a face filling the frame → a hill
filling the frame):
1. Keyframe `Scale` on the outgoing clip: 100 → 118 over its final 8 frames.
2. Keyframe `Scale` on the incoming clip: 118 → 100 over its first 8 frames.
3. The eye reads continuous expansion across the cut.

### Method C — the camera-pull transition
For the whip moves (3.04 tilt-up, 4.07 spear thrust):
`Transitions → Camera → Pull In` / `Pull Out` / `Whip` at **4–6 frames only**.
Longer than 8 frames and a camera-pull transition reads as a template.

### Method D — freeze-and-release (the micro-stop)
Used at 2.01, 4.06, and every drop:
1. `Split` the clip 3 frames after the in-point.
2. Select the 3-frame piece → right-click → **`Freeze`**. CapCut holds the frame.
3. Result: the image stops for a beat, then snaps into motion. On a drop, this hits hard.

### The specific matches to build

| Out | In | Shared shape | Method |
|---|---|---|---|
| 1.03 still lake | 4.01 rising arms | horizontal stillness → vertical rise | D + speed change |
| 2.06 spinning bells | 3.02 spinning bike wheel | rotation | A (Circle mask) |
| 2.11 turning line / round shield | 3.01 paddle splash | circle → circle | A |
| 3.10 painted spiral | 4.01 dancer's turning wrist | spiral | A + B |
| 3.12 gorilla's eye | 4.01 dancer's face | direct eye contact | D, music drops out |
| 4.17 flying mane | 5.05 wind in the tea terraces | fibres rippling | B |
| 5.07 golden lake | 1.03 grey lake | same frame, opposite colour | (colour rhyme, not a cut) |
| 6.08 dusk valley | 1.01 dawn valley | identical composition | D, full circle |

---

## Phase 5 — Keyframed motion (30 min)

`Select clip → playhead at frame → click the ◆ diamond → move/zoom → playhead later → ◆ again.`
CapCut interpolates between. Available on: `Scale`, `Position`, `Rotation`, `Opacity`, and
every `Adjust` parameter.

**The house moves for this film:**

| Move | Keyframes | Where |
|---|---|---|
| **Slow push-in** | Scale 100 → 108 over 2.5 s | 1.02, 4.14, 5.02 — anything that needs gravitas |
| **Drone lift** | Scale 100 → 90 **and** Position Y +120 px, together | 6.03 — fakes a real drone pull-up on a locked shot |
| **Drift rotate** | Rotation 0 → 8° over 2 s | 4.10 top-down formation |
| **Fake handheld** | Position ±6 px, 3 keyframes, irregular | Any locked-off shot that feels too static |
| **Text nudge** | Position on the text layer, 8 frames, synced to the drop | Act cards |

**Easing:** CapCut desktop lets you set the interpolation curve on a keyframe. Use
**ease-in-out** for the push-ins and lifts. Linear easing on a scale move looks mechanical.

---

## Phase 6 — Colour (40 min) · *do it with adjustment clips, not per clip*

**Do not** colour each of the 60 clips individually. You will get 60 different looks.

1. Put an `Adjustment clip` on **V5** spanning each whole act.
2. Grade the adjustment clip. Every shot in that act inherits the look.
3. Only then go back and fine-tune individual problem shots on V1.

### The three-temperature arc

| Act | Temp | Tint | Exposure | Contrast | Highlights | Shadows | Saturation | Glow | Fade | Vignette |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** Breath | −10 | +2 | −5 | +6 | −15 | +8 | −6 | 6 | 10 | 8 |
| **2** Prep | +8 | 0 | 0 | +10 | −5 | −4 | +6 | 10 | 4 | 6 |
| **3** Recreation | +6 | −2 | +5 | +8 | −8 | +4 | **+14** | 12 | 0 | 4 |
| **4** Dance | +10 | +2 | −3 | **+16** | −10 | −8 | +8 | 14 | 0 | 10 |
| **5** People | +14 | 0 | +3 | +6 | −10 | +8 | +4 | 18 | 6 | 6 |
| **6** Together | +16 | +2 | −2 | +8 | −14 | +6 | +8 | **22** | 8 | 12 |

### Per-clip refinements
- **Skin:** `Adjust → HSL → Orange` → Saturation +2–6, Luminance +8–12. This lifts faces
  without touching the whole frame. **Never** push skin saturation above +8 — it goes orange-plastic.
- **Water:** `HSL → Blue/Aqua` → Luminance +10, Saturation +6 for the Kivu shots.
- **Greenery:** `HSL → Green` → Hue shift slightly toward yellow (−5) for golden-hour warmth,
  Saturation −5 to avoid neon grass.
- **Silhouettes** (4.18, 6.04): `Exposure −15 to −18`, then `Highlights +20` to recover the rim light only.
- **Consistency tool:** desktop `Adjust → Colour Match` can match a reference clip's look —
  useful when the drone shots and the ground shots were exposed differently.
- **Filters:** if you prefer presets, apply a film-look filter to the **adjustment clip** at
  **20–35% intensity**, then override with the manual values above. Full-strength filters
  are the fastest way to make a film look like a template.

---

## Phase 7 — Effects, overlays, textures (30 min) · *restraint is the skill*

**Budget: maximum 2 effects playing at any given moment, and at least 40% of the film with none.**

### V2 overlay layers (looping, full-act)
| Effect | Path | Intensity | Where |
|---|---|---|---|
| Film grain | `Effects → Retro → Film Grain` | 12–18 | Whole film, on V2, looped. Unifies 4K drone and phone footage. |
| Dust / particles | `Effects → Particles → Dust` | 10–14 | Acts 3 and 4 |
| Light leak | `Effects → Light Effect → Light Leak` | 15–25 | Act 1 and Act 6 only |
| Halo blur | `Effects → Light Effect → Halo Blur` | 10–14 | 5.01 the exhale only |
| Sunset rays | `Effects → Light Effect → Sunset Rays` | 12–18 | 6.05 |
| Vignette | `Effects → Lens → Vignette` | 6–10 | Acts 4 and 6 |

Set every V2 overlay's blend mode to **`Screen`** or **`Filter`** and drop opacity to
**20–40%**. Overlays at 100% are what make edits look amateur.

### V1 in-clip effects (short, targeted)
| Effect | Path | Duration | Where |
|---|---|---|---|
| Shake | `Effects → Bling → Shake` | 4–6 frames only | 4.05 landing, 3.06 zipline launch |
| Zoom blur | `Effects → Bling → Zoom` | 4–6 frames | 4.07 spear thrust, 3.03 POV |
| Soft focus | `Effects → Lens → Soft Focus` | first 8 frames of a clip | 1.02, 4.03 |
| Glitch | `Effects → Glitch` | **use once, or never** | Optional: 27.0 drop |

### What to avoid in this film
- ❌ Rainbow / RGB-split effects — wrong tone entirely
- ❌ 3D zoom photo effect on live footage — it warps faces
- ❌ Sparkle / heart stickers anywhere near Act 5 portraits
- ❌ More than one transition type per act
- ❌ Any effect on 5.03 (the elder's face) or 5.06 (the face in the crowd). Faces need nothing.

---

## Phase 8 — Transitions (15 min)

`Transitions` panel → apply between two clips on V1. Duration 0.3–0.8 s.

| Act | Allowed transitions | Notes |
|---|---|---|
| 1 | `Basic → Fade` (Dissolve) 0.8 s | Slow, hushed |
| 2 | **Hard cut**, occasionally `Camera → Pull In` 0.2 s | Beat-locked; hard cuts are the default |
| 3 | `Camera → Whip Left/Right` 0.2 s, `Blur → Vertical/Horizontal Blur` 0.3 s | Motion-matched to the recreation action |
| 4 | **Hard cuts only** | A transition inside the warrior section kills the impact |
| 5 | `Basic → Dissolve` 1.0 s, `Light → White Flash` 0.3 s at 41.0 | Long, reverent |
| 6 | `Basic → Dissolve` 0.8 s, `Light → Sunset` for 6.05 | Warm |

> **Rule:** in a 60-second film, **no more than 12 transitions total.** The rest are hard cuts.
> CapCut's library is huge; using most of it is the mistake.

---

## Phase 9 — Titles, act cards, captions (30 min)

### Act cards (V4)
1. `Text → Default text` → type the Kinyarwanda word.
2. `Font` → pick **one** display face. If CapCut's library doesn't have what you want,
   `Text → Font → Import` a locally licensed font file (desktop only).
3. `Style` → colour **#F5EFE6** (warm off-white), size ~12 (relative), letter-spacing **+4**,
   stroke **off**, shadow **on** at 40% opacity / 6 px blur / 45° / 8 px distance.
   A shadow is what makes white text readable over bright sky and water.
4. `Animation → In → Fade` **plus** `Blur` (6–8 frames). `Animation → Out → Fade` (8 frames).
   Set `Loop` off.
5. Position: centre of frame for act cards; **bottom 250 px safe zone** for anything that
   must not be covered by platform UI on 9:16.
6. Duration per the copy table in §6 of the design sequence.

### Subtitles (if there's speech or an ibyivugo line)
1. `Text → Auto captions` → source: **Audio** → language: the spoken language.
   > ⚠️ **Auto captions is a Pro feature** and has monthly free-use limits on some regions.
   > Kinyarwanda support is inconsistent — **always proof-read the output**. If CapCut
   > mistranscribes (it likely will for Kinyarwanda), delete the auto result and type the
   > captions manually on the captions track. There are only a handful of lines in this film.
2. `Text → Auto captions → Batch edit` to fix all lines in one pass.
3. Style: same off-white, size ~8, with a 30% black background box for legibility over
   bright water, or a hard shadow for legibility over dark forest.
4. `Animation → In → Typewriter` at 2 frames per character for the closing tagline only.
   Everywhere else, plain `Fade` — typewriter everywhere is distracting.
5. `Text → Speech-to-text → Auto translate` can produce the English line under the
   Kinyarwanda. Verify every word with a native speaker.

---

## Phase 10 — Audio polish (20 min)

1. **Ducking:** every A3 or A5 event drops A1 by 4–6 dB. Desktop: keyframe `Volume` on A1.
   Mobile: split A1 around the phrase and set the middle piece's volume.
2. **Hit points:** the loudest moment in the whole mix should be **4.05** (the landing).
   Check the waveform — if something else is louder, pull it down.
3. `Audio → Fade In` 6 frames and `Fade Out` 12 frames on **every** audio clip. No clicks.
4. **Silence is a tool.** At 00:24.0 the music drops out completely for the breakdown.
   Don't fill it. The emptiness is what makes Drop 2 at 00:27.0 land.
5. Keep the real drum, bell and stomp audio (A3) — never replace authentic dance sound
   with library percussion. Sync issues of 1–2 frames are fine; the ear forgives it and
   the authenticity is worth more than sample-accurate sync.
6. Final levels: music −6 dB peak, A3 −3 dB on 4.05 only, SFX −14 dB, ambience −15 dB.
   Master peak under **−1 dB**, integrated loudness **−14 LUFS**.

---

## Phase 11 — Export and QC (15 min)

1. Top-right `Export`:
   - **Resolution:** 2160p / 4K (Pro) — otherwise 1080p
   - **Frame rate:** 60 fps
   - **Bit rate:** `Higher` (desktop) or `Recommended` at minimum
   - **Codec:** H.264 · **Format:** MP4
   - **Smart HDR:** OFF unless the whole source set is HDR (mixing gives inconsistent results)
2. Export, then **open the exported file and watch it**, not the timeline preview.
   CapCut's preview drops frames on effect-heavy sections; the export is the truth.
3. Run the §8 pre-flight checklist from the design sequence.
4. Watch it **on a phone**, at arm's length, with the sound on the phone's speakers, then
   again on headphones. Fix anything that only worked on one of the two.
5. Deliverables to export:
   ```
   URWANDA_master_9x16_4K60.mp4      (hero)
   URWANDA_social_9x16_1080p60.mp4   (30 s cutdown)
   URWANDA_hook_9x16_1080p60.mp4     (15 s cutdown)
   URWANDA_horizontal_16x9_4K30.mp4  (if required)
   URWANDA_coverframe.png            (thumbnail, from 4.04 or 6.04)
   ```

---

## Free vs Pro — what this film needs

| Capability used | Free | Standard | Pro |
|---|---|---|---|
| Multi-track timeline, split, trim | ✅ | ✅ | ✅ |
| Keyframe animation (all parameters) | ✅ | ✅ | ✅ |
| Speed curves + Optical Flow smooth slow-mo | ✅ | ✅ | ✅ |
| Chroma key, stabilisation | ✅ | ✅ | ✅ |
| Auto beat / beat markers | ✅ | ✅ | ✅ |
| Transitions & effects library | ✅ (subset) | ✅ (larger) | ✅ (full 12M+) |
| Watermark-free export | ⚠️ varies | ✅ | ✅ |
| **4K export** | ❌ (1080p max) | ❌ (1080p max) | ✅ |
| **Auto captions** | ❌ / very limited | ❌ / very limited | ✅ |
| **Motion tracking** (text following a dancer) | ❌ | ❌ | ✅ |
| **Noise reduction** on location audio | ❌ | ❌ | ✅ |
| Vocal isolation (separating the ibyivugo voice from drums) | ❌ | ❌ | ✅ |
| Cloud storage / cross-device project sync | Limited | Limited | ✅ |

**Verdict:** you can cut **90% of this film on the free tier** at 1080p. Buy Pro for a month
if you need 4K delivery, auto captions, or motion-tracked titles. Motion tracking is genuinely
worth it for one shot: tracking the words `INTORE` onto the leaping line at 4.04.

---

## Common failure modes — and the fix

| Symptom | Cause | Fix |
|---|---|---|
| Slow-mo looks smeary on the sisal manes | Optical Flow failing on fine fibres | Switch to `Frame blending`, or raise speed to 0.6× |
| The drop doesn't hit | Cut is 2–4 frames off the beat marker | Zoom to max, nudge by single frames. This is 90% of "why doesn't my edit feel good" |
| Everything looks oversaturated | Filter at full strength + saturation adjust stacked | Drop filter to 25%, remove the manual saturation boost |
| Faces look orange | HSL Orange saturation pushed too far | Cap at +6, and lift Luminance instead of Saturation |
| Titles unreadable over the lake | White text on white water, no shadow | Add a shadow (40%, 6 px) or a 30% black box behind the text |
| The middle feels long | Act 4B cuts are longer than 0.5 s | They must be 0.4–0.5 s. Trim 4 frames off each and it will snap |
| The ending feels abrupt | 6.07 not held long enough | Hold the last face for a full 1.6 s with the drum hit at 00:56.8 inside it |
| Edit feels like a template | Too many transitions and effects | Delete half of them. Hard cuts and clean colour are the look |
