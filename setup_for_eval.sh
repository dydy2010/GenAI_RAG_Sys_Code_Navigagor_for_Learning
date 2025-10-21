#!/bin/bash
echo "🎯 Setting up SOLID Evaluation System..."
python -m venv .venv_eval
source .venv_eval/bin/activate
pip install --upgrade pip

pip install ragas==0.1.8 langchain-openai==0.1.6 langchain-community==0.2.7 langchain-core==0.2.7 langchain-huggingface==0.0.2
pip install pandas==2.2.1 tqdm==4.66.1 datasets==2.18.0 openai==1.30.2 langsmith==0.1.c chromadb==0.4.24

echo "✅ Installation complete. Verifying..."
python check_eval.py

# Make it run:
# chmod +x setup_eval.sh
# ./setup_eval.sh