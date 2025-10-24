"""
RAG_Core.py
Unified RAG System Core - Updated for LangChain 0.3+
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from operator import itemgetter

# LangChain Core
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.load import dumps, loads

# LangChain Community
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.llms import Ollama

# Text Splitters
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Optional imports
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langsmith import traceable
except ImportError:
    def traceable(name=None):
        def decorator(func):
            return func
        return decorator


# ============================================================================
# CONFIGURATION
# ============================================================================

class RAGConfig:
    """Centralized configuration for RAG system"""
    
    # Folder paths
    JSON_FOLDER = "../parsed"
    PDF_FOLDER = "../data/raw/Materials_code_learning"
    CHROMA_DIR = "the ABSOLUTE path of the unzipped chroma-db folder"
    
    # Models
    EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"
    OLLAMA_MODEL = "llama3.2"
    
    # Processing settings
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 300
    
    # LLM settings
    LLM_TEMPERATURE = 0.3
    
    # Retrieval settings
    TOP_K = 5
    
    # RAG-Fusion settings
    USE_RAG_FUSION = False
    RRF_K = 60
    NUM_QUERIES = 4
    
    # Default course name
    DEFAULT_COURSE = "Code Examples"


# Export commonly used values
OLLAMA_MODEL = RAGConfig.OLLAMA_MODEL
EMBEDDING_MODEL = RAGConfig.EMBEDDING_MODEL


# ============================================================================
# HELPER CLASSES
# ============================================================================

class ChainWrapper:
    """Wrapper to make custom chain compatible with expected interface"""

    def __init__(self, chain_func, retriever):
        self.chain_func = chain_func
        self.retriever = retriever

    def invoke(self, inputs):
        """Execute the chain and return results"""
        query = inputs.get("query", "")

        # NEW - WORKS WITH LANGCHAIN 0.3+:
        # Use invoke() instead of get_relevant_documents()
        try:
            source_documents = self.retriever.invoke(query)
        except AttributeError:
            # Fallback for older versions
            source_documents = self.retriever.get_relevant_documents(query)

        # Get answer
        answer = self.chain_func.invoke(query)

        return {
            "result": answer,
            "source_documents": source_documents
        }


# ============================================================================
# EMBEDDING FUNCTIONS
# ============================================================================

def initialize_embeddings(model_name: str = None) -> HuggingFaceEmbeddings:
    """Initialize HuggingFace embeddings"""
    if model_name is None:
        model_name = RAGConfig.EMBEDDING_MODEL
    
    print(f"✓ Using HuggingFace embeddings: {model_name}")
    return HuggingFaceEmbeddings(model_name=model_name)


# ============================================================================
# VECTOR STORE FUNCTIONS
# ============================================================================

def load_vectorstore(embeddings: HuggingFaceEmbeddings = None, 
                     persist_directory: str = None) -> Optional[Chroma]:
    """Load existing vector store"""
    if embeddings is None:
        embeddings = initialize_embeddings()
    
    if persist_directory is None:
        persist_directory = RAGConfig.CHROMA_DIR
    
    if not Path(persist_directory).exists():
        print(f"⚠️  Vector store not found at: {persist_directory}")
        return None
    
    try:
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name="database",
        )
        
        # Check if it has documents
        try:
            count = vectorstore._collection.count()
            if count == 0:
                print("⚠️  Vector store is empty")
                return None
            print(f"✓ Loaded vector store with {count} documents from {persist_directory}")
            return vectorstore
        except Exception as e:
            print(f"⚠️  Could not verify vector store contents: {e}")
            return vectorstore
            
    except Exception as e:
        print(f"❌ Error loading vector store: {e}")
        return None


def create_vectorstore(include_pdfs: bool = True, 
                      rebuild: bool = False) -> Tuple[Optional[Chroma], int, str]:
    """Create vector store from documents"""
    
    if rebuild and Path(RAGConfig.CHROMA_DIR).exists():
        print(f"🗑️  Removing existing vector store at {RAGConfig.CHROMA_DIR}")
        shutil.rmtree(RAGConfig.CHROMA_DIR)
    
    embeddings = initialize_embeddings()
    all_chunks = []
    
    # Process JSON files
    json_folder = Path(RAGConfig.JSON_FOLDER)
    if json_folder.exists():
        json_files = list(json_folder.glob("*.json"))
        print(f"📁 Processing {len(json_files)} JSON code files...")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                content = data.get('content', '')
                metadata = {
                    'source': data.get('file_name', str(json_file.name)),
                    'file_type': 'code',
                    'language': data.get('language', 'unknown')
                }
                
                doc = Document(page_content=content, metadata=metadata)
                all_chunks.append(doc)
                
            except Exception as e:
                print(f"⚠️  Error processing {json_file.name}: {e}")
        
        print(f"✓ Processed {len(all_chunks)} code chunks from JSON files")
    
    # Process PDFs
    if include_pdfs:
        pdf_folder = Path(RAGConfig.PDF_FOLDER)
        if pdf_folder.exists():
            pdf_files = list(pdf_folder.glob("*.pdf"))
            print(f"📁 Processing {len(pdf_files)} PDF files...")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=RAGConfig.CHUNK_SIZE,
                chunk_overlap=RAGConfig.CHUNK_OVERLAP
            )
            
            for pdf_file in pdf_files:
                try:
                    loader = PyMuPDFLoader(str(pdf_file))
                    documents = loader.load()
                    
                    for doc in documents:
                        doc.metadata['file_type'] = 'pdf'
                        doc.metadata['language'] = 'text'
                    
                    chunks = text_splitter.split_documents(documents)
                    all_chunks.extend(chunks)
                    
                except Exception as e:
                    print(f"⚠️  Error processing {pdf_file.name}: {e}")
            
            print(f"✓ Processed {len(all_chunks)} total chunks (including PDFs)")
    
    if not all_chunks:
        return None, 0, "No documents found to process"
    
    # Create vector store
    print(f"📦 Creating vector store with {len(all_chunks)} total chunks...")
    try:
        vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=embeddings,
            persist_directory=RAGConfig.CHROMA_DIR
        )
        
        print(f"✅ Vector store created: {len(all_chunks)} documents in {RAGConfig.CHROMA_DIR}")
        return vectorstore, len(all_chunks), "success"
        
    except Exception as e:
        return None, 0, f"Error creating vector store: {e}"


def get_system_stats(vectorstore: Chroma) -> Dict[str, Any]:
    """Get statistics about the vector store"""
    if vectorstore is None:
        return {"status": "not_initialized"}
    
    try:
        collection = vectorstore._collection
        results = collection.get()
        
        total_docs = len(results['ids'])
        
        # Count by type
        by_type = {}
        by_language = {}
        
        for metadata in results['metadatas']:
            ftype = metadata.get('file_type', 'unknown')
            lang = metadata.get('language', 'unknown')
            
            by_type[ftype] = by_type.get(ftype, 0) + 1
            if ftype == 'code':
                by_language[lang] = by_language.get(lang, 0) + 1
        
        return {
            "status": "ready",
            "total_documents": total_docs,
            "by_type": by_type,
            "by_language": by_language
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

def get_qa_prompt() -> PromptTemplate:
    """Get the QA prompt template"""
    template = """You are a helpful AI assistant for a coding and data science course. 
Use the following pieces of context to answer the question at the end. 
The context may include code examples, lecture notes, or documentation.

If you don't know the answer based on the context provided, just say that you don't know. 
Don't try to make up an answer.

When providing code examples, format them properly with syntax highlighting.
Be concise but thorough in your explanations.

Context:
{context}

Question: {query}

Helpful Answer:"""
    
    return PromptTemplate(template=template, input_variables=["context", "query"])


# ============================================================================
# CHAIN SETUP (UPDATED FOR LANGCHAIN 0.3+)
# ============================================================================

def setup_rag_chain(vectorstore: Chroma = None,
                   use_fusion: bool = None,
                   model: str = None,
                   temperature: float = None,
                   top_k: int = None):
    """
    Setup RAG chain using modern LangChain 0.3+ approach
    
    Args:
        vectorstore: Pre-loaded vector store (if None, will load from config)
        use_fusion: Whether to use RAG-Fusion (default from config)
        model: Ollama model name (default from config)
        temperature: LLM temperature (default from config)
        top_k: Number of documents to retrieve (default from config)
    
    Returns:
        Configured chain with invoke() method
    """
    # Load defaults from config
    if use_fusion is None:
        use_fusion = RAGConfig.USE_RAG_FUSION
    if model is None:
        model = RAGConfig.OLLAMA_MODEL
    if temperature is None:
        temperature = RAGConfig.LLM_TEMPERATURE
    if top_k is None:
        top_k = RAGConfig.TOP_K
    
    # Load vector store if not provided
    if vectorstore is None:
        print("📝 Loading vector store...")
        embeddings = initialize_embeddings()
        vectorstore = load_vectorstore(embeddings)
        
        if vectorstore is None:
            print("❌ Vector store not available. Please create it first.")
            return None
    
    # Initialize LLM
    print(f"📝 Setting up {'RAG-Fusion' if use_fusion else 'Simple RAG'}...")
    llm = Ollama(model=model, temperature=temperature)
    
    # Create retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    
    # Get prompt
    qa_prompt = get_qa_prompt()
    
    # Helper function to format documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Build the chain using modern LCEL syntax
    chain = (
        {
            "context": retriever | format_docs,
            "query": RunnablePassthrough()
        }
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    # Wrap to return both answer and source documents
    wrapped_chain = ChainWrapper(chain, retriever)
    
    print(f"✓ {'RAG-Fusion' if use_fusion else 'Simple RAG'} chain initialized (model: {model}, temp: {temperature})")
    return wrapped_chain


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("RAG Core Module - Testing")
    print("="*80)
    
    # Test configuration
    print("\n📋 Configuration:")
    print(f"  JSON Folder: {RAGConfig.JSON_FOLDER}")
    print(f"  PDF Folder: {RAGConfig.PDF_FOLDER}")
    print(f"  Chroma DB: {RAGConfig.CHROMA_DIR}")
    print(f"  Model: {RAGConfig.OLLAMA_MODEL}")
    
    # Test embeddings
    print("\n🧪 Testing embeddings...")
    embeddings = initialize_embeddings()
    print("✓ Embeddings loaded")
    
    # Test vector store
    print("\n🧪 Testing vector store...")
    vectorstore = load_vectorstore(embeddings)
    
    if vectorstore:
        stats = get_system_stats(vectorstore)
        print(f"✓ Vector store stats: {stats}")
        
        # Test chain
        print("\n🧪 Testing chain...")
        chain = setup_rag_chain(vectorstore=vectorstore)
        
        if chain:
            test_query = "How do I create a pandas DataFrame?"
            print(f"\nTest query: {test_query}")
            result = chain.invoke({"query": test_query})
            print(f"\nAnswer: {result['result'][:200]}...")
            print(f"Sources: {len(result['source_documents'])} documents")
        else:
            print("❌ Failed to create chain")
    else:
        print("❌ Vector store not available")
        print("\nTo create vector store, run:")
        print("  python -c 'from RAG_Core import create_vectorstore; create_vectorstore(include_pdfs=True)'")
    
    print("\n" + "="*80)
