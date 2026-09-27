# 15 · Build a CLI Assistant

> **Time:** 45 minutes
> **You'll build:** a working terminal chatbot with memory, streaming, and cost tracking

Everything so far comes together here. At the end you'll have a real tool you can use daily.

**The full code is in [`code/04_cli_assistant.py`](./code/04_cli_assistant.py).**

---

## What we're building

A terminal assistant that:

- ✅ Remembers the whole conversation
- ✅ Streams replies as they're generated
- ✅ Tracks tokens and cost live
- ✅ Handles commands: `/reset`, `/save`, `/cost`, `/help`, `/quit`
- ✅ Fails gracefully on bad keys and network errors

---

## The core insight: you own the memory

The API is **stateless**. It remembers nothing between calls.

So the assistant keeps a list and sends the whole thing every time:

```python
self.history = [
    {"role": "user",      "content": "My name is Gide."},
    {"role": "assistant", "content": "Nice to meet you, Gide!"},
    {"role": "user",      "content": "What's my name?"},
]
```

Every AI chat application you've ever used is doing exactly this. **There is no magic — just a list you resend.**

```python
def say(self, text):
    self.history.append({"role": "user", "content": text})

    message = client.messages.create(
        model=self.model,
        max_tokens=1000,
        system=self.system,
        messages=self.history,      # ← the entire conversation, every time
    )

    reply = message.content[0].text
    self.history.append({"role": "assistant", "content": reply})
    return reply
```

---

## Streaming: why it feels so much faster

Without streaming, you wait 10 seconds, then get the whole reply at once.

With streaming, text appears word by word as it's generated. **Same total time — completely different experience.**

```python
with client.messages.stream(
    model=self.model,
    max_tokens=1000,
    system=self.system,
    messages=self.history,
) as stream:
    for event in stream:
        if event.type == "text":
            print(event.text, end="", flush=True)   # print as it arrives
            chunks.append(event.text)

    final = stream.get_final_message()
    usage = final.usage      # token counts available after completion
```

Two things to notice:

1. **`flush=True`** — without it, Python buffers the output and you lose the effect
2. **Usage stats only exist on the final message** — you get token counts *after* streaming ends

The model generates tokens one at a time, so printing as they arrive costs nothing and makes the tool feel alive.

---

## Cost tracking

```python
PRICES = {
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00},   # per 1M tokens
    "claude-sonnet-5":  {"in": 2.00, "out": 10.00},
    "claude-opus-5-5":  {"in": 4.00, "out": 20.00},
}

def cost_of(model, input_tokens, output_tokens):
    p = PRICES.get(model, {"in": 4.00, "out": 20.00})
    return (input_tokens * p["in"] + output_tokens * p["out"]) / 1_000_000
```

**Verify these against [the official pricing page](https://platform.claude.com/docs/en/models/overview) — they change.**

Track it per call and accumulate:

```python
def _track(self, usage):
    self.total_in += usage.input_tokens
    self.total_out += usage.output_tokens
    self.total_cost += cost_of(self.model, usage.input_tokens, usage.output_tokens)
```

Then `/cost` shows the running session total. **This is the habit that prevents billing surprises.**

---

## Graceful error handling

The difference between a script and a tool: a tool doesn't crash on you.

```python
try:
    bot.send(user_input)
except anthropic.AuthenticationError:
    print("\n[error] Bad API key. Check your .env file.")
except anthropic.RateLimitError:
    print("\n[error] Rate limited. Wait a moment and try again.")
except anthropic.APIConnectionError:
    print("\n[error] Network problem. Check your connection.")
except anthropic.APIError as e:
    print(f"\n[error] API error: {e}")
```

Catch **specific** exceptions. A bare `except Exception` hides real bugs and swallows the message you need.

---

## The main loop

```python
while True:
    try:
        user_input = input("\nyou> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
        break                      # Ctrl+C / Ctrl+D exits cleanly

    if not user_input:
        continue                   # ignore empty lines

    if user_input.lower() in {"/quit", "/exit"}:
        bot.show_stats()
        print("Goodbye.")
        break
    elif user_input.lower() == "/reset":
        bot.reset()
    elif user_input.lower() == "/save":
        bot.save()
    elif user_input.lower() == "/cost":
        bot.show_stats()
    elif user_input.startswith("/"):
        print("Unknown command. Type /help for the list.")
    else:
        bot.send(user_input)
```

Simple, predictable, and it handles the cases users actually hit.

---

## Run it

```bash
cp code/04_cli_assistant.py .
python3 04_cli_assistant.py
```

```
=======================================================
  Terminal Assistant — type /help for commands
=======================================================

you> Explain what a database index does, in two sentences.

ai>  A database index is a sorted lookup structure...
```

Type `/cost` after a few exchanges. On Haiku you'll likely see **fractions of a cent.**

---

## Extensions to try

Ordered by difficulty:

### 1. Persistent memory (easy)

Save history to JSON on exit, load it on start.

```python
import json

def save_history(self, path=".history.json"):
    with open(path, "w") as f:
        json.dump(self.history, f)

def load_history(self, path=".history.json"):
    try:
        with open(path) as f:
            self.history = json.load(f)
    except FileNotFoundError:
        self.history = []
```

Now your assistant remembers you across sessions.

### 2. Trim long conversations (easy, important)

Long histories cost more each call — you resend everything every time. Keep the last N turns:

```python
MAX_TURNS = 20   # 40 messages

def _trim(self):
    if len(self.history) > MAX_TURNS * 2:
        # keep the system context and the most recent turns
        self.history = self.history[-(MAX_TURNS * 2):]
```

**This is the cheapest optimisation in AI engineering.** On long chats it can cut cost by 10×.

### 3. A named persona (easy)

```python
python3 04_cli_assistant.py          # default
```

Add a `--persona` flag that loads a system prompt from a file:

```python
system = Path(args.persona).read_text() if args.persona else SYSTEM_PROMPT
```

Keep a folder of personas — `tutor.txt`, `editor.txt`, `therapist-ish.txt` — and switch by argument.

### 4. File input (medium)

Let it read a file so you can ask questions about documents:

```python
elif user_input.startswith("/file "):
    path = user_input[6:].strip()
    text = Path(path).read_text()
    self.history.append({"role": "user", "content": f"Here's a file:\n\n{text}"})
    print(f"[loaded {len(text)} characters]")
```

### 5. Streaming markdown rendering (medium)

Look at the [`rich`](https://github.com/Textualize/rich) library for rendering markdown, tables, and syntax-highlighted code live in the terminal.

---

## ✏️ Exercise 15.1 — Build it (20 min)

Copy the script, run it, then verify each feature:

- [ ] Conversation memory works (ask a question, then ask "what did I just ask?")
- [ ] Streaming works (text appears progressively)
- [ ] `/cost` shows real numbers
- [ ] `/save` produces a readable markdown file
- [ ] `/reset` clears context (verify by asking about something from before)
- [ ] Interrupting with Ctrl+C exits cleanly

---

## ✏️ Exercise 15.2 — Add two extensions (20 min)

Pick two from the list above. **Persistent memory and history trimming** are the most valuable — do those first if unsure.

---

## ✏️ Exercise 15.3 — Make it yours (15 min)

Rewrite `SYSTEM_PROMPT` for a specific job you do — a study tutor for your course, a drafting tool for a particular kind of email, a code reviewer for your language.

Use Module 13's five parts. Then **test it**, including the "I don't know" case.

---

## Key takeaways

- ✅ The API is **stateless** — you maintain and resend the history
- ✅ **Streaming** costs nothing and transforms the experience (`flush=True`!)
- ✅ **Track cost** from day one — it's three lines
- ✅ Catch **specific** exceptions, not bare `except Exception`
- ✅ **Trim long histories** — biggest cost optimisation available
- ✅ You now understand what every AI chat app is doing underneath

---

**Next: [16 · Chat With Your Documents](./16-rag-your-documents.md)**
