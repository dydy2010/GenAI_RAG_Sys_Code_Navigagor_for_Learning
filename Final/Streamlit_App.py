"""
Streamlit_App.py
Code Navigator - Streamlit Web Interface
Run with: streamlit run streamlit_app.py

Now uses unified rag_core.py for consistency with evaluation
"""

import streamlit as st
from pathlib import Path

# Import from shared core
from RAG_Core import (
    RAGConfig,
    setup_rag_chain,
    create_vectorstore,
    initialize_embeddings,
    load_vectorstore,
    get_system_stats,
)

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
# INITIALIZATION
# ============================================================================

@st.cache_resource
def initialize_system():
    """Initialize the RAG system (cached for performance)"""
    # Create folders
    Path(RAGConfig.JSON_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(RAGConfig.CHROMA_DIR).mkdir(parents=True, exist_ok=True)
    
    # Load embeddings
    embeddings = initialize_embeddings()
    vectorstore = load_vectorstore(embeddings)
    
    if vectorstore is None:
        return None, None, "Vector store not initialized"
    
    # Setup QA chain using unified function
    qa_chain = setup_rag_chain(vectorstore=vectorstore, use_fusion=False)
    
    if qa_chain is None:
        return None, vectorstore, "Failed to initialize QA chain"
    
    return qa_chain, vectorstore, "initialized"


def process_files_with_progress():
    """Process code files and PDFs with Streamlit progress bar"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Processing code files and PDFs...")
    progress_bar.progress(0.3)
    
    # Call the shared function (includes PDFs by default)
    vectorstore, chunks, status = create_vectorstore(include_pdfs=True)
    
    progress_bar.progress(1.0)
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    return chunks, status


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
            with st.spinner("Processing code files and PDFs..."):
                chunks, status = process_files_with_progress()
                if chunks > 0:
                    st.success(f"✓ Processed {chunks} total chunks")
                    st.rerun()
                else:
                    st.error(f"Failed: {status}")
    else:
        st.success("✓ System Ready")
        
        # Show detailed stats using unified function
        stats = get_system_stats(st.session_state.vectorstore)
        if stats["status"] == "ready":
            st.metric("Total Chunks", stats["total_documents"])
            
            # Show breakdown by type
            if stats["by_type"]:
                st.write("**By Type:**")
                for file_type, count in stats["by_type"].items():
                    st.text(f"  {file_type}: {count}")
            
            # Show breakdown by language (for code files)
            if stats["by_language"]:
                st.write("**Code Languages:**")
                for lang, count in stats["by_language"].items():
                    st.text(f"  {lang}: {count}")
        
        st.metric("Model", RAGConfig.OLLAMA_MODEL)
        st.metric("Temperature", RAGConfig.LLM_TEMPERATURE)
    
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
            chunks, status = process_files_with_progress()
            if chunks > 0:
                st.success(f"✓ Rebuilt with {chunks} chunks")
                st.rerun()
            else:
                st.error(f"Failed: {status}")
    
    st.markdown("---")
    st.caption("💡 Tip: Ask questions about your code and course materials!")

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("💬 Chat with Your Code")

# Check if system is ready
if st.session_state.qa_chain is None:
    st.warning("⚠️ Please initialize the system using the sidebar button")
    st.info(f"""
    **Steps to get started:**
    1. Make sure you have JSON files in `{RAGConfig.JSON_FOLDER}`
    2. Make sure you have PDFs in `{RAGConfig.PDF_FOLDER}` (optional)
    3. Click 'Initialize System' in the sidebar
    4. Wait for processing to complete
    5. Start asking questions!
    """)
    st.stop()

# Show list of files if requested
if "show_files" in st.session_state and st.session_state.show_files:
    with st.expander("📂 Available Files", expanded=True):
        try:
            collection = st.session_state.vectorstore._collection
            results = collection.get()

            files = {}
            for metadata in results['metadatas']:
                source = metadata.get('source', 'unknown')
                ftype = metadata.get('file_type', 'unknown')
                lang = metadata.get('language', 'unknown')
                key = f"{source} ({ftype})"
                if key not in files:
                    files[key] = {'type': ftype, 'lang': lang}

            # Group by type
            by_type = {}
            for key, info in files.items():
                ftype = info['type']
                if ftype not in by_type:
                    by_type[ftype] = []
                by_type[ftype].append(key)

            cols = st.columns(2)
            for idx, (ftype, sources) in enumerate(sorted(by_type.items())):
                with cols[idx % 2]:
                    st.markdown(f"**{ftype.upper()}** ({len(sources)} files)")
                    for source in sorted(sources)[:5]:
                        st.text(f"• {source[:40]}...")
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
                    name = source.get('name', 'unknown')
                    ftype = source.get('type', 'unknown')
                    lang = source.get('language', 'unknown')
                    
                    st.markdown(f"**{i}. {name}** `[{ftype}]` `[{lang}]`")

                    if show_code_preview and "preview" in source:
                        st.code(source["preview"], language=lang if lang != 'unknown' else 'python')

# Chat input
if prompt := st.chat_input("Ask a question about your code or course materials..."):
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
                            "type": doc.metadata.get('file_type', 'unknown'),
                            "language": doc.metadata.get('language', 'unknown'),
                            "preview": doc.page_content[:400]
                        })

                # Show sources
                if sources and show_sources:
                    with st.expander("📚 View Sources"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**{i}. {source['name']}** `[{source['type']}]` `[{source['language']}]`")

                            if show_code_preview:
                                lang = source['language'] if source['language'] != 'unknown' else 'python'
                                st.code(source["preview"], language=lang)

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
st.caption("🎓 Code Navigator | Powered by Ollama + LangChain + Streamlit | Using unified rag_core.py")
