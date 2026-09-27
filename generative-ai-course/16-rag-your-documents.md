# 16 · Chat With Your Documents

> **Time:** 50 minutes
> **You'll build:** an app that answers questions from your own files, with citations

This is the most useful thing in the course. Also the most requested feature in real AI products.

**The full code is in [`code/05_rag_documents.py`](./code/05_rag_documents.py).**

---

## What is RAG?

**RAG** = Retrieval-Augmented Generation. Three steps:

```
1. INDEX      split your documents into chunks
2. RETRIEVE   find the chunks relevant to the question
3. GENERATE   answer using ONLY those chunks
```

### Why not just paste everything?

Two reasons:

**Context limits.** You have a million tokens now, but a company's documents are far bigger — and bigger context costs more on every single call.

**Precision degrades with length.** Models are worse at finding a specific fact in 200 pages than in 2. Retrieval narrows to exactly what's relevant.

### Why this matters for accuracy

Recall Module 5: models invent things. RAG is the **structural fix.**

Instead of asking the model to recall a fact, you:

1. Find the relevant text yourself (retrieval — deterministic, verifiable)
2. Hand it to the model
3. **Instruct it to use only that text**

The model no longer has to remember. It only has to read and summarise — which it's excellent at.

> **RAG doesn't make the model smarter. It makes it grounded.**

---

## Step 1: Index

### Load documents

```python
def load_documents(folder="docs"):
    docs = []
    for path in sorted(Path(folder).glob("*")):
        if path.suffix.lower() in {".txt", ".md"}:
            docs.append((path.name, path.read_text(encoding="utf-8")))
    return docs
```

### Chunk them

Splitting matters more than people expect. **Chunk too big** → imprecise retrieval, wasted tokens. **Chunk too small** → you lose context, answers break.

```python
CHUNK_SIZE = 800       # characters
CHUNK_OVERLAP = 150    # so sentences aren't cut in half
```

The overlap matters: without it, a fact spanning a boundary gets split and neither half makes sense.

```python
def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]

        # prefer to end on a sentence boundary
        if end < len(text):
            last_stop = max(
                chunk.rfind(". "), chunk.rfind(".\n"),
                chunk.rfind("! "), chunk.rfind("? "),
            )
            if last_stop > size * 0.5:
                chunk = chunk[:last_stop + 1]
                end = start + len(chunk)

        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if c]
```

**The sentence-boundary trick is worth the five lines.** Chunks that end mid-sentence retrieve badly.

---

## Step 2: Retrieve

We need to find the chunks most relevant to a question. Two approaches:

| Approach | How | Trade-off |
|---|---|---|
| **Keyword** (used here) | Word overlap, TF-IDF weighted | No dependencies, free, instant. Misses synonyms. |
| **Embeddings** (production) | Semantic vector similarity | Catches meaning, not just words. Needs an embedding model. |

**We use keyword search** — no extra dependencies, works offline, and it's enough to understand the pattern.

### Scoring

```python
def score_chunk(question_terms, chunk, idf):
    chunk_terms = tokenize(chunk)
    if not chunk_terms:
        return 0.0

    counts = {}
    for term in chunk_terms:
        counts[term] = counts.get(term, 0) + 1

    score = 0.0
    for term in question_terms:
        tf = counts.get(term, 0)
        if tf:
            score += (1 + math.log(tf)) * idf.get(term, 1.0)

    return score / math.sqrt(len(chunk_terms))
```

Three ideas:

- **TF** (term frequency): the word appears often here. `1 + log(tf)` dampens repetition — a word appearing 20 times isn't 20× more relevant than once.
- **IDF** (inverse document frequency): rare words matter more. "the" appears everywhere (low IDF); "Kampala" is distinctive (high IDF).
- **Length normalisation**: divide by `√length` so long chunks don't win by default.

### The stemming gotcha

This bit a real bug during testing. **Without stemming, "return policy" fails to match "Returns:" and "Policies".**

```python
def stem(word):
    if len(word) > 5 and word.endswith("ies"):
        return word[:-3] + "y"          # policies -> policy
    for suffix in ("ing", "ed", "es", "s"):
        if len(word) > len(suffix) + 2 and word.endswith(suffix):
            return word[:-len(suffix)]  # returns  -> return
    return word
```

Crude, but it's the difference between working and mysteriously broken retrieval.

> **The honest limitation:** keyword search can't match "How do I pay?" to a section headed "Payment" if the stems differ. That's precisely why production systems use embeddings. More below.

---

## Step 3: Generate

The crucial part is the **prompt**. This is where grounding actually happens.

```python
SYSTEM_PROMPT = """You answer questions using only the provided document excerpts.

Rules:
- Use ONLY the information in <excerpts>. Do not add anything
  from your general knowledge.
- After each point, cite the source like this: [source: FILENAME]
- If the excerpts do not contain the answer, say exactly:
  "I don't have that information in the provided documents."
  Then, if useful, say what IS covered.
- Never guess, never fill gaps, never invent details.
- Be concise and direct."""
```

**Three instructions are doing the heavy lifting:**

1. *"Only the information in `<excerpts>`"* — bounds the source
2. *"Cite the source"* — makes claims checkable
3. *"If... not, say exactly..."* — gives it permission to fail

That third one is the most important. **Without an explicit graceful-failure instruction, models fill gaps from general knowledge** — which is exactly the behaviour RAG exists to prevent.

### Building the prompt

XML tags separate instructions from data (Module 13):

```python
def build_prompt(question, excerpts):
    blocks = "\n\n".join(
        f'<excerpt source="{e["source"]}" chunk="{e["index"]}">\n'
        f"{e['text']}\n</excerpt>"
        for e in excerpts
    )
    return f"<excerpts>\n{blocks}\n</excerpts>\n\nQuestion: {question}"
```

### The call

```python
def answer(store, question):
    excerpts = store.search(question)
    if not excerpts:
        return "No relevant passages found. Try different wording."

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        temperature=0,          # factual extraction — be deterministic
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(question, excerpts)}],
    )
    return "".join(b.text for b in message.content if b.type == "text")
```

**`temperature=0`** — this is a factual lookup, not a creative task.

---

## Run it

```bash
mkdir -p docs
cp my-notes.txt docs/
python3 05_rag_documents.py
```

Without a `docs/` folder, the script creates sample documents (a shop policy and a staff handbook) so you can try it immediately.

```
Indexed 4 chunks from 2 documents.

Ask questions about your documents.
Commands: /sources  /quit

question> What are the opening hours?

Monday to Saturday, 9am to 7pm. Closed on Sundays and
public holidays. [source: shop-policy.txt]

question> What's the weather in Kampala tomorrow?

I don't have that information in the provided documents.
The provided documents cover shop opening hours, returns,
delivery, payment methods, staff duties, and staff discounts.
```

**That second answer is the one to watch for.** The system correctly refuses to invent — and tells you what it *can* answer. That's RAG working as designed.

---

## Upgrading to embeddings

Keyword search works. Embeddings work *better* — they match meaning, so "How do I pay?" finds "Payment methods".

### The concept

An **embedding** turns text into a list of numbers (a vector) where similar meanings sit close together. Then retrieval is: embed the question, find chunks whose vectors are nearest.

```python
# pseudocode
question_vec = embed("How do I pay?")
chunk_vecs   = [embed(c) for c in chunks]

# cosine similarity — near 1.0 means very similar
best = sorted(chunks, key=lambda c: cosine(question_vec, embed(c)))[-TOP_K:]
```

| | Keyword (this module) | Embeddings |
|---|---|---|
| Matches | Exact/stemmed words | **Meaning** |
| "pay" → "Payment methods" | ❌ | ✅ |
| Dependencies | none | embedding model + vector store |
| Speed | instant | fast, needs an index at scale |
| Cost | free | small per-token cost |

### Available embedding models

- **Gemini Embedding** — [`gemini-embedding-001`](https://ai.google.dev/gemini-api/docs/models), and Gemini Embedding 2 which is multimodal (text, images, video, audio, PDFs in one space)
- **OpenAI Embeddings** — [see their embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- **Open-source** — sentence-transformers, runs locally for free

### Vector databases

For thousands of chunks, you need an index rather than scanning everything:

- **Start:** compute similarity in NumPy — fine up to ~10k chunks
- **Scale:** Chroma (simplest), Qdrant, Pinecone, pgvector (if you already use Postgres)

**Don't reach for a vector database on day one.** Plain NumPy handles far more than you'd guess, and it's one less thing to learn while you're getting the concept.

---

## Making it better

### Hybrid search (best value)

Combine both — keyword AND embedding scores. This is what production systems do:

```python
def hybrid_score(question, chunk):
    return 0.5 * keyword_score(question, chunk) + 0.5 * embedding_score(question, chunk)
```

### Reranking

Retrieve 20 chunks cheaply, then use the model to pick the best 4. More accurate, slightly slower.

### Better chunking

- **Respect structure** — split on headings, not raw character counts
- **Add metadata** — title, date, author — and filter on it before searching
- **Try 400–1000 characters** and measure which works for *your* documents

### Show your sources

Always return the source chunks with the answer, so users can check. **This is the single biggest trust-builder in any RAG app.**

---

## Common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| "Not in the documents" for things that are there | Retrieval failed | Check `/sources`; try smaller chunks |
| Answer ignores your documents | Prompt too weak | Strengthen the "only" instruction |
| Still invents details | No graceful-failure instruction | Add the exact refusal phrasing |
| Answers mix sources confusingly | Too many chunks | Lower `TOP_K` |
| Misses obvious answers | Keyword/synonym mismatch | Add stemming, or move to embeddings |

---

## ✏️ Exercise 16.1 — Run it (15 min)

1. Run the script with the sample docs
2. Ask 3 questions the docs **can** answer
3. Ask 2 they **cannot**
4. Confirm the refusals are clean

If a "cannot answer" question produces a confident invented answer, your system prompt needs strengthening.

---

## ✏️ Exercise 16.2 — Add your own documents (20 min)

Put 3–5 real files in `docs/` — notes, reports, saved articles, documentation.

Test with questions you know the answers to. **Count how many it gets right.** That number is your retrieval quality, and it's the thing to improve.

---

## ✏️ Exercise 16.3 — Tune the chunking (15 min)

Try `CHUNK_SIZE` at 400, 800, and 1500 with the same questions.

Record accuracy at each. **There's no universally correct chunk size** — it depends on your documents. Measuring is the only way to know.

---

## Key takeaways

- ✅ **RAG = retrieve relevant chunks, then generate from them**
- ✅ It doesn't make models smarter — it makes them **grounded**
- ✅ **Chunking quality drives everything** — break on sentence boundaries, use overlap
- ✅ **Stemming matters** for keyword retrieval — without it, obvious queries fail
- ✅ The **graceful-failure instruction** is what stops invention
- ✅ **Always show sources** — it's the biggest trust-builder there is
- ✅ **Embeddings** catch meaning where keywords can't — the standard production upgrade

---

**Next: [17 · Four Capstone Projects](./17-projects.md)**
