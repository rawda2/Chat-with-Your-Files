# 📄 Chat with Your Files - RAG Application

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5.5-orange.svg)](https://www.trychroma.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

**Chat with Your Files** is a production-ready RAG (Retrieval-Augmented Generation) application that allows you to upload documents and ask questions about their content. Built with FastAPI, ChromaDB, and open-source language models.

### ✨ Key Features

- 📁 **Multi-format Support**: Upload PDF, DOCX, and TXT files
- 🧠 **Smart Chunking**: Multiple strategies (fixed, overlapping, semantic)
- 🔍 **Vector Search**: ChromaDB for efficient similarity search
- 🤖 **Free LLM Support**: Local models with HF Transformers (zephyr-7b, TinyLlama)
- 🌐 **Interactive Web UI**: Clean, responsive interface for file uploads and Q&A
- 🔄 **SQL Server Integration**: Bonus feature - query your databases directly
- 📊 **Multi-tenant Ready**: Support for multiple users and files

## 🏗️ Architecture
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Upload │────▶│ Chunk │────▶│ Embed │
│ Files │ │ Text │ │ Vectors │
└─────────────┘ └─────────────┘ └─────────────┘
│
▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Answer │◀────│ LLM │◀────│ Retrieve │
│ Query │ │ Generate │ │ Context │
└─────────────┘ └─────────────┘ └─────────────┘


## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- 8GB+ RAM (recommended)
- (Optional) GPU for faster embeddings

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/chat-with-files.git
cd chat-with-files

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your settings

# Start the server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 127.0.0.1 --port 8000
