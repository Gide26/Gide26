# 14 · Structured Output (JSON)

> **Time:** 30 minutes  
> **You'll learn:** get reliable, machine-readable data out of a model

So far the model returns prose. But programs need **data**. This module is where your AI code becomes genuinely useful.

---

## Why this matters

Prose is for humans. Data is for programs.

```
❌ "The total comes to approximately 45,000 UGX..."
✅ {"total": 45000, "currency": "UGX", "confidence": "high"}
```

Once you have JSON you can:

- Save it to a database
- Show it in a table or chart
- Feed it into other code
- Validate it automatically

**Structured output is the bridge between "AI does something cool" and "AI is part of my application."**

---

## Method 1: Guaranteed JSON via schema (recommended)

Anthropic's [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) constrain the model to match your schema exactly. Valid JSON every time, no parsing errors.

```python
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "plan_interest": {"type": "string"},
        "demo_requested": {"type": "boolean"},
    },
    "required": ["name", "email", "plan_interest", "demo_requested"],
    "additionalProperties": False,
}

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": (
            "Extract the key information from this email: "
            "John Smith (john@example.com) is interested in our "
            "Enterprise plan and wants to schedule a demo for "
            "next Tuesday at 2pm."
        ),
    }],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": schema,
        }
    },
)

data = json.loads(message.content[0].text)
print(data)
# {'name': 'John Smith', 'email': 'john@example.com',
#  'plan_interest': 'Enterprise', 'demo_requested': True}
```

### The cleaner way: Pydantic

Writing raw JSON Schema is tedious. Use a Pydantic model and the SDK's `parse()` helper:

```bash
pip install pydantic
```

```python
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()


class ContactInfo(BaseModel):
    name: str
    email: str
    plan_interest: str
    demo_requested: bool


response = client.messages.parse(
    model="claude-sonnet-5",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": (
            "Extract the key information from this email: "
            "John Smith (john@example.com) is interested in our "
            "Enterprise plan and wants to schedule a demo for "
            "next Tuesday at 2pm."
        ),
    }],
    output_format=ContactInfo,
)

contact = response.parsed_output   # a real ContactInfo object
print(contact.name)                # John Smith
print(contact.demo_requested)      # True
```

**Note:** `parse()` works like `create()`, but takes `output_format=YourPydanticModel` and returns `response.parsed_output` as a validated object.

This is the nicest way to do it — you get **type safety and autocomplete** in your editor.

---

## Method 2: Ask, then parse (works everywhere)

Not every provider offers schema-constrained output. The universal approach: ask for JSON in the system prompt, then parse defensively.

```python
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

SYSTEM = """Extract contact details from the text.

Respond with JSON only. No markdown fences, no explanation.

Schema:
{
  "name": string,
  "email": string,
  "interest": string,
  "urgency": "low" | "medium" | "high"
}

If a field is not present in the text, use null.
Never invent a value."""

text = "Amara Nakato (amara@example.com) asked about bulk pricing. She needs an answer this week."

message = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    temperature=0,          # ← important for consistency
    system=SYSTEM,
    messages=[{"role": "user", "content": text}],
)

raw = message.content[0].text

# Strip markdown fences if the model added them anyway
cleaned = raw.strip()
if cleaned.startswith("```"):
    cleaned = cleaned.split("```")[1]
    if cleaned.startswith("json"):
        cleaned = cleaned[4:]

data = json.loads(cleaned)
print(data)
```

**Two things matter here:**

1. **`temperature=0`** — near-deterministic output. Always use it for structured extraction.
2. **Defensive cleaning** — even when told not to, models sometimes wrap JSON in ``` fences.

---

## Handling failure

Even with constrained output, **always handle the parse error**. Network hiccups, truncation, and edge cases happen.

```python
def extract_json(text):
    """Parse JSON, tolerating markdown fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    return json.loads(cleaned)


def extract_with_retry(client, text, schema_prompt, attempts=3):
    """Try extraction, retry on failure."""
    for i in range(attempts):
        try:
            message = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=500,
                temperature=0,
                system=schema_prompt,
                messages=[{"role": "user", "content": text}],
            )
            return extract_json(message.content[0].text)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  attempt {i+1} failed: {e}")
            if i == attempts - 1:
                return None
    return None
```

> **Truncation is the sneaky failure.** If `max_tokens` is too low, you get valid-looking JSON that's cut off mid-object. Check `stop_reason == "max_tokens"` and raise the limit.

---

## Designing good schemas

### Use constrained types

```python
from typing import Literal
from pydantic import BaseModel


class Ticket(BaseModel):
    category: Literal["bug", "feature", "pricing", "other"]  # ← only these
    urgency: Literal["low", "medium", "high"]
    summary: str
    customer_name: str | None    # nullable
```

**`Literal` types are powerful.** The model can only emit those exact values, which means you never have to handle `"High"`, `"HIGH"`, and `"high"` as three cases.

### Allow nulls

```python
class Invoice(BaseModel):
    vendor: str
    total: float | None      # None if not stated
    date: str | None
```

**Better than forcing a guess.** Combine with:

```
If a value is not present in the text, use null.
Never invent a value to fill a field.
```

### Describe your fields

```python
class Review(BaseModel):
    sentiment: str   # "positive", "negative", or "mixed"
    rating: int      # 1-5, where 5 is most positive
```

Descriptions become part of the schema the model sees, and they measurably improve accuracy.

### Keep it flat where you can

Nested is fine, but for a first version flat is easier to debug. Add nesting when you actually need it.

---

## A real example: extracting from many documents

```python
import json
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()


class Expense(BaseModel):
    vendor: str
    amount: float
    currency: str
    category: str
    date: str | None


SYSTEM = """Extract expense details from receipts.

Rules:
- amount must be a number, no currency symbols or commas
- currency as a 3-letter code (UGX, USD, KES)
- category: one of transport, food, supplies, utilities, other
- date in YYYY-MM-DD format; null if not stated
- If the text is not a receipt, set vendor to "NOT_A_RECEIPT"
- Never invent values"""

receipts = [
    "TAXI RECEIPT - 15,000 UGX - 12 March 2026 - Special Hire",
    "Nakumatt Supermarket: bread 3,500, milk 4,200, sugar 6,000. Total 13,700 UGX",
    "MTN airtime top up 5,000 UGX",
]

results = []
for i, receipt in enumerate(receipts, 1):
    response = client.messages.parse(
        model="claude-haiku-4-5",
        max_tokens=500,
        system=SYSTEM,
        messages=[{"role": "user", "content": receipt}],
        output_format=Expense,
    )
    exp = response.parsed_output
    results.append(exp.model_dump())
    print(f"{i}. {exp.vendor} — {exp.amount} {exp.currency} ({exp.category})")

# Now you have structured data — save it
with open("expenses.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved {len(results)} expenses to expenses.json")
```

**That's a real application.** Text in, structured data out, saved to a file. You could load this into pandas, chart it, or import it into accounting software.

---

## Validation: don't trust, verify

Constrained output guarantees *shape*, not *truth*.

```python
from pydantic import BaseModel, field_validator


class Expense(BaseModel):
    vendor: str
    amount: float
    currency: str

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError(f"amount must be positive, got {v}")
        return v

    @field_validator("currency")
    @classmethod
    def currency_must_be_known(cls, v):
        if v.upper() not in {"UGX", "USD", "KES", "EUR", "GBP"}:
            raise ValueError(f"unknown currency: {v}")
        return v.upper()
```

**Sanity checks catch the errors that matter** — a misread decimal point, a currency parsed as the wrong code, a date from the wrong century.

---

## Choosing an output shape

| You want | Use |
|---|---|
| Data for code | JSON via `messages.parse()` + Pydantic |
| A readable report | Markdown |
| A table | Ask for a markdown table, or JSON → render it |
| A classification | JSON with `Literal` types |
| Free-form text | Plain text |

---

## ✏️ Exercise 14.1 — Extract from your own text (15 min)

1. Take 5 real text items (emails, receipts, messages, notes)
2. Define a Pydantic model for what you want out
3. Run extraction with `messages.parse()`
4. Print results as a table

Check: **did any values get invented?** That's the thing to watch for.

---

## ✏️ Exercise 14.2 — Compare the methods (10 min)

Run the same extraction:

1. **Plain prompt**, no structure — see what comes back
2. **Method 2** (ask + parse), `temperature=0`
3. **Method 1** (`messages.parse()` with Pydantic)

Count how many needed cleanup in each. This is a genuinely convincing experiment.

---

## ✏️ Exercise 14.3 — Add validation (10 min)

Add two validators to your model:

1. A **range check** on any numeric field
2. An **allowed-values check** on any string field

Then deliberately feed it input that violates both. **Watch the validator catch it.** That's your safety net working.

---

## Key takeaways

- ✅ Structured output turns AI from a novelty into **part of an application**
- ✅ **Method 1:** `messages.parse()` + Pydantic → `response.parsed_output`. Guaranteed valid.
- ✅ **Method 2:** ask for JSON in the system prompt, parse defensively. Works everywhere.
- ✅ **Always `temperature=0`** for extraction
- ✅ **`Literal` types** constrain values; **`| None`** allows honest nulls
- ✅ **Validate** — constrained output guarantees *shape*, never *truth*
- ✅ Check `stop_reason` — truncation produces broken JSON

---

**Next: [15 · Build a CLI Assistant](./15-cli-assistant.md)**
