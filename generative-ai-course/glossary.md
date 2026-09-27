# Glossary

Plain English, no jargon where jargon isn't needed.

---

## A

**Agent** — An AI system that can take multi-step actions: use tools, run code, browse, and decide what to do next, rather than answering once and stopping.

**API (Application Programming Interface)** — A way for your code to talk to a service. The "AI API" is how programs send prompts and get responses, instead of you typing into a website.

**API key** — A secret string that identifies you to an API. **Treat it like a password** — anyone with it can spend your money.

---

## C

**Chunk** — A piece of a document, created by splitting it up. In RAG you retrieve chunks rather than whole documents, because small relevant pieces beat large mostly-irrelevant ones.

**Context window** — The maximum amount of text a model can consider at once, counting your input and its reply. Modern models handle hundreds of thousands to over a million tokens.

**Chain of thought** — Having the model show its reasoning step by step before answering. Often improves accuracy on multi-step problems.

---

## E

**Embedding** — A list of numbers representing the *meaning* of a piece of text. Texts with similar meanings produce similar numbers, which lets you search by meaning rather than by matching words.

**Eval (evaluation)** — A repeatable test of how well your AI system performs. The only reliable way to know whether a prompt change actually helped.

---

## F

**Fine-tuning** — Additional training on your own examples to change how a model behaves. Powerful but usually unnecessary — **good prompting and retrieval solve most problems first.**

**Few-shot prompting** — Including a few examples of desired output in your prompt. One of the most reliable ways to control format and tone.

---

## G

**Generative AI** — AI that produces new content — text, images, video, audio, code — rather than only classifying or predicting.

**Grounding** — Forcing a model to base its answer on provided sources rather than its own recollection. The main defence against fabrication. See **RAG**.

---

## H

**Hallucination** — Confident, plausible, false output. Not a bug — a consequence of predicting plausible text rather than retrieving verified facts. (Also: *confabulation*.)

---

## I

**IDF (inverse document frequency)** — A score rewarding rare words over common ones in search. "Kampala" tells you more than "the".

**Inference** — Running a model to get output. What happens every time you send a prompt.

---

## K

**Knowledge cutoff** — The date a model's training data ends. It has no reliable knowledge of events after that date unless connected to search.

---

## L

**LLM (Large Language Model)** — The models behind text-generating AI. "Large" refers to the number of internal parameters learned during training.

---

## M

**Model** — The trained system that does the generating. Different models have different strengths, speeds, and prices.

**Multimodal** — Handling more than one kind of input or output — text, images, audio, video — in a single model.

---

## O

**Open weights** — Models whose internal parameters are publicly downloadable, so you can run them on your own hardware. See **Local model**.

---

## P

**Parameters** — The internal numbers a model learned during training. Loosely associated with capability.

**Prompt** — Everything you send to a model: instructions, context, examples, and the question.

**Prompt engineering** — The craft of writing prompts that reliably produce good output.

**Prompt injection** — When user-supplied text contains instructions that hijack the model ("ignore your previous instructions"). Defended against by clearly separating your instructions from user data — see **XML tags**.

---

## R

**RAG (Retrieval-Augmented Generation)** — Find relevant text first, then have the model answer using only that. Makes answers grounded and checkable instead of recalled and possibly invented.

**Reasoning model** — A model trained to work through problems step by step before answering. Better at hard logic and maths; slower and more expensive.

---

## S

**Seed** — A number that makes generation reproducible. Same seed + same prompt = same output. Useful once you have something close and want to tweak it.

**Stemming** — Reducing words to a common root so "returns" matches "return" and "policies" matches "policy". Matters more than you'd think in keyword search.

**Stop reason** — Why the model stopped generating. `end_turn` = finished; `max_tokens` = **hit your limit, output is truncated**.

**Streaming** — Receiving output token by token as it's generated, instead of waiting for the whole reply.

**Structured output** — Forcing the model to reply in a specific format, usually JSON matching a schema, so code can use it reliably.

**System prompt** — Persistent instructions applying to every call in a session — role, tone, rules, output format. In OpenAI's API this is `instructions`.

---

## T

**Temperature** — How random the output is. `0` = near-deterministic (use for extraction and code). `1` = creative and varied (use for brainstorming).

**TF-IDF** — A search scoring method: reward words that are frequent in a document (TF) but rare across documents (IDF).

**Token** — The unit of text models read and write. Roughly ¾ of a word in English. Tokens determine context limits and cost.

**Tool use** — Letting a model call functions you provide — search the web, query a database, run code — and use the results.

---

## V

**Vector database** — A database optimised for storing and searching embeddings by similarity. Needed at scale; unnecessary for your first RAG app.

---

## X

**XML tags** — Marking up a prompt with tags like `<instructions>`, `<context>`, `<documents>` so the model can tell them apart. Anthropic's recommended practice, and a defence against prompt injection.

---

## Quick reference: the numbers

```
1 token      ≈ 4 characters ≈ ¾ word
1,000 tokens ≈ 750 words    ≈ 3-4 min read

Output tokens cost more than input — usually ~5×
Model prices span roughly 100× from cheapest to most expensive
```

---

**[← Back to the syllabus](./README.md)**
