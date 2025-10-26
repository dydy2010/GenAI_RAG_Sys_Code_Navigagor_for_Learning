#!/bin/bash
set -euo pipefail

echo "🎯 Setting up dual-environment Evaluation System..."

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load .env if present (exports OPENAI_API_KEY, etc.)
if [[ -f "$ROOT_DIR/.env" ]]; then
  echo "🔧 Loading environment variables from .env"
  set -a
  # shellcheck disable=SC1090
  source "$ROOT_DIR/.env"
  set +a
else
  echo "ℹ️  No .env found. Creating a template at $ROOT_DIR/.env"
  {
    echo "# RAG Evaluation environment"
    echo "# Add your OpenAI API key below"
    echo "OPENAI_API_KEY=your_key_here"
  } > "$ROOT_DIR/.env"
  echo "✅ Created .env template. Edit it to add your actual key, then re-run evaluation."
fi

### 1) RAG System Environment: build/load vector store
echo "\n📦 Creating RAG system venv (.venv_rag_sys) and installing deps..."
python3 -m venv "$ROOT_DIR/.venv_rag_sys"
source "$ROOT_DIR/.venv_rag_sys/bin/activate"
pip install --upgrade pip

# Minimal deps for evaluation_only_rag_sys.py
pip install langchain langchain-community langchain-huggingface chromadb sentence-transformers torch pymupdf langsmith tqdm

echo "✅ RAG system deps installed. Building/loading Chroma vector store and generating responses.json..."

# ensure Ollama is running and model is available
if ! curl -s "http://localhost:11434/api/tags" >/dev/null; then
  echo "✗ Ollama server not reachable at http://localhost:11434. Please start it (e.g., 'ollama serve') and rerun."
  exit 1
fi

# Ensure llama3.2 model is present; pull if missing
if ! curl -s "http://localhost:11434/api/tags" | grep -q '"name":"llama3.2"'; then
  echo "⬇️  Pulling Ollama model: llama3.2"
  ollama pull llama3.2
fi

# Run batch generation without swallowing errors
BATCH_EVAL=1 python3 "$ROOT_DIR/evaluation_only_rag_sys.py"
deactivate

### 2) Evaluation Environment: RAGAS and metrics
echo "\n🧪 Creating Evaluation venv (.venv_eval) and installing deps..."
python3 -m venv "$ROOT_DIR/.venv_eval"
source "$ROOT_DIR/.venv_eval/bin/activate"
pip install --upgrade pip

# Install ragas with latest stable versions and required dependencies
pip install --upgrade ragas datasets pandas tqdm langchain-openai openai langchain langchain-huggingface sentence-transformers

echo "✅ Evaluation deps installed."

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  echo "🔑 OPENAI_API_KEY detected. Running evaluation..."
  python3 "$ROOT_DIR/evaluate_ragas.py" || true
else
  echo "⚠️  OPENAI_API_KEY not set. Please add in .env file. Skipping evaluation run."
  echo "   To run later:"
  echo "     source $ROOT_DIR/.venv_eval/bin/activate && python3 $ROOT_DIR/evaluate_ragas.py"
fi

deactivate

echo "\n🎉 Done. Environments created:"
echo " - $ROOT_DIR/.venv_rag_sys (RAG system build/runtime)"
echo " - $ROOT_DIR/.venv_eval (RAGAS evaluation)"

echo "\nNext steps:"
echo " 1) To rebuild vector store:"
echo "    source $ROOT_DIR/.venv_rag_sys/bin/activate && python3 $ROOT_DIR/evaluation_only_rag_sys.py && deactivate"
echo " 2) To run evaluation:"
echo "    export OPENAI_API_KEY=\"YOUR_KEY\""
echo "    source $ROOT_DIR/.venv_eval/bin/activate && python3 $ROOT_DIR/evaluate_ragas.py && deactivate"