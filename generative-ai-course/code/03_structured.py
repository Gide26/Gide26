"""
03 — Structured output: get JSON data, not prose.

Two methods:
  A) messages.parse() with a Pydantic model  -> guaranteed valid
  B) ask for JSON in the system prompt, then parse defensively

Run:
    pip install anthropic python-dotenv pydantic
    python 03_structured.py
"""

import json

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator
from typing import Literal

load_dotenv()

client = anthropic.Anthropic()


# ---------------------------------------------------------------- method A
class Expense(BaseModel):
    vendor: str
    amount: float
    currency: str
    category: Literal["transport", "food", "supplies", "utilities", "other"]
    date: str | None = None

    @field_validator("amount")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"amount must be positive, got {v}")
        return v

    @field_validator("currency")
    @classmethod
    def must_be_known(cls, v: str) -> str:
        allowed = {"UGX", "USD", "KES", "EUR", "GBP"}
        if v.upper() not in allowed:
            raise ValueError(f"unknown currency: {v}")
        return v.upper()


SYSTEM_EXTRACT = """Extract expense details from the receipt text.

Rules:
- amount: a number only, no currency symbols or thousands separators
- currency: 3-letter code (UGX, USD, KES, EUR, GBP)
- category: exactly one of transport, food, supplies, utilities, other
- date: YYYY-MM-DD, or null if not stated
- If the text is not a receipt, set vendor to "NOT_A_RECEIPT"
- Never invent a value that is not in the text."""


def extract_expense(text: str) -> Expense | None:
    """Method A: schema-constrained output via Pydantic."""
    try:
        response = client.messages.parse(
            model="claude-haiku-4-5",
            max_tokens=500,
            system=SYSTEM_EXTRACT,
            messages=[{"role": "user", "content": text}],
            output_format=Expense,
        )
        return response.parsed_output
    except Exception as e:  # network, validation, or schema errors
        print(f"  extraction failed: {type(e).__name__}: {e}")
        return None


# ---------------------------------------------------------------- method B
def extract_json_fallback(text: str) -> dict | None:
    """Method B: ask for JSON, parse defensively. Works with any provider."""
    schema_hint = """Respond with JSON only. No markdown fences, no explanation.

Schema:
{
  "vendor": string,
  "amount": number,
  "currency": string,
  "category": "transport" | "food" | "supplies" | "utilities" | "other",
  "date": string or null
}

If a field is missing from the text, use null. Never invent a value."""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        temperature=0,  # near-deterministic, important for extraction
        system=schema_hint,
        messages=[{"role": "user", "content": text}],
    )
    raw = message.content[0].text.strip()

    # Models sometimes add ```json fences even when told not to.
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  JSON parse failed: {e}")
        return None


if __name__ == "__main__":
    receipts = [
        "TAXI RECEIPT - 15,000 UGX - 12 March 2026 - Special Hire",
        "Supermarket: bread 3,500, milk 4,200, sugar 6,000. Total 13,700 UGX",
        "MTN airtime top up 5,000 UGX",
    ]

    results = []
    for receipt in receipts:
        print(f"\nInput: {receipt}")
        expense = extract_expense(receipt)
        if expense:
            print(f"  -> {expense.vendor} | {expense.amount} {expense.currency} "
                  f"| {expense.category} | {expense.date}")
            results.append(expense.model_dump())

    if results:
        with open("expenses.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved {len(results)} expenses to expenses.json")
