# PALM Backend – Document Ingestion and Conversational RAG

A FastAPI-based backend for document ingestion, vector storage, and conversational Retrieval-Augmented Generation (RAG), including an interview booking system.

## Features

* Document ingestion API for PDF/TXT files with two chunking strategies
* Conversational RAG API with session-based memory
* Interview booking CRUD API
* Custom RAG pipeline (no LangChain chains)
* Vector storage using Qdrant 
* Redis-based memory
* SQLite for metadata storage
* Modular layered architecture (Routers → Services → Repositories → Storage)

## Tech Stack

| Component      | Technology              |
| -------------- | ----------------------- |
| Framework      | FastAPI                 |
| Database       | SQLite                  |
| Vector Store   | Qdrant                  |
| Cache/Memory   | Redis                   |
| Embeddings     | Mock embedding service  |
| PDF Processing | PyPDF                   |

## Project Structure

```
palm/
  app/
    main.py
    routers/ (ingest, chat, bookings)
    services/ (business logic)
    repositories/ (database access)
    utils/ (chunking, qdrant, redis, embeddings)
  tests/
  requirements.txt
  docker-compose.yml
  README.md
```

## Prerequisites

* Python 3.10+

## Quick Start

```
cd palm
python -m venv venv
source venv/bin/activate   # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Access API documentation at:
`http://localhost:8000/docs`



## API Endpoints

| Endpoint                       | Method      | Description                          |
| ------------------------------ | ----------- | ------------------------------------ |
| /api/ingest                    | POST        | Upload and chunk a document          |
| /api/chat                      | POST        | Send user query and get RAG response |
| /api/chat/{session_id}/history | GET         | Get chat history                     |
| /api/chat/{session_id}         | DELETE      | Clear session                        |
| /api/bookings                  | POST, GET   | Create or list bookings              |
| /api/bookings/{id}             | GET, DELETE | Retrieve or delete booking           |


## Notes

* No LangChain chains or external frameworks
* Two chunking strategies: fixed and semantic

## To run the api 
`.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8888`

---

