"""
RAG_Core.py – Extended with RAG-Fusion (Multi-query retrieval), RRF merging, and fallback answers
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

# Embeddings (keep Qwen embedding model)
from langchain_huggingface import HuggingFaceEmbeddings

# Optional OpenAI imports
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


# Export commonly used values
OLLAMA_MODEL = RAGConfig.OLLAMA_MODEL
EMBEDDING_MODEL = RAGConfig.EMBEDDING_MODEL

# ============================================================================
# HELPER CLASSES
# ============================================================================


class ChainWrapper:
    """Wrapper to make custom chain compatible with expected interface (for simple RAG)"""

    def __init__(self, chain_func, retriever):
        self.chain_func = chain_func
        self.retriever = retriever

    def invoke(self, inputs: Dict[str, Any]):
        """Execute the chain and return results (for simple single-query retrieval)"""
        query = inputs.get("query", "")
        # Retrieve source docs (LangChain 0.3+ retriever uses invoke)
        try:
            source_documents = self.retriever.invoke(query)
        except AttributeError:
            source_documents = self.retriever.get_relevant_documents(query)
        # Get the answer from the chain
        answer = self.chain_func.invoke(query)
        return {"result": answer, "source_documents": source_documents}


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


def load_vectorstore(
    embeddings: HuggingFaceEmbeddings = None, persist_directory: str = None
) -> Optional[Chroma]:
    """Load existing vector store from disk"""
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
        # Check contents
        try:
            count = vectorstore._collection.count()
            if count == 0:
                print("⚠️  Vector store is empty")
                return None
            print(
                f"✓ Loaded vector store with {count} documents from {persist_directory}"
            )
            return vectorstore
        except Exception as e:
            print(f"⚠️  Could not verify vector store contents: {e}")
            return vectorstore
    except Exception as e:
        print(f"❌ Error loading vector store: {e}")
        return None


def create_vectorstore(
    include_pdfs: bool = True, rebuild: bool = False
) -> Tuple[Optional[Chroma], int, str]:
    """Create vector store from documents (code JSON and PDFs)"""
    if rebuild and Path(RAGConfig.CHROMA_DIR).exists():
        print(f"🗑️  Removing existing vector store at {RAGConfig.CHROMA_DIR}")
        shutil.rmtree(RAGConfig.CHROMA_DIR)
    embeddings = initialize_embeddings()
    all_chunks = []
    # Process JSON files (code snippets)
    json_folder = Path(RAGConfig.JSON_FOLDER)
    if json_folder.exists():
        json_files = list(json_folder.glob("*.json"))
        print(f"📁 Processing {len(json_files)} JSON code files...")
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                content = data.get("content", "")
                metadata = {
                    "source": data.get("file_name", str(json_file.name)),
                    "file_type": "code",
                    "language": data.get("language", "unknown"),
                }
                doc = Document(page_content=content, metadata=metadata)
                all_chunks.append(doc)
            except Exception as e:
                print(f"⚠️  Error processing {json_file.name}: {e}")
        print(f"✓ Processed {len(all_chunks)} code chunks from JSON files")
    # Process PDFs (if any)
    if include_pdfs:
        pdf_folder = Path(RAGConfig.PDF_FOLDER)
        if pdf_folder.exists():
            pdf_files = list(pdf_folder.glob("*.pdf"))
            print(f"📁 Processing {len(pdf_files)} PDF files...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=RAGConfig.CHUNK_SIZE, chunk_overlap=RAGConfig.CHUNK_OVERLAP
            )
            for pdf_file in pdf_files:
                try:
                    loader = PyMuPDFLoader(str(pdf_file))
                    documents = loader.load()
                    # Tag metadata
                    for doc in documents:
                        doc.metadata["file_type"] = "pdf"
                        doc.metadata["language"] = "text"
                    chunks = text_splitter.split_documents(documents)
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"⚠️  Error processing {pdf_file.name}: {e}")
            print(f"✓ Processed {len(all_chunks)} total chunks (including PDFs)")
    if not all_chunks:
        return None, 0, "No documents found to process"
    # Create and persist Chroma vector store
    print(f"📦 Creating vector store with {len(all_chunks)} total chunks...")
    try:
        vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=embeddings,
            persist_directory=RAGConfig.CHROMA_DIR,
        )
        print(
            f"✅ Vector store created: {len(all_chunks)} documents in {RAGConfig.CHROMA_DIR}"
        )
        return vectorstore, len(all_chunks), "success"
    except Exception as e:
        return None, 0, f"Error creating vector store: {e}"


def get_system_stats(vectorstore: Chroma) -> Dict[str, Any]:
    """Get statistics about the vector store contents"""
    if vectorstore is None:
        return {"status": "not_initialized"}
    try:
        collection = vectorstore._collection
        results = collection.get()
        total_docs = len(results["ids"])
        # Count by type/language
        by_type = {}
        by_language = {}
        for metadata in results["metadatas"]:
            ftype = metadata.get("file_type", "unknown")
            lang = metadata.get("language", "unknown")
            by_type[ftype] = by_type.get(ftype, 0) + 1
            if ftype == "code":
                by_language[lang] = by_language.get(lang, 0) + 1
        return {
            "status": "ready",
            "total_documents": total_docs,
            "by_type": by_type,
            "by_language": by_language,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# PROMPT TEMPLATES
# ============================================================================


def get_qa_prompt() -> PromptTemplate:
    """Prompt template for QA with context and fallback instructions"""
    template = """You are a careful, helpful, and knowledgeable AI assistant for a coding and data science course.
Use the following pieces of context to answer the user question.
If the answer is clearly or reasonably implied by the context, explain it confidently in your own words.
If the context truly lacks relevant information, explicitly say:
"The uploaded documents do not contain that information. 
Based on general knowledge, here is what I can tell you:",
and then continue with your best general answer.

Always separate the two parts clearly if you combine them.
When providing code examples, format them properly with syntax highlighting.
Be concise but thorough in your explanations.

Context:
{context}

Question: {query}

Answer:"""
    return PromptTemplate(template=template, input_variables=["context", "query"])


def get_multi_query_prompt(num_queries: int = None) -> ChatPromptTemplate:
    """Prompt template to generate multiple search queries for RAG-Fusion"""
    if num_queries is None:
        num_queries = RAGConfig.NUM_QUERIES
    template = f"""
You are a thoughtful assistant helping to prepare document searches for a retrieval system.

Your goal is to generate {num_queries} diverse and semantically rich search queries 
that can retrieve all relevant pieces of information needed to answer the user question below.

When creating the queries:
- Include both direct keyword matches and rephrasings using synonyms or related terms.
- Add at least one reasoning-oriented query that may capture indirect or inferential context.
- Include one broad query that could return general background information if the question is open-ended.

Generate exactly {num_queries} queries (one per line).

User Question:
{{question}}"""
    return ChatPromptTemplate.from_template(template)


# ============================================================================
# RAG-FUSION: Multi-Query + Reciprocal Rank Fusion utilities
# ============================================================================


def reciprocal_rank_fusion(
    results: List[List[Document]], k: int = None
) -> List[Tuple[Document, float]]:
    """Combine multiple ranked lists of Documents using Reciprocal Rank Fusion (RRF)."""
    if k is None:
        k = RAGConfig.RRF_K  # default damping factor
    fused_scores: Dict[str, float] = {}
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)  # serialize doc to string for use as key
            # accumulate RRF score: 1/(rank + k)
            fused_scores[doc_str] = fused_scores.get(doc_str, 0) + 1.0 / (rank + 1 + k)
    # Sort documents by combined score (higher is better)
    fused_list = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    # Deserialize the documents back from string and pair with score
    fused_results = [(loads(doc_str), score) for doc_str, score in fused_list]
    return fused_results


def format_fused_context(
    docs_with_scores: List[Tuple[Document, float]], max_docs: int = 8
) -> str:
    """Format fused documents and scores into a context string for the prompt."""
    if not docs_with_scores:
        return "No context available."
    lines = []
    for i, (doc, score) in enumerate(docs_with_scores[:max_docs], start=1):
        src = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", None)
        page_str = f" (page {page})" if page is not None else ""
        preview = doc.page_content[:300].replace("\n", " ")
        lines.append(f"[{i}] score={score:.4f} — {src}{page_str}\n{preview}\n")
    return "\n".join(lines)


class FusionChain:
    """Custom chain for RAG-Fusion: generates queries, retrieves docs, fuses results, and produces answer."""

    def __init__(self, retriever, llm_query, llm_answer):
        self.retriever = retriever  # vectorstore retriever (for individual queries)
        self.llm_query = llm_query  # LLM for query generation
        self.llm_answer = llm_answer  # LLM for final answer generation

    def invoke(self, inputs: Dict[str, Any]):
        query_text = inputs.get("query", "") or inputs.get("question", "")
        # 1. Generate multiple query variations using the query-generation LLM
        multi_prompt = get_multi_query_prompt()
        # Format the multi-query prompt with the user question
        prompt_value = multi_prompt.format_prompt(question=query_text)
        multi_queries = self.llm_query.invoke(
            prompt_value.to_messages()
        )  # LLM returns a string with queries
        if isinstance(multi_queries, str):
            # Split the LLM output by lines to get individual queries
            queries = [q.strip() for q in multi_queries.split("\n") if q.strip()]
        else:
            # In case the LLM returns list or other format, handle accordingly
            queries = []
        print(f"🔍 Generated {len(queries)} queries for fusion: {queries}")
        # 2. Retrieve top-k documents for each generated query
        all_results: List[List[Document]] = []
        for q in queries:
            try:
                docs = self.retriever.invoke(q)
            except AttributeError:
                docs = self.retriever.get_relevant_documents(q)
            all_results.append(docs or [])
        # 3. Fuse the results from all queries using RRF
        fused = reciprocal_rank_fusion(all_results)
        fused_docs_with_scores = fused  # list of (Document, score) sorted by relevance
        # Prepare source_documents list (just the Document objects) for return
        source_documents = [doc for doc, score in fused_docs_with_scores]
        # 4. Format context from top fused docs for the final prompt
        context_text = format_fused_context(fused_docs_with_scores, max_docs=8)
        # 5. Generate final answer using the answer LLM with the combined context
        qa_template = get_qa_prompt().template  # using the same QA prompt with fallback
        prompt_text = qa_template.format(context=context_text, query=query_text)
        answer = self.llm_answer.invoke(prompt_text)
        return {"result": answer, "source_documents": source_documents}


# ============================================================================
# CHAIN SETUP (with RAG-Fusion support)
# ============================================================================


def setup_rag_chain(
    vectorstore: Chroma = None,
    use_fusion: bool = None,
    model: str = None,
    temperature: float = None,
    top_k: int = None,
):
    """
    Setup the retrieval-augmented generation chain, either simple or with RAG-Fusion.

    Args:
        vectorstore: Pre-loaded vector store (if None, will attempt to load from config).
        use_fusion: Whether to use multi-query RAG-Fusion (default from config).
        model: Ollama model name (default from config).
        temperature: LLM temperature for final answer (default from config).
        top_k: Number of documents to retrieve per query (default from config).
    Returns:
        A chain object with an invoke() method that returns answer and source docs.
    """
    # Load defaults from config if not provided
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
    # Create retriever with specified top_k
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    if use_fusion:
        print("📝 Setting up RAG-Fusion (multi-query + RRF)...")
        # Initialize two LLM instances: one for query generation, one for answering
        llm_query_gen = Ollama(model=model, temperature=0.0)  # deterministic queries
        llm_answer = Ollama(
            model=model, temperature=temperature
        )  # final answer generation
        # Create the FusionChain with retriever and LLMs
        chain = FusionChain(
            retriever=retriever, llm_query=llm_query_gen, llm_answer=llm_answer
        )
        print(f"✓ RAG-Fusion chain initialized (model: {model}, temp: {temperature})")
        return chain
    else:
        print("📝 Setting up Simple RAG (single-query)...")
        llm = Ollama(model=model, temperature=temperature)
        qa_prompt = get_qa_prompt()  # prompt includes fallback handling

        # Define how to format retrieved docs into the prompt context
        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(doc.page_content for doc in docs)

        # Build the LangChain expression chain
        chain = (
            {"context": retriever | format_docs, "query": RunnablePassthrough()}
            | qa_prompt
            | llm
            | StrOutputParser()
        )
        wrapped_chain = ChainWrapper(chain, retriever)
        print(f"✓ Simple RAG chain initialized (model: {model}, temp: {temperature})")
        return wrapped_chain


# ============================================================================
# MAIN (Testing)
# ============================================================================

if __name__ == "__main__":
    print("RAG Core Module - Testing Extended Features")
    print("=" * 80)
    # Test configuration
    print("\n📋 Configuration:")
    print(f"  JSON Folder: {RAGConfig.JSON_FOLDER}")
    print(f"  PDF Folder: {RAGConfig.PDF_FOLDER}")
    print(f"  Chroma DB: {RAGConfig.CHROMA_DIR}")
    print(f"  Embedding Model: {RAGConfig.EMBEDDING_MODEL}")
    print(f"  LLM Model: {RAGConfig.OLLAMA_MODEL}")
    # Initialize embeddings and load vector store
    print("\n🧪 Testing embeddings and vector store...")
    embeddings = initialize_embeddings()
    vectorstore = load_vectorstore(embeddings)
    if vectorstore:
        stats = get_system_stats(vectorstore)
        print(f"✓ Vector store stats: {stats}")
        # Setup chain (toggle RAG_Fusion via config or override)
        print("\n🧪 Testing chain setup...")
        chain = setup_rag_chain(vectorstore=vectorstore)
        if chain:
            # Example query tests
            test_query_1 = "How do I create a pandas DataFrame?"
            test_query_2 = (
                "How do you create a boxplot for different species using seaborn?"
            )
            for q in [test_query_1, test_query_2]:
                print(f"\nQuestion: {q}")
                result = chain.invoke({"query": q})
                answer = result["result"]
                print(
                    f"Answer:\n{answer[:300]}..."
                )  # print first 300 chars of answer for brevity
                print(f"Sources used: {len(result['source_documents'])} documents")
        else:
            print("❌ Failed to create chain")
    else:
        print("❌ Vector store not available. Run create_vectorstore() first.")
    print("\n" + "=" * 80)
