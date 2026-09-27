# Cheat Sheet

Every technique in the course on one page.

---

## The five ingredients of a prompt

| # | Ingredient | The question it answers |
|---|---|---|
| 1 | **Role** | Who should it act as? |
| 2 | **Task** | What exactly should it produce? |
| 3 | **Context** | What does it need to know? |
| 4 | **Format** | What shape? |
| 5 | **Constraints** | What to avoid? What are the limits? |

```
Act as [ROLE].

Context: [who I am, who it's for, why I need it]
Task: [specific deliverable]
Format: [shape, length]
Constraints: [avoid X, include Y, keep under Z]
```

---

## Six prompt patterns

**The Brief** — producing work

```
Act as [ROLE]. Context: [...] Task: [...] Format: [...]
Constraints: [...]
```

**The Critic** — improving your work

```
Here is [draft]: [PASTE]
Review as [ROLE]. Find the [N] weakest parts. For each: quote
the problem, why it's weak, a specific fix. Don't rewrite it all.
```

**The Explainer** — learning

```
Explain [X] to [AUDIENCE]. I know [Y] but not [Z].
Analogy from [FIELD I KNOW]. Intuition first, no formulas.
Then the formal version. Then test me with 3 questions —
no answers until I reply.
```

**The Extractor** — structure from mess

```
From the text below extract: [FIELDS].
Return as a markdown table. Write "not stated" rather
than guessing. [PASTE]
```

**The Reframer** — same content, new audience

```
Rewrite for [AUDIENCE], tone [TONE]. Keep: [X, Y, Z].
Remove: [X]. [PASTE]
```

**The Sparring Partner** — thinking

```
I'm considering [DECISION], leaning toward [A]. Don't just agree.
Argue the strongest case FOR [B], then say what evidence would
change my mind, then ask the two questions I'm not asking.
```

---

## Four steering moves

| Move | When | Say |
|---|---|---|
| **Narrow** | Too broad | `Focus only on [X], go deeper.` |
| **Sharpen** | Too wordy | `Cut to [N] words. Remove hedging.` |
| **Reshape** | Wrong form | `Convert to a table: [columns].` |
| **Re-level** | Wrong tone | `Explain to a smart 15-year-old.` |

**If three nudges fail → reset with a full brief.** Don't nudge a sixth time.

---

## Fixing bad output

| Problem | Fix |
|---|---|
| Generic | `What would you say if you knew my specific situation?` |
| Too long | `Half the length. Keep technical terms.` |
| Too short | `Expand point 2 with a worked example.` |
| Wrong tone | `Reads like marketing. Rewrite plain and direct.` |
| Hedging | `Commit to a recommendation and defend it.` |
| Missing the point | `Stop. Here's what I need: [RESTATE]. Start over.` |
| Sounds like AI | Give 2-3 examples of your writing; ban the tells |

**AI tells to ban:** delve, crucial, landscape, navigate, realm, unlock, harness, seamless, robust, leverage (as verb), "In today's fast-paced world", "It's important to note", everything in threes.

---

## Verification kit

```
1. How confident are you in each claim? Mark certain/likely/
   uncertain and say what you'd check.
2. What sources support this? Give URLs I can open.  → OPEN THEM
3. Now argue the opposite case as strongly as you can.
4. Which study? Title, authors, year. If you can't name
   one, say so.
5. List every assumption your answer makes.
```

🔴 **Never trust a citation you haven't opened.**
🔴 **Consistency is not accuracy** — it repeats its own inventions.

---

## Image prompt formula

```
[SUBJECT] + [ACTION] + [ENVIRONMENT] + [LIGHTING]
+ [STYLE] + [CAMERA] + [MOOD]
```

**Lighting:** golden hour · overcast diffused · harsh midday · rim light · studio softbox · neon night · candlelight

**Style:** 35mm film · Kodachrome 1970s · editorial fashion · flat vector · watercolour · woodcut · oil impasto · 3D render · isometric pixel art

**Camera:** close-up portrait · wide shot · low angle · overhead flat lay · rule of thirds · 85mm f/1.8 · slow dolly forward · handheld

For edits: **"keep everything else identical."**
Generate 4+ variations. Lock the seed once something is close.

---

## Video prompt formula

```
[SUBJECT] + [MOTION] + [CAMERA] + [ENVIRONMENT] + [LIGHTING]
+ [STYLE] + [DURATION]
```

**One subject, one action.** 4–10 seconds. **Image-to-video beats text-to-video.**

---

## Data analysis rule

🔴 **Never accept a number that didn't come from code that ran.**

```
1. Paste first 20 rows → ask what's wrong
2. Cleaning code → review every decision, ask what it guessed
3. RUN IT — verify row counts before and after
4. Ask for 8 candidate questions, pick what matters
5. Run analysis → paste real output back for interpretation
6. "What can't I conclude from this?"
7. Chart: specify size, labels, formatting
8. Sanity-check against what you already know  ← catches the most errors
```

---

## API quick reference

```python
import anthropic
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-haiku-4-5",     # sonnet-5 · opus-5-5 · fable-5-1
    max_tokens=500,               # ceiling, not target
    temperature=0,                # 0 = deterministic, 1 = creative
    system="You are...",          # persistent instructions
    messages=[{"role": "user", "content": "..."}],
)

text = "".join(b.text for b in message.content if b.type == "text")
message.usage.input_tokens
message.usage.output_tokens
message.stop_reason        # end_turn | max_tokens | tool_use
```

**Structured output:**

```python
response = client.messages.parse(
    model="claude-sonnet-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": text}],
    output_format=YourPydanticModel,
)
obj = response.parsed_output
```

**OpenAI equivalent:** `client.responses.create(model=..., instructions=..., input=...)` → `response.output_text`

---

## Model choice

| Need | Reach for |
|---|---|
| Learning, simple tasks, high volume | cheapest tier |
| Balanced real work | mid tier |
| Hard reasoning, agentic tasks | frontier tier |

**Start cheap. Escalate only when quality demands it.** Prices span ~100×.

---

## Cost control

```python
PRICES = {"claude-haiku-4-5": {"in": 1.00, "out": 5.00}}   # per 1M tokens

cost = (usage.input_tokens * PRICES[m]["in"]
        + usage.output_tokens * PRICES[m]["out"]) / 1_000_000
```

- Output tokens cost **more** than input (usually ~5×)
- **Trim conversation history** — biggest single saving
- **Set a spending cap** before your first call
- Verify prices on the official page — they change

---

## Debugging

| Symptom | Cause | Fix |
|---|---|---|
| Output cut off | `max_tokens` too low | Check `stop_reason == "max_tokens"` |
| `AuthenticationError` | Bad key | Check `.env` + `load_dotenv()` |
| `NotFoundError` | Wrong model name | Check official model list |
| `RateLimitError` | Too fast | Slow down, add retry |
| Invalid JSON | Truncation | Raise `max_tokens`, check `stop_reason` |
| Different answer each time | Normal | `temperature=0` for determinism |
| Invents facts | By design | Ground it with RAG, or verify |

---

## Safety

🔴 Never paste: passwords, API keys, ID numbers, PINs, others' private data
🔴 Always: `.env` in `.gitignore`, set a spending cap
🔴 Never clone a voice or generate a real person without consent
🔴 Never fake news imagery or misattribute quotes
🔴 Verify anything medical, legal, or financial with a human expert

---

**[← Back to the syllabus](./README.md)**
