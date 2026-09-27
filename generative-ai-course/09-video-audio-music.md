# 09 · Video, Voice & Music

> **Time:** 25 minutes
> **You'll learn:** what's realistically possible with generated video, speech, and music today

Video is the flashiest and least mature part of generative AI. Voice and music are the opposite: mature, cheap, and immediately practical.

Let's separate what genuinely works from what's still a demo.

---

## Video generation: the honest state of play

**What works well right now:**

- ✅ Short clips — roughly **4 to 10 seconds**
- ✅ Atmospheric shots — nature, crowds, abstract motion
- ✅ Simple single-subject action — someone walking, pouring coffee
- ✅ Extending or modifying footage you already have
- ✅ Shots with **native audio** — [Google's Veo 3.1](https://ai.google.dev/gemini-api/docs/models) generates synchronised audio

**What still doesn't:**

- ❌ Long, coherent narratives (a full scene with continuity)
- ❌ Reliable dialogue with correct lip-sync
- ❌ Complex multi-person interaction
- ❌ Consistent characters across multiple shots
- ❌ Physically complex actions — precise manipulation, acrobatics, sports
- ❌ Reliable on-screen text

**The practical mental model:** you're generating *shots*, not *scenes*. Think stock footage you can direct. Think B-roll. Think one beautiful 5-second clip to cut into a real video — not the video itself.

> **Where this helps right now:** social content, backgrounds, mood clips, animating stills, and filling gaps where you'd otherwise buy stock footage.

---

## Prompting video

Same principles as images, **plus motion and camera.**

```
[SUBJECT] + [MOTION] + [CAMERA MOVEMENT] + [ENVIRONMENT]
+ [LIGHTING] + [STYLE] + [DURATION]
```

### ❌ Weak

```
a market
```

### ✅ Strong

```
Medium shot. A woman arranges red tomatoes into neat piles
on a wooden stall. She looks up and smiles at someone
off-camera, then continues working.

Camera: slow dolly forward, shallow depth of field,
handheld feel.

Late afternoon golden light, dust motes drifting through
the frame, warm colour grade, 35mm documentary look.

6 seconds.
```

**The components that matter most for video:**

### Camera movement — name it

| Prompt | Result |
|---|---|
| `static camera` | Locked off, no movement |
| `slow dolly forward` | Pushes in toward the subject |
| `slow dolly out` | Pulls back, reveals context |
| `tracking shot` | Moves alongside the subject |
| `crane shot, rising` | Lifts up, establishing feel |
| `handheld, slight shake` | Documentary, immediate |
| `orbit around subject` | Circles the subject |
| `slow zoom in` | Subtle emphasis |

Naming your camera move is the single biggest quality jump in video prompting. Left unspecified, you get unpredictable drift.

### Keep motion simple

**One subject, one action.** Every added element multiplies the chance something melts.

```
✅ "A cup of coffee steaming on a wooden table, morning light"
❌ "A busy café with six people talking, a barista steaming
    milk, someone reading, and a dog under a table"
```

The second will produce something strange. Guaranteed.

### Duration

Shorter is more reliable. Start at 4–5 seconds. Push to 8–10 only when the simple version works.

---

## Generating video from a still image

**More reliable than pure text-to-video**, and the workflow you'll actually use.

1. Generate or shoot a still image you like
2. Animate it with a specific motion

```
Animate this image. The subject turns her head slightly
toward the camera and smiles. Steam rises from the cup.
Otherwise keep the frame still.
```

**Why it's better:** the composition is locked, so the model only has to solve motion. Fewer degrees of freedom, fewer failures.

Also excellent for:
- **Endless loops** — subtle ambient motion for backgrounds
- **Product shots** — slow rotation with a locked composition
- **Photo repair** — bringing old stills to life

---

## The voice / speech side — mature and genuinely useful

This is the most immediately practical part of this module, and the least hyped.

### Text-to-speech

Modern TTS is remarkably natural. [Google's Gemini 3.8 Flash TTS](https://ai.google.dev/gemini-api/docs/models) is described as studio-grade with voice design and replication; [OpenAI's audio models](https://developers.openai.com/api/docs/models) cover realtime voice conversations; ElevenLabs is the specialist choice.

**Genuinely good uses:**

| Use | Why it's great |
|---|---|
| **Narrating your own scripts** | Turn a blog post into audio |
| **Accessibility** | Read documents aloud for visually impaired users |
| **Learning a language** | Hear pronunciation on demand |
| **Draft voiceovers** | Test pacing before hiring a voice actor |
| **Localisation** | Translate and re-voice content |

**Prompting TTS** — you specify delivery, not just words:

```
Read this in a warm, unhurried female voice. Conversational
pace, slight smile in the tone. Pause naturally at commas.
Not a newsreader — more like someone telling a friend
something interesting.

[TEXT]
```

**Voice cloning** lets you replicate a specific voice from a short sample. Powerful and genuinely useful — and also the main tool for voice fraud.

**So:** only clone voices you own or have written permission to use. Never clone someone's voice without their explicit consent. This isn't a grey area.

### Speech-to-text

The inverse, and it's excellent:

- Meeting transcription with speaker labels
- Voice memos → searchable text
- Accessibility captions
- Interview transcription

Whisper-class models handle accented English well and are cheap to run.

---

## Music generation

Models like [Google's Lyria 3.5](https://ai.google.dev/gemini-api/docs/models) (full-length songs with structural coherence), Suno, and Udio generate complete tracks with vocals from a text description.

```
Upbeat afrobeats instrumental, 100 BPM, bright guitar
riff, percussion-forward, warm bass, no vocals.
Builds to a chorus at 0:45. 90 seconds.
```

**What it's good for:**
- ✅ Background tracks for videos and podcasts
- ✅ Loops and stingers
- ✅ Demoing a mood before briefing a composer
- ✅ Royalty-free-ish content (check terms per tool)

**What it's not good for:**
- ❌ Replacing a specific artist's sound (legal and ethical problem)
- ❌ Precise musical control — you describe, you don't notate
- ❌ Perfectly hitting an exact video length without editing

Always **check the licensing terms** before using generated music commercially. They differ a lot between tools and have changed before.

---

## A realistic project workflow

How this actually gets used today:

```
1. Write the script              → AI drafts, you edit
2. Narrate it                    → TTS
3. Generate B-roll               → 5-8 second video clips
4. Generate a music bed          → music model
5. Assemble in an editor         → CapCut / DaVinci / Premiere
6. Add text and titles           → in the editor, always
```

AI does steps 2–4. **You do 1, 5, and 6** — the parts that are actually about judgement and craft.

Notice that the generated pieces are all *short*. That's not a limitation you're working around; it's the shape of the technology right now.

---

## Ethics — the one that matters

**Generated video and audio are the deepfake problem.** This is where generative AI causes real harm.

- ❌ Never generate real people saying or doing things they didn't
- ❌ Never clone a voice without explicit consent
- ❌ Never create misleading political or news content
- ✅ **Disclose** AI-generated media where it could be mistaken for real
- ✅ Consider consent even for people you know

For audio especially: voice cloning fraud — impersonating a relative in an emergency phone call — is a live, real scam. **Don't build it, and warn your family it exists.**

---

## ✏️ Exercise 9.1 — One clip, three camera moves (10 min)

Generate the same simple scene with three different camera moves:

1. `static camera, locked off`
2. `slow dolly forward`
3. `handheld, slight shake`

Same subject, same everything else. **Watch how much the camera move changes the feel.** This is the video equivalent of the lighting exercise in Module 8.

---

## ✏️ Exercise 9.2 — Narrate something you wrote (10 min)

1. Take something short you've written
2. Generate speech from it, specifying voice and delivery
3. **Listen to it.** Does the pacing work?

You'll notice AI reads too evenly. The fix is in your script: shorter sentences, and punctuation where you want pauses. **This is a genuinely useful writing test** — bad writing is obvious the moment you hear it.

---

## ✏️ Exercise 9.3 — Animate a still (5 min)

Take any image from Module 8. Animate it with a single subtle motion.

```
Keep this image exactly as is. Add subtle motion: [X].
Everything else stays still.
```

Compare the result to generating video from text alone. **Image-to-video is more reliable, and it's the workflow you'll use most.**

---

## Key takeaways

- ✅ Video: **you're generating shots, not scenes.** 4–10 seconds, one subject, one action.
- ✅ **Name the camera move** — biggest quality lever in video.
- ✅ **Image-to-video beats text-to-video.** Lock the composition, animate the motion.
- ✅ **Voice and music are mature and immediately useful** — less hyped, more practical.
- ✅ **Never clone a voice without consent.** Voice fraud is real and happening now.
- ✅ AI makes the *pieces*. You do the script, the assembly, and the judgement.

---

**Next: [10 · Analysing Data with AI](./10-data-analysis.md)**
