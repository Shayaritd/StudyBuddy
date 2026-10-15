"""
PHASE 1: JUST A MODEL (no agent)
================================
Run:  python phase1_model.py

This is JUST a model. No memory, no tools, no instructions.
You send text in, you get text out. Every call is completely independent:
the model has no idea what you asked before.

Azure Foundry equivalent: picking a model from the MODEL CATALOG and
sending it a single prompt.
"""

import sys
import requests
from rich.console import Console
from rich.panel import Panel

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

console = Console()


def ask_model(prompt: str) -> str:
    """Send ONE prompt to the local model and return its text reply.

    /api/generate is Ollama's "raw completion" endpoint: prompt in, text out.
    "stream": False means we wait for the full answer instead of word-by-word.
    """
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        console.print("[bold red]Can't reach Ollama.[/] Is it running? Try: [cyan]ollama serve[/]")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Ollama error:[/] {e}\nDid you run [cyan]ollama pull {MODEL}[/]?")
        sys.exit(1)
    return response.json()["response"].strip()


if __name__ == "__main__":
    console.rule("[bold]PHASE 1: Just a Model[/]")

    prompts = [
        # 1) Works fine: models are great at explaining things.
        "Explain recursion in two sentences.",
        # 2) No memory: it has never met you.
        "What is my name?",
        # 3) No tools: it cannot look at a clock, so it will guess or refuse.
        "What time is it right now?",
    ]

    for i, prompt in enumerate(prompts, 1):
        console.print(f"\n[bold cyan]Prompt {i}:[/] {prompt}")
        answer = ask_model(prompt)
        console.print(Panel(answer, title="Model reply", border_style="green"))

    console.print(
        "\n[bold yellow]Takeaway:[/] Prompt 2 and 3 show the limits. "
        "No memory, no tools, no instructions. Just a model."
    )
