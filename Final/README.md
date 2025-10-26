## CodeRAG

- **What it is**: RAG app to query your study code/PDFs with sources, for data science students.
- **LLM**: Ollama (default: `llama3.2`), Qwen, OpenAI API
- **Vector DB**: Chroma .
- **Evaluation**: RAGAS
- **Data**: PDFs and source materials from university courses.

### Requirements
- Python, Ollama running (`ollama serve`), model pulled: `ollama pull llama3.2`.
- Optional: OpenAI key for evaluation (`Final/Evaluation/.env`).

### Quick Start (App)
```bash
cd Final/Rag_Core
python RAG_Core.py            # CLI test
streamlit run Streamlit_App.py  # Web UI at http://localhost:8501
```

### Evaluate with RAGAS (optional)
```bash
cd Final/Evaluation
./setup_for_eval.sh           # creates venvs, generates responses.json, runs eval
```
Outputs: CSVs in `Final/Evaluation`.

### Data paths (relative to Final/)
- Vector store: `data/chroma_db` (Rag_Core uses `../chroma-db`)
- Parsed JSON: `data/parsed`
- PDFs: `data/raw/Materials_code_learning`

GitHub: https://github.com/dydy2010/GenAI_RAG_Sys_Code_Navigagor_for_Learning

# CodeRAG: The AI-Powered Code Navigator for Data Science Students

**CodeRAG** is an intelligent code navigation system designed to help developers and data science students understand complex personal
educational codebases. Using Retrieval-Augmented Generation (RAG)
architecture, this tool allows users to ask questions about source code in natural language and receive accurate, context-aware answers grounded in their study materials.

------------------------------------------------------------------------

##  The Problem

Navigating large, messy learning materials for coding is a major
challenge for students. After semesters of accumulating materials, it becomes difficult to search for the exact code or lecture related to a specific knowledge point. Current LLMs like ChatGPT cannot ingest all files and find precise university-specific context from lectures.

Students waste time manually piecing together information, slowing
down their learning process.

##  Our Solution: CodeRAG

CodeRAG solves this problem by providing a conversational interface to
your codebase. Instead of manually searching, you can simply **ask**.

Our system works in several phases:

1.  **Data Collection:** Scans your defined directory and collects all the
    files you want to include for studying (Python files, Jupyter notebooks,
    PDFs, etc.).

2.  **Preprocessing & Indexing:** The entire codebase is parsed, broken into 
    chunks, and converted into vector embeddings using sentence transformers. 
    This creates a searchable knowledge base stored in a ChromaDB vector database.

3.  **Query and Retrieval:** When you ask a question, CodeRAG finds the
    most relevant code chunks from the knowledge base using semantic search.

4.  **Generation:** The retrieved context, along with your question, is fed 
    to a Large Language Model (LLM). The LLM generates a comprehensive answer 
    based *specifically* on your code context. Works locally with Ollama models 
    (llama3.2, etc.).

5.  **Evaluation:** We developed a RAGAS-based evaluation system to test RAG 
    performance on metrics like faithfulness, answer relevancy, and context 
    precision.

------------------------------------------------------------------------

##  Project Structure

This `module/` subfolder contains the python code used at each step of the pipeline, as well as the streamlit application `module/streamlit_app.py`. Most notably, `module/rag_core.py` is the main script that runs the RAG system, `module/indexing/` is a sub-folder containins classes and script relevant to the RAG's indexing section. More specifically, `module/indexing/data_collection.py` is a python script that, given specified directories, scrapes for all '.py', '.R', '.ipynb', '.qmd', '.Rmd' and '.pdf' file, collects content and metadata, and finally stores this information inside a JSON file. 
`module/indexing/database.py` contains classes pertaining to establishing the connection with the Chroma Database `chroma-db/` and writing information to it.

The `chroma-db/` folder contains the vectorized database used throughout the project.

The `data/` folder contains the `raw` and `parsed` data.
Raw data refers to python, R, Jupyter Notebook, Quarto, RMarkdown document, as well as PDF of the same format. Parsed data refers to JSON files constructed using raw data content and metadata information.
Additionnaly, this folder also contains the `evaluation_results` of the evaluation pipeline, found in `module/evaluation/`.

`requirements.txt` contains the project's dependencies.
Be aware that, due to dependencies conflicts, the RAG's evaluation have its own set of dependencies to set up using `module/evaluation/setup_for_eval.sh`

```
GenAI_RAG_Sys_Code_Navigator_for_Learning/
├── README.md
├── requirement.txt
├── module/ 
│   ├── __init__.py
│   ├── rag_core.py
│   ├── streamlit_app.py
│   ├── indexing/
│   │   ├── __init__.py/
│   │   ├── data_collection.py
│   │   ├── preprocessing.py
│   │   ├── database.py
│   ├── evaluation/
│   ├── README.md 
│   ├── Evaluation_Dataset.py 
│   ├── check_eval.py 
│   ├── evaluate_ragas.py 
│   ├── setup_for_eval.sh 
│   ├── evaluation_only_rag_sys.sh 
├── chroma-db/ 
├── data/ 
│   ├── raw/ 
│   ├── parsed/ 
│   ├── evaluation_results/ 
```

##  Key Concepts

### Data Storage Architecture

**Data lives in TWO places:**

1. **PRIMARY: Local ChromaDB** (`Final/chroma-db/`)
   - Main production database
   - Contains all processed JSON embeddings
   - Accessed via SQLite connection
   - **This is what the system uses by default**

2. **BACKUP: GitHub Repository**
   - Demonstration/backup copy
   - Used if local DB connection fails
   - Suboptimal for performance
   - Acts as fallback

### Database Connection

The system connects to ChromaDB using a **local SQLite connection**:

```
File: /Users/[username]/path/to/Final/chroma-db/chroma.sqlite3
URL: jdbc:sqlite:/Users/[username]/path/to/Final/chroma-db/chroma.sqlite3
Driver: SQLite
```

You can connect to this database using:
- **PyCharm Database Tools** (see screenshot reference)
- **DBeaver** or other database clients
- **Python code** (via ChromaDB client)

### Module Folder Purpose

⚠ **IMPORTANT:** The `Final/Rag_Core/module/` folder is **REFERENCE ONLY**

- Contains scripts showing how data was originally processed
- **Already executed** - do not run these again
- Data is already in ChromaDB
- Kept for documentation and understanding the pipeline

------------------------------------------------------------------------

##  Configuration

### RAGConfig Settings

Located in `Final/Rag_Core/RAG_Core.py` (around line 50):

```python
class RAGConfig:
    """Centralized configuration for RAG system"""
    
    # Folder paths (relative to Rag_Core directory)
    JSON_FOLDER = "../data/parsed"        # Reference JSONs (demo)
    PDF_FOLDER = "../data/raw/Materials_code_learning"  # Source PDFs
    CHROMA_DIR = "../chroma-db"          # Vector database (IMPORTANT!)
    
    # Models
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    OLLAMA_MODEL = "llama3.2"            # Change to your preferred model
    
    # Processing settings (only for rebuilding)
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 300
    
    # LLM settings
    LLM_TEMPERATURE = 0.3                # Lower = more deterministic
    
    # Retrieval settings
    TOP_K = 5                            # Number of documents to retrieve
```

### Customizing for Your Data

**If you want to use your own codebase:**

1. **Add your files** to `Final/data/raw/Materials_code_learning/`
2. **Process them** (if needed):
   ```python
   from RAG_Core import create_vectorstore
   vectorstore, count, status = create_vectorstore(
       include_pdfs=True, 
       rebuild=True
   )
   ```
3. **Verify** new embeddings:
   ```bash
   python RAG_Core.py
   ```

**⚠ Warning:** Rebuilding will overwrite your existing ChromaDB!


------------------------------------------------------------------------

##  Testing & Verification

### Quick System Check

```bash
# From project root
python test_all_systems_v2.py
```

This verifies:
- ✅ Directory structure
- ✅ File existence
- ✅ Python syntax
- ✅ Module imports
- ✅ Dependencies
- ✅ Database files
- ✅ Data files
- ✅ Configuration paths

Expected result:
```
============================================================
TEST SUMMARY
============================================================
Passed: 40-45
Failed: 0
Warnings: 2-5 (only minor/optional)

ALL SYSTEMS OPERATIONAL ✓
============================================================

##  Evaluation with RAGAS

### Please refer to the Evaluation/README.MD for detailed instructions.


------------------------------------------------------------------------

##  Usage Examples

### Command Line Interface

```python
from RAG_Core import setup_rag_chain, load_vectorstore, initialize_embeddings

# Initialize system
embeddings = initialize_embeddings()
vectorstore = load_vectorstore(embeddings)
chain = setup_rag_chain(vectorstore)

# Ask questions
result = chain.invoke({"query": "How do I use list comprehension?"})
print(result['result'])
print(f"Sources: {len(result['source_documents'])}")
```

### Web Interface Features
**Chat Interface**


------------------------------------------------------------------------

##  Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'module'`

**Solution:**
```bash
cd Final/Rag_Core
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python RAG_Core.py
```

#### 2. ChromaDB Connection Failed

**Problem:** "Vector store not available"

**Solution:**
```bash
# Verify database exists
ls -la Final/chroma-db/chroma.sqlite3

# Check file size (should be > 0)
du -h Final/chroma-db/chroma.sqlite3

# Test connection
cd Final/Rag_Core
python -c "from RAG_Core import load_vectorstore, initialize_embeddings; \
           load_vectorstore(initialize_embeddings())"
```

#### 3. Ollama Not Running

**Problem:** "Connection refused" or "Ollama not available"

**Solution:**
```bash
# Start Ollama
ollama serve

# Verify model is downloaded
ollama list

# Pull model if missing
ollama pull llama3.2
```

#### 4. Streamlit Won't Start

**Problem:** Port already in use

**Solution:**
```bash
# Use different port
streamlit run Streamlit_App.py --server.port 8502

# Or kill existing process
lsof -ti:8501 | xargs kill -9
```

#### 5. Path Configuration Issues

**Problem:** "File not found" errors

**Solution:**
```python
# In RAG_Core.py, use relative paths:
JSON_FOLDER = "../data/parsed"
PDF_FOLDER = "../data/raw/Materials_code_learning"
CHROMA_DIR = "../chroma-db"

# Always run from: Final/Rag_Core/
```

### Getting Help

If issues persist:
1. Run: `python test_all_systems_v2.py`
2. Check error messages carefully
3. Verify all paths are correct
4. Ensure Ollama is running
5. Check ChromaDB file exists and is not empty


------------------------------------------------------------------------

### System Components

1. **Embeddings** (sentence-transformers/all-MiniLM-L6-v2/Qwen)
   - Converts text to 384-dimensional vectors
   - Enables semantic search
   - Cached for efficiency

2. **Vector Database** (ChromaDB + SQLite)
   - Stores document embeddings
   - Enables fast similarity search
   - Persists on disk

3. **Retriever**
   - Finds top K similar documents
   - Uses cosine similarity
   - Returns context for LLM

4. **LLM** (Ollama llama3.2)
   - Generates answers
   - Grounded in retrieved context
   - Runs locally (no API costs)

5. **Interface** (Streamlit)
   - User-friendly chat UI
   - Real-time responses
   - Source attribution

------------------------------------------------------------------------

##  Future Improvements

### Possible Implementations

1. **Query Enhancement**
   - Query expansion with synonyms
   - Sub-question decomposition
   - Multi-step reasoning

2. **Improved Retrieval**
   - Re-ranking with cross-encoders
   - Hybrid search (dense + sparse)
   - Contextual compression

3. **Enhanced Evaluation**
   - BERTScore integration
   - Expanded test datasets
   - Custom evaluation metrics
   - A/B testing framework

4. **UI Improvements**
   - Dark mode
   - Export conversations
   - Advanced filters
   - Multi-language support

5. **Performance**
   - Batch processing
   - Caching layer
   - Async operations
   - GPU acceleration

### Contributing

We welcome contributions! Areas we need help with:
- Expanding test datasets
- Improving prompts
- Adding new evaluation metrics
- UI/UX enhancements
- Documentation

------------------------------------------------------------------------

##  Authors

- **Cyriel Van Helleputte**
- **Sever Alin Girardin**
- **Robin Ramiro Díez-Liébana**
- **Dongyuan Gao**


------------------------------------------------------------------------

##  License

This project is licensed under the MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.

*Learned a lot in GenAI! 🚀*
