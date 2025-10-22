#!/bin/bash
# setup_for_eval.sh
# Sets up isolated evaluation environment with rag_core support

echo "🎯 Setting up SOLID Evaluation System..."
echo ""

# Create virtual environment
echo "📦 Creating virtual environment (.venv_eval)..."
python -m venv .venv_eval

# Activate it
echo "🔌 Activating virtual environment..."
source .venv_eval/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install evaluation-specific packages with fixed versions
echo "📥 Installing evaluation packages (fixed versions)..."
pip install ragas==0.1.8 
pip install langchain-openai==0.1.6 
pip install langchain-community==0.2.7 
pip install langchain-core==0.2.7 
pip install langchain-huggingface==0.0.2

# Install supporting packages
echo "📥 Installing supporting packages..."
pip install pandas==2.2.1 
pip install tqdm==4.66.1 
pip install datasets==2.18.0 
pip install openai==1.30.2 
pip install langsmith==0.1.c 
pip install chromadb==0.4.24

# Install additional packages needed by rag_core
echo "📥 Installing rag_core dependencies..."
pip install langchain
pip install sentence-transformers
pip install pymupdf

echo ""
echo "=" * 60
echo "✅ Installation complete!"
echo "=" * 60
echo ""

# Run verification
echo "🔍 Verifying installation..."
python check_eval.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "=" * 60
    echo "🎉 SUCCESS! Evaluation environment is ready."
    echo "=" * 60
    echo ""
    echo "To use this environment:"
    echo "  source .venv_eval/bin/activate"
    echo ""
    echo "To run evaluation:"
    echo "  python evaluate_ragas.py"
    echo ""
    echo "To deactivate:"
    echo "  deactivate"
else
    echo ""
    echo "⚠️  Some packages failed verification."
    echo "Please check the output above and fix any issues."
fi
