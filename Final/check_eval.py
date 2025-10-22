#!/usr/bin/env python3
"""
check_eval.py
Verifies evaluation environment is properly set up and rag_core is compatible
"""

import sys
from pathlib import Path

def test_import(name):
    """Test if a package can be imported"""
    try:
        __import__(name)
        return True
    except ImportError:
        return False

print("🔍 SOLID EVAL SYSTEM CHECK")
print("=" * 40)

# Critical packages for evaluation
critical = [
    "ragas",
    "langchain_openai", 
    "langchain_community",
    "langchain_core",
    "langchain_huggingface",
    "pandas",
    "tqdm",
    "datasets",
    "openai",
    "chromadb"
]

all_good = True
for package in critical:
    if test_import(package):
        print(f"✅ {package}")
    else:
        print(f"❌ {package}")
        all_good = False

print("=" * 40)

# Check for rag_core.py
rag_core_path = Path("RAG_Core.py")
if rag_core_path.exists():
    print(f"✅ rag_core.py found")
    
    # Try importing rag_core
    try:
        import rag_core
        print(f"✅ rag_core.py imports successfully")
        
        # Check for required functions
        required_functions = [
            'setup_rag_chain',
            'RAGConfig',
            'OLLAMA_MODEL',
            'EMBEDDING_MODEL'
        ]
        
        for func in required_functions:
            if hasattr(rag_core, func):
                print(f"✅ rag_core.{func} available")
            else:
                print(f"❌ rag_core.{func} missing")
                all_good = False
                
    except Exception as e:
        print(f"❌ Error importing rag_core: {e}")
        all_good = False
else:
    print(f"⚠️  rag_core.py not found in current directory")
    print(f"   Make sure you're running from project root")
    all_good = False

print("=" * 40)

# Check for evaluation files
eval_files = [
    "evaluation_only_rag_sys.py",
    "Evaluation_Dataset.py",
    "evaluate_ragas.py"
]

print("\n📁 Checking evaluation files:")
for file in eval_files:
    if Path(file).exists():
        print(f"✅ {file}")
    else:
        print(f"⚠️  {file} not found")

print("=" * 40)

# Check for data and database
data_checks = [
    ("./data/parsed", "JSON code files"),
    ("./data/raw/Materials_code_learning", "PDF lecture files"),
    ("./chroma_db", "Vector database")
]

print("\n💾 Checking data availability:")
for path, description in data_checks:
    p = Path(path)
    if p.exists():
        if p.is_dir():
            count = len(list(p.glob("*")))
            print(f"✅ {description}: {count} items in {path}")
        else:
            print(f"✅ {description}: {path} exists")
    else:
        print(f"⚠️  {description}: {path} not found")

print("=" * 40)

if all_good:
    print("\n🎯 SOLID! Your evaluation system is ready.")
    print("\nNext steps:")
    print("  1. Ensure Ollama is running: ollama serve")
    print("  2. Ensure vector database exists:")
    print("     python -c \"from rag_core import create_vectorstore; create_vectorstore()\"")
    print("  3. Run evaluation:")
    print("     python evaluate_ragas.py")
else:
    print("\n⚠️  Some issues detected. Please fix them before running evaluation.")
    sys.exit(1)
