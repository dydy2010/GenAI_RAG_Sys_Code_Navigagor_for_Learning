"""
RAG-Fusion (Multi-query + Reciprocal Rank Fusion)

OpenAI Chat + OpenAI Embeddings + Chroma + RAG-Fusion (Multi-query + Reciprocal Rank Fusion)

Prerequisites:
- pip install:
  langchain langchain-community langchain-openai chromadb pymupdf
  sentence-transformers  # (only if you later want HF embeddings)
  langsmith

Notes:
  * Ollama  -> OpenAI Chat (gpt-4o-mini by default)
  * HF embeddings -> OpenAI embeddings (text-embedding-3-small)
  * RetrievalQA -> Query expansion + Reciprocal Rank Fusion + final answer
"""

# Setup Environment Variables

import os

os.environ["LANGCHAIN_PROJECT"] = 'RAG-project'

# --- LangSmith tracing ---

os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ["LANGCHAIN_API_KEY"] = 'your key'


# --- OpenAI key  ---

# os.environ["OPENAI_API_KEY"] = "sk-abcd1234efgh5678abcd1234efgh5678abcd1234"  

#if os.getenv("OPENAI_API_KEY"):
#    print("✓ OpenAI API key detected")
#else:
#    print("⚠️  OpenAI API key not found. Please set OPENAI_API_KEY")

# LangSmith convenience print
if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    print("✓ LangSmith tracing enabled")
else:
    print("ℹ️ LangSmith tracing is disabled (optional)")


# === Imports ===

import json
from pathlib import Path
from typing import List, Dict, Any
from operator import itemgetter

# Text & vector
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# LLM (Ollama local)
from langchain_community.llms import Ollama

# Prompts / RAG building
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.load import dumps, loads

# ----  OpenAI imports ----
from langchain_openai import OpenAIEmbeddings


#rint("Libraries imported (HF + Ollama mode)")



try:
    from langsmith import traceable
except Exception:
    # Fallback no-op decorator
    def traceable(*args, **kwargs):
        def _decorator(fn):
            return fn
        return _decorator

print("Libraries imported")


# --- Test llama LLM connection ---

from langchain_community.llms import Ollama


# Test if LangChain can talk to Ollama
llm = Ollama(model="llama3.2")
response = llm.invoke("Hello!")
print(response)

# --- Test OpenAI LLM connection ---

#from langchain_openai import ChatOpenAI
#import os

# ----- Initialize OpenAI chat model - API KEY PROVIDED AT THE TOP

#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ----- Test a simple prompt

#response = llm.invoke("Hello! Please confirm that OpenAI connection is working.")
#print(response)


# Configuration ---------------------------------

PARSED_JSON_FOLDER = "./parsed_json"   # folder for pre-parsed JSON notes (optional)
PDF_FOLDER         = "./raw_data"          # folder containing your PDFs
CHROMA_DIR         = "./chroma_db"     # Chroma persistence directory

# Embedding model & LLMs (OpenAI)-------------------------

# EMBEDDING_MODEL = "text-embedding-3-small"  # or "text-embedding-3-large"
# LLM_QUERY_MODEL = "gpt-4o-mini"             # for query expansion
# LLM_ANSWER_MODEL = "gpt-4o-mini"            # for final answering


# Retrieval / chunking params
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 5  # top-k per query

print("Config loaded")

# --- Current Free Version (Hugging Face) ----------------------

from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
print(f"Embeddings model loaded: {EMBEDDING_MODEL}")


# Initialize Embeddings (OpenAI)------------------

#embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
#print(f"Embeddings model loaded: {EMBEDDING_MODEL}")


# Process JSON Files (optional) - With LangSmith Tracing --------------------

@traceable(name="process_json_files")
def process_json_folder(folder: str) -> List[Dict[str, Any]]:
    path = Path(folder)
    if not path.exists():
        print(f"ℹ️  JSON folder '{folder}' not found. Skipping.")
        return []

    docs = []
    for fp in path.glob("**/*.json"):
        try:
            data = json.loads(Path(fp).read_text(encoding="utf-8"))
            if isinstance(data, dict):
                content = json.dumps(data, indent=2)
            else:
                content = str(data)

            doc = {
                "page_content": content,
                "metadata": {
                    "source": str(fp),
                    "file_type": "json",
                    "course": "N/A",
                }
            }
            docs.append(doc)
        except Exception as e:
            print(f"⚠️ Failed to parse {fp}: {e}")

    # chunk
    if docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=["\n\n", "\n", " "]
        )
        # convert to LC Document objects
        from langchain_core.documents import Document
        lc_docs = [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in docs]
        return text_splitter.split_documents(lc_docs)
    return []


json_chunks = process_json_folder(PARSED_JSON_FOLDER)
print(f"✅ JSON chunks: {len(json_chunks)}")


# Process PDFs - With LangSmith Tracing -----------------------------------------

@traceable(name="process_pdfs")
def process_pdfs(folder: str):
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"ℹ️  PDF folder '{folder}' not found. Skipping.")
        return []

    from langchain_core.documents import Document
    all_docs = []
    for pdf in folder_path.glob("**/*.pdf"):
        try:
            loader = PyMuPDFLoader(str(pdf))
            pages = loader.load()
            for d in pages:
                # Ensure metadata parity with your structure
                d.metadata.setdefault("source", str(pdf))
                d.metadata.setdefault("file_type", "pdf")
                d.metadata.setdefault("course", "N/A")
            all_docs.extend(pages)
        except Exception as e:
            print(f"⚠️  Failed to load {pdf}: {e}")

    if not all_docs:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=["\n\n", "\n", " "]
    )
    return text_splitter.split_documents(all_docs)


pdf_chunks = process_pdfs(PDF_FOLDER)
print(f"✅ PDF chunks: {len(pdf_chunks)}")


# ⚠️ This will delete the existing database --------------------------

REBUILD_DB = True  # set True if you want to refresh from scratch

import shutil

if REBUILD_DB:
    shutil.rmtree(CHROMA_DIR, ignore_errors=True)
    print("Old ChromaDB deleted — fresh build will follow.")
else:
    print("📂 Reusing existing ChromaDB (no duplication).")

# Create Chroma Vector Store - With Tracing -----------------------------------

@traceable(name="build_chroma")
def build_vectorstore(chunks):
    if not chunks:
        print("⚠️  No chunks provided to vectorstore.")
        return None
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    #vectordb.persist() - not needed in the new Chroma DB saves automatically
    print("✅ Chroma vectorstore built and persisted")
    return vectordb

all_chunks = (json_chunks or []) + (pdf_chunks or [])
vectorstore = build_vectorstore(all_chunks) if all_chunks else None
retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K}) if vectorstore else None




# Setup RAG Chain (OpenAI) with RAG-Fusion: Multi-query + Reciprocal Rank Fusion-----

# --- Current Free Version (Ollama) ---
llm_query_gen = Ollama(model="llama3.2", temperature=0.0)
llm_answer    = Ollama(model="llama3.2", temperature=0.7)

# --- (OpenAI) ---
# llm_query_gen = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# llm_answer    = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)



# ---- Multi-query generation prompt ----
template_multi = """
You are a thoughtful assistant helping to prepare document searches for a retrieval system.

Your goal is to generate 4 diverse and semantically rich search queries 
that can retrieve all relevant pieces of information needed to answer the user question below.

When creating the queries:
- Include both direct keyword matches and rephrasings using synonyms or related terms.
- Add at least one reasoning-oriented query that may capture indirect or inferential context.
- Include one broad query that could return general background information if the question is open-ended.

Generate exactly 4 queries (one per line).

User Question:
{question}
"""
prompt_rag_fusion = ChatPromptTemplate.from_template(template_multi)

generate_queries = (
    prompt_rag_fusion
    | llm_query_gen
    | StrOutputParser()
    | (lambda x: [q.strip() for q in x.split("\n") if q.strip()])
)

# ---- Reciprocal Rank Fusion (RRF) ----
def reciprocal_rank_fusion(results: list[list], k=60):
    """ Reciprocal_rank_fusion that takes multiple lists of ranked documents 
        and an optional parameter k used in the RRF formula """
    fused_scores = {}
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)  # robust key for dict
            fused_scores[doc_str] = fused_scores.get(doc_str, 0) + 1 / (rank + k)

    reranked = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]
    return reranked

# Wrap python function so it composes in LC runnables
rrf = RunnableLambda(lambda res: reciprocal_rank_fusion(res, k=60))

# ---- Compose: query-gen -> retriever.map() -> RRF ----
if retriever is None:
    raise RuntimeError("Retriever is not initialized. Ensure you have documents indexed.")

retrieval_chain_rag_fusion = generate_queries | retriever.map() | rrf



# ---- Final answer prompt ----
template_final = template_final = """
You are a careful and knowledgeable assistant.

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

Answer:
"""

prompt_final = ChatPromptTemplate.from_template(template_final)

# Convert fused (doc, score) tuples to a readable text block
def format_context(fused_docs_with_scores, max_docs=8):
    lines = []
    for i, (doc, score) in enumerate(fused_docs_with_scores[:max_docs], 1):
        src = doc.metadata.get("source", "unknown")
        pno = doc.metadata.get("page", None)
        page_str = f" (page {pno})" if pno is not None else ""
        preview = doc.page_content[:300].replace("\n", " ")
        lines.append(f"[{i}] score={score:.4f} — {src}{page_str}\n{preview}\n")
    return "\n".join(lines) if lines else "No context available."

format_context_runnable = RunnableLambda(format_context)

# Final chain: build {context, question} -> prompt -> llm -> text
final_rag_chain = (
    {
        "context": retrieval_chain_rag_fusion | format_context_runnable,
        "question": itemgetter("question"),
    }
    | prompt_final
    | llm_answer
    | StrOutputParser()
)

print("✅ RAG-Fusion chain initialized (Ollama + HFembeddings)")




# Query the RAG System--------------------------------------

def ask_question(question: str, show_sources: bool = True, max_sources: int = 8):
    print(f"Question: {question}\n")

    # Get fused results (docs + scores)
    fused = retrieval_chain_rag_fusion.invoke({"question": question})
    # Prepare context preview
    context_block = format_context(fused, max_docs=max_sources)

    # Final answer
    answer = final_rag_chain.invoke({"question": question})

    print("Answer:\n")
    print(answer)

    if show_sources:
        print("\n Sources used (top fused docs):")
        for i, (doc, score) in enumerate(fused[:max_sources], 1):
            src = doc.metadata.get("source", "unknown")
            ftype = doc.metadata.get("file_type", "unknown")
            course = doc.metadata.get("course", "unknown")
            page = doc.metadata.get("page", "N/A") if doc.metadata.get("file_type") == "pdf" else "N/A"
            preview = doc.page_content[:150].replace("\n", " ")
            print(f"\n{i}. {src}")
            print(f"   Type: {ftype} | Course: {course} | Score: {score:.4f} | Page: {page}")
            print(f"   Preview: {preview}...")

    return {
        "answer": answer,
        "fused_results": fused,
        "context_preview": context_block,
    }



# SMART RAG ROUTER  (RAG → fallback to LLM knowledge)------------------------------


# --- Current local models (Ollama) ---
# =========================================================
# SMART RAG ROUTER v3 — balanced confidence + semantic overlap
# =========================================================

from langchain_community.llms import Ollama
llm_answer = Ollama(model="llama3.2", temperature=0.7)

# --- Later (OpenAI) ---
# from langchain_openai import ChatOpenAI
# llm_answer = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

def smart_ask(question: str, show_sources: bool = True, confidence_threshold: float = 0.01):
    """
    Smarter RAG router:
    - checks semantic keyword overlap
    - uses lower RRF threshold (0.05)
    - falls back only when context clearly missing or model denies
    """
    print(f"\n🔎 Question: {question}\n")

    fused = retrieval_chain_rag_fusion.invoke({"question": question})
    rag_answer = final_rag_chain.invoke({"question": question})
    context_text = format_context(fused, max_docs=8)

    # --- Extract simple features ---
    not_in_docs_flags = [
        "does not contain", "not found", "no information", "no mention",
        "not discussed", "no reference", "not covered", "doesn't discuss",
        "cannot find", "absent from", "there is no", "not available in",
        "missing from", "not included"
    ]

    lower_answer = rag_answer.lower()
    flag_detected = any(flag in lower_answer for flag in not_in_docs_flags)
    empty_context = len(context_text.strip()) < 50

    top_score = fused[0][1] if fused else 0
    low_confidence = top_score < confidence_threshold

    # --- Simple keyword overlap heuristic ---
    question_terms = [w.lower() for w in question.split() if len(w) > 3]
    overlap = any(term in context_text.lower() for term in question_terms)
    semantic_relevant = overlap or not low_confidence

    # --- Decide ---
    trigger_fallback = (flag_detected or empty_context) and not semantic_relevant

    if trigger_fallback:
        print("⚠️  Likely not in documents — routing to general LLM.\n")
        general_answer = llm_answer.invoke(
            f"The uploaded documents do not appear to contain relevant information for this question. "
            f"Please answer based on your own knowledge and say so clearly.\n\nQuestion: {question}"
        )

        print("💬 Answer (General Knowledge):\n")
        print(general_answer)

        return {
            "answer_type": "llm_general",
            "rag_answer": rag_answer,
            "final_answer": general_answer,
            "top_confidence": top_score,
            "sources_used": [],
        }

    else:
        print("💬 Answer (From Documents):\n")
        print(rag_answer)
        print(f"\n🧮 Confidence = {top_score:.3f} | Overlap = {overlap}")

        if show_sources:
            print("\n📚 Top Sources:")
            for i, (doc, score) in enumerate(fused[:5], 1):
                src = doc.metadata.get("source", "unknown")
                preview = doc.page_content[:150].replace("\n", " ")
                print(f"{i}. {src} — score={score:.4f}")
                print(f"   {preview}...")

        return {
            "answer_type": "rag",
            "final_answer": rag_answer,
            "top_confidence": top_score,
            "sources_used": fused,
        }



result = smart_ask("How do you create a boxplot for different species using seaborn?")
result = smart_ask("In what city was seaborn doing the boxplot")
