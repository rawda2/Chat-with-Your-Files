# app/models.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class ChunkStrategy(str, Enum):
    FIXED = "fixed"
    SEMANTIC = "semantic"
    OVERLAPPING = "overlapping"

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    chunk_count: int
    total_chars: int
    status: str
    message: str

class QueryRequest(BaseModel):
    query: str
    file_id: Optional[str] = None
    top_k: int = 3

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    processing_time: float

class SQLConnectionRequest(BaseModel):
    server: str
    database: str
    username: str
    password: str
    query: str

class ChunkInfo(BaseModel):
    chunk_id: str
    content: str
    source: str
    chunk_index: int
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    embedding_model: str
    llm_model: str
    vector_store: str