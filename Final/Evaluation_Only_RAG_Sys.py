"""
evaluation_only_rag_sys.py
Simplified RAG system for evaluation - uses unified rag_core.py

This ensures evaluation tests the EXACT same system as users experience
"""

from RAG_Core import setup_rag_chain, RAGConfig, OLLAMA_MODEL, EMBEDDING_MODEL
# Re-export for backward compatibility with evaluate_ragas.py
__all__ = ['setup_rag_chain', 'OLLAMA_MODEL', 'EMBEDDING_MODEL']

# Optional: Test the RAG chain when run directly
if __name__ == '__main__':
    import os
    
    # Optional: Set up LangSmith
    os.environ['LANGCHAIN_TRACING_V2'] = 'false'
    
    print("="*80)
    print("Testing RAG Chain (using unified rag_core.py)")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  JSON Folder: {RAGConfig.JSON_FOLDER}")
    print(f"  PDF Folder: {RAGConfig.PDF_FOLDER}")
    print(f"  ChromaDB: {RAGConfig.CHROMA_DIR}")
    print(f"  Model: {OLLAMA_MODEL}")
    print(f"  Chunk Size: {RAGConfig.CHUNK_SIZE}")
    print(f"  Temperature: {RAGConfig.LLM_TEMPERATURE}")
    print()
    
    qa_chain = setup_rag_chain(use_fusion=False)  # Use simple RAG for evaluation
    
    if qa_chain:
        # Test query
        question = "How do I create a pandas dataframe?"
        print(f"🔍 Test Question: {question}\n")
        
        result = qa_chain.invoke({"query": question})
        
        print(f"💡 Answer:\n{result['result']}\n")
        print(f"📚 Sources: {len(result['source_documents'])} documents retrieved")
        print("="*80)
    else:
        print("❌ Failed to initialize RAG chain")
        print("\nPossible issues:")
        print(f"  1. ChromaDB not found at: {RAGConfig.CHROMA_DIR}")
        print(f"  2. No JSON files in: {RAGConfig.JSON_FOLDER}")
        print(f"  3. Ollama not running (try: ollama serve)")
        print("\nTo create the vector store, run:")
        print("  python -c 'from rag_core import create_vectorstore; create_vectorstore(include_pdfs=True)'")
