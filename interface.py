"""
Code Navigator - Streamlit Web Interface
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import os
import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Try new Ollama import
try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    from langchain_community.llms import Ollama

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Code Navigator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .code-preview {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

JSON_FOLDER = "./data/parsed"
CHROMA_DIR = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2"


# ============================================================================
# INITIALIZATION
# ============================================================================

@st.cache_resource
def initialize_system():
    """Initialize the RAG system (cached for performance)"""

    # Create folders
    Path(JSON_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # Check if vector store exists
    if not Path(CHROMA_DIR).exists() or not list(Path(CHROMA_DIR).glob("*")):
        return None, embeddings, "Vector store not initialized"

    # Load vector store
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

    # Check if it has documents
    try:
        count = vectorstore._collection.count()
        if count == 0:
            return None, embeddings, "No documents in vector store"
    except:
        return None, embeddings, "Error loading vector store"

    # Initialize LLM
    llm = Ollama(model=OLLAMA_MODEL, temperature=0.3)

    # Create prompt
    code_prompt_template = """You are an expert programming tutor helping students learn from code examples.

Your role:
- Explain code clearly and concisely
- Show practical examples from the provided context
- Break down complex concepts into simple steps
- Highlight best practices and common patterns

Context (Code Examples):
{context}

Question: {question}

Answer (be concise and code-focused):"""

    PROMPT = PromptTemplate(
        template=code_prompt_template,
        input_variables=["context", "question"]
    )

    # Create chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    return qa_chain, vectorstore, "initialized"


def process_code_files():
    """Process JSON code files and create vector store"""
    json_path = Path(JSON_FOLDER)
    json_files = list(json_path.glob("*.json"))

    if len(json_files) == 0:
        return 0, "No JSON files found"

    all_chunks = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        separators=["\n\nclass ", "\n\ndef ", "\n\nfunction ", "\n\n# ", "\n\n", "\n", " ", ""]
    )

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, json_file in enumerate(json_files):
        try:
            status_text.text(f"Processing {json_file.name}...")

            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            content = data.get("content", "")
            if not content:
                continue

            extension = data.get("extension", "").lower()
            language = "python" if extension in [".py", ".python"] else "r" if extension in [".r", ".R"] else "other"

            doc = Document(
                page_content=content,
                metadata={
                    "source": data.get("name", json_file.stem),
                    "filename": json_file.name,
                    "extension": extension,
                    "language": language,
                    "file_type": "code",
                }
            )

            chunks = text_splitter.split_documents([doc])
            all_chunks.extend(chunks)

            progress_bar.progress((idx + 1) / len(json_files))

        except Exception as e:
            st.warning(f"Error processing {json_file.name}: {e}")

    progress_bar.empty()
    status_text.empty()

    if len(all_chunks) == 0:
        return 0, "No content extracted from files"

    # Create embeddings and vector store
    status_text.text("Creating vector store...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    status_text.empty()

    return len(all_chunks), "Success"


# ============================================================================
# SESSION STATE
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "qa_chain" not in st.session_state:
    qa_chain, vectorstore, status = initialize_system()
    st.session_state.qa_chain = qa_chain
    st.session_state.vectorstore = vectorstore
    st.session_state.init_status = status

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title("🎓 Code Navigator")
    st.markdown("---")

    # System Status
    st.subheader("📊 System Status")

    if st.session_state.qa_chain is None:
        st.error("⚠️ System not initialized")
        st.info(st.session_state.init_status)

        if st.button("🔄 Initialize System", type="primary"):
            with st.spinner("Processing code files..."):
                chunks, status = process_code_files()
                if chunks > 0:
                    st.success(f"✓ Processed {chunks} code chunks")
                    st.rerun()
                else:
                    st.error(f"Failed: {status}")
    else:
        st.success("✓ System Ready")

        # Show stats
        try:
            count = st.session_state.vectorstore._collection.count()
            st.metric("Code Chunks", count)
        except:
            pass

        st.metric("Model", OLLAMA_MODEL)

    st.markdown("---")

    # Settings
    st.subheader("⚙️ Settings")

    show_sources = st.checkbox("Show sources", value=True)
    show_code_preview = st.checkbox("Show code preview", value=True)

    st.markdown("---")

    # Quick Actions
    st.subheader("🔍 Quick Actions")

    if st.button("📂 List All Files"):
        st.session_state.show_files = True

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("🔄 Rebuild Index"):
        with st.spinner("Rebuilding..."):
            chunks, status = process_code_files()
            if chunks > 0:
                st.success(f"✓ Rebuilt with {chunks} chunks")
                st.rerun()
            else:
                st.error(f"Failed: {status}")

    st.markdown("---")
    st.caption("💡 Tip: Ask questions about your code!")

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("💬 Chat with Your Code")

# Check if system is ready
if st.session_state.qa_chain is None:
    st.warning("⚠️ Please initialize the system using the sidebar button")
    st.info(f"""
    **Steps to get started:**
    1. Make sure you have JSON files in `{JSON_FOLDER}`
    2. Click 'Initialize System' in the sidebar
    3. Wait for processing to complete
    4. Start asking questions!
    """)
    st.stop()

# Show list of files if requested
if "show_files" in st.session_state and st.session_state.show_files:
    with st.expander("📂 Available Code Files", expanded=True):
        try:
            collection = st.session_state.vectorstore._collection
            results = collection.get()

            files = {}
            for metadata in results['metadatas']:
                source = metadata.get('source', 'unknown')
                lang = metadata.get('language', 'unknown')
                if source not in files:
                    files[source] = lang

            # Group by language
            by_language = {}
            for source, lang in files.items():
                if lang not in by_language:
                    by_language[lang] = []
                by_language[lang].append(source)

            cols = st.columns(3)
            for idx, (lang, sources) in enumerate(sorted(by_language.items())):
                with cols[idx % 3]:
                    st.markdown(f"**{lang.upper()}** ({len(sources)} files)")
                    for source in sorted(sources)[:5]:
                        st.text(f"• {source[:30]}...")
                    if len(sources) > 5:
                        st.text(f"... +{len(sources) - 5} more")

            st.info(f"📊 Total: {len(files)} unique files")
        except Exception as e:
            st.error(f"Error loading files: {e}")

    if st.button("Close"):
        st.session_state.show_files = False
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show sources if available
        if "sources" in message and show_sources:
            with st.expander("📚 View Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**{i}. {source['name']}** `[{source['language']}]`")

                    if show_code_preview and "preview" in source:
                        st.code(source["preview"], language=source.get("language", "python"))

# Chat input
if prompt := st.chat_input("Ask a question about your code..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.qa_chain.invoke({"query": prompt})
                response = result['result']

                st.markdown(response)

                # Prepare sources
                sources = []
                seen = set()
                for doc in result['source_documents']:
                    source_name = doc.metadata.get('source', 'unknown')
                    if source_name not in seen:
                        seen.add(source_name)
                        sources.append({
                            "name": source_name,
                            "language": doc.metadata.get('language', 'unknown'),
                            "preview": doc.page_content[:400]
                        })

                # Show sources
                if sources and show_sources:
                    with st.expander("📚 View Sources"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**{i}. {source['name']}** `[{source['language']}]`")

                            if show_code_preview:
                                st.code(source["preview"], language=source.get("language", "python"))

                # Add to message history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources
                })

            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Make sure Ollama is running: `ollama serve`")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("🎓 Code Navigator | Powered by Ollama + LangChain + Streamlit")
