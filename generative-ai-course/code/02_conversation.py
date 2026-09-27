"""
02 — Conversation: keeping history across turns.

The API has no memory. Every call is independent.
You maintain the history and send it every time.

Run:
    python 02_conversation.py
"""

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()


class Conversation:
    """A chat session that remembers what was said."""

    def __init__(self, system: str = None, model: str = "claude-haiku-4-5"):
        self.model = model
        self.system = system
        self.history: list[dict] = []

    def say(self, text: str) -> str:
        """Send a message, get a reply, remember both."""
        self.history.append({"role": "user", "content": text})

        kwargs = {
            "model": self.model,
            "max_tokens": 500,
            "messages": self.history,
        }
        if self.system:
            kwargs["system"] = self.system

        message = client.messages.create(**kwargs)

        reply = "".join(
            block.text for block in message.content if block.type == "text"
        )
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def reset(self) -> None:
        """Start over."""
        self.history = []


if __name__ == "__main__":
    chat = Conversation(
        system="You are a concise tutor. Answer in under 60 words."
    )

    print("You: My name is Gide and I'm learning data analysis.")
    print("AI: ", chat.say("My name is Gide and I'm learning data analysis."))

    print("\nYou: What's my name and what am I learning?")
    print("AI: ", chat.say("What's my name and what am I learning?"))

    print(f"\n(Conversation has {len(chat.history)} messages stored)")
