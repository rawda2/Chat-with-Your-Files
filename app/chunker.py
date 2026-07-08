# app/chunker.py
from typing import List, Dict, Any
import re

class TextChunker:
    """Chunk text into pieces using different strategies."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, file_id: str, strategy: str = "semantic") -> List[Dict[str, Any]]:
        """
        Split text according to the chosen strategy.
        strategies: fixed, semantic, overlapping
        """
        if strategy == "fixed":
            chunks = self._fixed_size_chunking(text)
        elif strategy == "overlapping":
            chunks = self._overlapping_chunking(text)
        else:  # semantic
            chunks = self._semantic_chunking(text)
        
        # Add metadata for each chunk
        chunks_with_meta = []
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 20:  # Skip chunks that are empty or too small
                chunks_with_meta.append({
                    "chunk_id": f"{file_id}_chunk_{i}",
                    "file_id": file_id,
                    "chunk_index": i,
                    "content": chunk.strip(),
                    "chunk_size": len(chunk),
                    "strategy": strategy
                })
        
        return chunks_with_meta
    
    def _fixed_size_chunking(self, text: str) -> List[str]:
        """Fixed-size non-overlapping chunking."""
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    def _overlapping_chunking(self, text: str) -> List[str]:
        """Overlapping chunking."""
        chunks = []
        step = self.chunk_size - self.chunk_overlap
        
        for i in range(0, len(text), step):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def _semantic_chunking(self, text: str) -> List[str]:
        """Smart chunking by sentences and paragraphs."""
        # Preliminary paragraph split
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If a paragraph exceeds the desired chunk size
            if len(para) > self.chunk_size:
                # Split large paragraph into sentences
                sentences = re.split(r'(?<=[.!?؟])\s+', para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) <= self.chunk_size:
                        current_chunk += sentence + " "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + " "
            else:
                # Regular paragraph
                if len(current_chunk) + len(para) <= self.chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text[:self.chunk_size]]