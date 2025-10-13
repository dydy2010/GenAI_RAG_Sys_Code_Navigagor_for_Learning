from chromadb.api.types import EmbeddingFunction, Embeddings, Documents
import ollama
from sentence_transformers import SentenceTransformer


class CodeEmbedder(EmbeddingFunction[Documents]):
    """Custom embedding model used for code,
    as default `chromadb` embedding model don't provide supports for programming languages."""

    def __init__(self, model_name: str = "jinaai/jina-code-embeddings-1.5b"):
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: Documents) -> Embeddings:
        documents = [doc.text for doc in input]
        return self.model.encode(documents)


class TextEmbedder(EmbeddingFunction):
    """Custom embedding model used for texts."""

    def __init__(self, model: str = "qwen3-embedding:4b"):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        documents = [doc.text for doc in input]
        return ollama.embed(model=self.model, input=documents).embeddings
