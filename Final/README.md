---
editor_options: 
  markdown: 
    wrap: 72
---

# CodeRAG: The AI-Powered Code Navigator for Data Science Students

**CodeRAG** is an intelligent code navigation system designed to help
developers and data science students understand complex personal
educational codebases. Using Retrieval-Augmented Generation (RAG)
architecture, this tool allows users to ask questions about source code
in natural language and receive accurate, context-aware answers grounded
in their study materials.

------------------------------------------------------------------------

##  The Problem

Navigating large, messy learning materials for coding is a major
challenge for students. After semesters of accumulating materials, it becomes 
difficult to search for the exact code or lecture related to a specific
knowledge point. Current LLMs like ChatGPT cannot ingest all files and find 
precise university-specific context from lectures.

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

```
GenAI_RAG_Sys_Code_Navigator_for_Learning/
├── Final/
│   ├── Rag_Core/                      # Main application code
│   │   ├── module/                    # Reference: Data processing pipeline
│   │   │   ├── __init__.py           # Package initialization
│   │   │   ├── data_collection.py    # How data was collected (reference)
│   │   │   ├── database.py           # How DB was set up (reference)
│   │   │   └── preprocessing.py      # How data was preprocessed (reference)
│   │   ├── RAG_Core.py               # Main RAG system (connects to ChromaDB)
│   │   └── Streamlit_App.py          # Web interface
│   ├── Evaluation/                    # Evaluation scripts
│   │   ├── .env                      # API keys (CREATE THIS - not in git)
│   │   ├── Results/                  # Evaluation outputs
│   │   ├── check_eval.py             # Verification script
│   │   ├── Evaluate_Ragas.py         # Main RAGAS evaluation
│   │   ├── Evaluation_Dataset.py     # Dataset creation
│   │   ├── Evaluation_Only_RAG_Sys.py
│   │   ├── RAG_Core_Compat.py
│   │   └── requirements_eval.txt     # Evaluation dependencies
│   ├── data/
│   │   ├── chroma-db/                # LOCAL Vector database (PRIMARY)
│   │   │   ├── chroma.sqlite3       # Main database file
│   │   │   └── [UUID folders]       # Vector embeddings storage
│   │   ├── parsed/                   # Reference: Original JSON files
│   │   ├── raw/                      # PDFs and source materials
│   │   │   └── Materials_code_learning/
│   │   └── raw_data/                 # Additional raw data
│   └── README.md
├── docs/                              # Documentation
└── test_all_systems_v2.py            # System verification script
```

##  Key Concepts

### Data Storage Architecture

**Your data lives in TWO places:**

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

##  Quick Start for New Users

### Prerequisites

**Required:**
- Python 3.8+
- Ollama installed and running
- ~2GB disk space for ChromaDB

**Optional:**
- OpenAI API key (for evaluation only)
- PyCharm or VS Code (recommended)

### Step 1: Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download
```

Start Ollama:
```bash
ollama serve
```

Pull the model:
```bash
ollama pull llama3.2
```

### Step 2: Clone and Navigate

```bash
git clone [your-repo-url]
cd GenAI_RAG_Sys_Code_Navigator_for_Learning/Final/Rag_Core
```

### Step 3: Install Dependencies

```bash
# Core dependencies
pip install langchain langchain-core langchain-community
pip install langchain-text-splitters langchain-huggingface
pip install chromadb streamlit pandas numpy sentence-transformers

# Or use requirements file if available
pip install -r requirements.txt
```

### Step 4: Verify Database Connection

Before verifying the database, ensure you have downloaded the project ZIP file and extracted it locally. The ChromaDB files are included within this ZIP archive.

1. **Download the ZIP file**
   - Go to your repository or the provided project link.
   - Click on “Download ZIP” and extract it to a local folder.

2. **Locate the ChromaDB directory**
   - Inside the extracted folder, navigate to:
     ```
     Final/chroma-db/
     ```
   - This folder should contain the `chroma.sqlite3` database file and additional folders with UUIDs for vector embeddings.

3. **Establish the local connection**
   - In PyCharm, go to **View → Tool Windows → Database**.
   - Add a **new SQLite data source** and connect it to:
     ```
     Final/chroma-db/chroma.sqlite3
     ```
   - Test the connection to confirm it works.


**Database path configuration:**
- Open `RAG_Core.py`
- Find `RAGConfig` class (around line 55)
- Verify `CHROMA_DIR = "../chroma-db"` (relative path)
- Verify `JSON_FOLDER = "../data/parsed"` (for demos)

### Step 5: Test the System

```bash
# Test ChromaDB connection
python RAG_Core.py
```

Expected output:
```
✓ Using HuggingFace embeddings: sentence-transformers/all-MiniLM-L6-v2
✓ Loaded vector store with XXXX documents from ../chroma-db
✓ Vector store stats: {...}
✓ Test query successful
```

### Step 6: Launch Web Interface

```bash
streamlit run Streamlit_App.py
```

Open browser to: `http://localhost:8501`

You should see:
-  System Ready (green indicator)
- Document count displayed
- Chat interface ready

### Step 7: Ask Your First Question!

Try asking:
- "How do I create a pandas DataFrame?"
- "Show me examples of for loops in Python"
- "What is the difference between lists and tuples?"

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

## ️ Database Connection Setup

### Using PyCharm Database Tools

1. **Open Database Tool Window**
   - View → Tool Windows → Database
   - Or press `⌘ + Shift + A` and search "Database"

2. **Add Data Source**
   - Click `+` → Data Source → SQLite
   
3. **Configure Connection**
   - **Name:** `Chroma-db` (or any name)
   - **Driver:** SQLite
   - **File:** Browse to `Final/chroma-db/chroma.sqlite3`
   
   Example path:
   ```
   /Users/yourname/path/to/Final/chroma-db/chroma.sqlite3
   ```

4. **Test Connection**
   - Click "Test Connection"
   - Should show: "SQLite 3.45.1" or similar
   - Click "OK" to save

5. **Explore Database**
   - Expand connection → schemas → tables
   - You should see ChromaDB tables:
     - `collections`
     - `embeddings`
     - `metadata`
     - etc.

### Connection URL Format

```
jdbc:sqlite:/absolute/path/to/Final/chroma-db/chroma.sqlite3
```

### Troubleshooting Database Connection

**Issue:** "Database file is locked"
- **Solution:** Close Streamlit/RAG_Core if running
- SQLite allows only one writer at a time

**Issue:** "No such table: collections"
- **Solution:** ChromaDB not initialized properly
- Run `python RAG_Core.py` to verify

**Issue:** "File not found"
- **Solution:** Use absolute path
- Verify file exists: `ls -la Final/chroma-db/chroma.sqlite3`

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
```

### Individual Component Tests

```bash
cd Final/Rag_Core

# Test 1: ChromaDB connection
python -c "from RAG_Core import load_vectorstore, initialize_embeddings; \
           emb = initialize_embeddings(); \
           vs = load_vectorstore(emb); \
           print(f'✓ Connected: {vs._collection.count()} documents')"

# Test 2: Imports
python -c "from module import data_collection, database, preprocessing; \
           print('✓ All modules imported')"

# Test 3: Full system
python RAG_Core.py

# Test 4: Web interface
streamlit run Streamlit_App.py
```

------------------------------------------------------------------------

##  Evaluation with RAGAS

### Setup Evaluation Environment

1. **Get OpenAI API Key**
   - Visit: https://platform.openai.com/api-keys
   - Create new key (starts with `sk-`)

2. **Create .env File**
   ```bash
   cd Final/Evaluation
   echo "OPENAI_API_KEY=sk-your-key-here" > .env
   ```

3. **Install Evaluation Dependencies**
   PLEASE set up a SEPARATE .venv environment than the RAG environment,
   to avoid library version conflicts. You can name it .venv_eval.
   
   Please also see if you have python3 already installed in this environment.

   ```bash
   pip install -r requirements_eval.txt
   ```
   
   Or manually:
   ```bash
   pip install ragas langchain-openai openai datasets python-dotenv
   ```

4. **Verify Setup**
Please verify with this script if you have the correct setup. 

   ```bash
   python3 check_eval.py
   ```

### Run Evaluation

```bash
cd Final/Evaluation
python3 Evaluate_Ragas.py
```

This will:
1. Load your RAG system
2. Generate test questions (or use existing dataset)
3. Get answers from the system
4. Compute RAGAS metrics:
   - **Faithfulness** (hallucination check)
   - **Answer Relevancy** (question match)
   - **Context Precision** (retrieval quality)
   - **Context Recall** (completeness)
5. Save results to `Results/ragas_evaluation_results_[timestamp].csv`

### Understanding Results

**Good scores (0-1 scale):**
- Faithfulness: > 0.80
- Answer Relevancy: > 0.75
- Context Precision: > 0.70
- Context Recall: > 0.70

**Cost:** ~$0.05-0.10 for 10 questions (using GPT-3.5-turbo)

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

1. **Chat Interface**
   - Natural language queries
   - Streaming responses
   - Conversation history

2. **Source Attribution**
   - Toggle to show/hide sources
   - Code preview with syntax highlighting
   - File type and language tags

3. **System Status**
   - Document count
   - Model information
   - Database statistics

4. **Quick Actions**
   - List all files
   - Clear chat history
   - Rebuild index (if needed)

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

#### 6. Evaluation Setup Issues

**Problem:** "OpenAI API key not found"

**Solution:**
```bash
cd Final/Evaluation

# Create .env file
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-actual-key-here
EOF

# Verify
cat .env
```

### Getting Help

If issues persist:
1. Run: `python test_all_systems_v2.py`
2. Check error messages carefully
3. Verify all paths are correct
4. Ensure Ollama is running
5. Check ChromaDB file exists and is not empty

------------------------------------------------------------------------

##  Updating and Maintaining

### Adding New Data

**To add more code examples or PDFs:**

```bash
# 1. Add files to the appropriate directory
cp your_new_code.py Final/data/raw/Materials_code_learning/
cp your_lecture.pdf Final/data/raw/Materials_code_learning/

# 2. Rebuild the index (WARNING: overwrites existing data)
cd Final/Rag_Core
python -c "from RAG_Core import create_vectorstore; \
           create_vectorstore(include_pdfs=True, rebuild=True)"

# 3. Verify new documents
python RAG_Core.py
```

### Backing Up Your Database

```bash
# Create backup
cp -r Final/chroma-db Final/chroma-db.backup_$(date +%Y%m%d)

# Verify backup
ls -lh Final/chroma-db.backup_*
```

### Model Updates

**To use a different Ollama model:**

```bash
# 1. Pull new model
ollama pull mistral

# 2. Update RAG_Core.py
# Change: OLLAMA_MODEL = "llama3.2"
# To: OLLAMA_MODEL = "mistral"

# 3. Restart application
```

------------------------------------------------------------------------

##  Understanding the System

### Data Flow

```
User Query
    ↓
Streamlit_App.py / RAG_Core.py
    ↓
load_vectorstore() ─────→ Final/chroma-db/ (local SQLite)
    ↓                            ↓
Embedding Model                 Retrieve relevant chunks
    ↓                            ↓
Semantic Search ←────────────── Vector similarity
    ↓
Retrieved Context (top K documents)
    ↓
Ollama LLM (llama3.2)
    ↓
Generated Answer (grounded in context)
    ↓
Response to User
```

### System Components

1. **Embeddings** (sentence-transformers/all-MiniLM-L6-v2)
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

##  Data Format

### JSON Code Files (Reference)

```json
{
  "file_name": "example.py",
  "content": "def hello():\n    print('Hello World')",
  "language": "python",
  "course": "Python for Data Science",
  "week": 1
}
```

### PDF Files

Place PDFs in `Final/data/raw/Materials_code_learning/` with any structure:
```
Materials_code_learning/
├── Python for data science/
│   ├── week1/
│   │   └── lecture.pdf
│   └── week2/
└── Machine Learning 1/
    └── lesson1/
        └── slides.pdf
```

------------------------------------------------------------------------

##  Documentation

### Additional Resources

- **SIMPLE_FINAL_GUIDE.md** - Quick start guide
- **FINAL_UNDERSTANDING.md** - System architecture deep dive
- **EVALUATION_QUICK_START.md** - Evaluation setup
- **EVALUATION_SETUP_GUIDE.md** - Complete evaluation reference
- **test_all_systems_v2.py** - Verification script

### Project Links

- GitHub Repository: [your-repo-url]
- Documentation: See `docs/` folder
- Issue Tracker: [your-issues-url]

------------------------------------------------------------------------

##  Authors

- **Cyriel Van Helleputte**
- **Sever Alin Girardin**
- **Robin Ramiro Díez-Liébana**
- **Dongyuan Gao**

------------------------------------------------------------------------

##  Acknowledgments

This project was made possible by:

- **LangChain** - RAG framework and orchestration
- **Ollama** - Local LLM inference
- **ChromaDB** - Vector database storage
- **Streamlit** - Interactive web interface
- **HuggingFace** - Embedding models and transformers
- **RAGAS** - Evaluation framework

------------------------------------------------------------------------

##  License

This project is licensed under the MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.

------------------------------------------------------------------------

##  Support & Contact

### For Technical Issues

1. **Check troubleshooting section** above
2. **Run test suite:** `python test_all_systems_v2.py`
3. **Verify configuration:** Check `RAGConfig` in `RAG_Core.py`
4. **Database connection:** Verify ChromaDB exists and is accessible
5. **Open an issue** on GitHub with error details

### For Questions

- Check documentation in `docs/` folder
- Review code comments in source files
- See example usage in `RAG_Core.py`

### Performance Issues

- Reduce `TOP_K` for faster retrieval
- Use smaller embedding model
- Switch to lighter Ollama model
- Reduce `CHUNK_SIZE` for less memory usage

------------------------------------------------------------------------

##  Pre-Launch Checklist

Before deploying or demonstrating:

```
Setup:
[ ] Ollama installed and running
[ ] ollama pull llama3.2 completed
[ ] Python 3.8+ installed
[ ] All dependencies installed

Database:
[ ] ChromaDB exists at Final/chroma-db/
[ ] Database file not empty (>100MB typical)
[ ] Can connect via PyCharm/DBeaver
[ ] Document count > 0

Configuration:
[ ] RAG_Core.py paths are relative
[ ] CHROMA_DIR = "../chroma-db"
[ ] JSON_FOLDER = "../data/parsed"
[ ] PDF_FOLDER points to your materials

Testing:
[ ] test_all_systems_v2.py passes
[ ] python RAG_Core.py works
[ ] streamlit run Streamlit_App.py works
[ ] Can ask questions and get answers
[ ] Sources are displayed correctly

Evaluation (Optional):
[ ] .env file created in Final/Evaluation/
[ ] OpenAI API key configured
[ ] check_eval.py passes
[ ] Can run Evaluate_Ragas.py
```

------------------------------------------------------------------------

##  Quick Reference

### Essential Commands

```bash
# Start Ollama
ollama serve

# Run main application
cd Final/Rag_Core
python RAG_Core.py

# Launch web interface
streamlit run Streamlit_App.py

# Run tests
cd ../..
python test_all_systems_v2.py

# Run evaluation
cd Final/Evaluation
python check_eval.py
python Evaluate_Ragas.py
```

### Important File Locations

- **Main app:** `Final/Rag_Core/RAG_Core.py`
- **Web UI:** `Final/Rag_Core/Streamlit_App.py`
- **Database:** `Final/chroma-db/chroma.sqlite3`
- **Config:** `RAGConfig` class in `RAG_Core.py`
- **Tests:** `test_all_systems_v2.py`
- **Evaluation:** `Final/Evaluation/`

------------------------------------------------------------------------

**Version:** 1.0  
**Last Updated:** October 2025  
**Status:** Production Ready  
**Powered by:** LangChain 0.3+ | Ollama (llama3.2) | ChromaDB | Streamlit

---

*Happy coding and learning! 🚀*