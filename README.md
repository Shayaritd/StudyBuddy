# 📚 Study Buddy Agent: learn how GenAI models and agents work

A 5-phase Python project that builds an AI agent from scratch using **only free, local tools**
(Ollama + llama3.2). No API keys, no cloud accounts. Each phase adds exactly one concept
and runs on its own, so you can see what changed.

```
Phase 1  Model
Phase 2  Model + Instructions
Phase 3  Model + Instructions + Memory
Phase 4  Model + Instructions + Memory + Tools      <- now it's an AGENT
Phase 5  Model + Instructions + Memory + Tools-style loop + Knowledge (RAG)
```

## 1. Install Ollama and pull the model

1. Download Ollama: <https://ollama.com/download> (macOS, Windows, Linux).
   Linux one-liner: `curl -fsSL https://ollama.com/install.sh | sh`
2. Make sure the server is running. The desktop app starts it automatically, or run `ollama serve`.
3. Pull the model (~2 GB, one-time):
   ```bash
   ollama pull llama3.2
   ```
4. Quick test: `ollama run llama3.2 "Say hi"`

## 2. Set up Python

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Or just run `./run.sh`. It checks Python, creates the venv, installs dependencies, verifies Ollama
is running, pulls llama3.2 if missing, then launches the phase you pick.

## 3. Run each phase

| Phase | Command | Mode |
|---|---|---|
| 1 | `python phase1_model.py` | auto demo (3 prompts) |
| 2 | `python phase2_instructions.py` | auto demo (same question, 4 personas) |
| 3 | `python phase3_memory.py` | interactive chat (`--demo` for auto) |
| 4 | `python phase4_agent_tools.py` | interactive agent (`--demo` for auto) |
| 5 | `python phase5_rag_agent.py` | interactive RAG (`--demo` for auto) |

With the launcher: `./run.sh 4`, `./run.sh 4 --demo`, or `./run.sh d` for all demos.

## 4. What each phase teaches (and the Azure AI Foundry equivalent)

| Phase | Concept | The key idea | Azure AI Foundry equivalent |
|---|---|---|---|
| 1 | **Model** | A model is a text-in/text-out function. No memory, no tools, no goals. Every call is independent. | **Model catalog**: choosing a model (here llama3.2 instead of GPT-4o). |
| 2 | **System instructions** | A `system` prompt sets role, tone, and rules. Same question, different behavior. | **Playground / agent "Instructions"** box. |
| 3 | **Memory** | The model remembers nothing. Your code stores the message list and re-sends all of it every call. | **Threads**: a conversation attached to an agent. |
| 4 | **Tools** | The model writes `TOOL: name(args)`; *your code* runs it and feeds back the result. That loop is what makes an agent. | **Tools**: function calling, code interpreter. |
| 5 | **Knowledge (RAG)** | Chunk → retrieve → inject into prompt, so the model can answer from data it was never trained on, with citations. | **Knowledge**: file search, Azure AI Search, grounding. |

### Things to try
- **Phase 2:** write your own persona ("a strict exam examiner") and compare.
- **Phase 3:** run `/history` and notice memory is just a list. Run `/reset` and ask your name again.
- **Phase 4:** ask something that needs two tools ("what's 15*15 and save it as a note"). Watch the loop.
  Add your own tool (say `word_count(text)`) by writing a function and adding it to `TOOLS` plus the system prompt.
- **Phase 5:** replace `my_notes.txt` with real notes. Ask a question using *different words* than your notes
  and watch keyword matching miss it. That's exactly the problem **embeddings** solve.

## 5. Known limitations (these are lessons too)
- llama3.2 (3B) is small. It sometimes ignores the `TOOL:` format or adds extra text. Production agents use
  native structured function calling, but the text protocol shows the mechanism clearly. Re-run or rephrase if it flubs.
- Keyword retrieval can't understand synonyms. Real RAG uses embeddings and a vector store.
- Memory is unbounded in Phase 3/4. Long chats eventually exceed the model's context window.
- `calculator` parses math with Python's `ast` instead of `eval()` so model output can never run arbitrary code.

## Files
```
phase1_model.py         phase2_instructions.py   phase3_memory.py
phase4_agent_tools.py   phase5_rag_agent.py      my_notes.txt  (your study notes + a fake fact)
requirements.txt        run.sh                   README.md
```
