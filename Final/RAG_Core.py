"""
RAG_Core.py
Unified RAG System Core - Single Source of Truth

Consolidates:
- streamlit_app.py (simple RAG with code focus)
- evaluation_only_rag_sys.py (simple RAG with PDFs)
- RAG-Fusion implementation (multi-query + RRF)

Features:
- Flexible configuration (simple RAG or RAG-Fusion)
- JSON + PDF processing
- Multiple LLM backends (Ollama, OpenAI)
- Consistent chunking and metadata
- Optional LangSmith tracing
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from operator import itemgetter

# LangChain core
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.load import dumps, loads

# Vector store and embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader

# LLM imports
try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    from langchain_community.llms import Ollama

# Optional: OpenAI
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Optional: LangSmith tracing
try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None):
        def decorator(func):
            return func
        return decorator


# ============================================================================
# CONFIGURATION - SINGLE SOURCE OF TRUTH
# ============================================================================

class RAGConfig:
    # Folder paths
    JSON_FOLDER = "/Users/cyrielvanhelleputte/Downloads/SCHOOL/Courses 2nd Semester/GenAI/chroma-db"           # Go UP one level
    PDF_FOLDER = "../data/raw/Materials_code_learning"
    CHROMA_DIR = "../chroma-db"              # NOTE: chroma-db (hyphen!)
    
    # Models
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    OLLAMA_MODEL = "llama3.2"
    
    # Processing settings
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 300
    
    # LLM settings
    LLM_TEMPERATURE = 0.3
    
    # Retrieval settings
    TOP_K = 5
    
    # RAG-Fusion settings
    USE_RAG_FUSION = False  # Set to True for multi-query + RRF
    RRF_K = 60  # Reciprocal rank fusion parameter
    NUM_QUERIES = 4  # Number of queries to generate
    
    # Default course name
    DEFAULT_COURSE = "Code Examples"
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]):
        """Update configuration from dictionary"""
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(cls, key, value)


# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================

@traceable(name="process_json_files")
def process_json_files(
    json_folder: str = None,
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[Document]:
    """
    Process JSON code files with smart chunking for code
    
    Args:
        json_folder: Path to JSON folder (default: RAGConfig.JSON_FOLDER)
        chunk_size: Chunk size (default: RAGConfig.CHUNK_SIZE)
        chunk_overlap: Chunk overlap (default: RAGConfig.CHUNK_OVERLAP)
    
    Returns:
        List of Document objects
    """
    json_folder = json_folder or RAGConfig.JSON_FOLDER
    chunk_size = chunk_size or RAGConfig.CHUNK_SIZE
    chunk_overlap = chunk_overlap or RAGConfig.CHUNK_OVERLAP
    
    json_path = Path(json_folder)
    if not json_path.exists():
        print(f"⚠️  JSON folder not found: {json_folder}")
        return []
    
    json_files = list(json_path.glob("*.json"))
    
    if len(json_files) == 0:
        print(f"⚠️  No JSON files found in {json_folder}")
        return []
    
    print(f"📁 Processing {len(json_files)} JSON code files...")
    all_chunks = []
    
    # Code-aware text splitter - preserves code structure
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\nclass ",    # Python classes
            "\n\ndef ",      # Python functions
            "\n\nfunction ", # R/JS functions
            "\n\n# ",        # Major comments
            "\n\n",          # Paragraphs
            "\n",            # Lines
            " ",
            ""
        ]
    )
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            content = data.get("content", "")
            if not content:
                continue
            
            # Detect language
            extension = data.get("extension", "").lower()
            language = "python" if extension in [".py", ".python"] else \
                      "r" if extension in [".r", ".R"] else "other"
            
            # Create Document with unified metadata
            doc = Document(
                page_content=content,
                metadata={
                    "source": data.get("name", json_file.stem),
                    "filename": json_file.name,
                    "extension": extension,
                    "language": language,
                    "course": data.get("course", RAGConfig.DEFAULT_COURSE),
                    "file_type": "code",
                }
            )
            
            # Split into chunks
            chunks = text_splitter.split_documents([doc])
            all_chunks.extend(chunks)
            
        except Exception as e:
            print(f"✗ Error processing {json_file.name}: {e}")
    
    print(f"✓ Processed {len(all_chunks)} code chunks from JSON files")
    return all_chunks


@traceable(name="process_pdfs")
def process_pdfs(
    pdf_folder: str = None,
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[Document]:
    """
    Process PDF lecture materials
    
    Args:
        pdf_folder: Path to PDF folder (default: RAGConfig.PDF_FOLDER)
        chunk_size: Chunk size (default: RAGConfig.CHUNK_SIZE)
        chunk_overlap: Chunk overlap (default: RAGConfig.CHUNK_OVERLAP)
    
    Returns:
        List of Document objects
    """
    pdf_folder = pdf_folder or RAGConfig.PDF_FOLDER
    chunk_size = chunk_size or RAGConfig.CHUNK_SIZE
    chunk_overlap = chunk_overlap or RAGConfig.CHUNK_OVERLAP
    
    pdf_path = Path(pdf_folder)
    
    if not pdf_path.exists():
        print(f"⚠️  PDF folder not found: {pdf_folder}")
        return []
    
    pdf_files = list(pdf_path.glob("**/*.pdf"))
    
    if len(pdf_files) == 0:
        print(f"⚠️  No PDF files found in {pdf_folder}")
        return []
    
    print(f"📁 Processing {len(pdf_files)} PDF files...")
    all_chunks = []
    
    # Text splitter for PDFs
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    for pdf_file in pdf_files:
        try:
            loader = PyMuPDFLoader(str(pdf_file))
            pages = loader.load()
            
            # Extract course from folder structure
            try:
                relative_path = pdf_file.relative_to(pdf_path)
                course = relative_path.parts[0] if len(relative_path.parts) > 1 else RAGConfig.DEFAULT_COURSE
            except:
                course = RAGConfig.DEFAULT_COURSE
            
            chunks = text_splitter.split_documents(pages)
            
            # Add unified metadata
            for chunk in chunks:
                chunk.metadata["course"] = course
                chunk.metadata["file_type"] = "pdf"
                chunk.metadata["source"] = pdf_file.stem
            
            all_chunks.extend(chunks)
            
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")
    
    print(f"✓ Processed {len(all_chunks)} chunks from PDF files")
    return all_chunks


# ============================================================================
# VECTOR STORE FUNCTIONS
# ============================================================================

def initialize_embeddings(model_name: str = None, use_openai: bool = False):
    """
    Initialize embeddings (HuggingFace or OpenAI)
    
    Args:
        model_name: Embedding model name
        use_openai: Use OpenAI embeddings instead of HuggingFace
    
    Returns:
        Embeddings object
    """
    if use_openai:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI not available. Install: pip install langchain-openai")
        model_name = model_name or "text-embedding-3-small"
        print(f"✓ Using OpenAI embeddings: {model_name}")
        return OpenAIEmbeddings(model=model_name)
    else:
        model_name = model_name or RAGConfig.EMBEDDING_MODEL
        print(f"✓ Using HuggingFace embeddings: {model_name}")
        return HuggingFaceEmbeddings(model_name=model_name)


def load_vectorstore(embeddings=None, chroma_dir: str = None):
    """
    Load existing ChromaDB vector store
    
    Args:
        embeddings: Embeddings object (default: initialize_embeddings())
        chroma_dir: ChromaDB directory (default: RAGConfig.CHROMA_DIR)
    
    Returns:
        Chroma vectorstore or None if not found
    """
    if embeddings is None:
        embeddings = initialize_embeddings()
    
    chroma_dir = chroma_dir or RAGConfig.CHROMA_DIR
    
    if not Path(chroma_dir).exists() or not list(Path(chroma_dir).glob("*")):
        print(f"⚠️  Vector store not found: {chroma_dir}")
        return None
    
    try:
        vectorstore = Chroma(
            persist_directory=chroma_dir,
            embedding_function=embeddings
        )
        
        # Check if it has documents
        count = vectorstore._collection.count()
        if count == 0:
            print("⚠️  Vector store is empty")
            return None
        
        print(f"✓ Loaded vector store with {count} documents from {chroma_dir}")
        return vectorstore
        
    except Exception as e:
        print(f"✗ Error loading vector store: {e}")
        return None


@traceable(name="create_vectorstore")
def create_vectorstore(
    include_pdfs: bool = True,
    rebuild: bool = False,
    embeddings=None,
    chroma_dir: str = None
) -> Tuple[Optional[Chroma], int, str]:
    """
    Create new ChromaDB vector store from source documents
    
    Args:
        include_pdfs: Whether to include PDF files (default: True)
        rebuild: Delete existing DB and rebuild (default: False)
        embeddings: Embeddings object (default: initialize_embeddings())
        chroma_dir: ChromaDB directory (default: RAGConfig.CHROMA_DIR)
    
    Returns:
        tuple: (vectorstore, number of chunks, status message)
    """
    chroma_dir = chroma_dir or RAGConfig.CHROMA_DIR
    
    # Handle rebuild
    if rebuild and Path(chroma_dir).exists():
        shutil.rmtree(chroma_dir, ignore_errors=True)
        print(f"🗑️  Deleted existing vector store: {chroma_dir}")
    
    print("\n🛠️  Creating new vector store...")
    
    # Process documents
    code_chunks = process_json_files()
    
    if include_pdfs:
        pdf_chunks = process_pdfs()
    else:
        pdf_chunks = []
        print("⚠️  Skipping PDF processing (include_pdfs=False)")
    
    all_documents = code_chunks + pdf_chunks
    
    if len(all_documents) == 0:
        return None, 0, "No documents found to process"
    
    # Create embeddings and vector store
    print(f"📦 Creating vector store with {len(all_documents)} total chunks...")
    if embeddings is None:
        embeddings = initialize_embeddings()
    
    vectorstore = Chroma.from_documents(
        documents=all_documents,
        embedding=embeddings,
        persist_directory=chroma_dir
    )
    
    count = vectorstore._collection.count()
    print(f"✅ Vector store created: {count} documents in {chroma_dir}")
    return vectorstore, count, "Success"


# ============================================================================
# SIMPLE RAG CHAIN (Original Implementation)
# ============================================================================

def setup_simple_rag_chain(
    vectorstore=None,
    temperature: float = None,
    model: str = None
) -> Optional[RetrievalQA]:
    """
    Initialize simple RAG chain (original implementation)
    
    Args:
        vectorstore: Optional pre-loaded vectorstore
        temperature: LLM temperature (default: RAGConfig.LLM_TEMPERATURE)
        model: Ollama model name (default: RAGConfig.OLLAMA_MODEL)
    
    Returns:
        RetrievalQA chain or None if initialization fails
    """
    # Load vectorstore if not provided
    if vectorstore is None:
        embeddings = initialize_embeddings()
        vectorstore = load_vectorstore(embeddings)
    
    if vectorstore is None:
        print("❌ Vector store not available. Please create it first.")
        return None
    
    # Initialize LLM
    temperature = temperature or RAGConfig.LLM_TEMPERATURE
    model = model or RAGConfig.OLLAMA_MODEL
    llm = Ollama(model=model, temperature=temperature)
    
    # Code-focused prompt template
    code_prompt_template = """You are an expert programming tutor helping students learn from code examples and course materials.

Your role:
- Explain code clearly and concisely
- Show practical examples from the provided context
- Break down complex concepts into simple steps
- Highlight best practices and common patterns
- Reference course materials when explaining concepts

Context (Code Examples and Materials):
{context}

Question: {question}

Answer (be concise and code-focused):"""
    
    PROMPT = PromptTemplate(
        template=code_prompt_template,
        input_variables=["context", "question"]
    )
    
    # Create retrieval chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": RAGConfig.TOP_K}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    print(f"✓ Simple RAG chain initialized (model: {model}, temp: {temperature})")
    return qa_chain


# ============================================================================
# RAG-FUSION CHAIN (Multi-query + Reciprocal Rank Fusion)
# ============================================================================

def reciprocal_rank_fusion(results: List[List], k: int = 60):
    """
    Reciprocal Rank Fusion: combines multiple ranked lists
    
    Args:
        results: List of lists of ranked documents
        k: RRF parameter (default: 60)
    
    Returns:
        List of (document, score) tuples, sorted by fused score
    """
    fused_scores = {}
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            fused_scores[doc_str] = fused_scores.get(doc_str, 0) + 1 / (rank + k)
    
    reranked = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]
    return reranked


def setup_rag_fusion_chain(
    vectorstore=None,
    temperature_query: float = 0.0,
    temperature_answer: float = None,
    model: str = None
):
    """
    Initialize RAG-Fusion chain (multi-query + RRF)
    
    Args:
        vectorstore: Optional pre-loaded vectorstore
        temperature_query: Temperature for query generation (default: 0.0)
        temperature_answer: Temperature for answer generation
        model: Ollama model name
    
    Returns:
        Dictionary with components: {
            'retrieval_chain': chain for retrieving fused docs,
            'final_chain': chain for generating final answer,
            'smart_ask': function for smart routing
        }
    """
    # Load vectorstore if not provided
    if vectorstore is None:
        embeddings = initialize_embeddings()
        vectorstore = load_vectorstore(embeddings)
    
    if vectorstore is None:
        print("❌ Vector store not available. Please create it first.")
        return None
    
    # Initialize LLMs
    model = model or RAGConfig.OLLAMA_MODEL
    temperature_answer = temperature_answer or RAGConfig.LLM_TEMPERATURE
    
    llm_query_gen = Ollama(model=model, temperature=temperature_query)
    llm_answer = Ollama(model=model, temperature=temperature_answer)
    
    # Multi-query generation prompt
    template_multi = """You are a thoughtful assistant helping to prepare document searches for a retrieval system.
Your goal is to generate {num_queries} diverse and semantically rich search queries 
that can retrieve all relevant pieces of information needed to answer the user question below.

When creating the queries:
- Include both direct keyword matches and rephrasings using synonyms or related terms.
- Add at least one reasoning-oriented query that may capture indirect or inferential context.
- Include one broad query that could return general background information if the question is open-ended.

Generate exactly {num_queries} queries (one per line).

User Question:
{{question}}
"""
    
    prompt_rag_fusion = ChatPromptTemplate.from_template(
        template_multi.format(num_queries=RAGConfig.NUM_QUERIES)
    )
    
    # Query generation chain
    generate_queries = (
        prompt_rag_fusion
        | llm_query_gen
        | StrOutputParser()
        | (lambda x: [q.strip() for q in x.split("\n") if q.strip()])
    )
    
    # Retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": RAGConfig.TOP_K})
    
    # RRF wrapper
    rrf = RunnableLambda(lambda res: reciprocal_rank_fusion(res, k=RAGConfig.RRF_K))
    
    # Retrieval chain: query-gen -> retriever.map() -> RRF
    retrieval_chain_rag_fusion = generate_queries | retriever.map() | rrf
    
    # Final answer prompt
    template_final = """You are a careful and knowledgeable assistant.
Use the following context to answer the user question. 

If the answer is clearly or reasonably implied by the context, explain it confidently in your own words.
If the context truly lacks relevant information, explicitly say:
"The uploaded documents do not contain that information. 
Based on general knowledge, here is what I can tell you:", 
and then continue with your best general answer.

Always separate the two parts clearly if you combine them.

Context (from retrieved documents):
{context}

Question:
{question}

Answer:"""
    
    prompt_final = ChatPromptTemplate.from_template(template_final)
    
    # Context formatting
    def format_context(fused_docs_with_scores, max_docs=8):
        lines = []
        for i, (doc, score) in enumerate(fused_docs_with_scores[:max_docs], 1):
            src = doc.metadata.get("source", "unknown")
            ftype = doc.metadata.get("file_type", "unknown")
            preview = doc.page_content[:300].replace("\n", " ")
            lines.append(f"[{i}] score={score:.4f} — {src} ({ftype})\n{preview}\n")
        return "\n".join(lines) if lines else "No context available."
    
    format_context_runnable = RunnableLambda(format_context)
    
    # Final chain
    final_rag_chain = (
        {
            "context": retrieval_chain_rag_fusion | format_context_runnable,
            "question": itemgetter("question"),
        }
        | prompt_final
        | llm_answer
        | StrOutputParser()
    )
    
    # Smart routing function
    def smart_ask(question: str, confidence_threshold: float = 0.01):
        """Smart router: RAG with fallback to general LLM knowledge"""
        fused = retrieval_chain_rag_fusion.invoke({"question": question})
        rag_answer = final_rag_chain.invoke({"question": question})
        
        # Check if context is relevant
        not_in_docs_flags = [
            "does not contain", "not found", "no information", "no mention",
            "not discussed", "not covered", "cannot find", "missing from"
        ]
        
        flag_detected = any(flag in rag_answer.lower() for flag in not_in_docs_flags)
        top_score = fused[0][1] if fused else 0
        low_confidence = top_score < confidence_threshold
        
        if flag_detected and low_confidence:
            # Fallback to general knowledge
            general_answer = llm_answer.invoke(
                f"The uploaded documents do not appear to contain relevant information for this question. "
                f"Please answer based on your own knowledge and say so clearly.\n\nQuestion: {question}"
            )
            return {
                "answer_type": "llm_general",
                "answer": general_answer,
                "confidence": top_score,
                "sources": []
            }
        else:
            return {
                "answer_type": "rag",
                "answer": rag_answer,
                "confidence": top_score,
                "sources": fused
            }
    
    print(f"✓ RAG-Fusion chain initialized (model: {model})")
    
    return {
        "retrieval_chain": retrieval_chain_rag_fusion,
        "final_chain": final_rag_chain,
        "smart_ask": smart_ask,
        "format_context": format_context
    }


# ============================================================================
# UNIFIED SETUP FUNCTION
# ============================================================================

def setup_rag_chain(
    use_fusion: bool = None,
    vectorstore=None,
    **kwargs
):
    """
    Unified RAG chain setup - automatically chooses simple or fusion
    
    Args:
        use_fusion: Use RAG-Fusion (default: RAGConfig.USE_RAG_FUSION)
        vectorstore: Optional pre-loaded vectorstore
        **kwargs: Additional arguments passed to specific setup function
    
    Returns:
        RAG chain (simple) or RAG-Fusion components (dict)
    """
    use_fusion = use_fusion if use_fusion is not None else RAGConfig.USE_RAG_FUSION
    
    if use_fusion:
        print("🔀 Setting up RAG-Fusion (multi-query + RRF)...")
        return setup_rag_fusion_chain(vectorstore=vectorstore, **kwargs)
    else:
        print("📝 Setting up Simple RAG...")
        return setup_simple_rag_chain(vectorstore=vectorstore, **kwargs)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_system_stats(vectorstore=None, chroma_dir: str = None):
    """
    Get statistics about the vector store
    
    Args:
        vectorstore: Optional vectorstore object
        chroma_dir: ChromaDB directory
    
    Returns:
        Dictionary with statistics
    """
    if vectorstore is None:
        embeddings = initialize_embeddings()
        chroma_dir = chroma_dir or RAGConfig.CHROMA_DIR
        vectorstore = load_vectorstore(embeddings, chroma_dir)
    
    if vectorstore is None:
        return {
            "status": "not_initialized",
            "total_documents": 0,
            "by_type": {},
            "by_language": {},
            "by_course": {}
        }
    
    try:
        collection = vectorstore._collection
        results = collection.get()
        
        total = len(results['metadatas'])
        by_type = {}
        by_language = {}
        by_course = {}
        
        for metadata in results['metadatas']:
            # Count by file type
            file_type = metadata.get('file_type', 'unknown')
            by_type[file_type] = by_type.get(file_type, 0) + 1
            
            # Count by language (for code files)
            if file_type == 'code':
                lang = metadata.get('language', 'unknown')
                by_language[lang] = by_language.get(lang, 0) + 1
            
            # Count by course
            course = metadata.get('course', 'unknown')
            by_course[course] = by_course.get(course, 0) + 1
        
        return {
            "status": "ready",
            "total_documents": total,
            "by_type": by_type,
            "by_language": by_language,
            "by_course": by_course
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def list_available_files(vectorstore=None):
    """
    List all files in the vector store
    
    Args:
        vectorstore: Optional vectorstore object
    
    Returns:
        Dictionary grouped by file type and language
    """
    if vectorstore is None:
        embeddings = initialize_embeddings()
        vectorstore = load_vectorstore(embeddings)
    
    if vectorstore is None:
        print("❌ Vector store not available")
        return {}
    
    try:
        collection = vectorstore._collection
        results = collection.get()
        
        files = {}
        for metadata in results['metadatas']:
            source = metadata.get('source', 'unknown')
            file_type = metadata.get('file_type', 'unknown')
            lang = metadata.get('language', 'unknown')
            
            if source not in files:
                files[source] = {
                    'type': file_type,
                    'language': lang,
                    'course': metadata.get('course', 'unknown')
                }
        
        # Group by type
        by_type = {}
        for source, info in files.items():
            ftype = info['type']
            if ftype not in by_type:
                by_type[ftype] = []
            by_type[ftype].append(source)
        
        return {
            'files': files,
            'by_type': by_type,
            'total': len(files)
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}


# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

# Export key variables for backward compatibility
JSON_FOLDER = RAGConfig.JSON_FOLDER
PDF_FOLDER = RAGConfig.PDF_FOLDER
CHROMA_DIR = RAGConfig.CHROMA_DIR
EMBEDDING_MODEL = RAGConfig.EMBEDDING_MODEL
OLLAMA_MODEL = RAGConfig.OLLAMA_MODEL

__all__ = [
    # Configuration
    'RAGConfig',
    # Data processing
    'process_json_files',
    'process_pdfs',
    # Vector store
    'initialize_embeddings',
    'load_vectorstore',
    'create_vectorstore',
    # RAG chains
    'setup_simple_rag_chain',
    'setup_rag_fusion_chain',
    'setup_rag_chain',  # Unified
    # Utilities
    'get_system_stats',
    'list_available_files',
    # Backward compatibility
    'JSON_FOLDER',
    'PDF_FOLDER',
    'CHROMA_DIR',
    'EMBEDDING_MODEL',
    'OLLAMA_MODEL',
]
