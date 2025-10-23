#!/bin/bash
# setup_eval.sh
# Setup script for RAGAS evaluation environment

set -e  # Exit on any error

echo "🧪 Setting up RAGAS Evaluation Environment"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "RAG_Core.py" ]; then
    echo "❌ Error: RAG_Core.py not found in current directory"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Create evaluation directory if it doesn't exist
if [ ! -d "evaluation" ]; then
    echo "📁 Creating evaluation/ directory..."
    mkdir evaluation
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher required (found $python_version)"
    exit 1
fi
echo "✓ Python $python_version"

# Remove existing eval environment if requested
if [ "$1" == "--rebuild" ]; then
    if [ -d ".venv_eval" ]; then
        echo "🗑️  Removing existing .venv_eval..."
        rm -rf .venv_eval
    fi
fi

# Create virtual environment
if [ ! -d ".venv_eval" ]; then
    echo ""
    echo "📦 Creating virtual environment (.venv_eval)..."
    python -m venv .venv_eval
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment .venv_eval already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source .venv_eval/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "📥 Installing evaluation dependencies..."
echo "   This may take a few minutes..."

# Install in order of importance
echo "   [1/4] Installing RAGAS..."
pip install ragas==0.1.8 --quiet

echo "   [2/4] Installing LangChain packages..."
pip install langchain==0.2.7 langchain-core==0.2.7 langchain-community==0.2.7 --quiet
pip install langchain-huggingface==0.0.2 langchain-text-splitters==0.2.2 --quiet
pip install langchain-openai==0.1.6 --quiet

echo "   [3/4] Installing data processing packages..."
pip install pandas==2.2.1 datasets==2.18.0 tqdm==4.66.1 --quiet

echo "   [4/4] Installing supporting packages..."
pip install openai==1.30.2 langsmith==0.1.75 --quiet
pip install chromadb==0.4.24 sentence-transformers==2.7.0 --quiet
pip install pymupdf==1.24.5 python-dotenv==1.0.0 --quiet

echo "✓ All packages installed"

# Copy compatibility layer to evaluation folder
echo ""
echo "📄 Setting up compatibility layer..."
if [ -f "RAG_Core_Compat.py" ]; then
    cp RAG_Core_Compat.py evaluation/
    echo "✓ RAG_Core_Compat.py copied to evaluation/"
elif [ -f "evaluation/RAG_Core_Compat.py" ]; then
    echo "✓ RAG_Core_Compat.py already in evaluation/"
else
    echo "⚠️  RAG_Core_Compat.py not found!"
    echo "   Please ensure this file exists before running evaluation"
fi

# Create .env template if it doesn't exist
if [ ! -f "evaluation/.env" ]; then
    echo ""
    echo "📝 Creating .env template..."
    cat > evaluation/.env << 'EOF'
# OpenAI API Key for RAGAS evaluation
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-key-here

# Optional: LangSmith tracing
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your-langsmith-key
EOF
    echo "✓ Created evaluation/.env template"
    echo "   ⚠️  IMPORTANT: Add your OpenAI API key to evaluation/.env"
else
    echo "✓ evaluation/.env already exists"
fi

# Run verification
echo ""
echo "🔍 Running compatibility verification..."
python evaluation/RAG_Core_Compat.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "="*80
    echo "🎉 SUCCESS! Evaluation environment is ready."
    echo "="*80
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1. Add your OpenAI API key to evaluation/.env:"
    echo "   nano evaluation/.env"
    echo ""
    echo "2. Ensure Ollama is running:"
    echo "   ollama serve"
    echo ""
    echo "3. Ensure vector database exists:"
    echo "   source .venv_eval/bin/activate"
    echo "   python -c 'from RAG_Core import create_vectorstore; create_vectorstore()'"
    echo ""
    echo "4. Run evaluation:"
    echo "   source .venv_eval/bin/activate"
    echo "   cd evaluation"
    echo "   python Evaluate_Ragas.py"
    echo ""
    echo "To activate this environment: source .venv_eval/bin/activate"
    echo "To deactivate: deactivate"
else
    echo ""
    echo "="*80
    echo "⚠️  Setup completed with warnings"
    echo "="*80
    echo ""
    echo "Some verification checks failed. Common issues:"
    echo ""
    echo "1. Vector store not found:"
    echo "   python -c 'from RAG_Core import create_vectorstore; create_vectorstore()'"
    echo ""
    echo "2. Ollama not running:"
    echo "   ollama serve"
    echo "   ollama pull llama3.2"
    echo ""
    echo "3. Missing data files:"
    echo "   Check RAGConfig paths in RAG_Core.py"
    echo ""
    echo "Run verification again: python evaluation/RAG_Core_Compat.py"
fi

# Deactivate at the end
deactivate

echo ""
echo "Setup script complete!"
