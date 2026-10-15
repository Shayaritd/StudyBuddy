"""
PHASE 2: MODEL + SYSTEM INSTRUCTIONS
====================================
Run:  python phase2_instructions.py

This is a model + instructions. Still no memory or tools.
A "system prompt" tells the model WHO it is and HOW to behave. The user
prompt stays identical, but the personality and style change completely.

Azure Foundry equivalent: the "Instructions" box in the agent / playground.
"""

import sys
import requests
from rich.console import Console
from rich.panel import Panel

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

console = Console()


def ask_model(prompt: str, system: str | None = None) -> str:
    """Same as Phase 1, plus an optional `system` instruction.

    Ollama's /api/generate accepts a "system" field which is prepended
    to the conversation as the model's standing orders.
    """
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    if system:
        payload["system"] = system
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        console.print("[bold red]Can't reach Ollama.[/] Try: [cyan]ollama serve[/]")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Ollama error:[/] {e}\nDid you run [cyan]ollama pull {MODEL}[/]?")
        sys.exit(1)
    return response.json()["response"].strip()


if __name__ == "__main__":
    console.rule("[bold]PHASE 2: Model + Instructions[/]")

    SAME_QUESTION = "Why is the sky blue?"

    personas = {
        "No system prompt": None,
        "Pirate tutor": (
            "You are a pirate tutor. Explain things step-by-step, "
            "speak like a pirate, and keep it under 80 words."
        ),
        "Formal professor": (
            "You are a formal university professor. Use precise academic "
            "language, define terms, and keep it under 80 words."
        ),
        "ELI5 teacher": (
            "You explain things to a 5-year-old using a simple analogy. "
            "Keep it under 60 words."
        ),
    }

    console.print(f"\n[bold cyan]Same user prompt every time:[/] {SAME_QUESTION}")

    for name, system in personas.items():
        console.print(f"\n[bold magenta]System prompt:[/] {name}")
        answer = ask_model(SAME_QUESTION, system=system)
        console.print(Panel(answer, title=name, border_style="green"))

    console.print(
        "\n[bold yellow]Takeaway:[/] Instructions shape behavior without "
        "changing the question. Still no memory, still no tools."
    )
