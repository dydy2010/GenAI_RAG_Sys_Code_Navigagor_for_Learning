"""
Simple PDF RAG System - Complete Setup
Using FREE: Ollama LLM + HuggingFace Embeddings

Prerequisites:
1. add your langsmith API in Cell 1
2. pip install langchain langchain-community langchain-huggingface sentence-transformers chromadb pymupdf langsmith
3. Install Ollama: https://ollama.ai
- Run: ollama pull llama3.2
- Run: ollama pull codellama
- not sure if we can call llama3.2 and olama code depending on the question
"""

#%% Cell 1
# Setup Environment Variables

import os

# LangSmith Configuration
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = 'pls add your api key here'
os.environ['LANGCHAIN_PROJECT'] = 'rag-project'  # Name your project for organization

print("✓ LangSmith tracing enabled")

#%% Cell 2
# Import Libraries

import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.schema import BaseRetriever
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

print("Libraries imported")


#%% Cell 3
# Configuration

PARSED_JSON_FOLDER = "data/parsed"
PDF_FOLDER = "data/raw/Materials_code_learning"
CHROMA_DIR = "data/chroma_db"
DEFAULT_COURSE = "RAG ALIN"

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Ollama model
OLLAMA_MODEL = "llama3.2"  # "codellama"


#%% Cell 4
# Initialize Embeddings

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)
print(f"Embeddings model loaded: {EMBEDDING_MODEL}")

#%% Cell 5
# Process JSON Files (Code) - With LangSmith Tracing

from langsmith import traceable

@traceable(name="process_json_files")
def process_json_files(json_folder: str, chroma_dir: str):
    """
    Process JSON files (code) with LangSmith tracing
    """
    json_path = Path(json_folder)
    json_files = list(json_path.glob("*.json"))

    print(f"\nProcessing {len(json_files)} JSON files (code)...\n")

    all_chunks = []

    # Code-aware text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\nclass ", "\n\ndef ", "\n\n", "\n", " ", ""]
    )

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            content = data.get("content", "")
            if not content:
                print(f"Skipping {json_file.name}: no content")
                continue

            # Create Document with metadata
            doc = Document(
                page_content=content,
                metadata={
                    "source": data.get("name", "unknown"),
                    "extension": data.get("extension", ""),
                    "course": data.get("course", DEFAULT_COURSE),
                    "file_type": "code",
                    "original_size": data.get("st_size", 0),
                }
            )

            # Split into chunks
            chunks = text_splitter.split_documents([doc])
            all_chunks.extend(chunks)

            print(f"{json_file.name}: {len(chunks)} chunks")

        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")

    return all_chunks


# Run with tracing
code_chunks = process_json_files(PARSED_JSON_FOLDER, CHROMA_DIR)
print(f"\nTotal code chunks: {len(code_chunks)}")

#%% Cell 6
# Process PDFs - With LangSmith Tracing

@traceable(name="process_pdfs")
def process_pdfs(pdf_folder: str):
    """
    Process PDFs with LangSmith tracing
    """
    pdf_path = Path(pdf_folder)
    pdf_files = list(pdf_path.glob("**/*.pdf"))

    print(f"\n📄 Processing {len(pdf_files)} PDF files (including subfolders)...\n")

    all_chunks = []

    # PDF text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    for pdf_file in pdf_files:
        try:
            # Load PDF
            loader = PyMuPDFLoader(str(pdf_file))
            pages = loader.load()

            # Extract course from folder structure
            try:
                relative_path = pdf_file.relative_to(pdf_path)
                course = relative_path.parts[0] if len(relative_path.parts) > 1 else DEFAULT_COURSE
            except:
                course = DEFAULT_COURSE

            # Split into chunks
            chunks = text_splitter.split_documents(pages)

            # Add metadata
            for chunk in chunks:
                chunk.metadata["course"] = course
                chunk.metadata["file_type"] = "pdf"
                chunk.metadata["source"] = pdf_file.stem

            all_chunks.extend(chunks)

            print(f"✓ {pdf_file.name} (course: {course}): {len(chunks)} chunks")

        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")

    return all_chunks


# Run with tracing
pdf_chunks = process_pdfs(PDF_FOLDER)
print(f"\n📊 Total PDF chunks: {len(pdf_chunks)}")

#%% Cell 7
# Create Chroma Vector Store - With Tracing

@traceable(name="create_vectorstore")
def create_vectorstore(all_documents: list, chroma_dir: str):
    """
    Create Chroma vector store with LangSmith tracing
    """
    print(f"\n📦 Total documents: {len(all_documents)}")
    print("⏳ Adding to Chroma (this may take a minute)...")

    vectorstore = Chroma.from_documents(
        documents=all_documents,
        embedding=embeddings,
        persist_directory=chroma_dir
    )

    print("✅ Vector store created successfully!")
    return vectorstore


# Combine all chunks
all_documents = code_chunks + pdf_chunks

# Create vector store
vectorstore = create_vectorstore(all_documents, CHROMA_DIR)

# Verify
collection = vectorstore._collection
print(f"\n📊 Total chunks in Chroma: {collection.count()}")

#%% Cell 8
# Setup RAG Chain with Ollama - With Full Tracing

# Initialize Ollama LLM
llm = Ollama(
    model=OLLAMA_MODEL,
    temperature=0.7
)

# Create custom prompt
prompt_template = """You are a helpful assistant answering questions based on course materials and code.
Use the following context to answer the question. If you don't know the answer based on the context, say so.

Context:
{context}

Question: {question}

Answer: """

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# Create retrieval chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

print("✓ RAG chain created with Ollama")
print(f"✓ Model: {OLLAMA_MODEL}")
print("✓ LangSmith will trace all queries automatically!")



#%% Cell 9
# Query the RAG System - Fully Traced!

def ask_question(question: str):
    """
    Ask a question to the RAG system
    All steps are automatically traced in LangSmith!
    """
    print(f"\n🔍 Question: {question}\n")

    # Query (automatically traced by LangSmith!)
    result = qa_chain.invoke({"query": question})

    # Display answer
    print(f"💡 Answer:\n{result['result']}\n")

    # Display sources
    print("📚 Sources used:")
    for i, doc in enumerate(result['source_documents'], 1):
        print(f"\n{i}. {doc.metadata.get('source', 'unknown')}")
        print(f"   Type: {doc.metadata.get('file_type', 'unknown')}")
        print(f"   Course: {doc.metadata.get('course', 'unknown')}")
        if doc.metadata.get('file_type') == 'pdf':
            print(f"   Page: {doc.metadata.get('page', 'N/A')}")
        print(f"   Preview: {doc.page_content[:150]}...")

    return result


# Test it! Please wait a second for result
result = ask_question("How do I create a pandas dataframe?")