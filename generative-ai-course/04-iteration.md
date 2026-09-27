# 04 · Iteration: The Real Skill

> **Time:** 25 minutes  
> **You'll learn:** how to steer output to quality — the skill that actually matters

Here's the thing almost nobody tells beginners: **nobody writes the perfect prompt first time.** Not experts, not prompt engineers, nobody.

The skill isn't writing one brilliant prompt. It's **getting to a good answer in three or four moves.**

---

## Why one-shot prompts fail

You don't know exactly what you want until you see something close to it. That's not a personal failing — it's how creative and analytical work works. You recognise the right answer when it appears.

So don't try to specify everything up front. **Get a draft fast, then steer.** Working in an AI chat is closer to sculpting than to ordering at a restaurant.

> **The loop:** Prompt → Look → Name what's wrong → Steer → Repeat.

Most tasks resolve in 2–4 turns. If you're 8 turns deep and still unhappy, that's a signal — see "When to stop iterating" below.

---

## The four steering moves

### 1. Narrow — too broad, too shallow

```
Too general. Focus only on [SPECIFIC PART] and go much deeper.
Drop the other points entirely.
```
```
I only care about the cost side. Cut everything about scheduling.
```

### 2. Sharpen — too soft, too wordy, too hedged

```
Cut every sentence that doesn't contain a specific fact or action.
```
```
Remove all hedging. Instead of "it may be beneficial," state it
directly or cut it.
```
```
Half the length. Keep all technical terms.
```

### 3. Reshape — right content, wrong form

```
Convert this to a table: option | cost | time | risk.
```
```
Restructure as: problem → cause → fix, three sections max.
```
```
Turn these paragraphs into 6 bullets a busy person can scan.
```

### 4. Re-level — wrong difficulty or tone

```
Too advanced. Explain as if to a smart 15-year-old.
```
```
Too casual. Make it formal enough for a funding application,
but keep the sentences short.
```
```
Less enthusiastic. Drop the exclamation marks and the word
"exciting" entirely.
```

---

## Six fixes for specific problems

| The output is… | Say this |
|---|---|
| Generic and obvious | `That's advice that would apply to anyone. What would you say if you knew my specific situation? Now answer again.` |
| Too long | `Cut to 100 words. Keep only what I'd act on.` |
| Too short | `Expand point 2 with a concrete worked example.` |
| Wrong tone | `Reads like marketing copy. Rewrite in plain, direct language.` |
| Hedging everything | `Commit to a recommendation. Pick the best option and defend it.` |
| Missing the point | `Stop. Here's what I actually need: [RESTATE]. Ignore my earlier framing and start over.` |

**That last one is important.** When a chat has gone wrong, don't keep nudging a bad thread — restate the goal clearly and explicitly tell it to start over. It works far better than the fifth variation of "no, I meant…"

---

## Three techniques worth knowing

### Technique 1: Make it critique its own work

Genuinely effective, and it costs one line.

```
Before answering, write down three ways a first draft could go
wrong. Then write the answer avoiding all three.
```

Or after the fact:

```
Now review what you just wrote. What's the weakest claim in it?
```

### Technique 2: Ask for options before committing

```
Give me 3 different approaches: one conservative, one bold,
one cheap. For each, say who it suits and what could go wrong.
Then recommend one and justify the choice.
```

Far more useful than a single confident answer — because it exposes the trade-offs you're actually choosing between.

### Technique 3: Show it what good looks like

The single most powerful move for matching a style. **One example beats a paragraph of description.**

```
Here are two emails I wrote that got good responses:

[EXAMPLE 1]
[EXAMPLE 2]

Match this style — short, direct, one clear ask — and write a
third email to a supplier about a late delivery.
```

This is called **few-shot prompting**, and it's how you get output that sounds like *you* instead of like an AI.

---

## When to stop iterating

Iteration has diminishing returns. Stop when:

- ✅ You've made 3–4 passes and it's *good enough for the purpose*
- ✅ You're fixing wording rather than substance — you're polishing; do it yourself
- ✅ You keep asking for the same change and it keeps missing — **the prompt is wrong, not the answer**

That third case is the real signal. If three attempts at "shorter" fail, the problem is upstream: the task is unclear, the context is missing, or the task genuinely needs a different tool.

**The reset move:**

```
Let's start over. I'll give you the context properly this time.

[Write a fresh, complete brief using all five ingredients
from Module 3]
```

Starting clean with a full brief beats a sixth nudge, almost every time.

---

## Build a prompt library

You'll notice you reuse the same shapes. **Save them.** Every time a prompt works well, paste it into a notes file with a one-line label.

Structure that works:

```markdown
## Weekly report summary
Act as a business editor. Below is my weekly activity log.
Summarise into: 3 wins, 2 risks, 1 ask. Under 120 words.
No hedging. British English.

## Explain a concept (learning mode)
Explain [X] to someone who knows [Y] but not [Z].
Intuition first, no formulas. Then the formal version.
Then test me with 3 questions, no answers until I reply.

## Meeting notes → actions
From these notes extract: decisions made, action items with
owners, open questions. Markdown table. Write "not stated"
rather than guessing.
```

Over a few weeks this becomes a genuine personal asset — a toolkit tuned to *your* work, which no generic prompt collection can match.

---

## ✏️ Exercise 4.1 — Three-pass refinement (15 min)

Pick a real task — an email, a summary, a plan.

**Pass 1:** Write a solid brief using all five ingredients. Get output.

**Pass 2:** Identify the single biggest weakness. Apply the matching steering move from the table above.

**Pass 3:** Apply one of the three techniques (self-critique, options, or example-driven).

Then ask yourself honestly: *is pass 3 better than pass 1?* If yes, you've internalised the loop. If the answer is "barely," your pass-1 brief was already good — which is also a win.

---

## ✏️ Exercise 4.2 — Match your voice (10 min)

1. Find two things you've written that sound like you (emails, messages, a report).
2. Paste both into a chat.
3. Ask it to describe your style in 5 bullet points.
4. Ask it to write something new in that style.
5. Read it. **Does it sound like you?**

If yes — save that prompt with your examples attached. That's the fix for "AI output sounds like AI," and it's worth more than most prompting tricks.

---

## Key takeaways

- ✅ Nobody gets it right first time. **The skill is steering, not guessing.**
- ✅ Four moves: **narrow, sharpen, reshape, re-level.**
- ✅ If three nudges fail, **reset with a full brief** — don't nudge a sixth time.
- ✅ **Show, don't tell:** one example of good output beats a paragraph describing it.
- ✅ Save what works. **Your prompt library is the real deliverable.**

---

**Next: [05 · When AI Is Wrong](./05-when-ai-lies.md)** — the most important module in this course.
