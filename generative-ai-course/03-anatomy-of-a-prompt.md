# 03 · The Anatomy of a Great Prompt

> **Time:** 30 minutes
> **You'll learn:** a reusable recipe for prompts, plus six patterns that handle most real work

Module 2 showed you *that* specific prompts win. This module gives you a repeatable method for writing them.

---

## The recipe

You don't need all five parts every time. You need to know all five exist so you can add the missing one when output disappoints.

```
┌─────────────────────────────────────────────┐
│  1. ROLE        Who are you?                │
│  2. TASK        What do I want?             │
│  3. CONTEXT     What should you know?       │
│  4. FORMAT      What shape?                 │
│  5. CONSTRAINTS What to avoid / limits?     │
└─────────────────────────────────────────────┘
```

**Order matters less than presence** — but putting role and task first, and hard constraints last, tends to work well. Instructions at the very start and very end of a prompt carry the most weight.

---

## 1. Role

Sets the voice, the priorities, and the standards it draws on.

```
You are a patient tutor explaining to a beginner.
You are a sceptical editor looking for weak arguments.
You are a senior Python developer who cares about readable code.
You are a Ugandan small-business accountant.
```

**Why it works:** the model has absorbed how these people write and what they prioritise. Naming a role activates that pattern.

**Pro move — combine roles for tension:**

```
You are both a creative brainstormer and a harsh practical critic.
First suggest 10 ideas, then ruthlessly reject the 7 weakest and
explain why.
```

**Careful:** a role is a style hint, not a qualification. "Act as a doctor" does not make it a doctor. Never use roles to justify skipping verification of medical, legal, or financial output.

---

## 2. Task

Say exactly what to produce. Use a **strong verb** and name the deliverable.

| ❌ Weak | ✅ Strong |
|---|---|
| "Help me with my presentation" | "Write an 8-slide outline for a 10-minute presentation" |
| "Thoughts on this?" | "Identify the three weakest points in this argument" |
| "Fix my writing" | "Rewrite this to be 40% shorter, keeping all technical terms" |
| "Tell me about Python" | "Explain Python lists to someone who knows Excel but has never coded" |

**Name the output noun.** Outline, table, email, critique, summary, list of 5, 200-word paragraph. Vague tasks get vague outputs.

---

## 3. Context

Everything it needs to know that it cannot guess. This is where most people under-invest — and where most of the quality comes from.

**Context worth giving:**

- **Who you are** — your level, role, situation
- **Who the audience is** — expert or novice? Boss, customer, or classmate?
- **Why you need this** — a school assignment needs different treatment than a client proposal
- **What you've tried** — prevents it re-suggesting the obvious
- **What "good" looks like here** — speed, depth, brevity, creativity?
- **Your material** — paste the actual document, data, or draft

```
I'm a second-year statistics student. I understand mean and
median but not standard deviation. I have an exam on Friday.

Explain standard deviation using an example from football
goal-scoring, since I follow the Uganda Premier League.

Avoid formulas in the first explanation — I want the intuition
first, then the formula once I understand the idea.
```

Every line there is doing work. Remove any of them and the answer gets worse.

---

## 4. Format

Tell it the shape. This is the cheapest quality upgrade available — it costs one line and the improvement is immediate.

```
Answer in a table with columns: option | cost | time | risk
Use short paragraphs. No headers.
Give me exactly 5 bullet points, each under 15 words.
Return valid JSON with keys: name, price, in_stock.
Start with a one-sentence summary, then details.
Format as an email with subject line.
Use markdown with ## for each section.
```

**Bonus:** specifying a machine-readable format (JSON, CSV, markdown table) makes output *stricter and more structured* even when you only wanted to read it. Structure constrains rambling. Module 14 covers this properly in code.

---

## 5. Constraints

Boundaries, exclusions, and limits. Often the difference between "technically answered" and "actually useful."

```
Under 200 words.
Don't use the word "revolutionary."
No jargon — assume no background in the topic.
Only suggest free tools.
Avoid anything requiring a credit card.
If you're not certain about a fact, say so explicitly.
Don't mention [X] at all.
Use British English spelling.
```

**The most valuable constraint in the whole course:**

```
If you are not confident about something, say "I'm not sure"
rather than guessing.
```

This measurably reduces fabrication. Use it by default on anything factual.

---

## Six patterns that cover most real work

Reusable shapes. Copy, adapt, save to your prompt library.

### Pattern 1 — The Brief

For producing a piece of work.

```
Act as [ROLE].

Context: [who I am, who it's for, why I need it]

Task: [specific deliverable]

Format: [shape, length]

Constraints: [avoid X, include Y, keep under Z]
```

### Pattern 2 — The Critic

For improving work you've already done. Far more effective than asking it to "improve" things — a named lens produces targeted feedback.

```
Here is [my draft / my code / my argument]:

[PASTE]

Review it as [ROLE]. Find the [N] weakest parts.
For each: quote the problem, explain why it's weak, and suggest
a specific fix. Don't rewrite the whole thing.
```

### Pattern 3 — The Explainer

For learning anything.

```
Explain [CONCEPT] to [AUDIENCE].

I already understand [X] but not [Y].
Use an analogy from [FIELD THEY KNOW].

Start with intuition, no formulas. Then give me the formal
version. Then test me with 3 questions — don't give answers
until I respond.
```

That last line is excellent: it turns a passive explanation into an active tutoring session.

### Pattern 4 — The Extractor

For pulling structure out of messy material.

```
From the text below, extract:
- All dates mentioned
- All monetary amounts, with currency
- Every person named and their role

Return as a markdown table. If something isn't present, write
"not stated" — do not guess.

[PASTE TEXT]
```

Note "do not guess" — critical for extraction.

### Pattern 5 — The Reframer

For changing tone or audience without rewriting from scratch.

```
Rewrite the following for [NEW AUDIENCE], changing the tone to
[NEW TONE].

Keep: all technical terms, the deadline, and the three action points.
Remove: anything that sounds like marketing copy.

[PASTE]
```

### Pattern 6 — The Sparring Partner

For thinking, not producing. Deeply underrated.

```
I'm considering [DECISION]. I'm leaning toward [OPTION A].

Don't just agree with me. Argue the strongest case FOR [OPTION B],
then tell me what evidence would most change my mind, then ask me
the two questions I should be asking but probably aren't.
```

---

## ✏️ Exercise 3.1 — Diagnose the weak prompt (10 min)

Here's a real prompt. Identify which of the five ingredients is missing or weak, then rewrite it.

```
Write a summary of this report for my manager.
```

<details>
<summary>Answer</summary>

**Missing: role** (unspecified), **context** (what report? what does the manager care about? how long have they got?), **format** (email? bullets? how long?), **constraints** (what to leave out? what decision is this informing?).

Only the **task** is present, and even that is thin — "summary" could mean a hundred things.

Rewrite:

```
Act as a sharp business communicator.

Below is a 12-page report on customer churn at our company.
My manager has not read it and has about 2 minutes.

Write a summary email she can read on her phone:
- Subject line under 8 words
- First line: the single most important finding
- Three bullet points: what's happening, why, what we should do
- One line on what I need from her

Under 150 words. No methodology details. No hedging language
like "it could be suggested that."

[PASTE REPORT]
```

</details>

---

## ✏️ Exercise 3.2 — Build three briefs (15 min)

Write a full brief for three of these, using all five ingredients. Then actually run them and judge the results.

1. A difficult email you've been putting off
2. A concept you need to learn for work or study
3. A decision you're currently weighing up
4. Feedback on something you wrote
5. A recurring task you'd like to speed up

Save the ones that work well. **This is your prompt library, and it's the real deliverable of this course.**

---

## Key takeaways

- ✅ Five ingredients: **role, task, context, format, constraints** — add the missing one when output disappoints.
- ✅ **Context is where the quality lives.** Most people under-invest here.
- ✅ **Strong verb + named output noun** beats vague requests every time.
- ✅ **Format** is the cheapest quality upgrade — one line, big gain.
- ✅ **Constraints** turn "technically correct" into "actually useful."
- ✅ Six reusable patterns: Brief, Critic, Explainer, Extractor, Reframer, Sparring Partner.

---

**Next: [04 · Iteration: The Real Skill](./04-iteration.md)**
