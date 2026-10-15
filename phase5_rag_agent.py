"""
PHASE 5: KNOWLEDGE (RAG = Retrieval-Augmented Generation)
=========================================================
Run interactive:  python phase5_rag_agent.py
Run auto demo:    python phase5_rag_agent.py --demo

Model + instructions + memory + KNOWLEDGE.

The model only knows what it was trained on. It has never seen YOUR notes.
RAG fixes that in three steps:
    1. CHUNK     split your document into small overlapping pieces
    2. RETRIEVE  find the pieces most relevant to the question
    3. AUGMENT   paste those pieces into the prompt, then let the model answer

Here retrieval is plain keyword matching. Real systems use embeddings
(vectors that capture meaning), but the pipeline shape is identical.

Azure Foundry equivalent: KNOWLEDGE (file search / Azure AI Search / grounding data).
"""

import re
import sys
from pathlib import Path

import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"
NOTES_PATH = Path(__file__).parent / "my_notes.txt"

CHUNK_SIZE = 500   # characters per chunk
OVERLAP = 100      # characters shared between neighbouring chunks
TOP_K = 3          # how many chunks to retrieve
MAX_HISTORY = 6    # keep only recent Q&A messages as memory

console = Console()

STOPWORDS = set("""a an the is are was were be been of to in on at for and or but with as by from
this that these those it its what who whom which when where why how do does did can could should
would i me my you your we our they them their about tell explain please give""".split())


# ---------------------------------------------------------------- 1. CHUNKING
def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """Split text into `size`-char chunks; each starts `size - overlap` after the last.

    Overlap protects against a fact being cut in half at a chunk boundary.
    """
    text = text.strip()
    step = size - overlap
    return [text[i:i + size].strip() for i in range(0, len(text), step) if text[i:i + size].strip()]


# -------------------------------------------------------------- 2. RETRIEVAL
def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS and len(w) > 1]


def retrieve(question: str, chunks: list[str], k: int = TOP_K) -> list[tuple[int, float, str]]:
    """Score each chunk by how many question keywords it contains.

    Returns [(chunk_number, score, chunk_text), ...] best first, dropping zero-score chunks.
    """
    q_terms = set(tokenize(question))
    scored = []
    for idx, chunk in enumerate(chunks, 1):
        words = tokenize(chunk)
        score = sum(words.count(t) for t in q_terms)   # keyword hits
        if score > 0:
            scored.append((idx, float(score), chunk))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]


# -------------------------------------------------------------- 3. AUGMENTING
SYSTEM_PROMPT = """You are Study Buddy, a tutor who answers using the student's own notes.

RULES:
1. Answer ONLY from the NOTES CONTEXT provided with each question.
2. Cite the chunk(s) you used like this: [Chunk 3].
3. If the answer is not in the context, say: "I couldn't find that in your notes."
4. Keep answers short and clear.
"""


def build_augmented_prompt(question: str, hits) -> str:
    if not hits:
        context = "(no relevant chunks found)"
    else:
        context = "\n\n".join(f"[Chunk {i}]\n{text}" for i, _, text in hits)
    return f"NOTES CONTEXT:\n{context}\n\nQUESTION: {question}"


def chat(messages: list[dict]) -> str:
    payload = {"model": MODEL, "messages": messages, "stream": False,
               "options": {"temperature": 0.2}}
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


def answer(question: str, chunks: list[str], history: list[dict]) -> str:
    hits = retrieve(question, chunks)

    # Show the retrieval step so you can SEE how RAG works.
    table = Table(title="Retrieved chunks", show_lines=True)
    table.add_column("Chunk", justify="center"); table.add_column("Score", justify="center")
    table.add_column("Preview")
    for i, score, text in hits:
        table.add_row(str(i), f"{score:.0f}", text[:90].replace("\n", " ") + "...")
    console.print(table if hits else "[yellow]No matching chunks found.[/]")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history[-MAX_HISTORY:]
    messages.append({"role": "user", "content": build_augmented_prompt(question, hits)})
    reply = chat(messages)

    # Memory stores the plain question (not the big context) to keep history small.
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": reply})
    return reply


def load_chunks() -> list[str]:
    if not NOTES_PATH.exists():
        console.print(f"[bold red]{NOTES_PATH.name} not found.[/] Create it and add your study notes.")
        sys.exit(1)
    chunks = chunk_text(NOTES_PATH.read_text(encoding="utf-8"))
    console.print(f"[dim]Loaded {NOTES_PATH.name}: {len(chunks)} chunks "
                  f"({CHUNK_SIZE} chars, {OVERLAP} overlap)[/]")
    return chunks


def run_demo():
    console.rule("[bold]PHASE 5 DEMO: RAG[/]")
    chunks, history = load_chunks(), []
    for q in ["Who invented the Zorblax Protocol and when?",
              "What is the third step of the Zorblax Protocol called?",
              "What is the capital of Australia?"]:   # not in notes -> should say so
        console.print(f"\n[bold cyan]You:[/] {q}")
        console.print(Panel(Markdown(answer(q, chunks, history)), title="Study Buddy", border_style="green"))


def run_interactive():
    console.rule("[bold]PHASE 5: Study Buddy with Knowledge[/]")
    chunks, history = load_chunks(), []
    console.print("Ask about your notes. Type [cyan]quit[/] to exit.\n")
    while True:
        try:
            q = console.input("[bold cyan]You:[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in {"quit", "exit"}:
            break
        if q:
            console.print(Panel(Markdown(answer(q, chunks, history)), title="Study Buddy", border_style="green"))
    console.print("Bye!")


if __name__ == "__main__":
    run_demo() if "--demo" in sys.argv else run_interactive()
