from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import time
import os
from dotenv import load_dotenv

from app.models import *
from app.file_processor import FileProcessor
from app.chunker import TextChunker
from app.embedding_service import EmbeddingService
from app.vector_store import VectorStore
from app.llm_service import LLMService
from app.sql_extractor import SQLExtractor

load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Chat with Your Files", description="Chat application for files using free models")

# Mount static files - IMPORTANT!
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
file_processor = FileProcessor(upload_dir=os.getenv("UPLOAD_DIR", "./uploads"))
chunker = TextChunker(chunk_size=500, chunk_overlap=50)
embedding_service = EmbeddingService(model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"))
vector_store = VectorStore(
    persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./chroma_db"),
    collection_name=os.getenv("CHROMA_COLLECTION_NAME", "documents")
)
llm_service = LLMService(model_name=os.getenv("LLM_MODEL", "HuggingFaceH4/zephyr-7b-beta"))
sql_extractor = SQLExtractor()

# Cache for user files
active_files = {}

# ============= Endpoints =============

@app.get("/", response_class=HTMLResponse)
async def root():
    """Home page."""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    stats = vector_store.get_collection_stats()
    return {
        "status": "healthy",
        "embedding_model": embedding_service.model_name,
        "llm_model": llm_service.model_name,
        "vector_store": f"ChromaDB - {stats['total_chunks']} chunks"
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), strategy: str = "semantic"):
    """Upload and process a file."""
    try:
        file_path, file_id, original_name = await file_processor.save_file(file)
        text = file_processor.extract_text(file_path)
        
        if not text or text.startswith("Error") or text.startswith("Failed"):
            file_processor.delete_file(file_path)
            raise HTTPException(status_code=400, detail=text)
        
        chunks = chunker.chunk_text(text, file_id, strategy)
        
        if not chunks:
            file_processor.delete_file(file_path)
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")
        
        chunks_with_embeddings = embedding_service.embed_chunks(chunks)
        vector_store.add_chunks(chunks_with_embeddings)
        
        active_files[file_id] = {
            "name": original_name,
            "path": file_path,
            "chunks": len(chunks),
            "strategy": strategy
        }
        
        return {
            "file_id": file_id,
            "filename": original_name,
            "chunk_count": len(chunks),
            "total_chars": len(text),
            "status": "success",
            "message": f"File processed successfully: {len(chunks)} chunks"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/query")
async def ask_question(request: dict):
    """Ask a question about the documents."""
    start_time = time.time()
    query = request.get("query", "")
    file_id = request.get("file_id")
    top_k = request.get("top_k", 3)
    
    try:
        results = vector_store.search(query=query, file_id=file_id, top_k=top_k)
        
        if not results:
            return {
                "query": query,
                "answer": "No documents uploaded to search. Please upload a file first.",
                "sources": [],
                "processing_time": time.time() - start_time
            }
        
        context_parts = []
        sources = []
        
        for i, result in enumerate(results):
            context_parts.append(f"[Source {i+1}]\n{result['content']}")
            sources.append({
                "source_id": result['chunk_id'],
                "content": result['content'][:200] + "...",
                "similarity": 1 - result['distance']
            })
        
        context = "\n\n".join(context_parts)
        answer = llm_service.generate_response(query, context)
        
        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "processing_time": time.time() - start_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/api/files")
async def list_files():
    """List uploaded files."""
    files = [
        {"id": fid, "name": data["name"], "chunks": data["chunks"]}
        for fid, data in active_files.items()
    ]
    return {"files": files}

@app.get("/api/stats")
async def get_stats():
    """System statistics."""
    stats = vector_store.get_collection_stats()
    return {
        "vector_store": stats,
        "active_files": len(active_files),
        "files": active_files
    }

@app.delete("/api/delete/{file_id}")
async def delete_file(file_id: str):
    """Delete a file."""
    try:
        deleted = vector_store.delete_file_chunks(file_id)
        
        if file_id in active_files:
            file_path = active_files[file_id].get("path")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            del active_files[file_id]
        
        return {
            "status": "success",
            "message": f"Deleted {deleted} chunks from the database"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print("=" * 50)
    print(f"🚀 Server running on http://localhost:{port}")
    print(f"📁 Upload files to: ./uploads")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=port)