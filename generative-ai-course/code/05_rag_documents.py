"""
05 — RAG: chat with your own documents.

Retrieval-Augmented Generation, in three steps:
  1. INDEX    split your documents into chunks
  2. RETRIEVE find the chunks most relevant to a question
  3. GENERATE answer using ONLY those chunks

This version uses keyword scoring, so it needs no extra
dependencies and works offline for the retrieval step.

Run:
    mkdir -p docs && cp your-notes.txt docs/
    python 05_rag_documents.py
"""

import math
import re
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

MODEL = "claude-haiku-4-5"
CHUNK_SIZE = 800       # characters per chunk
CHUNK_OVERLAP = 150    # overlap so sentences aren't cut in half
TOP_K = 4              # how many chunks to send to the model


# ------------------------------------------------------------------ 1. INDEX
def load_documents(folder: str = "docs") -> list[tuple[str, str]]:
    """Read every .txt and .md file in a folder."""
    docs = []
    for path in sorted(Path(folder).glob("*")):
        if path.suffix.lower() in {".txt", ".md"}:
            docs.append((path.name, path.read_text(encoding="utf-8")))
    return docs


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """Split text into overlapping chunks, breaking at sentence ends."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]

        # try to end on a sentence boundary
        if end < len(text):
            last_stop = max(
                chunk.rfind(". "),
                chunk.rfind(".\n"),
                chunk.rfind("! "),
                chunk.rfind("? "),
            )
            if last_stop > size * 0.5:
                chunk = chunk[: last_stop + 1]
                end = start + len(chunk)

        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if c]


# --------------------------------------------------------------- 2. RETRIEVE
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "this", "that", "these", "those", "it", "its", "as", "if", "then",
    "what", "which", "who", "how", "when", "where", "why", "do", "does",
    "did", "can", "could", "would", "should", "i", "you", "we", "they",
}


def stem(word: str) -> str:
    """
    Very light stemming so "returns" matches "return" and
    "policies" matches "policy".

    Deliberately crude — it only needs to be good enough to
    make keyword retrieval work. Swap in a real stemmer or
    embeddings if you need better recall.
    """
    if len(word) > 5 and word.endswith("ies"):
        return word[:-3] + "y"
    for suffix in ("ing", "ed", "es", "s"):
        if len(word) > len(suffix) + 2 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def tokenize(text: str) -> list[str]:
    return [
        stem(w)
        for w in re.findall(r"[a-z0-9]+", text.lower())
        if w not in STOPWORDS and len(w) > 2
    ]


def score_chunk(question_terms: list[str], chunk: str, idf: dict) -> float:
    """
    TF-IDF-flavoured scoring.

    - rare words (high IDF) count for more than common ones
    - we normalise by length so long chunks don't win by default
    """
    chunk_terms = tokenize(chunk)
    if not chunk_terms:
        return 0.0

    counts: dict[str, int] = {}
    for term in chunk_terms:
        counts[term] = counts.get(term, 0) + 1

    score = 0.0
    for term in question_terms:
        tf = counts.get(term, 0)
        if tf:
            # 1 + log(tf) dampens repetition; idf rewards rare words
            score += (1 + math.log(tf)) * idf.get(term, 1.0)

    return score / math.sqrt(len(chunk_terms))


class DocumentStore:
    """Holds chunks and finds the relevant ones."""

    def __init__(self):
        self.chunks: list[dict] = []
        self.idf: dict[str, float] = {}

    def build(self, docs: list[tuple[str, str]]) -> None:
        self.chunks = []
        for name, text in docs:
            for i, chunk in enumerate(chunk_text(text)):
                self.chunks.append(
                    {"source": name, "index": i, "text": chunk}
                )
        self._compute_idf()
        print(f"Indexed {len(self.chunks)} chunks from {len(docs)} documents.")

    def _compute_idf(self) -> None:
        n = len(self.chunks)
        df: dict[str, int] = {}
        for chunk in self.chunks:
            for term in set(tokenize(chunk["text"])):
                df[term] = df.get(term, 0) + 1
        self.idf = {
            term: math.log((n + 1) / (count + 1)) + 1
            for term, count in df.items()
        }

    def search(self, question: str, k: int = TOP_K) -> list[dict]:
        terms = tokenize(question)
        scored = [
            (score_chunk(terms, c["text"], self.idf), c) for c in self.chunks
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for score, c in scored[:k] if score > 0]


# --------------------------------------------------------------- 3. GENERATE
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


def build_prompt(question: str, excerpts: list[dict]) -> str:
    blocks = "\n\n".join(
        f'<excerpt source="{e["source"]}" chunk="{e["index"]}">\n'
        f"{e['text']}\n</excerpt>"
        for e in excerpts
    )
    return f"<excerpts>\n{blocks}\n</excerpts>\n\nQuestion: {question}"


def answer(store: DocumentStore, question: str) -> str:
    excerpts = store.search(question)
    if not excerpts:
        return ("No relevant passages found in your documents. "
                "Try different wording.")

    message = client.messages.create(
        model=MODEL,
        max_tokens=600,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(question, excerpts)}],
    )
    return "".join(b.text for b in message.content if b.type == "text")


# ----------------------------------------------------------------- demo data
SAMPLE_DOCS = {
    "shop-policy.txt": """Zawadi Boutique — Shop Policies

Opening hours: Monday to Saturday, 9am to 7pm. Closed on Sundays
and public holidays.

Returns: Items can be returned within 14 days of purchase. Items
must be unworn, with tags attached, and you must bring the receipt.
Refunds are processed within 5 working days to the original payment
method. Sale items can be exchanged but not refunded.

Delivery: We deliver anywhere within Kampala for 8,000 UGX.
Delivery takes 1 to 2 working days. Orders above 150,000 UGX
qualify for free delivery.

Payment: We accept cash, MTN Mobile Money, and Airtel Money.
We do not accept cheques.

Contact: Call us on 0700 000 000 or email hello@zawadi.example.""",

    "staff-handbook.txt": """Zawadi Boutique — Staff Handbook (extract)

Opening duties: The first staff member to arrive unlocks the shop,
turns on the lights, and counts the float. The opening float is
50,000 UGX in small notes and coins.

Closing duties: Count the till, record the day's total in the
red ledger, and lock all cash in the safe. The safe code is
changed monthly and is given to supervisors only.

Customer complaints: Listen without interrupting. If you cannot
resolve the issue, refer the customer to the supervisor on duty.
Never argue with a customer in the shop.

Staff discount: All permanent staff receive a 20% discount on
full-price items. The discount does not apply to sale items and
cannot be combined with other offers.""",
}


def create_sample_docs(folder: str = "docs") -> None:
    Path(folder).mkdir(exist_ok=True)
    for name, content in SAMPLE_DOCS.items():
        path = Path(folder) / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    print(f"Sample documents ready in ./{folder}/")


def main() -> None:
    create_sample_docs()

    docs = load_documents("docs")
    if not docs:
        print("No .txt or .md files found in ./docs — add some and rerun.")
        return

    store = DocumentStore()
    store.build(docs)

    print("\nAsk questions about your documents.")
    print("Commands: /sources  /quit\n")

    while True:
        try:
            question = input("question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in {"/quit", "/exit", "quit", "exit"}:
            print("Goodbye.")
            break
        if question.lower() == "/sources":
            print("\nIndexed chunks:")
            for c in store.chunks:
                print(f"  {c['source']} #{c['index']}: {c['text'][:60]}...")
            continue

        try:
            print(f"\n{answer(store, question)}\n")
        except anthropic.AuthenticationError:
            print("\n[error] Bad API key. Check your .env file.")
        except anthropic.APIError as e:
            print(f"\n[error] API error: {e}")


if __name__ == "__main__":
    main()
