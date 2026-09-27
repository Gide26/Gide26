# 08 · Generating Images

> **Time:** 30 minutes
> **You'll learn:** a reliable prompt formula for images, plus how to edit what you make

Image generation is the most immediately fun part of AI — and the part where most people give up too early, because their first few attempts look wrong.

The fix is a formula. Let's get it.

---

## Why your first images look bad

People type `a nice picture of a market` and get something generic. Same problem as text prompting: **vague in, vague out.**

Image models don't compose a scene the way you're imagining it. They start from noise and refine toward something matching your description. Every detail you omit gets filled in with whatever is statistically likely — which is almost never what you pictured.

**So: describe more than feels necessary.** Especially lighting, camera, and style. Those three change everything.

---

## The image prompt formula

```
[SUBJECT] + [ACTION/POSE] + [ENVIRONMENT] + [LIGHTING]
+ [STYLE] + [COMPOSITION/CAMERA] + [DETAILS/MOOD]
```

You don't need all seven every time. But when an image disappoints, check which you left out — it's usually **lighting** or **style**.

### ❌ Weak

```
a market in Kampala
```

### ✅ Strong

```
A bustling outdoor produce market in Kampala at golden hour.
In the foreground, a woman in her 40s arranges bright red
tomatoes into neat piles, laughing at something off-camera.
Behind her, stalls under faded blue tarpaulins stretch into
hazy depth. Warm late-afternoon sunlight rakes across the
scene, long shadows, dust motes catching the light.

Shot on 35mm film, shallow depth of field, documentary
photography, candid, rich warm colour grade, slight grain.
```

Notice how much of that is **light and camera**, not subject. That's the pattern.

---

## The seven components

### 1. Subject — who or what

Be specific. Age, clothing, expression, ethnicity, posture.

```
a woman in her 40s wearing a yellow headwrap, laughing
```
not
```
a person
```

### 2. Action / pose

Static subjects look lifeless. Give it something to do.

```
reaching up to hang laundry
looking over her shoulder mid-stride
stirring a pot, steam rising
```

### 3. Environment

Where, and what's around.

```
on a wooden veranda, potted plants, peeling green paint
```

### 4. Lighting — the highest-leverage one

This is where most people under-invest. **Lighting does more for an image than almost anything else.**

| Lighting | Effect |
|---|---|
| `golden hour` | Warm, flattering, nostalgic |
| `overcast diffused light` | Soft, even, no harsh shadows |
| `harsh midday sun, hard shadows` | High contrast, dramatic |
| `rim lighting from behind` | Subject separated from background, cinematic |
| `studio lighting, softbox` | Clean, commercial, product-shot |
| `neon, night, reflections in wet pavement` | Cyberpunk, moody |
| `candlelight, warm and dim` | Intimate, painterly |

### 5. Style — the second highest-leverage one

This is how you escape the default "AI image" look.

**Photographic:**
```
35mm film photography, shallow depth of field, slight grain
Kodachrome colour, 1970s documentary photography
editorial fashion photography, high contrast
iPhone snapshot, natural, unposed
product photography, white background, studio softbox
```

**Illustration:**
```
flat vector illustration, limited palette, clean lines
watercolour, loose brushwork, paper texture
woodcut print, high contrast black and white
children's book illustration, soft gouache texture
anime cel shading, Studio Ghibli background painting
```

**Artistic / render:**
```
oil painting, impasto, chiaroscuro, Rembrandt lighting
3D render, soft subsurface scattering, studio HDRI
isometric pixel art, 16-bit
linocut, two colours, hand-printed texture
```

### 6. Composition / camera

Controls how the image is framed.

```
close-up portrait, head and shoulders, eye level
wide shot, subject small in frame, vast landscape
low angle looking up, heroic framing
overhead flat lay, top-down
rule of thirds, subject left of frame
centred, symmetrical, frontal
85mm portrait lens, f/1.8, blurred background
```

### 7. Details and mood

```
warm, nostalgic, late-summer feeling
dust in the air, slightly worn, lived-in
muted earth tones with one pop of red
```

---

## Negative prompts

Some tools let you say what to **avoid**. Useful, but don't over-rely on it — long negative lists can degrade quality on some models.

```
avoid: text, watermark, signature, extra fingers, deformed
hands, blurry, oversaturated, plastic skin, cartoonish
```

The classic one: **hands are hard.** Models still struggle with fingers. If hands matter, either hide them (pockets, behind the back, out of frame) or ask for something that doesn't show them clearly.

```
hands in pockets
seated at a table, hands below frame
holding a mug with both hands
```

---

## Text in images — the known weak spot

Rendering readable words has historically been the hardest thing for image models. It's improving fast — [Google's Nano Banana Pro](https://ai.google.dev/gemini-api/docs/models) is specifically marketed for "precise text rendering" and studio-quality 4K layouts, and [OpenAI's image models](https://developers.openai.com/api/docs/models) handle text well too.

**But the reliable professional answer hasn't changed: generate the image, add the text in a design tool.** Canva, Figma, Photoshop, even PowerPoint.

If you do want text in the image:

```
A poster with the words "NAKASAERO MARKET" in large bold
sans-serif letters at the top, centred, high contrast
```

- Keep it short — one to five words. Long text almost always breaks.
- Put the exact words in **quotation marks**
- Check every letter after generating

---

## Iterating on images

Image generation is stochastic: **the same prompt gives a different image each time.** So:

### 1. Generate several, then choose

Always make 4+ variations before judging. Your first result is not representative.

### 2. Change one thing at a time

If you change style, lighting, and composition at once, you can't tell what helped.

### 3. Use the seed if available

Many tools expose a **seed** — a number that makes generation reproducible. Same seed + same prompt = same image. Lock the seed when you have something close, then tweak.

### 4. Describe the change, don't repeat the prompt

Good tools remember the image in the conversation:

```
Keep this exact composition and lighting, but change her
headwrap to deep blue.
```
```
Same image, but make it late evening instead of golden hour.
Cooler light, longer shadows.
```

---

## Editing images with AI

Editing is often more useful than generating — and now widely available.

| Edit | Prompt |
|---|---|
| Remove something | `Remove the person in the background.` |
| Change background | `Keep the subject exactly as is, replace the background with a plain studio grey.` |
| Change a colour | `Change the shirt to deep green, keep everything else identical.` |
| Extend the canvas | `Extend the image to the left, continuing the street scene in the same style.` |
| Change time of day | `Make this same scene at night with streetlights.` |
| Add an element | `Add a bicycle leaning against the wall on the right.` |
| Restyle | `Redraw this as a loose watercolour illustration, keeping the composition.` |

**The key phrase for edits:** *"keep everything else identical / keep the subject exactly as is."* Without it, models tend to regenerate the whole image.

### Where to do this

- **Gemini / Nano Banana** — conversational image editing (["Nano Banana" models](https://ai.google.dev/gemini-api/docs/models))
- **ChatGPT** — image generation and editing built into chat ([OpenAI image models](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst))
- **Midjourney** — strongest aesthetic quality for artistic work
- **Adobe Firefly / Canva** — commercial-safe, integrated with design tools
- **Flux** (open weights) — runs locally if you have the hardware

---

## Honest limits

| Limit | Workaround |
|---|---|
| **Hands and fingers** | Hide them, or generate several and pick |
| **Long rendered text** | Add text in a design tool |
| **Exact brand/logo reproduction** | Don't — trademark issues, and it'll get it wrong |
| **Consistent characters across images** | Hard. Use a reference image, or accept variation |
| **Precise spatial layout** | Rough composition works; exact placement doesn't |
| **Real people's likenesses** | Don't generate them without consent |

---

## Ethics — worth two minutes

- **Don't generate real people** without consent, especially in compromising situations.
- **Don't fake news imagery.** Ever. This is the genuinely harmful use case.
- **Check licensing** before commercial use. Terms vary substantially by tool.
- **Disclose AI-generated images** where it matters — journalism, advertising, political content.
- **Be careful with style mimicry** of living artists.

---

## ✏️ Exercise 8.1 — Light the same scene five ways (15 min)

Take one subject and change **only the lighting**. Generate all five:

1. `golden hour, warm light from the side, long shadows`
2. `overcast, soft even light, no harsh shadows`
3. `harsh midday sun, strong shadows from directly above`
4. `blue hour, deep blue shadows, artificial lights just coming on`
5. `single candle, warm and dim, deep shadow falloff`

This is the single most instructive image exercise there is. **Same subject, five completely different photographs.** Once you see it, you won't forget it.

---

## ✏️ Exercise 8.2 — Style transfer on one subject (10 min)

Same subject, same composition, five styles:

1. `35mm film photography, shallow depth of field, grain`
2. `flat vector illustration, limited palette`
3. `loose watercolour on textured paper`
4. `oil painting, impasto, chiaroscuro`
5. `isometric pixel art, 16-bit`

Same lesson as lighting: **style is doing a huge share of the work.**

---

## ✏️ Exercise 8.3 — Edit, don't regenerate (5 min)

Generate any image. Then edit it three times:

1. Change one colour
2. Remove an element
3. Change the time of day

Notice how much faster editing is than re-prompting from scratch. **Editing is the real workflow for most practical work.**

---

## Key takeaways

- ✅ Formula: **subject + action + environment + lighting + style + camera + mood**
- ✅ **Lighting and style do most of the work.** Most people omit them.
- ✅ **Generate 4+ variations** before judging — same prompt, different image every time.
- ✅ For edits, say **"keep everything else identical."**
- ✅ **Add text in a design tool**, not in the generator.
- ✅ Hide hands if they don't matter.

---

**Next: [09 · Video, Voice & Music](./09-video-audio-music.md)**
