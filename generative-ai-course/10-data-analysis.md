# 10 · Analysing Data with AI

> **Time:** 35 minutes  
> **You'll learn:** how to use AI as a data-analysis partner — and the one rule that stops it inventing your numbers

This module is where AI becomes genuinely valuable for real work. It's also where a specific, dangerous mistake shows up — so read the warning below carefully.

---

## The promise and the trap

**The promise:** describe what you want in plain English, get working analysis code and a chart. You don't need to memorise pandas syntax.

**The trap:** asked to analyse data, a model will sometimes **produce plausible numbers it did not compute.** It describes what the answer probably looks like rather than running the calculation.

This happens because the model predicts text. Given "here's my sales data, what's the total?" it may generate a confident number shaped like the right answer — especially if the data is long and it can't hold it all precisely.

> ### 🔴 The rule
>
> **Never let AI compute numbers it hasn't actually run code on.**
>
> Either (a) use a tool where code genuinely executes — ChatGPT's Advanced Data Analysis, Claude's analysis feature, a Jupyter notebook — and check that it ran, or (b) have AI *write the code* and **you run it yourself**.
>
> If you can't see code that ran, you don't have a result. You have a guess.

---

## Two safe modes

### Mode A — Let it run code (easiest)

ChatGPT, Claude, and Gemini can execute Python in a sandbox. Upload your file, describe the analysis, and it writes *and runs* the code.

**Always verify it actually ran** — look for executed code and real output, not just prose.

```
Here's my sales data [upload file.csv].

Write and RUN Python to:
1. Show the shape and the first 5 rows
2. Report missing values per column
3. Give summary statistics for numeric columns
4. Show total revenue by month

Show me the code you ran and the actual output. If you cannot
run code, say so instead of estimating.
```

That last line is the important one.

### Mode B — It writes code, you run it (most reliable)

Better for anything you'll repeat, share, or trust. Part 3 teaches you exactly this workflow.

```
Write a Python script using pandas that:
- Reads 'sales.csv'
- Cleans the 'date' column to datetime
- Drops rows where 'amount' is null
- Groups by month and sums revenue
- Saves a bar chart to 'revenue_by_month.png'

Assume pandas and matplotlib are installed. Include a comment
explaining each step. Don't run it — just give me the code.
```

You run it locally. **You see the real numbers.** No fabrication possible.

---

## Cleaning messy data

Real data is messy. This is where AI saves the most time.

```
Here are the first 20 rows of my CSV:

[PASTE]

1. What's wrong with this data? List every problem you can see.
2. Write pandas code to fix each one.
3. Flag anything you'd need to ask me about rather than guess.
```

That third point matters enormously. AI will happily guess that `-999` means "missing" — but in your dataset it might mean "refund." **Ask it to flag ambiguities instead of resolving them silently.**

### Common cleaning tasks

| Problem | Prompt |
|---|---|
| Inconsistent categories | `Standardise the 'region' column — find variants that mean the same thing and show me each mapping before applying it.` |
| Mixed date formats | `Parse 'date' handling both DD/MM/YYYY and MM/DD/YYYY. Show me rows where the format is ambiguous.` |
| Currency as text | `Convert 'amount' from strings like "UGX 1,200,000" to numeric. Report any values that fail.` |
| Duplicates | `Find duplicates — first exact, then on (customer_id, date). Show examples of each before dropping.` |
| Outliers | `Show outliers in 'amount' using IQR. List them with the full row so I can judge whether they're errors.` |

**The pattern: show me, don't just do it.** Every cleaning decision is a judgement call, and you want to see what it decided.

---

## Exploratory analysis

Once data is clean, use AI to explore faster.

```
This is cleaned sales data. Columns: date, product, region,
quantity, unit_price, amount. About 5,000 rows.

Suggest 8 interesting questions this data could answer.
For each: the question, why it's interesting, and the pandas
code to answer it.

Prioritise questions that could change a business decision,
not just descriptive stats.
```

That last line is the difference between a real analysis and a pile of charts.

### Interpreting results

Once you have real output, **paste it back and ask for interpretation:**

```
Here's the output:

[PASTE ACTUAL NUMBERS]

What does this actually tell me? Specifically:
1. What's the headline finding?
2. What's surprising?
3. What can't I conclude from this? (be strict)
4. What should I look at next?
```

Question 3 is the valuable one. AI is agreeable by default; asking it what you *can't* conclude counteracts that.

---

## Charts

### Asking for chart code

```
Using matplotlib, plot revenue by month as a bar chart.

Requirements:
- Figure size 10x6
- Rotate x labels 45 degrees
- Y axis formatted in millions with 'UGX' prefix
- Colour the best month differently
- Add a title: 'Monthly Revenue, 2026'
- Tight layout, save at 150 dpi
```

The more specific you are, the fewer iterations. AI's default charts are ugly — say what you want.

### Chart choice

| You want to show | Ask for |
|---|---|
| Change over time | Line chart |
| Compare categories | Bar chart (horizontal if long labels) |
| Distribution | Histogram or box plot |
| Relationship between two numbers | Scatter plot |
| Part of a whole | Stacked bar (**not** pie, unless 2–3 slices) |
| Correlation across many variables | Heatmap |

```
I have 8 numeric columns. Which chart would best show
[THE POINT I WANT TO MAKE], and why? Give me the code.
```

### Fixing ugly charts

```
This chart is unreadable. Fix it:
- X labels overlap
- Legend covers the data
- Colours are too similar
- Y axis starts at 0 but should be closer to the data range
```

---

## The statistical caveat

AI will suggest a t-test, a regression, or a chi-square test — and sometimes the suggestion is wrong for your data.

Always ask:

```
I want to test whether [X] differs by [Y].

1. What test would you recommend, and what assumptions
   does it make?
2. How do I check those assumptions on my data?
3. What happens if the assumptions are violated?
4. What would you conclude if you only had 30 rows?
```

**And remember: AI did not design your study.** It can't tell you whether your sample is biased, whether your measurement is valid, or whether your control group makes sense. Those are your job.

---

## A complete workflow

```
1. LOOK    → Paste first 20 rows. Ask what's in here and
             what's wrong with it.
2. CLEAN   → Ask for cleaning code. Review every decision.
             Ask what it had to guess.
3. VERIFY  → Run the code yourself. Check row counts and
             totals before and after.
4. EXPLORE → Ask for 8 candidate questions. Pick the ones
             that matter.
5. ANALYSE → Run the code. Paste real output back for
             interpretation.
6. CHALLENGE → "What can't I conclude? What am I missing?"
7. PRESENT → Ask for chart code. Make it readable.
8. SANITY  → Do the numbers make sense against what you
             already know? If not, find out why.
```

**Step 8 catches more errors than every other step combined.** If the analysis says revenue went up 300% and you know it didn't, something is wrong — duplicate rows, a bad join, a unit error. Trust your knowledge of the domain over the output.

---

## ✏️ Exercise 10.1 — Profile a dataset (15 min)

Get any CSV — export from a spreadsheet, or download an open dataset.

```
Here are the first 25 rows of my data:

[PASTE]

1. Describe what this dataset appears to be
2. List every data quality problem you can see
3. What questions could this answer?
4. What questions can it NOT answer, given what's here?
5. What would you want to ask me before analysing it?
```

Question 4 is where you learn the most. **Datasets can't answer most questions people want answered** — knowing which, early, saves days.

---

## ✏️ Exercise 10.2 — Clean and verify (15 min)

```
Write pandas code to clean this data. For each fix, print
how many rows it affected so I can verify.

[Paste column names and the problems you found]
```

Then **run it** and check that the numbers affected match what you expected. If it dropped 40% of your rows and you expected 2%, stop and find out why.

---

## ✏️ Exercise 10.3 — The fabrication test (5 min)

Do this once. It's the most valuable five minutes in the module.

1. Take a dataset with a number you **know** the answer to
2. Ask in a plain chat, **without** code execution: `What is the total of the amount column?`
3. Compare to the real answer

If it's wrong — and it often will be — you've just experienced the trap directly. **You will never forget it.** That instinct is worth more than any amount of reading.

Now repeat **with** code execution enabled, or by running its code yourself. That's the difference between Mode A/B and the trap.

---

## Key takeaways

- ✅ 🔴 **Never accept numbers that weren't produced by code that actually ran.**
- ✅ Mode A: it runs code in a sandbox — **verify it ran.** Mode B: it writes code, **you run it** — most reliable.
- ✅ Ask it to **flag what it had to guess** rather than resolving ambiguities silently.
- ✅ For cleaning: **"show me, don't just do it."**
- ✅ Ask **"what can't I conclude?"** to counteract its agreeableness.
- ✅ **Sanity-check against what you already know.** Step 8 finds more errors than everything else.
- ✅ AI can't tell you if your study design is sound. That's still you.

---

**Next: [11 · Setup: Python & API Keys](./11-setup-python-and-api-keys.md)** — Part 3 begins. Time to write code.
