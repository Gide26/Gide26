# 02 · Your First Real Conversation

> **Time:** 25 minutes
> **You'll learn:** the difference between a *question* and a *brief* — the habit that separates mediocre results from great ones

Most people use AI like a search engine. Type a few words, hope, scan the answer, leave slightly disappointed.

The people getting remarkable results do something different. **They brief it.** Not a question — a brief, like you'd give a capable person you hired.

This lesson teaches that shift. It is the highest-leverage 25 minutes in the course.

---

## Questions vs. briefs

A **question** asks for information that already exists.

```
How do I start a small business?
```

A **brief** specifies what you want produced, for whom, in what form, to what standard.

```
I'm advising a friend in Kampala who wants to start a small
poultry business with about 500,000 UGX. She has space behind
her house and no prior farming experience.

Write a practical first-90-days plan: what to spend money on
first, what to avoid, and the three things most likely to go
wrong. Plain English, under 400 words, no motivational filler.
```

Both go to the same model. The second one comes back usable.

**Why the difference is so large:** the model is predicting the most plausible continuation. A vague prompt matches *millions* of possible continuations, so you get the bland average of all of them. A specific prompt narrows the space to a small set of good answers.

> **Vague in, vague out.** Specific in, specific out. This is the whole game.

---

## The five ingredients

Every strong prompt contains some mix of these. You won't always need all five, but when output disappoints, check which one you left out.

| # | Ingredient | The question it answers |
|---|---|---|
| 1 | **Role** | Who should it act as? |
| 2 | **Task** | What exactly do you want produced? |
| 3 | **Context** | What does it need to know about the situation? |
| 4 | **Format** | What shape should the answer take? |
| 5 | **Constraints** | What should it avoid, and what are the limits? |

Module 3 goes deep on each. Here, let's just *feel* the difference.

---

## Watch it happen

Try these three prompts in order, in fresh chats. Read each answer before sending the next.

### ❌ Version 1 — the search-engine instinct

```
How can I get more customers?
```

Notice what you get: generic advice applicable to every business on earth, useful to none. Not because the model is stupid — because you gave it nothing to work with.

### ⚠️ Version 2 — add context

```
I run a small bakery in Kampala. How can I get more customers?
```

Better. Now it's about bakeries. But it's still guessing: what kind of customers? What's the budget? What have you tried?

### ✅ Version 3 — a real brief

```
Act as a small-business marketing advisor.

I run a small bakery in a busy Kampala suburb. I sell bread,
cakes, and mandazi. Most customers walk in off the street, but
weekday mornings are very quiet while Saturdays are rushed.

My budget for marketing is essentially zero and I have no
online presence beyond a personal WhatsApp.

Suggest 5 concrete, cheap ways to increase weekday morning
sales within the next month.

For each: what to do, roughly how long it takes, and what it
costs. Skip anything requiring paid advertising or a website.
Be specific to this situation — no generic small-business advice.
```

Look at the difference. That third version would take you 90 seconds to write and might genuinely change your week.

**What changed?**

- **Role** — "small-business marketing advisor"
- **Task** — "suggest 5 concrete ways to increase weekday morning sales"
- **Context** — location, products, the actual problem (dead weekday mornings), zero budget, WhatsApp only
- **Format** — per idea: what / time / cost
- **Constraints** — no paid ads, no website, no generic advice, one-month horizon

---

## The four follow-up moves

You rarely get perfection first try. That's normal and expected — and *steering* is the actual skill. Four moves cover almost everything.

### 1. Narrow it

```
That's too broad. Focus only on the two ideas with the lowest cost,
and go deeper on each.
```

### 2. Sharpen it

```
Cut the introduction. Start directly with the first recommendation.
```

### 3. Change the shape

```
Turn this into a table with columns: idea | effort | expected impact | cost.
```

### 4. Change the level

```
Rewrite this as if explaining to someone who has never run a business.
```

Notice none of these start a new conversation. You're editing, not restarting. **The chat is your draft document.**

---

## Give it material to work with

The single most under-used move: **paste your actual stuff in.**

Instead of *"help me write a CV"*, paste your current CV and say what job you're targeting. Instead of *"check my code"*, paste the code and the error. Instead of *"summarise this article"*, paste the article.

You have real material — documents, data, emails, half-finished drafts. **The model is far more useful with your material than with your description of it.**

```
Here is the email I drafted. Rewrite it to be firmer but still
polite. Keep it under 120 words and keep the Friday deadline.

[Paste your email]
```

---

## When to start a new chat

Start fresh when:

- ✅ You're switching to an unrelated topic
- ✅ The conversation has drifted and answers are getting worse
- ✅ You pasted something sensitive earlier that shouldn't colour this task
- ✅ The chat is very long and it's losing track of earlier instructions

Keep going in the same chat when:

- ✅ You're refining one piece of work
- ✅ You want it to remember decisions you made together
- ✅ You're building on its previous output

**Practical tip:** when a long chat starts going stale, ask it to summarise the key decisions, copy that summary, and paste it into a fresh chat. Clean slate, no lost context.

---

## ✏️ Exercise 2.1 — Upgrade three prompts (15 min)

Take three prompts below. Rewrite each into a proper brief using all five ingredients where relevant. Then run both versions and compare.

1. `Write a cover letter.`
2. `Explain climate change.`
3. `Help me study for my exam.`

There's no single right answer — the point is feeling the gap between vague and specific.

<details>
<summary><b>Example rewrite of #1</b> — read after you've tried</summary>

```
Act as a careers advisor helping early-career applicants.

I'm applying for a junior data analyst role at a small NGO in
Kampala. I have a diploma in statistics, six months of experience
building spreadsheets for a shop, and I taught myself basic Python.
I have no formal work experience in data analysis.

Write a one-page cover letter that:
- Opens with something specific, not "I am writing to apply"
- Connects my spreadsheet and Python experience to what the role needs
- Is honest about my experience level without underselling it
- Closes with a clear next step

Warm and professional. Under 300 words. Avoid the phrase
"passionate about data" and avoid generic NGO-sector flattery.
```

Note what did the work: the role, the real details, the specific bloopers to avoid. Anyone could write this, and almost nobody does.

</details>

---

## ✏️ Exercise 2.2 — Steer one answer three ways (10 min)

Ask:

```
Explain how mobile money works in simple terms.
```

Then, in the same chat, apply each follow-up move in turn:

1. `Now rewrite that for a 12-year-old, in under 80 words.`
2. `Now turn it into 4 bullet points a shopkeeper could put on a sign.`
3. `Now give me one thing in that explanation you're not fully confident is accurate, and why.`

That third one is a preview of Module 5. It's a powerful habit.

---

## Key takeaways

- ✅ Stop asking questions; start **writing briefs**.
- ✅ Five ingredients: **role, task, context, format, constraints.**
- ✅ Vague prompts produce the average of everything. Specific prompts narrow the space.
- ✅ Steering — narrow, sharpen, reshape, re-level — is the real skill.
- ✅ Paste your **real material** in whenever you can.

---

**Next: [03 · The Anatomy of a Great Prompt](./03-anatomy-of-a-prompt.md)** — the five ingredients, in depth.
