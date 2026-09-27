"""
04 — A command-line AI assistant.

Features:
  - Remembers the conversation
  - Streaming output (text appears as it's generated)
  - Commands: /reset  /save  /cost  /help  /quit
  - Tracks what you've spent

Run:
    python 04_cli_assistant.py
"""

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

MODEL = "claude-haiku-4-5"

# USD per 1M tokens. Verify against
# https://platform.claude.com/docs/en/models/overview
PRICES = {
    "claude-haiku-4-5": {"in": 1.00, "out": 5.00},
    "claude-sonnet-5": {"in": 2.00, "out": 10.00},
    "claude-opus-5-5": {"in": 4.00, "out": 20.00},
}

SYSTEM_PROMPT = """You are a helpful assistant running in the user's terminal.

Style:
- Concise. Short sentences. No filler.
- Use markdown when it helps readability.
- If you are not sure about a fact, say so plainly rather than guessing.
- Never invent citations, URLs, names, or numbers."""


def cost_of(model: str, input_tokens: int, output_tokens: int) -> float:
    p = PRICES.get(model, {"in": 4.00, "out": 20.00})
    return (input_tokens * p["in"] + output_tokens * p["out"]) / 1_000_000


class Assistant:
    def __init__(self, system: str = SYSTEM_PROMPT, model: str = MODEL):
        self.system = system
        self.model = model
        self.history: list[dict] = []
        self.total_cost = 0.0
        self.total_in = 0
        self.total_out = 0

    def _track(self, usage) -> None:
        self.total_in += usage.input_tokens
        self.total_out += usage.output_tokens
        self.total_cost += cost_of(
            self.model, usage.input_tokens, usage.output_tokens
        )

    def send(self, text: str) -> str:
        """Stream one reply, remember it, track cost."""
        self.history.append({"role": "user", "content": text})

        chunks = []
        usage = None

        # streaming: text arrives as it is generated
        with client.messages.stream(
            model=self.model,
            max_tokens=1000,
            system=self.system,
            messages=self.history,
        ) as stream:
            for event in stream:
                if event.type == "text":
                    print(event.text, end="", flush=True)
                    chunks.append(event.text)
            final = stream.get_final_message()
            usage = final.usage

        reply = "".join(chunks)
        print()  # newline after the streamed block

        self.history.append({"role": "assistant", "content": reply})
        if usage:
            self._track(usage)
        return reply

    def reset(self) -> None:
        self.history = []
        print("\n[conversation cleared]")

    def show_stats(self) -> None:
        print(
            f"\n[model: {self.model}] "
            f"tokens: {self.total_in} in / {self.total_out} out | "
            f"session cost: ${self.total_cost:.6f}"
        )

    def save(self, path: str = "conversation.md") -> None:
        with open(path, "w") as f:
            f.write("# Conversation\n\n")
            for msg in self.history:
                who = "You" if msg["role"] == "user" else "Assistant"
                f.write(f"## {who}\n\n{msg['content']}\n\n")
        print(f"[saved to {path}]")


HELP = """
Commands:
  /reset   clear the conversation
  /save    save the conversation to conversation.md
  /cost    show tokens used and cost this session
  /help    show this message
  /quit    exit
"""


def main() -> None:
    bot = Assistant()

    print("=" * 55)
    print("  Terminal Assistant — type /help for commands")
    print("=" * 55)

    while True:
        try:
            user_input = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"/quit", "/exit", "quit", "exit"}:
            bot.show_stats()
            print("Goodbye.")
            break
        elif user_input.lower() == "/reset":
            bot.reset()
        elif user_input.lower() == "/save":
            bot.save()
        elif user_input.lower() == "/cost":
            bot.show_stats()
        elif user_input.lower() == "/help":
            print(HELP)
        elif user_input.startswith("/"):
            print(f"Unknown command. Type /help for the list.")
        else:
            try:
                print("ai> ", end="", flush=True)
                bot.send(user_input)
            except anthropic.AuthenticationError:
                print("\n[error] Bad API key. Check your .env file.")
            except anthropic.RateLimitError:
                print("\n[error] Rate limited. Wait a moment and try again.")
            except anthropic.APIConnectionError:
                print("\n[error] Network problem. Check your connection.")
            except anthropic.APIError as e:
                print(f"\n[error] API error: {e}")


if __name__ == "__main__":
    main()
