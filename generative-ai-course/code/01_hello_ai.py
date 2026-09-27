"""
01 — Hello AI: your first API call.

Run:
    pip install anthropic python-dotenv
    export ANTHROPIC_API_KEY="sk-ant-..."   (or put it in a .env file)
    python 01_hello_ai.py
"""

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment


def ask(prompt: str, model: str = "claude-haiku-4-5", max_tokens: int = 300) -> str:
    """Send one prompt, return the text reply."""
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in message.content if block.type == "text")


if __name__ == "__main__":
    reply = ask("Explain what an API is, in one sentence, to a 12-year-old.")
    print(reply)
