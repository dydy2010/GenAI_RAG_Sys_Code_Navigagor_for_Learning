"""
RAG_Core_Compat.py
Compatibility layer for RAG_Core that works with RAGAS requirements

This wrapper ensures RAG_Core logic works with both:
- Modern LangChain 0.3+ (production)
- LangChain Community patterns (RAGAS evaluation)

Place this file in your evaluation/ directory
"""

import sys
from pathlib import Path

# Add parent directory to path to import RAG_Core
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional
import os

# Import configuration and utilities from main RAG_Core
from RAG_Core import (
    RAGConfig,
    OLLAMA_MODEL,
    EMBEDDING_MODEL,
    initialize_embeddings,
    load_vectorstore,
    get_qa_prompt
)

# LangChain imports compatible with RAGAS
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


class EvaluationChainWrapper:
    """
    Wrapper that ensures compatibility with RAGAS expectations
    while using the same underlying RAG_Core logic
    
    Key differences from RAG_Core.ChainWrapper:
    - Explicitly designed for RAGAS compatibility
    - Ensures proper document retrieval format
    - Handles both invoke() and get_relevant_documents() patterns
    """
    
    def __init__(self, vectorstore, model: str, temperature: float, top_k: int):
        """
        Initialize the evaluation chain
        
        Args:
            vectorstore: Chroma vector store instance
            model: Ollama model name (e.g., "llama3.2")
            temperature: LLM temperature (0.0 to 1.0)
            top_k: Number of documents to retrieve
        """
        self.vectorstore = vectorstore
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        
        # Initialize LLM
        self.llm = Ollama(model=model, temperature=temperature)
        
        # Create retriever
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
        
        # Get prompt template
        self.qa_prompt = get_qa_prompt()
        
        # Build chain
        self.chain = self._build_chain()
    
    def _build_chain(self):
        """Build the LCEL chain using modern LangChain patterns"""
        def format_docs(docs):
            """Format retrieved documents for context"""
            return "\n\n".join(doc.page_content for doc in docs)
        
        return (
            {
                "context": self.retriever | format_docs,
                "query": RunnablePassthrough()
            }
            | self.qa_prompt
            | self.llm
            | StrOutputParser()
        )
    
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute chain and return results in RAGAS-compatible format
        
        Args:
            inputs: Dict with 'query' key
            
        Returns:
            Dict with keys:
                - 'result': The generated answer (str)
                - 'source_documents': List of retrieved Document objects
        """
        query = inputs.get("query", "")
        
        # Retrieve source documents
        # Try modern invoke() first, fallback to legacy get_relevant_documents()
        try:
            source_documents = self.retriever.invoke(query)
        except AttributeError:
            # Fallback for older LangChain versions
            source_documents = self.retriever.get_relevant_documents(query)
        
        # Generate answer
        answer = self.chain.invoke(query)
        
        return {
            "result": answer,
            "source_documents": source_documents
        }


def setup_rag_chain(
    vectorstore: Optional[Any] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    top_k: Optional[int] = None,
    use_fusion: bool = False  # Ignored for compatibility, kept for signature match
) -> Optional[EvaluationChainWrapper]:
    """
    Setup RAG chain for evaluation - compatible with RAGAS
    
    This function mirrors RAG_Core.setup_rag_chain() signature but ensures
    compatibility with RAGAS evaluation framework by:
    1. Using the same configuration from RAG_Core
    2. Wrapping in RAGAS-compatible format
    3. Handling version differences transparently
    
    Args:
        vectorstore: Pre-loaded vector store (if None, loads from RAGConfig)
        model: Ollama model name (default from RAGConfig)
        temperature: LLM temperature (default from RAGConfig)
        top_k: Number of documents to retrieve (default from RAGConfig)
        use_fusion: Ignored (kept for backward compatibility)
        
    Returns:
        EvaluationChainWrapper instance or None if setup fails
    """
    # Load defaults from RAG_Core configuration
    if model is None:
        model = OLLAMA_MODEL
    if temperature is None:
        temperature = RAGConfig.LLM_TEMPERATURE
    if top_k is None:
        top_k = RAGConfig.TOP_K
    
    # Load vector store if not provided
    if vectorstore is None:
        print("📝 Loading vector store for evaluation...")
        embeddings = initialize_embeddings()
        vectorstore = load_vectorstore(embeddings)
        
        if vectorstore is None:
            print("❌ Vector store not available. Cannot initialize evaluation chain.")
            print(f"   Expected location: {RAGConfig.CHROMA_DIR}")
            print("\n   To create vector store:")
            print("   python -c 'from RAG_Core import create_vectorstore; create_vectorstore(include_pdfs=True)'")
            return None
    
    print(f"✓ Setting up evaluation chain:")
    print(f"  - Model: {model}")
    print(f"  - Temperature: {temperature}")
    print(f"  - Top-K retrieval: {top_k}")
    
    try:
        chain = EvaluationChainWrapper(
            vectorstore=vectorstore,
            model=model,
            temperature=temperature,
            top_k=top_k
        )
        print("✓ Evaluation chain initialized successfully")
        return chain
        
    except Exception as e:
        print(f"❌ Error initializing evaluation chain: {e}")
        import traceback
        traceback.print_exc()
        return None


# Re-export configuration for compatibility with evaluation scripts
__all__ = [
    'setup_rag_chain',
    'OLLAMA_MODEL',
    'EMBEDDING_MODEL',
    'RAGConfig'
]


def verify_compatibility():
    """Verify that the compatibility layer is working correctly"""
    print("="*80)
    print("🔍 Verifying RAG_Core Compatibility Layer")
    print("="*80)
    
    checks = []
    
    # Check 1: Configuration import
    try:
        print(f"\n✓ RAGConfig imported successfully")
        print(f"  - JSON Folder: {RAGConfig.JSON_FOLDER}")
        print(f"  - PDF Folder: {RAGConfig.PDF_FOLDER}")
        print(f"  - Chroma DB: {RAGConfig.CHROMA_DIR}")
        checks.append(True)
    except Exception as e:
        print(f"\n❌ Configuration import failed: {e}")
        checks.append(False)
    
    # Check 2: Embeddings
    try:
        embeddings = initialize_embeddings()
        print(f"\n✓ Embeddings initialized: {EMBEDDING_MODEL}")
        checks.append(True)
    except Exception as e:
        print(f"\n❌ Embeddings initialization failed: {e}")
        checks.append(False)
    
    # Check 3: Vector store
    try:
        vectorstore = load_vectorstore()
        if vectorstore:
            print(f"\n✓ Vector store loaded successfully")
            checks.append(True)
        else:
            print(f"\n⚠️  Vector store not found (needs to be created)")
            checks.append(False)
    except Exception as e:
        print(f"\n❌ Vector store loading failed: {e}")
        checks.append(False)
    
    # Check 4: Chain initialization
    try:
        chain = setup_rag_chain()
        if chain:
            print(f"\n✓ Evaluation chain initialized")
            checks.append(True)
            
            # Check 5: Test query
            try:
                test_query = "How do I create a pandas DataFrame?"
                result = chain.invoke({"query": test_query})
                
                if "result" in result and "source_documents" in result:
                    print(f"\n✓ Test query successful!")
                    print(f"  - Answer length: {len(result['result'])} chars")
                    print(f"  - Sources retrieved: {len(result['source_documents'])} documents")
                    print(f"\n  Sample answer:\n  {result['result'][:200]}...")
                    checks.append(True)
                else:
                    print(f"\n❌ Test query returned unexpected format")
                    checks.append(False)
            except Exception as e:
                print(f"\n❌ Test query failed: {e}")
                checks.append(False)
        else:
            print(f"\n❌ Chain initialization returned None")
            checks.append(False)
    except Exception as e:
        print(f"\n❌ Chain initialization failed: {e}")
        checks.append(False)
    
    # Summary
    print("\n" + "="*80)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"🎉 ALL CHECKS PASSED ({passed}/{total})")
        print("\n✅ Compatibility layer is fully functional!")
        print("   You can now run: python evaluation/Evaluate_Ragas.py")
    else:
        print(f"⚠️  SOME CHECKS FAILED ({passed}/{total} passed)")
        print("\nTroubleshooting:")
        if not checks[0]:
            print("  - Check that RAG_Core.py is in parent directory")
        if not checks[2] or not checks[3]:
            print("  - Create vector store: python -c 'from RAG_Core import create_vectorstore; create_vectorstore()'")
        if not checks[3]:
            print("  - Check Ollama is running: ollama serve")
            print("  - Check model is available: ollama pull llama3.2")
    
    print("="*80)
    return passed == total


if __name__ == '__main__':
    # Run verification when executed directly
    verify_compatibility()
