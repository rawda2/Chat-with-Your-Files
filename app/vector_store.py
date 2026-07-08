# app/vector_store.py
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import os

class VectorStore:
    """Handle ChromaDB vector storage operations."""
    
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "documents"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        
        # Create storage folder if it does not exist
        os.makedirs(persist_dir, exist_ok=True)
        
        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Use custom embedding function
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection(collection_name)
        
        print(f"✅ Vector Store ready: {persist_dir}")
        print(f"📁 Collection: {collection_name}")
    
    def _get_or_create_collection(self, name: str):
        """Get existing collection or create a new one."""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(
                name=name,
                embedding_function=self.embedding_fn
            )
    
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Add chunks with embeddings to the database."""
        if not chunks:
            return 0
        
        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [
            {
                "file_id": chunk["file_id"],
                "chunk_index": chunk["chunk_index"],
                "strategy": chunk.get("strategy", "semantic"),
                "chunk_size": chunk.get("chunk_size", 0)
            }
            for chunk in chunks
        ]
        
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            return len(chunks)
        except Exception as e:
            print(f"❌ Error adding chunks: {e}")
            return 0
    
    def search(self, query: str, file_id: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for the most similar chunks to the query."""
        where_filter = None
        if file_id:
            where_filter = {"file_id": file_id}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter
        )
        
        # Format results
        documents = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                documents.append({
                    "chunk_id": doc_id,
                    "content": results['documents'][0][i] if results['documents'] else "",
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })
        
        return documents
    
    def delete_file_chunks(self, file_id: str) -> int:
        """Delete all chunks belonging to a specific file."""
        try:
            # Get all IDs for this file
            results = self.collection.get(
                where={"file_id": file_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                return len(results['ids'])
            return 0
        except Exception as e:
            print(f"❌ Error deleting chunks: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "persist_dir": self.persist_dir
            }
        except:
            return {"total_chunks": 0}