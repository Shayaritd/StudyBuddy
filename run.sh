#!/usr/bin/env bash
# Study Buddy Agent launcher: checks your setup, then runs a phase.
# Usage:  ./run.sh          (interactive menu)
#         ./run.sh 3        (run phase 3)
#         ./run.sh 4 --demo (pass extra flags through)

set -u
cd "$(dirname "$0")"
MODEL="llama3.2"
GREEN=$'\033[32m'; RED=$'\033[31m'; YELLOW=$'\033[33m'; RESET=$'\033[0m'
ok()   { echo "${GREEN}✔${RESET} $1"; }
fail() { echo "${RED}✘${RESET} $1"; exit 1; }
warn() { echo "${YELLOW}!${RESET} $1"; }

echo "== Checking your setup =="

# 1. Python 3.10+
PY=$(command -v python3 || command -v python) || fail "Python not found. Install Python 3.10+."
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' \
  || fail "Python 3.10+ required (found $("$PY" --version 2>&1))."
ok "Python: $("$PY" --version 2>&1)"

# 2. Virtual environment + dependencies
if [ ! -d ".venv" ]; then
  warn "Creating virtual environment (.venv)..."
  "$PY" -m venv .venv || fail "Could not create venv."
fi
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null || fail "Could not activate .venv"
if ! python -c "import requests, rich, colorama" 2>/dev/null; then
  warn "Installing dependencies from requirements.txt..."
  pip install -q -r requirements.txt || fail "pip install failed."
fi
ok "Dependencies: requests, rich, colorama"

# 3. Ollama installed
command -v ollama >/dev/null 2>&1 || fail "Ollama not installed. Get it at https://ollama.com/download"
ok "Ollama installed"

# 4. Ollama server running
if ! curl -s --max-time 3 http://localhost:11434/api/tags >/dev/null; then
  fail "Ollama server not responding. Start it with:  ollama serve   (or open the Ollama app)"
fi
ok "Ollama server running on localhost:11434"

# 5. Model pulled
if ! ollama list | awk 'NR>1{print $1}' | grep -q "^${MODEL}"; then
  warn "Model '${MODEL}' not found. Pulling it now (about 2 GB)..."
  ollama pull "$MODEL" || fail "Could not pull ${MODEL}."
fi
ok "Model '${MODEL}' available"
echo

# Pick a phase
PHASE="${1:-}"
if [ -z "$PHASE" ]; then
  cat << MENU
Which phase do you want to run?
  1) Just a model
  2) + System instructions
  3) + Memory           (interactive chat)
  4) + Tools = AGENT    (interactive)
  5) + Knowledge (RAG)  (interactive)
  d) Run ALL phases' auto-demos in order
MENU
  read -r -p "Choice: " PHASE
fi
shift 2>/dev/null || true

case "$PHASE" in
  1) python phase1_model.py ;;
  2) python phase2_instructions.py ;;
  3) python phase3_memory.py "$@" ;;
  4) python phase4_agent_tools.py "$@" ;;
  5) python phase5_rag_agent.py "$@" ;;
  d|D) python phase1_model.py && python phase2_instructions.py && python phase3_memory.py --demo \
        && python phase4_agent_tools.py --demo && python phase5_rag_agent.py --demo ;;
  *) fail "Unknown choice '$PHASE'" ;;
esac
