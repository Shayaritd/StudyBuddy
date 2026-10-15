# 📚 Study Buddy Agent
### Learn How GenAI Models and AI Agents Work — From Scratch

Build your own AI study assistant in Python through **5 progressive phases**, using completely free, local tools: **Ollama + Llama 3.2**.

This project helps you understand how Large Language Models (LLMs), system instructions, conversational memory, tool calling, and Retrieval-Augmented Generation (RAG) work together to create an AI agent.

No API keys. No paid APIs. No cloud accounts required.

The goal is simple: **understand how an AI agent works by building one yourself.**

---

## ✨ Project Highlights

- 🧠 **Local LLM:** Run Llama 3.2 locally using Ollama.
- 📝 **System Instructions:** Control the model's role, tone, and behavior.
- 💬 **Conversational Memory:** Maintain context across multiple messages.
- 🛠️ **Tool Calling:** Allow the model to request actions such as calculations and note-taking.
- 📚 **RAG:** Retrieve relevant information from local study notes.
- 🔒 **Local Execution:** Keep model inference and study data on your machine.
- 🆓 **Free to Run:** No API keys or cloud subscriptions required.

## 🏗️ Architecture

The project introduces one new concept at each phase.

```text
Phase 1: Model
    ↓
Phase 2: Model + System Instructions
    ↓
Phase 3: Model + Instructions + Memory
    ↓
Phase 4: Model + Instructions + Memory + Tools
    ↓
Phase 5: Model + Instructions + Memory + Tools + RAG
    ↓
       Study Buddy Agent
```

Each phase is a standalone Python program, making it easy to compare the behavior before and after introducing a new capability.

## 🧩 The Five Phases

### Phase 1 — Understanding an LLM

**File:** `phase1_model.py`

Learn how a language model accepts a prompt and generates a response.

**Concepts covered:**
- Sending prompts to a local LLM.
- Understanding input and generated output.
- Why independent requests do not automatically share conversational context.

**Try it:**

```bash
python phase1_model.py
```

The program runs three example prompts automatically.

### Phase 2 — System Instructions and Personas

**File:** `phase2_instructions.py`

Learn how system instructions influence a model's behavior without changing the underlying model.

**Concepts covered:**
- System prompts and role definition.
- Controlling tone, format, and response style.
- Comparing different personas using the same question.

**Try it:**

```bash
python phase2_instructions.py
```

Experiment with personas such as:
- A patient programming tutor.
- A strict exam examiner.
- A concise technical assistant.
- A beginner-friendly AI mentor.

### Phase 3 — Conversational Memory

**File:** `phase3_memory.py`

Build a conversational chatbot that maintains context across multiple messages.

**Concepts covered:**
- Chat history and message roles.
- Sending previous messages with each model request.
- Understanding how application-managed memory works.

**Try it:**

```bash
python phase3_memory.py
```

Useful commands:

```text
/history   View conversation history
/reset     Clear conversation memory
/exit      End the session
```

**Key takeaway:** The application stores the conversation and sends the relevant message history back to the model. The model does not automatically remember previous independent requests.

### Phase 4 — Building an AI Agent with Tools

**File:** `phase4_agent_tools.py`

Transform the chatbot into a basic AI agent that can request actions through tools.

**Concepts covered:**
- Tool definitions and arguments.
- Model-generated tool requests.
- Executing functions in Python.
- Returning tool results to the model.
- The agent execution loop.

**Try it:**

```bash
python phase4_agent_tools.py
```

Example tasks:

```text
What is 15 multiplied by 15?

Calculate 125 + 375 and save the result as a note.

Count the words in this sentence.
```

The agent can request a tool, your Python code executes the corresponding function, and the result is passed back to the model to continue the response.

**Important:** The model requests actions; the application code actually executes them. Tool execution should be restricted to explicitly registered, validated functions.

### Phase 5 — RAG: Giving the Agent Knowledge

**File:** `phase5_rag_agent.py`

Extend the agent with a simple retrieval system so it can answer questions using your own study notes.

**Concepts covered:**
- Document loading and text chunking.
- Retrieving relevant passages.
- Adding retrieved context to a prompt.
- Grounding answers in source material.
- Understanding the limitations of keyword-based retrieval.

**Try it:**

```bash
python phase5_rag_agent.py
```

Add your own content to:

```text
my_notes.txt
```

Ask questions about the information in your notes.

The basic implementation uses keyword matching. It demonstrates the RAG workflow but is not a full semantic search system.

**Key takeaway:** RAG helps a model answer questions using external information supplied at query time, rather than relying only on information learned during training.

---

## ⚙️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and agent orchestration |
| Ollama | Local model runtime |
| Llama 3.2 | Language model |
| Python functions | Custom tools and actions |
| `ast` | Safe parsing of supported calculator expressions |
| Text files | Local knowledge source for RAG |
| Virtual environment | Isolated Python dependencies |

## 📋 Prerequisites

Before starting, make sure you have:

- Python 3.10 or a compatible version required by the project dependencies.
- Ollama installed and running.
- Approximately 2 GB of free storage for the model download, plus space for dependencies and runtime files.
- A computer with sufficient memory to run Llama 3.2 locally.
- A terminal such as PowerShell, Command Prompt, or a Linux/macOS shell.

Download Ollama: https://ollama.com/download

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

Replace the placeholders with your repository URL and folder name.

### 2. Download the model

Start Ollama, then run:

```bash
ollama pull llama3.2
```

Verify that it works:

```bash
ollama run llama3.2 "Explain AI agents in simple words."
```

### 3. Create a Python virtual environment

**Windows — PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows — Command Prompt:**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run a phase

Start with Phase 1 and progress sequentially.

```bash
python phase1_model.py
python phase2_instructions.py
python phase3_memory.py
python phase4_agent_tools.py
python phase5_rag_agent.py
```

