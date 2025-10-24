#!/usr/bin/env python3
import sys

def test_import(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False

print("🔍 SOLID EVAL SYSTEM CHECK")
print("=" * 40)

# Critical packages
critical = [
    "ragas",
    "langchain_openai", 
    "langchain_community",
    "langchain_core",
    "pandas",
    "tqdm",
    "datasets",
    "openai",
    "langchain-huggingface=",
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
if all_good:
    print("🎯 SOLID! Your evaluation system is ready.")
    print("Run: python evaluate_ragas.py")
else:
    print("Install missing packages and try again.")
    sys.exit(1)