# Document Injection API

FastAPI backend for document ingestion and conversational RAG with vector storage.

## Features

* Document ingestion (PDF/TXT) with smart chunking
* Conversational RAG with session memory
* Interview booking system
* Standalone system (no external LLM required)
* Qdrant Cloud vector storage
* Redis memory with in-memory fallback

## Tech Stack

**FastAPI** · **SQLite** · **Qdrant Cloud** · **Redis** · **sentence-transformers**

## Quick Start

```bash
# Clone and setup
git clone https://github.com/supremkc05/Document-Injection-api.git
cd Document-Injection-api
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure (copy .env.example to .env and add your Qdrant credentials)
cp .env.example .env

# Run server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API Docs:** http://localhost:8000/docs

## Configuration

Required in `.env`:
```env
QDRANT_URL=your-qdrant-cloud-url
QDRANT_API_KEY=your-api-key
```

Required for redis
```env
REDIS_HOST=localhost
REDIS_PORT=6379
```


## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ingest` | POST | Upload document (PDF/TXT) |
| `/api/chat` | POST | Query with RAG |
| `/api/chat/{session_id}/history` | GET | Get chat history |
| `/api/bookings` | POST/GET | Manage bookings |

## Chunking Strategies

- **`fixed_size`**: Fixed chunks with overlap (default: 500 chars)
- **`semantic`**: Sentence-based semantic chunks (min: 200 chars)

