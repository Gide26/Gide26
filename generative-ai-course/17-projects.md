# 17 · Four Capstone Projects

> **Time:** 2–6 hours each  
> **You'll do:** build something real

Reading teaches you nothing on its own. These four projects are where the course becomes a skill.

**Build at least one. Change it to solve a problem you actually have.**

---

## How to approach these

1. **Build the simplest version first** — get it working end to end, however ugly
2. **Then improve** — resist building everything at once
3. **Test with real data** — your own files, your own problems
4. **Ship it** — show someone, use it for a week, put it on GitHub

> **The goal is finished, not perfect.** A small tool you actually use beats an ambitious one you abandon at 70%.

---

## Project 1 · Personal knowledge assistant ⭐ *start here*

**Difficulty:** ●●○○ | **Time:** 2–3 hours | **Builds on:** Modules 15, 16

An assistant that answers questions from **your own notes**, with citations.

### What it does

- Indexes a folder of notes, articles, PDFs, and saved documents
- Answers questions in a terminal or simple web interface
- **Always shows which file the answer came from**
- Says "I don't have that" when it doesn't know

### Requirements

**Core (must have):**
- [ ] Load `.txt`, `.md`, and `.pdf` files from a folder
- [ ] Chunk with overlap
- [ ] Retrieve relevant chunks
- [ ] Answer using **only** retrieved chunks
- [ ] Cite the source file with every answer
- [ ] Refuse cleanly when the answer isn't there

**Stretch:**
- [ ] Embeddings instead of keyword search (Module 16)
- [ ] Simple web UI with [Streamlit](https://streamlit.io/) or [Gradio](https://www.gradio.app/)
- [ ] `/reindex` command after you add files
- [ ] Highlight the exact passage the answer came from
- [ ] Filter by date or tag

### Getting PDF text

```bash
pip install pypdf
```

```python
from pypdf import PdfReader

def read_pdf(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() for page in reader.pages)
```

### Test it with

- 10 questions you **know** the answers to → measures retrieval
- 5 questions your notes **don't** cover → measures honest refusal
- 3 questions with answers spanning **two** documents → measures chunking quality

### Why this one first

It's genuinely useful *immediately*, and it teaches the pattern behind most production AI applications. If you build one thing from this course, build this.

---

## Project 2 · Document processing pipeline ⭐ *most practical*

**Difficulty:** ●●○○ | **Time:** 3–4 hours | **Builds on:** Module 14

Turn a pile of messy unstructured documents into clean, structured, queryable data.

### What it does

- Reads many documents (receipts, invoices, CVs, forms, emails)
- Extracts the same fields from each
- Validates the extracted data
- Exports to CSV / JSON / SQLite
- **Flags low-confidence extractions for human review**

### Requirements

**Core:**
- [ ] Process a folder of documents
- [ ] Define a Pydantic model for the fields you want
- [ ] Extract from each with `messages.parse()`
- [ ] Validate with Pydantic rules
- [ ] Export structured results
- [ ] **Report failures without crashing** — one bad document shouldn't kill the run

**Stretch:**
- [ ] Confidence scores; route low-confidence rows to a review queue
- [ ] A CSV of everything that failed, with reasons
- [ ] Resume from where it stopped (skip already-processed files)
- [ ] Cost estimate before running
- [ ] Simple summary report at the end

### The pattern that matters

```python
for doc in documents:
    try:
        result = extract(doc)
        validate(result)
        save(result)
    except ValidationError as e:
        log_failure(doc, e)     # ← keep going, don't crash
        continue
```

**Batch processing is where AI delivers real economic value** — hours of manual data entry reduced to minutes plus a review pass.

### Ideas for real data

- Receipts and invoices → expense spreadsheet
- Job postings → structured skills/requirements table
- Customer feedback → categorised tickets with urgency
- Research papers → structured summary table

### Test it with

- 20+ real documents
- Deliberately include 2–3 **malformed** ones — a scanned image, an empty file, a document in the wrong language. **Handling these is what makes it a tool rather than a script.**

---

## Project 3 · Content workflow tool

**Difficulty:** ●●●○ | **Time:** 4–6 hours | **Builds on:** Modules 7, 13

A tool that handles a content task you do repeatedly — with **your voice**, not generic AI voice.

### What it does

Picks one recurring writing task and owns it end to end.

### Choose one

| Option | What it does |
|---|---|
| **Newsletter writer** | Takes rough notes → structured draft in your style |
| **Social scheduler** | One idea → platform-specific versions (LinkedIn, X, Instagram) |
| **Report generator** | Structured data → written narrative report |
| **Email responder** | Incoming email → draft reply matching your tone |
| **Study assistant** | Course notes → summaries, flashcards, practice questions |

### Requirements

**Core:**
- [ ] Takes input (notes, data, or a brief)
- [ ] Produces output in a **consistent, defined format**
- [ ] Matches a **specific voice** you've defined with examples
- [ ] Supports iteration — you can ask for changes
- [ ] Saves output to files
- [ ] Has a **voice/style guide stored as a prompt file**

**Stretch:**
- [ ] Few-shot examples drawn from your own past writing
- [ ] Multiple tones (formal / casual / brief)
- [ ] A self-critique pass before showing output
- [ ] Version history of drafts
- [ ] Fact-check pass that flags unverifiable claims

### The part everyone gets wrong

**Don't let it write from scratch.** Give it:

1. **Examples of your best past work** (3–5 samples)
2. **A banned-phrase list** (Module 7)
3. **Structure constraints** (headings, length, format)

Generic output almost always means missing examples — not a weak model.

### Test it with

- 5 real instances of your task
- Show output to someone who knows your writing. **Can they tell it's yours?**
- Check for invented facts (Module 5)

---

## Project 4 · Data analysis agent

**Difficulty:** ●●●● | **Time:** 4–6 hours | **Builds on:** Module 10

Give it a dataset, ask questions in plain English, get real answers and charts — **with code that actually ran.**

### ⚠️ Read before starting

This project has the highest risk of producing **fabricated numbers**. The rule from Module 10 applies absolutely:

> **Never show a number that didn't come from code that ran.**

Your design must make that structurally impossible.

### What it does

- Loads a CSV or Excel file
- Answers questions in plain English
- **Generates code, runs it, and shows both**
- Produces charts
- Explains findings in plain language

### Requirements

**Core:**
- [ ] Load a dataset
- [ ] Describe the data (columns, types, missing values)
- [ ] Answer plain-English questions
- [ ] **Generate pandas code and actually execute it**
- [ ] Show the code alongside the result — non-negotiable
- [ ] Generate charts on request
- [ ] Explain results in plain language

**Stretch:**
- [ ] Suggests interesting questions automatically
- [ ] Remembers earlier analysis in the session
- [ ] Handles follow-ups ("now break that down by region")
- [ ] Exports a full analysis report
- [ ] Asks for clarification when a question is ambiguous

### Safe execution

Running model-generated code is genuinely risky. **Minimum safeguards:**

```python
import io
import contextlib
import pandas as pd

ALLOWED = {"pd": pd, "df": None}   # only expose what's needed

def run_analysis(code: str, df):
    """Execute generated code in a restricted namespace."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, {"__builtins__": {}}, {**ALLOWED, "df": df})
        return buf.getvalue()
    except Exception as e:
        return f"Error running code: {e}"
```

**For anything beyond a personal tool, run generated code in a proper sandbox** — a container, a subprocess with no network, or a dedicated execution service. **Never exec model-generated code in an environment with your credentials in it.**

### The design that prevents fabrication

```
User question
    ↓
Model writes pandas code      ← we show this to the user
    ↓
Code EXECUTES                 ← real computation
    ↓
Real output captured
    ↓
Model interprets the output   ← only ever sees real numbers
    ↓
Answer shown with code + result
```

**The model never states a number it didn't compute.** It writes code, the code runs, and it explains the output. This is exactly the Mode B workflow from Module 10, automated.

### Test it with

- Questions where you **already know** the answer — verify every one
- A question the data **can't** answer → should say so, not invent
- Ambiguous questions → should ask for clarification

---

## General advice

### Start smaller than feels right

If a project seems like 6 hours, **build a 1-hour version first.** Get the whole loop working end to end, then add.

### Use real data from day one

Toy data hides the problems that matter. Your actual messy files will surface issues immediately — which is the point.

### Keep prompts in files

```python
# prompts/extract_invoice.py
SYSTEM_PROMPT = """..."""
```

Version them in Git. Review changes like code. This is what production teams do ([OpenAI's prompting guide](https://developers.openai.com/api/docs/guides/prompting) recommends exactly this).

### Log everything

```python
import logging

logging.basicConfig(filename="app.log", level=logging.INFO)
logging.info(f"prompt={prompt!r} response={response!r} cost={cost}")
```

When something behaves strangely — and it will — logs are how you find out why.

### Set a budget before you start

Spending limits in your account. Cost printed in your app. Check it after every run.

---

## Showing your work

When it's working:

1. **Write a README** — what it does, how to run it, what you learned
2. **Push to GitHub** — including your `.gitignore` for `.env` 🔴
3. **Share it** — post it, show a friend, use it for a week
4. **Note what you'd do differently** — that reflection is where the learning consolidates

---

## What's next

Once you've built one:

| Direction | Where to go |
|---|---|
| **Agents** — AI that uses tools and takes multi-step actions | Anthropic's [agent guidance](https://platform.claude.com/docs/en/build-with-claude/overview), OpenAI's [Agents docs](https://developers.openai.com/api/docs/agents) |
| **Production** — caching, retries, evals, monitoring | Provider production guides |
| **Multimodal** — vision, audio, realtime | [Gemini](https://ai.google.dev/gemini-api/docs/models), [OpenAI audio](https://developers.openai.com/api/docs/guides/audio) |
| **Local models** — privacy, offline, zero marginal cost | Ollama, LM Studio |
| **Structured agents** — typed tool use | [Strict tool use](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) |

See [Resources](./resources.md) for the full list.

---

## ✅ Course complete

If you've built one of these, you can now:

- Write prompts that reliably produce good output
- Recognise when AI is wrong, and know how to check
- Choose the right tool for a job
- Generate text, images, video, and audio
- Use AI to analyse data without trusting it blindly
- Call AI APIs from code
- Build applications that use AI

**That's a genuinely valuable skill set.** Go build something.

---

**[← Back to the syllabus](./README.md)**
