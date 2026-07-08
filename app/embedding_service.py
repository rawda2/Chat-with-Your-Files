# app/embedding_service.py
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
import torch

class EmbeddingService:
    """Embedding generation service using free models."""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"✅ Embedding model loaded: {self.model_name}")
            print(f"📊 Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"⚠️ Model load error: {e}")
            # Fallback to a smaller model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Fallback model loaded")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding for a single text."""
        if not self.model:
            self._load_model()
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts (faster and more efficient)."""
        if not self.model:
            self._load_model()
        
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        return embeddings.tolist()
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embeddings to each chunk."""
        if not chunks:
            return chunks
        
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embed_batch(texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding
        
        return chunks
    
    def get_embedding_dimension(self) -> int:
        """Get the embedding vector dimension."""
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 384  # Default embedding dimension if model fails to load