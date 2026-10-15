"""
PHASE 4: TOOLS, THIS MAKES IT AN AGENT
======================================
Run interactive:  python phase4_agent_tools.py
Run auto demo:    python phase4_agent_tools.py --demo

This is a full AGENT: model + instructions + memory + tools.

THE AGENT LOOP (the core idea of this whole project):
    1. User asks something.
    2. Model either answers directly OR outputs a line:  TOOL: tool_name(args)
    3. OUR CODE parses that line and runs the real Python function.
    4. We feed the result back to the model as a new message.
    5. Model uses the result to write the final answer.

The model never runs anything. It only writes text. Your code does the acting.

Azure Foundry equivalent: TOOLS (function calling, code interpreter, etc.).
"""

import ast
import operator
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"
NOTES_FILE = Path(__file__).parent / "notes.txt"
MAX_TOOL_STEPS = 4  # safety: stop runaway loops

console = Console()

# ----------------------------------------------------------------------------
# TOOLS: ordinary Python functions. Each returns a string for the model to read.
# ----------------------------------------------------------------------------

def get_time(_: str = "") -> str:
    """Return the current local date and time."""
    return datetime.now().strftime("%A, %d %B %Y, %I:%M:%S %p")


# Safe math: we NEVER call eval() on model output (it could run any code).
# Instead we parse into an AST and only allow numbers and basic operators.
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval_node(node.left), _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("exponent too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("unsupported expression")


def calculator(expression: str) -> str:
    """Safely evaluate a math expression like '123 * 456'."""
    try:
        # Friendly aliases: 2^3 -> 2**3, 6x7 -> 6*7 (only when it looks like pure math)
        if re.fullmatch(r"[\d\s.xX^()+\-*/%]+", expression):
            expression = expression.replace("^", "**").replace("x", "*").replace("X", "*")
        result = _eval_node(ast.parse(expression.strip(), mode="eval").body)
        return str(result)
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception as e:
        return f"Error: could not evaluate ({e})"


def save_note(text: str) -> str:
    """Append a note to notes.txt."""
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M}] {text}\n")
    return f"Saved note: {text}"


def read_notes(_: str = "") -> str:
    """Return all saved notes."""
    if not NOTES_FILE.exists() or not NOTES_FILE.read_text(encoding="utf-8").strip():
        return "No notes saved yet."
    return NOTES_FILE.read_text(encoding="utf-8").strip()


# The registry maps tool names (what the model writes) to real functions.
TOOLS = {
    "get_time": get_time,
    "calculator": calculator,
    "save_note": save_note,
    "read_notes": read_notes,
}

# ----------------------------------------------------------------------------
# INSTRUCTIONS: we teach the model the tool-calling "protocol" in plain English.
# ----------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Study Buddy, a helpful tutor with access to tools.

AVAILABLE TOOLS:
- get_time()               -> current date and time
- calculator(expression)   -> evaluates math, e.g. calculator(123 * 456)
- save_note(text)          -> saves a note, e.g. save_note(buy milk)
- read_notes()             -> shows all saved notes

RULES:
1. If you need a tool, reply with ONLY one line in exactly this format:
   TOOL: tool_name(args)
   Write nothing else in that message.
2. NEVER guess the time or do arithmetic yourself. Use the tools.
3. After you receive a TOOL RESULT, answer the user in a short friendly sentence.
4. If no tool is needed, just answer normally.
"""

# Matches:  TOOL: calculator(123 * 456)
TOOL_PATTERN = re.compile(r"TOOL:\s*(\w+)\((.*)\)", re.IGNORECASE)


def parse_tool_call(reply: str):
    """Look for 'TOOL: name(args)' in the model's reply. Return (name, args) or None."""
    match = TOOL_PATTERN.search(reply)
    if not match:
        return None
    name, args = match.group(1).lower(), match.group(2).strip()
    args = re.sub(r"^\w+\s*=\s*", "", args)       # tolerate expression="..."
    args = args.strip().strip("'\"")              # tolerate quotes around args
    return name, args


def chat(history: list[dict]) -> str:
    payload = {"model": MODEL, "messages": history, "stream": False,
               "options": {"temperature": 0.2}}  # low temperature = more reliable format
    try:
        r = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=120)
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        console.print("[bold red]Can't reach Ollama.[/] Try: [cyan]ollama serve[/]")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]Ollama error:[/] {e}\nDid you run [cyan]ollama pull {MODEL}[/]?")
        sys.exit(1)
    return r.json()["message"]["content"].strip()


def agent_turn(history: list[dict], user_text: str) -> str:
    """One full agent turn: may involve several model calls and tool runs."""
    history.append({"role": "user", "content": user_text})

    for step in range(MAX_TOOL_STEPS):
        reply = chat(history)
        call = parse_tool_call(reply)

        if call is None:                      # No tool requested -> this is the final answer
            history.append({"role": "assistant", "content": reply})
            return reply

        name, args = call
        console.print(f"  [yellow]🔧 Model chose tool:[/] {name}({args!r})")
        if name in TOOLS:
            result = TOOLS[name](args)        # <-- YOUR CODE runs the tool, not the model
        else:
            result = f"Error: unknown tool '{name}'. Available: {', '.join(TOOLS)}"
        console.print(f"  [yellow]📦 Tool result:[/] {result}")

        # Feed the result back so the model can use it.
        history.append({"role": "assistant", "content": reply})
        history.append({"role": "user",
                        "content": f"TOOL RESULT: {result}\nNow answer the user's question using this result."})

    return "Sorry, I got stuck in a tool loop."


def new_history():
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def run_demo():
    console.rule("[bold]PHASE 4 DEMO: Agent with Tools[/]")
    history = new_history()
    for text in ["What time is it?", "What is 123 * 456?", "Save a note: buy milk",
                 "What notes do I have?", "Explain what a prime number is in one sentence."]:
        console.print(f"\n[bold cyan]You:[/] {text}")
        console.print(Panel(Markdown(agent_turn(history, text)), title="Study Buddy", border_style="green"))


def run_interactive():
    console.rule("[bold]PHASE 4: Study Buddy Agent (tools)[/]")
    console.print("Try: 'what time is it', 'what is 17 * 23', 'save a note: ...', 'show my notes'. Type [cyan]quit[/] to exit.\n")
    history = new_history()
    while True:
        try:
            text = console.input("[bold cyan]You:[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in {"quit", "exit"}:
            break
        if text:
            console.print(Panel(Markdown(agent_turn(history, text)), title="Study Buddy", border_style="green"))
    console.print("Bye!")


if __name__ == "__main__":
    run_demo() if "--demo" in sys.argv else run_interactive()
