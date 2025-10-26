## CodeRAG

- **What it is**: RAG app to query your study code/PDFs with sources, for data science students.
- **LLM**: Ollama (default: `llama3.2`), OpenAI API
- **Embedding**: Qwen-Embedding-8b trough HuggingFace 
- **Vector DB**: Chroma.
- **Evaluation**: RAGAS
- **Data**: PDFs, code files and source materials from university courses.

### Requirements
- `requiremenets.txt`
- Ollama running (`ollama serve`), model pulled: `ollama pull llama3.2`.
- Enough computational power to support HuggingFace `Qwen/Qwen3-Embedding-8b` embedding model.
- Optional: OpenAI key for evaluation (`Final/Evaluation/.env`).

Specific requirement are tied to the RAG's evaluation.
For more information, please read `module/evaluation/README.md`.

### Quick Start (App)

For a quick start, you can run the command below to run the RAG on 2 prepared questions.

Beware that, since everything relied on your machine ressources, processing might take some time. 

```bash
python module/rag_core.py            # CLI test
```

Alternatively, you can also run the Streamlit app using the command below.

```
streamlit run Streamlit_App.py  # Web UI at http://localhost:8501
```

### Evaluate with RAGAS (optional)
```bash
cd Final/Evaluation
./setup_for_eval.sh           # creates venvs, generates responses.json, runs eval
```
Outputs: CSVs in `Final/Evaluation`.

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

The `module/evaluation/` folder contains code and instruction to run the RAG evaluation pipeline. 
`module/evaluation/setup_for_eval.sh` create a proper python virtual environnement that will be used for the evaluation and install the correct dependencies.
`module/evaluation/evaluation_only_rag_sys.py` is a script containing the RAG, while `module/evaluation/evaluate_ragas.py` is the evaluation script itself.
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
│   │   ├── README.md
│   │   ├── Evaluation_Dataset.py
│   │   ├── check_eval.py
│   │   ├── evaluate_ragas.py
│   │   ├── setup_for_eval_sh
│   │   ├── evaluation_only_rag_sys.py
├── chroma-db/ 
├── data/ 
│   ├── raw/ 
│   ├── parsed/ 
│   ├── evaluation_results/ 
```

##  Key Concepts

### Data Storage Architecture

The data used by the RAG system is readily embedding and preprecossed inside `chroma-db/`.

Alternatively,
Alternatively, `data/raw` and `data/parsed` contains files using at the different step of the indexing pipeline.
This folder has been kept for reproducability purposes only.
Be aware that files inside `data/raw` corresponds to a fraction of all files indexed inside `chroma-db/`

### Database Connection

The system connect to the ChromaDB using the `PersistentClient` class of the
`chromaDB` python library, wrapped inside a dedicated `Database` dataclass.
The Chroma database contains a single collection, named database, which contains all of our data.

```python
from module.indexing.database import Database

database = Database(client_path = "./chroma-db/")

database.client.get_collection(name="database")
```

##  Configuration

### RAGConfig Settings

Located in `Final/Rag_Core/RAG_Core.py` (around line 50):

```python
class RAGConfig:
    """Centralized configuration for RAG system"""

    # Folder paths
    JSON_FOLDER = "../parsed/"
    PDF_FOLDER = "../data/raw/Materials_code_learning"
    CHROMA_DIR = "./chroma-db/"

    # Models
    EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8b"
    OLLAMA_MODEL = "llama3.2"  # local LLM via Ollama

    # Processing settings
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 300

    # LLM settings
    LLM_TEMPERATURE = 0.3

    # Retrieval settings
    TOP_K = 5

    # RAG-Fusion settings
    USE_RAG_FUSION = True
    RRF_K = 60
    NUM_QUERIES = 4

    # Default course name
    DEFAULT_COURSE = "Code Examples"
```

### Customizing for Your Data

**If you want to use your own codebase:**

1. Scrape and parse PDFs, Python and R files, as well as Quarto document, Jupyter Notebook and RMarkdown into their JSON counterpart.

```bash
python3 module/indexing/data_collection.py [from] [course_name] [to]
```
*Note*: [course_name] argument is used as metadata information, nothing more.

2. Create your own persistent chroma database using `chromaDB` python library.

```python
import chromadb

client = chromadb.PersistentClient(path="/path/to/save/to")
```

3. Create a collection inside your newly created database

```
collection = client.create_collection(name="my_collection")
```

4. Use the `DataPreprocessor` class and its dedicated routes for each supported extensions to preprocess and index all the parsed JSON files inside your newly created database collection. As this process is chunking and embedding files locally, this might take some time.
```python
from module.indexing.database import Database
from module.indexing.preprocessing import DataPreprocessor

database = Database(client_path="/path/to/save/to")

path_files = [str(child) for child in Path("path/of/your/parsed/data").iterdir()]

preprocessor = DataPreprocessor(path_files, database, collection_name="my_collection")

preprocessor.prepare()
```

5. Access your newly created database using either the `chromaDB` library or the `Database` dataclass again.

```python
database = Database(client_path="/path/to/save/to")

database.client.list_collections()
database.client.get_collection(name="my_collection").count()
```

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

This problem often comes when the code cannot locate the Chroma database. 
In this case, please make sure that the specified database path is the correct one.
Consider using the absolue path for safety.

```bash
# Verify database exists
ls -la ./chroma-db/chroma.sqlite3

# Check file size (should be > 0)
du -h ./chroma-db/chroma.sqlite3
```

#### 3. Ollama Not Running

**Problem:** "Connection refused" or "Ollama not available"

**Solution:**

Verify that you started ollama and that 'Llama3.2' model is downloaded. 

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
streamlit run streamlit_app.py --server.port 8502

# Or kill existing process
lsof -ti:8501 | xargs kill -9
```

#### 5. Path Configuration Issues

**Problem:** "File not found" errors

**Solution:**

Make sure that the file path used are correct.
For any doubt, use the absolute file paths.

```python
# In RAG_Core.py, use relative paths:
JSON_FOLDER = "../data/parsed"
PDF_FOLDER = "../data/raw/Materials_code_learning"
CHROMA_DIR = "../chroma-db"
```

### Getting Help

If issues persist:
1. Check error messages carefully
2. Verify all paths are correct
3. Ensure Ollama is running
4. Check ChromaDB file exists and is not empty

If nothing works, consider contacting use via email.

------------------------------------------------------------------------

### System Components

1. **Embeddings** (Qwen/Qwen-Embedding-8b)
   - Converts text to 384-dimensional vectors
   - Enables semantic search
   - Cached for efficiency

2. **Vector Database** (ChromaDB)
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
