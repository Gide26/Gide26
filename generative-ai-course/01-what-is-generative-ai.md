# 01 · What *Is* Generative AI?

> **Time:** 20 minutes
> **You'll learn:** the one mechanism behind all of it — in plain language

You cannot prompt well without a rough mental model of what's happening. This lesson gives you that model. No maths. No code. One idea, explained properly.

---

## The one idea: it predicts what comes next

Everything in this course rests on a single mechanism.

A language model was shown a large fraction of the internet — books, articles, code, conversations — and given one repetitive task, over and over:

> *Here is the beginning of a piece of text. Guess the next piece.*

That's it. That's the training. Do this billions of times, on text covering nearly every topic humans write about, and something surprising happens: **to be good at guessing the next word, you have to learn a lot about the world.**

To correctly continue *"The capital of Uganda is…"* a model must have absorbed that fact. To correctly continue a Python function it must have absorbed how code works. To continue a poem in iambic pentameter it must have absorbed rhythm.

Knowledge, reasoning patterns, writing styles, and logic all get squeezed in as a side effect of compression.

### The autocomplete analogy — and where it breaks

Your phone keyboard suggests the next word. That's the same core mechanism.

The difference is **scale and training**, and scale changes the character of the thing:

| Phone autocomplete | A frontier language model |
|---|---|
| Predicts the next word | Predicts the next word |
| Trained on *your* typing | Trained on a large share of human written output |
| Knows your habits | Absorbs facts, logic, styles, languages |
| Suggests 3 words | Writes essays, code, analysis, dialogue |
| No understanding of task | Follows complex multi-part instructions |

**Where the analogy breaks — and this matters:** autocomplete isn't trying to be *correct*, and neither is the model. It's trying to be *plausible*. Most of the time plausible and correct coincide. When they don't, you get a confident, well-written, completely false answer.

That single sentence explains most of the problems people have with AI. Hold onto it.

---

## Why it feels like talking to something

The model generates text. The *chat* feeling comes from a layer on top: your messages and its messages get glued together into one continuous document, and it predicts what a helpful assistant would write next.

```
[System: You are a helpful assistant.]
[User: How do I remove a background from a photo?]
[Assistant: ← the model predicts this]
```

It isn't retrieving a stored reply. It is continuing a conversation transcript in the most plausible way — one word at a time, each choice influenced by every word before it.

This has two practical consequences:

1. **Earlier messages shape later answers.** The context is literally part of the input. Which is why supplying context works so well, and why a long rambling chat can drift.
2. **Order matters.** Instructions at the start and end of a long prompt tend to land harder than instructions buried in the middle.

---

## Tokens: what you're actually paying for

Models don't read characters or words — they read **tokens**, chunks of text that are usually part of a word.

Rough guide for English:

```
1 token      ≈ 4 characters  ≈ ¾ of a word
100 tokens   ≈ 75 words      ≈ a short paragraph
1,000 tokens ≈ 750 words     ≈ a 3–4 minute read
```

Why you care:

- **Context window** — the maximum tokens a model can consider at once, counting your input *and* its output. Modern models handle hundreds of thousands to over a million tokens ([Claude models](https://platform.claude.com/docs/en/models/overview) and [OpenAI's flagship models](https://developers.openai.com/api/docs/models) both list ~1M-token windows). That's why you can paste a whole book and ask questions.
- **Cost** — the API charges per token, separately for input and output (Module 12).
- **Limits** — free chat tiers often cap by message count or by tokens.

You never need to count tokens by hand. You only need to know they exist and that *longer input costs more and eventually hits a ceiling.*

---

## The same idea, other media

"Generative AI" isn't only text. The pattern — *learn the shape of real data, then produce new samples* — applies everywhere:

| Medium | What it learns | What you give it |
|---|---|---|
| **Text** | How words follow words | A prompt |
| **Images** | How pixels arrange into photos and art | A description (Module 8) |
| **Video** | How images change over time | A description or a starting clip (Module 9) |
| **Audio / music** | How sound waves form speech and songs | Text or a reference (Module 9) |
| **Code** | How programs are structured | A description of what to build (throughout Part 3) |

For images the mechanism is often described as **starting from random noise and gradually refining it toward something that matches your description** — which is a genuinely useful mental model, because it explains why you get a *different* image each time you press generate even with an identical prompt.

---

## What it genuinely cannot do

Knowing the limits makes you a better user than 90% of people.

**It doesn't know facts — it generates plausible text.** Sometimes that matches reality. Sometimes it doesn't. It has no internal fact-checker. (Module 5.)

**It doesn't know what it doesn't know.** It has no reliable sense of its own confidence. It will invent a citation as fluently as it recalls a real one.

**It has no persistent memory across chats** unless the product explicitly provides memory. New chat, blank slate.

**It can't do anything in the real world** unless given tools — web search, code execution, file access. On its own it only produces text. "Search the web for X" in a chat app works because the *app* searches and pastes results in, not because the model browses.

**It doesn't know the current date or today's news** unless connected to search. Every model has a **knowledge cutoff** — the date its training data ends. Current frontier models have cutoffs in 2026; [OpenAI](https://developers.openai.com/api/docs/models) and [Anthropic](https://platform.claude.com/docs/en/models/overview) both publish these per model.

**It mirrors your framing.** Leading questions produce leading answers. Ask "why is X terrible?" and you'll get a case against X — not because it has that opinion, but because it's continuing the pattern you started.

---

## ✏️ Exercise 1.1 — See the mechanism (10 min)

This exercise makes the core idea concrete. Do it.

**Step 1.** Start a new chat. Paste exactly:

```
The capital city of Uganda is
```

**Step 2.** Look at what came back. It completed your sentence. It didn't answer a question — you asked none. It continued text.

**Step 3.** Now try:

```
My name is Gide and I run a small bakery. Three problems I have are:
1.
```

Watch it generate a plausible list. It knows nothing about you or your bakery. It produced the most statistically likely continuation of that pattern.

**Step 4.** Finally, try a question you're confident the model *cannot* reliably know:

```
What is my baker's phone number?
```

If it gives a number, that's a fabrication — and a perfect demonstration of the whole problem. If it says it doesn't know, good.

**What just happened:** you watched prediction become apparent knowledge, and apparent knowledge become confident invention. Everything in Module 5 follows from this.

---

## ✏️ Exercise 1.2 — Spot the cutoff (5 min)

Ask your assistant:

```
What is today's date, and what is the most recent major world news story you know about?
```

Then compare the date it gives against your calendar. If it's wrong or vague, that's the knowledge cutoff showing through. Ask it what its knowledge cutoff is — most will tell you.

---

## Key takeaways

- ✅ Generative AI **predicts plausible continuations** of input. Everything else is a consequence.
- ✅ Learning to predict text well forced these systems to absorb a great deal about the world — but as *patterns*, not as *verified facts*.
- ✅ Chat works by gluing the conversation together and predicting the next turn.
- ✅ Tokens are the unit of text, context, and cost.
- ✅ The same core idea generates images, video, audio, and code.
- ✅ It cannot check facts, doesn't know its own limits, and only acts in the world through tools it's given.

---

**Next: [02 · Your First Real Conversation](./02-your-first-conversation.md)** — where we turn this understanding into results.
