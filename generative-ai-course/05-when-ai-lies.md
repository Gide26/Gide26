# 05 · When AI Is Wrong

> **Time:** 30 minutes  
> **You'll learn:** how AI fails, and the verification habits that protect you

**This is the most important module in this course.** Everything else makes you more effective. This one stops you from being confidently, publicly, expensively wrong.

Read it even if you skip everything else.

---

## The core problem

Generative AI predicts *plausible* text, not *true* text.

When those two diverge — and they diverge regularly — you get output that is fluent, specific, well-formatted, and completely false.

This has a name: **hallucination** (also called *confabulation*). The model isn't lying. It isn't malfunctioning. It's doing exactly what it was built to do: producing the most statistically likely continuation. Truth was never part of the objective.

**What makes this dangerous isn't that it happens. It's that the output sounds identical whether it's true or false.** No hesitation. No apologetic tone. Same confident structure.

---

## Five ways it goes wrong

### 1. Fabricated facts

Straight inventions — numbers, dates, events, people.

```
Q: Who won the 1987 Ugandan general election, and what
   percentage of the vote did they get?
A: [Confidently states a name and a precise percentage.
    Both invented.]
```

Ask a model about something obscure and specific, and you maximise the chance of invention. The more precise the request, the more precise the fabrication.

### 2. Fake citations — the worst offender

**This catches out students, journalists, researchers, and lawyers constantly.**

The model produces a citation that follows the exact shape of a real academic reference — plausible author, plausible journal, plausible year, plausible title — and **none of it exists.**

```
Smith, J. A. (2023). "Digital Payment Adoption in East African
Markets." Journal of Development Economics, 45(2), 112-134.
```

Looks perfect. Search for it. Nothing.

**Why this happens:** the model knows what citations in that field *look like*. It has never checked whether this one exists. It can't — it has no database of papers, only patterns.

> **Never trust a citation you haven't opened yourself.** Not once. Not ever. This is the single most repeated failure mode in AI use.

### 3. Confident guessing where it should decline

Asked about something unknowable — someone's phone number, tomorrow's news, the contents of a document it hasn't seen — it often invents rather than saying "I don't know."

**Why:** during training, *guessing* was always rewarded. A guess at the next word scores something; "I don't know" almost never was the expected continuation.

### 4. Plausible-sounding reasoning, wrong conclusion

The steps look logical. The conclusion is wrong. Especially common in:

- **Arithmetic** — models predict text, they don't compute. They can produce "the answer is 47" with total confidence. (If your chat tool has code execution enabled, use it for maths.)
- **Multi-step logic** — errors compound silently
- **Legal, medical, financial reasoning** — where edge cases matter enormously

### 5. Bias and skewed framing

Models learn from human text, which contains human bias. Output can carry stereotypes about gender, race, nationality, and profession — and can systematically favour Western/Anglophone perspectives.

Practical effect: ask for "a typical name for a nurse" and you may get a female name; ask for "a typical engineer" and you may get a male one. Ask for business advice and you may get advice that assumes infrastructure, capital, and legal frameworks you don't have.

**Watch for advice that quietly assumes a rich-country context.** Ask it to name its assumptions.

---

## Your defence kit

Nine habits. You won't use all of them every time — apply more scrutiny as the stakes rise.

### Habit 1: The confidence question

```
How confident are you in each claim above? Mark each as
certain / likely / uncertain, and explain what you'd need
to check.
```

Doesn't guarantee accuracy — but it surfaces the weak spots, and it costs you nothing.

### Habit 2: Demand sources, then open them

```
What specific sources support this? Give me URLs I can check.
```

Then **actually open them.** A model that invented a claim will often invent a URL to match. This is where most people stop short — they get the citation and feel reassured. Opening it takes ten seconds. Do it.

### Habit 3: Ask for the strongest counter-case

```
Now argue the opposite case as strongly as you can.
```

If it produces an equally compelling argument against its own answer, the original answer was never as solid as it sounded.

### Habit 4: Verify anything specific independently

Names, dates, figures, prices, quotes, statistics, citations — check them against a source you trust. Not against the same model in a new chat; it will often repeat the same invention consistently.

> **Consistency is not accuracy.** Two chats agreeing means nothing if both are drawing on the same pattern.

### Habit 5: Turn on search when it's available

Most assistants have a web-search toggle. **Use it for anything current or factual.** The model then grounds its answer in retrieved pages, and good implementations link the sources.

But verify anyway: it can still misread a source, or cite a source that doesn't say what it claims.

### Habit 6: Separate drafting from fact-checking

The safest workflow for anything factual:

1. **Use AI to draft** the structure and argument
2. **You verify** every factual claim independently
3. **You add** the verified facts

Never ask AI to produce facts you won't check. Ask it to produce *structure*, *alternatives*, *critique*, *wording* — things where plausibility is the right standard.

### Habit 7: Push back on confident vagueness

Watch for phrases that sound authoritative but mean nothing:

- *"Studies have shown…"* — which studies?
- *"It is widely believed…"* — by whom?
- *"Experts recommend…"* — which experts?
- *"Research indicates…"* — where?

```
Which specific study? Give me the title, authors, and year.
If you can't name one, say so.
```

### Habit 8: Test the edges

Ask about something adjacent that you *know* the answer to. If it gets that wrong, distrust everything else in the response.

Useful for evaluating whether a model knows a domain well at all.

### Habit 9: Scale scrutiny to stakes

| Stakes | Standard |
|---|---|
| Brainstorming, drafting, summarising your own notes | Skim it — plausibility is enough |
| Internal documents, learning, casual research | Spot-check numbers and names |
| Anything published, submitted, or sent to clients | Verify every factual claim and every citation |
| Medical, legal, financial, safety, or academic-integrity decisions | **Do not rely on AI output alone.** Consult a qualified human and a primary source |

---

## Special warning: academic integrity

If you're a student:

- **Submitting AI output as your own work is usually academic misconduct.** Policies vary by institution, but assume the strict reading until you've confirmed otherwise.
- **Fake citations are the fastest way to fail an assignment.** Markers search for references.
- Using AI to *understand* material, generate practice questions, or critique your draft is normally fine and often encouraged. Check your institution's policy — then follow it.

Legitimate and valuable uses: explaining concepts you're stuck on, quizzing you, critiquing your draft's argument, suggesting what to research next. That last category is where AI genuinely makes you better rather than merely faster.

---

## ✏️ Exercise 5.1 — Catch it lying (15 min)

Deliberately provoke a hallucination. This is the fastest way to build the instinct.

**Step 1.** Ask about something real but obscure, that you happen to know well — a local business, a school you attended, a small event you were at.

```
Tell me about [a very specific local thing you know well].
Give me three specific facts about it and cite your sources.
```

**Step 2.** Check each fact against what you know.

**Step 3.** Now ask:

```
Which of those facts are you least confident about?
Were any of them partly invented?
```

You'll often get a candid admission — and that candid admission is exactly the muscle you're building. **Learn the feeling of "this sounds great but might be nothing."**

---

## ✏️ Exercise 5.2 — Practice the defence kit (10 min)

Pick a factual claim and run it through the full kit:

1. Ask for the claim **with sources**
2. Open every URL
3. Ask for the **opposite case**
4. Ask it to **label its confidence** per claim
5. **Independently verify** the central fact

Note how often step 2 fails. That's the honest answer to "can I trust the sources?"

---

## ✏️ Exercise 5.3 — Find the hidden assumption (5 min)

```
I want to start an online business. Give me a step-by-step plan.
```

Then:

```
List every assumption your plan makes about my country's
infrastructure, payment systems, and legal environment.
Then rewrite the plan for Uganda specifically.
```

Notice how much of the first answer quietly assumed a US or European context. This is bias showing up as something more mundane — and more practically damaging — than stereotypes.

---

## Key takeaways

- ✅ AI produces **plausible** text, not **true** text. The sound is identical either way.
- ✅ **Fake citations are the most dangerous failure mode.** Never use one you haven't opened.
- ✅ **Consistency is not accuracy** — a model will repeat its own inventions across chats.
- ✅ Use AI for **structure, alternatives, critique, and wording.** Verify **facts** yourself.
- ✅ **Scale scrutiny to stakes.** Published claims get checked; medical and legal decisions get a human expert.
- ✅ Ask it to **name its assumptions** — advice often hides a rich-country default.

---

**Next: [06 · Choosing Your Tools](./06-choosing-tools.md)**
