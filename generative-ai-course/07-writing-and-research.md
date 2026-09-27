# 07 · Writing, Research & Ideas

> **Time:** 35 minutes  
> **You'll learn:** practical workflows for the three things people actually use AI for — no code

Part 2 starts here. Everything in this module works in a plain chat window.

---

## The principle: AI is a draft, not an author

The failure mode to avoid: copy the prompt, paste the output, ship it. The result is generic, occasionally wrong, and sounds like an AI wrote it — because one did.

The workflow that works:

```
You set the direction      → what's this for, who's it for, what's the point
AI produces the volume     → drafts, options, structures, alternatives
You make the judgements    → what's true, what's good, what to cut
AI polishes                → tighten, reformat, catch errors
You own the result         → final read, final responsibility
```

**You are the editor. The AI is the drafter.** Every good workflow in this module follows that shape.

---

## Workflow 1: Writing that sounds like you

### The blank page problem

AI is genuinely excellent at beating the blank page. Don't ask for a finished piece — ask for **something to react to**.

```
I need to write a [THING] for [AUDIENCE].
Purpose: [what should happen after they read it]

Don't write it for me yet. First give me 4 different angles
I could take, each in one sentence, with a note on who each
would appeal to.
```

Pick an angle. *Then* ask for the draft. You've just turned a blank page into a decision.

### The "sounds like AI" problem

Three causes, three fixes.

**Cause 1: No voice specified.** Fix — give it examples (Module 4).

**Cause 2: AI defaults are generic.** Certain patterns scream "AI wrote this":

| AI tells | Replacement |
|---|---|
| "In today's fast-paced world…" | Start with the actual point |
| "It's important to note that…" | Just say the thing |
| "delve", "tapestry", "testament to" | Plain words |
| "not only… but also" (constantly) | Vary the structure |
| Tricolons — "efficient, effective, and scalable" | Say one thing well |
| Everything in threes | Use two, or five |
| Ending with a tidy summary | End with the point, or stop |

**Give it a banned list:**

```
Avoid: "delve", "crucial", "landscape", "navigate", "realm",
"unlock", "harness", "seamless", "robust", "leverage" (as a verb).
No sentences starting with "Moreover" or "Furthermore".
Vary sentence length — some short.
```

**Cause 3: It's hedging everything.** Fix:

```
Commit to your claims. Cut "it could be argued" and
"it's worth considering." State things directly.
```

### The editing pass

Once you have a draft, this is the highest-value prompt in writing:

```
Act as a harsh editor. Review the draft below.

For each issue: quote it, say why it's weak in one line,
and give a specific fix. Don't rewrite the whole thing.

Flag specifically:
- Sentences that could be cut with no loss
- Claims without support
- Anything generic that would apply to any [THING]
- Where the tone drifts

[PASTE DRAFT]
```

Asking it to **quote and explain rather than rewrite** keeps you in control. You decide what changes.

### Shortening

```
Cut this to 60% of its length. Rules:
- Keep every specific fact, number, and name
- Cut all throat-clearing and transition padding
- One idea per sentence
- Don't merge two points to save space
```

---

## Workflow 2: Research you can trust

Combine this with Module 5. Research is where fabrication does the most damage.

### Step 1: Scope it

```
I'm researching [TOPIC]. My goal is to [DECIDE / UNDERSTAND
/ WRITE] about it.

Before searching: list the 5 questions that actually matter
for this goal, and tell me which are likely to be contested
or hard to answer.
```

### Step 2: Search with sources

**Turn on web search.** Then:

```
Research [QUESTION] using web search.

For each key claim: give the claim, the source (name + URL),
and how confident the source is. Separate established facts
from disputed claims. Flag anything you couldn't verify.
```

### Step 3: Attack it

```
Here's what you found. Now:
1. What's the strongest argument against the main conclusion?
2. What's missing from this picture?
3. Which sources are weakest, and why?
4. What would a critic of this say I'm ignoring?
```

### Step 4: Verify independently

**Open the links.** Check the central claims against a source you trust. Non-negotiable for anything you'll publish or act on.

### The document-grounded alternative

If you have your own sources — papers, reports, notes — **don't ask the model to recall facts. Give it the documents and ask it to work from them.**

```
Using ONLY the documents below, answer [QUESTION].

Quote the relevant passage with each point. If the answer
isn't in these documents, say "not in the provided sources"
— do not fill the gap from your general knowledge.

[DOCUMENT 1]
[DOCUMENT 2]
```

That last instruction is the important one — it turns off fabrication. This is the manual version of what Module 16 builds in code.

### Summarising long documents

```
Summarise this document. For each section:
- The main claim, in one sentence
- Any number or date, exactly as written
- Anything the author flags as uncertain

Then: what's the single most important takeaway, and what
does this document NOT cover that I should know about?

[PASTE DOCUMENT]
```

Asking what's **not** covered is the move that separates a real summary from a paraphrase.

---

## Workflow 3: Ideas and problem-solving

### Diverge, then converge

Never ask for "ideas." Ask for many, then filter.

```
I need ideas for [PROBLEM].
Constraints: [budget, time, resources, what's failed before]

Give me 15 ideas. Make them genuinely different — not
variations on one theme. Include at least 4 that are
unconventional or slightly risky.

Then: score each on (impact × feasibility), and recommend
the top 3 with reasoning.
```

Forcing 15 with variety beats asking for 5 — it has to move past the obvious ones.

### The pre-mortem

One of the most useful prompts in this whole course.

```
I'm planning to [PLAN].

Assume it's 6 months later and it failed completely.
Write the post-mortem: what went wrong?

Be specific and realistic. I want the failure modes I'm
not seeing, not generic project risks.
```

### The assumption attack

```
Here's my plan: [PLAN]

1. List every assumption it depends on.
2. Rank them by how much the plan breaks if the assumption
   is false.
3. For the top 3, tell me the cheapest way to test each
   assumption this week.
```

### Role-play a difficult conversation

```
I need to [ask my landlord for more time / negotiate a
price / give difficult feedback].

Play the other person. Be realistically resistant — don't
make it easy for me. Respond as they'd actually respond.

Start by telling me their likely objection, then let me
try. Correct me when I handle it badly.
```

Genuinely useful practice, and telling it to *be resistant* is what makes it realistic.

---

## Workflow 4: Learning anything

### The tutor loop

```
I want to learn [TOPIC]. I currently [what you know].

Teach it in this order:
1. The core idea, with an analogy from [FIELD YOU KNOW]
2. A worked example
3. The formal terminology, now that I understand the idea
4. Test me with 3 questions — wait for my answers, don't
   reveal them upfront

After each of my answers: tell me if I'm right, explain
any gap, then go deeper.
```

Step 4 is what makes it stick. Passive reading feels productive and isn't.

### The confusion signal

```
I don't understand [SPECIFIC BIT]. Don't re-explain from the
top. Ask me what I think it means first, then correct the
specific thing I've got wrong.
```

Far more effective than "explain again" — it finds *your* actual misconception.

---

## What NOT to use AI for

Be honest about the limits:

| Don't use it for | Why |
|---|---|
| Facts you won't verify | Fabrication risk (Module 5) |
| Anything where your authentic voice *is* the value | Poetry, personal essays, condolence messages |
| Medical, legal, financial decisions without an expert | Stakes are too high |
| Judgements about people | It has no real information about them |
| Work you've been told to do yourself | Integrity, and you won't learn it |
| Anything needing true originality | It recombines; it doesn't originate |

That second row is worth dwelling on. **Where the value is your voice — a eulogy, a love letter, an apology — AI assistance cheapens it.** Use AI for the things that are work. Keep the things that are yours.

---

## ✏️ Exercise 7.1 — Write something real (15 min)

Pick something you actually need to write.

1. Ask for **4 angles**, pick one
2. Get a draft
3. Run the **harsh editor** prompt
4. Apply the **shortening** prompt
5. **Read it aloud.** Fix anything you'd never say out loud

That last step is the real test. If it doesn't survive being read aloud, it isn't finished.

---

## ✏️ Exercise 7.2 — Learn something (15 min)

Pick a concept you've been avoiding.

1. Run the **tutor loop** with an analogy from a field you love
2. Answer its questions honestly
3. When you're stuck, use the **confusion signal** prompt
4. Finish by asking: `What should I learn next, and why?`

---

## ✏️ Exercise 7.3 — Pre-mortem a real plan (10 min)

Take a plan you're genuinely considering. Run the **pre-mortem**, then the **assumption attack**.

If either surfaces something that changes your plan, this exercise just paid for the whole module.

---

## Key takeaways

- ✅ **You're the editor; AI is the drafter.** Direction and judgement stay with you.
- ✅ Beat the blank page by asking for **angles**, then picking one.
- ✅ Kill AI tells with a **banned-words list** and by banning hedging.
- ✅ For research: **ground it in documents** and tell it not to fill gaps from memory.
- ✅ **Diverge then converge** — ask for 15 varied ideas, then score them.
- ✅ The **pre-mortem** and **assumption attack** find problems you can't see yourself.
- ✅ Where **your voice is the value**, don't use AI.

---

**Next: [08 · Generating Images](./08-images.md)**
