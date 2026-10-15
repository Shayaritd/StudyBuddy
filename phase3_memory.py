"""
PHASE 3: MODEL + INSTRUCTIONS + MEMORY
======================================
Run interactive:  python phase3_memory.py
Run auto demo:    python phase3_memory.py --demo

Model + instructions + memory. Still no tools.

KEY INSIGHT: the model itself NEVER remembers anything. "Memory" is just
our code keeping a list of past messages and re-sending the WHOLE list on
every call. We switch to /api/chat, which takes a list of messages with roles:
    system    -> standing instructions
    user      -> what you said
    assistant -> what the model said

Azure Foundry equivalent: a THREAD (conversation) attached to the agent.
"""

import sys
import requests
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

SYSTEM_PROMPT = (
    "You are Study Buddy, a friendly tutor who explains things step-by-step "
    "and keeps answers concise. Use details the student told you earlier."
)

console = Console()


def chat(history: list[dict]) -> str:
    """Send the ENTIRE history to the model and return its next message."""
    payload = {"model": MODEL, "messages": history, "stream": False}
    try:
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        console.print("[bold red]Can't reach Ollama.[/] Try: [cyan]ollama serve[/]")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Ollama error:[/] {e}\nDid you run [cyan]ollama pull {MODEL}[/]?")
        sys.exit(1)
    return response.json()["message"]["content"].strip()


def new_history() -> list[dict]:
    # MEMORY lives here. It starts with only the system message.
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def send(history: list[dict], user_text: str) -> str:
    history.append({"role": "user", "content": user_text})   # remember what user said
    reply = chat(history)
    history.append({"role": "assistant", "content": reply})  # remember what model said
    return reply


def run_demo():
    console.rule("[bold]PHASE 3 DEMO: Memory[/]")
    history = new_history()
    for text in ["Hi! My name is Priya and I'm studying for a biology exam.",
                 "What's my name?",
                 "What am I studying for?"]:
        console.print(f"\n[bold cyan]You:[/] {text}")
        console.print(Panel(Markdown(send(history, text)), title="Study Buddy", border_style="green"))
    console.print(f"\n[dim]History now holds {len(history)} messages.[/]")


def run_interactive():
    console.rule("[bold]PHASE 3: Chat with Memory[/]")
    console.print("Commands: [cyan]/history[/] show memory, [cyan]/reset[/] forget everything, [cyan]quit[/] exit\n")
    history = new_history()
    while True:
        try:
            text = console.input("[bold cyan]You:[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if text.lower() in {"quit", "exit"}:
            break
        if text == "/reset":
            history = new_history()
            console.print("[yellow]Memory wiped.[/]")
            continue
        if text == "/history":
            for m in history:
                console.print(f"[dim]{m['role']:>9}:[/] {m['content']}")
            continue
        console.print(Panel(Markdown(send(history, text)), title="Study Buddy", border_style="green"))
    console.print("Bye!")


if __name__ == "__main__":
    run_demo() if "--demo" in sys.argv else run_interactive()
