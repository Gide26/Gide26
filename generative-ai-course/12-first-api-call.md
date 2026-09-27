# 12 · Your First API Call

> **Time:** 30 minutes  
> **You'll learn:** make a real API call, understand tokens and cost, choose models

Let's actually call a model from code. By the end of this module you'll understand what every AI application is doing underneath.

---

## The smallest useful program

Create `hello_ai.py`:

```python
import anthropic
from dotenv import load_dotenv

load_dotenv()

# The client automatically reads ANTHROPIC_API_KEY
# from your environment variables.
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Explain what an API is in one sentence."}
    ],
)

# The response content is a list of blocks.
# We want the text ones.
for block in message.content:
    if block.type == "text":
        print(block.text)
```

Run it:

```bash
python3 hello_ai.py
```

**That's it. You just called a frontier AI model from your own code.**

Everything else in AI engineering is this, plus more structure around it.

---

## Anatomy of the call

```python
message = client.messages.create(
    model="claude-sonnet-5",       # WHICH model
    max_tokens=200,                # HOW LONG can the reply be
    messages=[                     # THE CONVERSATION
        {"role": "user", "content": "..."},
    ],
)
```

### `model` — which brain

From [Anthropic's model list](https://platform.claude.com/docs/en/models/overview) (September 2026):

| Model | Input / Output per 1M tokens | Use for |
|---|---|---|
| `claude-haiku-4-5` | $1 / $5 | Cheap, fast — **start here** |
| `claude-sonnet-5` | $2 / $10 | Balanced — good default for real work |
| `claude-opus-5-5` | $4 / $20 | Anthropic's recommended default for most workloads |
| `claude-fable-5-1` | $10 / $50 | Hardest reasoning, long agentic tasks |

> **Start with `claude-haiku-4-5` for learning.** It's capable enough for nearly every exercise here and roughly 4–50× cheaper than the biggest models. Switch up only when output quality actually demands it.

### `max_tokens` — the ceiling

The maximum length of the reply. Not the target — the hard cap.

- 200 ≈ a short paragraph
- 1000 ≈ a decent email
- 4000 ≈ an article section

**If output gets cut off mid-sentence, raise `max_tokens`.** That's the most common beginner bug.

### `messages` — the conversation

A list of turns, each with a `role`:

- `"user"` — what you say
- `"assistant"` — what the model said before

```python
messages=[
    {"role": "user", "content": "My name is Gide."},
    {"role": "assistant", "content": "Nice to meet you, Gide!"},
    {"role": "user", "content": "What's my name?"},
]
```

**There's no server-side memory.** The model only knows what's in this list. Every call is independent. *You* maintain the history — which is exactly what Module 15 does.

---

## Reading the response

The reply isn't a plain string. It's an object:

```python
message.content        # list of content blocks
message.model          # which model actually answered
message.stop_reason    # why it stopped
message.usage          # token counts — see below
```

Let's see the important ones:

```python
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Name three fruits in one sentence."}
    ],
)

print("--- TEXT ---")
for block in message.content:
    if block.type == "text":
        print(block.text)

print("\n--- METADATA ---")
print("Model:      ", message.model)
print("Stop reason:", message.stop_reason)
print("Input tokens: ", message.usage.input_tokens)
print("Output tokens:", message.usage.output_tokens)
```

### `stop_reason` — why it stopped

| Value | Meaning | What to do |
|---|---|---|
| `end_turn` | Finished naturally | ✅ Normal |
| `max_tokens` | **Hit your cap — reply is truncated** | ⚠️ Raise `max_tokens` |
| `stop_sequence` | Hit a stop sequence you set | ✅ Intentional |
| `tool_use` | Wants to call a tool | Handle the tool call |

> **`max_tokens` is the silent killer.** Your code runs fine, the output is just cut off halfway, and you waste an hour debugging the wrong thing. **Always check `stop_reason`.**

### `usage` — what you're paying for

```python
message.usage.input_tokens    # tokens you sent
message.usage.output_tokens   # tokens it generated
```

**Output tokens cost more than input tokens** — typically 5× more. Generating is more expensive than reading.

---

## What does it actually cost?

Let's compute it. For `claude-haiku-4-5` at **$1 per million input** and **$5 per million output**:

```
A typical call:
  Input:  200 tokens  →  200 / 1,000,000 × $1  = $0.000200
  Output: 300 tokens  →  300 / 1,000,000 × $5  = $0.001500
                                        Total   = $0.0017
```

**That's 0.17 of a US cent per call.**

You could make roughly **580 calls for one dollar.**

This is why API work is cheap to learn on — and why costs matter at scale (10,000 calls/day × $0.0017 ≈ $51/month).

### Let's make the code tell you

```python
import anthropic
from dotenv import load_dotenv

load_dotenv()

# Prices in USD per 1M tokens — verify against
# https://platform.claude.com/docs/en/models/overview
PRICES = {
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00},
    "claude-sonnet-5":  {"in": 2.00, "out": 10.00},
    "claude-opus-5-5":  {"in": 4.00, "out": 20.00},
}

def cost(model, usage):
    p = PRICES.get(model, {"in": 4.00, "out": 20.00})
    return (usage.input_tokens * p["in"] + usage.output_tokens * p["out"]) / 1_000_000

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=150,
    messages=[{"role": "user", "content": "Give me one tip for learning Python."}],
)

print(message.content[0].text)
print(f"\nTokens: {message.usage.input_tokens} in / {message.usage.output_tokens} out")
print(f"Cost:   ${cost(message.model, message.usage):.6f}")
```

**Get in the habit of printing cost.** It costs nothing to add and it stops nasty surprises.

---

## Temperature (optional, but know it)

```python
message = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=200,
    temperature=0.3,      # ← new
    messages=[{"role": "user", "content": "..."}],
)
```

Controls randomness:

| Temperature | Behaviour | Use for |
|---|---|---|
| `0.0` | Nearly deterministic | Extraction, classification, JSON, code |
| `0.3` | Mostly focused | Factual Q&A, analysis |
| `0.7` | Balanced | General use |
| `1.0` | Creative, varied | Brainstorming, creative writing |

**Rule of thumb: use `0` for anything machine-readable, and default (omit it) for everything else.**

---

## The OpenAI equivalent

Worth seeing, because you'll meet it everywhere. OpenAI uses the **Responses API**:

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()   # reads OPENAI_API_KEY

response = client.responses.create(
    model="gpt-6-luna",
    instructions="You are a concise assistant.",   # system-level guidance
    input="Explain what an API is in one sentence.",
)

print(response.output_text)
```

Notice the differences:

| Anthropic | OpenAI (Responses API) |
|---|---|
| `messages=[...]` | `input="..."` |
| `system="..."` | `instructions="..."` |
| `max_tokens` required | optional |
| `message.content[0].text` | `response.output_text` |
| `ANTHROPIC_API_KEY` | `OPENAI_API_KEY` |

Different shapes, **identical concepts**: model, instructions, conversation, token limits, cost.

Learn one properly and the other takes an afternoon. [OpenAI's text generation guide](https://developers.openai.com/api/docs/guides/text) has the current details.

---

## Errors you'll hit

```python
import anthropic

try:
    message = client.messages.create(...)
except anthropic.AuthenticationError:
    print("Bad API key — check your .env file")
except anthropic.RateLimitError:
    print("Too many requests — wait a moment and retry")
except anthropic.APIConnectionError:
    print("Network problem — check your internet")
except anthropic.APIError as e:
    print(f"API error: {e}")
```

| Error | Cause | Fix |
|---|---|---|
| `AuthenticationError` | Bad or missing key | Check `.env` and `load_dotenv()` |
| `RateLimitError` | Too many calls too fast | Slow down, or add retry |
| `APIConnectionError` | No internet | Check connection |
| `NotFoundError` | Model name wrong | Check the model ID |
| Output truncated | `max_tokens` too low | Check `stop_reason == "max_tokens"` |

**Model names change.** If you get `NotFoundError` on a model from this course, check the [official model list](https://platform.claude.com/docs/en/models/overview) for the current name.

---

## ✏️ Exercise 12.1 — Explore the response (10 min)

Run the metadata example above. Then try:

1. Set `max_tokens=10` and watch `stop_reason` become `max_tokens`
2. Ask a long question and compare input vs output tokens
3. Run the same prompt 3 times at `temperature=1.0` — **notice the outputs differ**

That third one explains why "the AI gave me a different answer" is normal, not a bug.

---

## ✏️ Exercise 12.2 — Track your spend (10 min)

Write a script that:

1. Makes 5 different calls
2. Prints cost for each
3. Prints a **running total** at the end

```python
total = 0.0
# ... inside your loop ...
c = cost(message.model, message.usage)
total += c
print(f"Cost: ${c:.6f}  (running total: ${total:.6f})")
```

You'll almost certainly find the total is under a cent. **That's a genuinely useful thing to have discovered.**

---

## ✏️ Exercise 12.3 — Model comparison (10 min)

Same prompt, three models: `claude-haiku-4-5`, `claude-sonnet-5`, `claude-opus-5-5`.

Ask something requiring real reasoning, like:

```
A shop sells bread at 3,500 UGX. It costs 2,200 UGX to make.
Rent is 300,000 UGX per month. How many loaves must it sell
to break even? Show your reasoning.
```

Compare **quality, speed, and cost.** Often the cheap model is right — and when it is, you've learned the most valuable economic lesson in this course.

---

## Key takeaways

- ✅ Every AI app is: **model + messages + token limits**
- ✅ `max_tokens` is a **ceiling** — check `stop_reason` for silent truncation
- ✅ **Output tokens cost more than input** (usually ~5×)
- ✅ Costs are **tiny per call** — fractions of a cent on cheap models
- ✅ **No server-side memory** — you maintain conversation history
- ✅ `temperature=0` for machine-readable output; omit it otherwise
- ✅ **Start cheap.** Escalate only when quality demands it.

---

**Next: [13 · System Prompts & Roles](./13-system-prompts-and-roles.md)**
