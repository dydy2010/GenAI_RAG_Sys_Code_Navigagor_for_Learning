#  Restructured Rag_sys for Reusability
"""
why having this separate rag sys for eval:
two modes:
When run directly (python evaluation_only_rag_sys.py): It executes the code inside the block to test the RAG chain on its own.
When imported (from evaluation_only_rag_sys import ...): It ignores the code inside the block, acting purely as a module that provides the setup_rag_chain() function.

Other scripts can now import this function and call it when they need a RAG chain, giving them full control.
Nothing happens automatically when import file.

If import this script into another file (e.g., from rag_system import qa_chain),
it would re-run the entire script from scratch, including the process of processing all PDFs and building the Chroma database.
"""

import os
import json
from pathlib import Path
from langsmith import traceable
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# --- Prerequisite ---
BASE_DIR = Path(__file__).parent
REPO_ROOT = BASE_DIR.parents[1]

PARSED_JSON_FOLDER = str(REPO_ROOT / "data" / "parsed")
PDF_FOLDER = str(REPO_ROOT / "data" / "raw" / "Materials_code_learning")
CHROMA_DIR = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2"
DEFAULT_COURSE = "RAG ALIN"


# --- Data Processing Functions (Copied from original script) ---
@traceable(name="process_json_files")
def process_json_files(json_folder: str):
    # ... (code from your original Cell 5, no changes needed)
    json_path = Path(json_folder)
    json_files = list(json_path.glob("*.json"))
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=50,
        chunk_overlap=0,
        separators=["\n\nclass ", "\n\ndef ", "\n\n", "\n", " ", ""],
    )
    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            content = data.get("content", "")
            if not content:
                continue
            doc = Document(
                page_content=content,
                metadata={
                    "source": data.get("name", "unknown"),
                    "extension": data.get("extension", ""),
                    "course": data.get("course", DEFAULT_COURSE),
                    "file_type": "code",
                    "original_size": data.get("st_size", 0),
                },
            )
            chunks = text_splitter.split_documents([doc])
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
    return all_chunks


@traceable(name="process_pdfs")
def process_pdfs(pdf_folder: str):
    # ... (code from original script Cell 6, no changes needed)
    pdf_path = Path(pdf_folder)
    pdf_files = list(pdf_path.glob("**/*.pdf"))
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=50, chunk_overlap=0, separators=["\n\n", "\n", " ", ""]
    )
    for pdf_file in pdf_files:
        try:
            loader = PyMuPDFLoader(str(pdf_file))
            pages = loader.load()
            try:
                relative_path = pdf_file.relative_to(pdf_path)
                course = (
                    relative_path.parts[0]
                    if len(relative_path.parts) > 1
                    else DEFAULT_COURSE
                )
            except:
                course = DEFAULT_COURSE
            chunks = text_splitter.split_documents(pages)
            for chunk in chunks:
                chunk.metadata["course"] = course
                chunk.metadata["file_type"] = "pdf"
                chunk.metadata["source"] = pdf_file.stem
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")
    return all_chunks


# --- Main Setup Function ---
def setup_rag_chain():
    """
    Sets up the entire RAG pipeline.
    It will process and ingest data only if the vector store doesn't exist.
    Otherwise, it loads the existing vector store.
    """
    print("Setting up RAG chain...")

    # Initialize Embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Check if Chroma DB already exists
    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        print(f"📚 Loading existing vector store from {CHROMA_DIR}...")
        vectorstore = Chroma(
            persist_directory=CHROMA_DIR, embedding_function=embeddings
        )
    else:
        print("🛠️ No existing vector store found. Building a new one...")
        # Process all documents
        print("Processing source documents...")
        # Log and validate data paths
        print(f"Using parsed JSON folder: {PARSED_JSON_FOLDER}")
        print(f"Using PDF folder: {PDF_FOLDER}")
        parsed_path = Path(PARSED_JSON_FOLDER)
        pdf_path = Path(PDF_FOLDER)
        if not parsed_path.exists():
            raise FileNotFoundError(f"Parsed JSON folder not found: {parsed_path}")
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF folder not found: {pdf_path}")
        json_count_dbg = len(list(parsed_path.glob("*.json")))
        pdf_count_dbg = len(list(pdf_path.glob("**/*.pdf")))
        print(f"Discovered files -> JSON: {json_count_dbg}, PDFs: {pdf_count_dbg}")
        code_chunks = process_json_files(PARSED_JSON_FOLDER)
        pdf_chunks = process_pdfs(PDF_FOLDER)
        all_documents = code_chunks + pdf_chunks

        if not all_documents:
            raise ValueError(
                "No documents were processed. Check your data folders and processing functions. "
                f"(JSON dir: {PARSED_JSON_FOLDER}, PDF dir: {PDF_FOLDER})"
            )

        # Create and persist the vector store
        print(
            f"📦 Creating and persisting vector store with {len(all_documents)} documents..."
        )
        vectorstore = Chroma.from_documents(
            documents=all_documents, embedding=embeddings, persist_directory=CHROMA_DIR
        )
        print("✅ Vector store created successfully!")

    # Initialize Ollama LLM
    llm = Ollama(model=OLLAMA_MODEL, temperature=0.3)

    # Create custom prompt
    prompt_template = """You are a helpful assistant answering questions based on course materials and code.
Use the following context to answer the question. If you don't know the answer based on the context, say so.

Context:
{context}

Question: {question}

Answer: """
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    # Create a simple QA wrapper compatible with .invoke({"query": ...})
    class SimpleQA:
        def __init__(self, llm, vectorstore, prompt):
            self.llm = llm
            self.retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
            self.prompt = prompt

        def invoke(self, inputs):
            query = inputs.get("query", "")
            # Support both older and newer retriever
            if hasattr(self.retriever, "get_relevant_documents"):
                docs = self.retriever.get_relevant_documents(query)
            else:
                docs = self.retriever.invoke(query)
            context = "\n\n".join([d.page_content for d in docs])
            prompt_text = self.prompt.format(context=context, question=query)
            answer = self.llm.invoke(prompt_text)
            if not isinstance(answer, str):
                answer = str(answer)
            return {"result": answer, "source_documents": docs}

    qa = SimpleQA(llm=llm, vectorstore=vectorstore, prompt=PROMPT)
    print("✓ RAG chain setup complete.")
    return qa


# --- Main execution block (for running this file directly) ---
if __name__ == "__main__":
    # This block allows you to still run this file to test the RAG system directly,optional
    # Set up LangSmith if you haven't set it in your environment
    # os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    # os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
    # os.environ['LANGCHAIN_API_KEY'] = 'Replace with your key'
    # os.environ['LANGCHAIN_PROJECT'] = 'rag-project'

    my_qa_chain = setup_rag_chain()

    if os.environ.get("BATCH_EVAL", "0") == "1":
        try:
            from Evaluation_Dataset import test_questions
        except Exception as e:
            print(f"✗ Failed to import test questions: {e}")
            raise  # Batch evaluation mode: generate responses.json for evaluation

        print("\n--- Generating responses.json for evaluation ---")
        responses = []
        for item in test_questions:
            try:
                q = item.get("question", "")
                r = my_qa_chain.invoke({"query": q})
                responses.append(
                    {
                        "question": q,
                        "answer": r.get("result", ""),
                        "contexts": [
                            doc.page_content for doc in r.get("source_documents", [])
                        ],
                        "ground_truth": item.get("ground_truth", ""),
                        "ground_truth_context": item.get("ground_truth_context", []),
                    }
                )
            except Exception as e:
                print(f"Error processing question '{item.get('question', '')}': {e}")
                responses.append(
                    {
                        "question": item.get("question", ""),
                        "answer": f"ERROR: {e}",
                        "contexts": [],
                        "ground_truth": item.get("ground_truth", ""),
                        "ground_truth_context": item.get("ground_truth_context", []),
                    }
                )

        out_path = Path(__file__).parent / "responses.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(responses, f, ensure_ascii=False, indent=2)
        print(f"✅ Wrote {len(responses)} responses to {out_path}")
    else:
        # Simple smoke test
        print("\n--- Testing the RAG chain ---")
        question = "How do I create a pandas dataframe?"
        print(f"\n🔍 Question: {question}\n")
        result = my_qa_chain.invoke({"query": question})
        print(f"💡 Answer:\n{result['result']}\n")

