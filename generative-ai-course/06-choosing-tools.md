# 06 · Choosing Your Tools

> **Time:** 25 minutes  
> **You'll learn:** which assistant to reach for, and how to decide for yourself as things change

There is no single "best" AI. There are tools with different strengths, and the people who get the most out of AI use **several**.

---

## First: the landscape changes constantly

Model names, prices, and features move every few months. **Anything you read comparing specific models — including this page — has a shelf life of roughly one quarter.**

So this module does two things:

1. Gives you a **current snapshot** (verified September 2026, with links so you can re-check)
2. Teaches you a **method** for choosing that doesn't expire

---

## The main chat assistants

| Tool | Made by | Genuinely good at | Weaker at | Free tier |
|---|---|---|---|---|
| **ChatGPT** | OpenAI | All-round work, widest ecosystem, voice and image features, custom GPTs | Can drift on very long threads | Yes |
| **Claude** | Anthropic | Long documents, careful reasoning, writing quality, coding | Smaller integration ecosystem | Yes |
| **Gemini** | Google | Google Workspace (Gmail/Docs/Sheets), huge context, research | Weaker outside Google's ecosystem | Yes |
| **Grok** | xAI | Real-time X/Twitter context, fast informal chat | Long-form depth, research | Yes (limited) |
| **Copilot** | Microsoft | Microsoft 365, Windows integration, coding in VS Code | General creative writing | Yes |
| **Perplexity** | Perplexity | Research with visible citations | General drafting | Yes |

**Practical advice:** use the default that matches your ecosystem, and keep a second one for the jobs your first is bad at.

- Live in Gmail/Docs? → **Gemini** first
- Live in Word/Excel/Outlook? → **Copilot** first
- Care most about writing and long documents? → **Claude**
- Want the biggest ecosystem and most features? → **ChatGPT**

Most people converge on two. That's healthy.

---

## The models behind them (September 2026)

These are the API model lineups — the engines underneath the chat apps. Chat apps often use a rotating selection, so treat this as "roughly what's under the hood."

**OpenAI** — [official model list](https://developers.openai.com/api/docs/models)

| Model | Input / Output (per 1M tokens) | Context | Positioning |
|---|---|---|---|
| GPT-6 Astra | $10 / $50 | 1.05M | Flagship, hardest reasoning and coding |
| GPT-6 Sol | $2 / $10 | 1.05M | Balance of intelligence and cost |
| GPT-6 Luna | $0.10 / $0.50 | 1.05M | Cheap, high-volume |

**Anthropic** — [official model list](https://platform.claude.com/docs/en/models/overview)

| Model | Input / Output (per 1M tokens) | Context | Positioning |
|---|---|---|---|
| Claude Fable 5.1 | $10 / $50 | 1M | Demanding reasoning, long-horizon agentic work |
| Claude Opus 5.5 | $4 / $20 | 1M | Default recommendation for most workloads |
| Claude Sonnet 5 | $2 / $10 | 1M | Speed and intelligence balance |
| Claude Haiku 4.5 | $1 / $5 | 200K | Fastest, near-frontier quality |

**Google** — [official model list](https://ai.google.dev/gemini-api/docs/models)

| Model | Notes |
|---|---|
| Gemini 3.8 Flash | Latest stable Flash — long-horizon coding and agents |
| Gemini 3.8 Flash-Lite | Cheapest, high-throughput |
| Nano Banana 2 / Pro | Image generation and editing |
| Veo 3.1 | Video generation with synchronised audio |
| Lyria 3.5 | Music generation |

> **Prices and models change.** Always confirm on the linked official pages before you budget anything.

### The pattern worth noticing

Look at the price spread: **$0.10 to $10 per million input tokens — a 100× range.** And the cheap models are genuinely capable for most tasks.

**This is the single most useful economic fact in AI:** the cheap model is usually good enough, and it costs one-hundredth as much. Default cheap, escalate when quality demands it. Module 12 puts this into practice.

---

## Beyond chat: the rest of the toolkit

| Category | Tools | Use for |
|---|---|---|
| **Research with citations** | Perplexity, NotebookLM, ChatGPT/Gemini with search on | Anything factual where you need to check sources |
| **Image generation** | Nano Banana (Gemini), GPT-Image (OpenAI), Midjourney, Flux | Illustrations, concepts, social graphics (Module 8) |
| **Video generation** | Veo, Sora, Runway, Kling | Short clips from text (Module 9) |
| **Voice / speech** | ElevenLabs, Gemini TTS, OpenAI TTS | Voiceovers, narration, accessibility |
| **Music** | Suno, Udio, Lyria | Songs, loops, background tracks |
| **Coding assistants** | GitHub Copilot, Cursor, Claude Code | Writing and refactoring code with you |
| **Local / offline models** | Ollama, LM Studio | Privacy, no internet, no per-token cost |
| **Automation** | Zapier, Make, n8n | Chaining AI into workflows |

You do not need all of these. You need to know they exist so that when a job calls for one, you know what to search for.

---

## The method: how to choose (doesn't expire)

When a new tool appears — and one will, next month — run it through these five questions.

### 1. What's the actual job?

Name it precisely. "Write" is not a job. "Draft a 200-word client email that sounds like me" is a job.

### 2. Does it need current information?

- **Yes** → you need a tool with **web search** switched on, or a research tool with citations
- **No** → any strong model works

### 3. Does it need my private data?

- **Yes** → check the data policy, or use a local model via Ollama/LM Studio
- **No** → no constraint

### 4. How much does being wrong cost?

- **High** (medical, legal, financial, published, safety) → use a strong model, verify everything, and get a human expert involved
- **Low** (brainstorming, drafting, personal learning) → any capable tool, skim the output

### 5. How often will I do this?

- **Once** → just do it in chat
- **Repeatedly** → save a prompt, or build a small script with the API (Part 3)

```
Job: summarise 40-page PDFs into 5 bullets, weekly
Needs current info?  No  → any model
Private data?        Yes → check policy, or run locally
Cost of error?       Med → verify names and numbers
Frequency?           Weekly → save a reusable prompt
→ Decision: Claude or Gemini (both handle long documents well),
            saved prompt, spot-check numbers.
```

---

## Free vs paid: an honest take

**Free tiers are genuinely good.** For most people doing most things, they're enough.

Pay when you hit a limit that actually costs you time:

| Upgrade when… | Why |
|---|---|
| You hit message caps during real work | Interrupted flow costs more than $20 |
| You need the strongest model for hard tasks | Frontier models show up on paid tiers first |
| You need larger file/document uploads | Free tiers cap document size |
| You need API access | Billed separately and by usage — and usually tiny amounts |

**Don't pay** out of curiosity or FOMO. Free tiers are the right place to learn, and everything in Parts 1 and 2 of this course works on them.

---

## Running models locally (optional, worth knowing)

Tools like **Ollama** and **LM Studio** let you run open-weight models on your own machine.

**Why you'd want to:**
- ✅ Complete privacy — nothing leaves your computer
- ✅ Works offline
- ✅ No per-token cost

**The trade-offs:**
- ❌ Needs decent hardware (RAM especially)
- ❌ Open models generally lag the frontier closed models
- ❌ More setup

You don't need this for the course. Know it exists for the day you have a privacy constraint.

---

## ✏️ Exercise 6.1 — Compare two tools (15 min)

Take **one real task** you have — a document to summarise, an email to write, a concept to learn.

1. Run it in your primary assistant
2. Run the **identical prompt** in a different assistant
3. Compare: accuracy, usefulness, tone, length, formatting

Write down which you preferred and **why**. You're building personal judgement, which beats any comparison table — including this one.

---

## ✏️ Exercise 6.2 — Find your second tool (10 min)

Identify the thing your main assistant is *worst* at. Try that specific job in a tool that's supposed to be good at it.

If the improvement is real, you now have a two-tool setup. That's the normal end state.

---

## Key takeaways

- ✅ **No single best tool.** Most people settle on two.
- ✅ Start with your **ecosystem default**; add a second tool for its weak spot.
- ✅ **Model prices span ~100×**. Default cheap; escalate when quality demands it.
- ✅ Choose by **job → currency → privacy → stakes → frequency.**
- ✅ **Free tiers are enough to learn on.** Pay only when a limit costs you real time.
- ✅ Comparison tables expire in about a quarter. **The method doesn't.**

---

**Next: [07 · Writing, Research & Ideas](./07-writing-and-research.md)** — Part 2 begins.
