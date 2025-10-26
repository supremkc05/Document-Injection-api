from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import ingest, chat, bookings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("🚀 Starting PALM Backend...")
    print("📊 Initializing SQLite database: palm_local.db")
    init_db()
    print("✅ Database initialized")
    print("✨ Application ready!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down PALM Backend...")


# Create FastAPI application
app = FastAPI(
    title="PALM Backend API",
    description="""
    ## PALM - Document Ingestion and Conversational RAG Backend
    
    This backend provides:
    - **Document Ingestion**: Upload and process PDF/TXT documents with customizable chunking
    - **Conversational RAG**: Multi-turn conversations with context from ingested documents
    - **Interview Bookings**: Create and manage interview bookings
    
    ### Technologies
    - FastAPI for REST APIs
    - Mock Qdrant for vector storage (in-memory)
    - SQLite for metadata storage
    - Mock Redis for conversation memory (in-memory)
    
    ### Features
    - Two chunking strategies (fixed-size and semantic)
    - Custom RAG implementation (no LangChain chains)
    - Session-based conversation memory
    - Fully typed with Pydantic
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(bookings.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "PALM Backend API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "ingest": "/api/ingest",
            "chat": "/api/chat",
            "bookings": "/api/bookings"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "SQLite (palm_local.db)",
        "vector_store": "Mock Qdrant (in-memory)",
        "memory": "Mock Redis (in-memory)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
