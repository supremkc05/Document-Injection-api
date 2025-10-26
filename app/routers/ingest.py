from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional
import io

from app.database import get_db
from app.schemas import (
    DocumentIngestResponse,
    ChunkingStrategy
)
from app.services.document_service import DocumentIngestionService

router = APIRouter(prefix="/api", tags=["Document Ingestion"])


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(
    file: UploadFile = File(..., description="PDF or TXT file to ingest"),
    chunking_strategy: ChunkingStrategy = Form(
        default=ChunkingStrategy.STRATEGY_A,
        description="Chunking strategy to use"
    ),
    chunk_size: Optional[int] = Form(
        default=None,
        description="Chunk size (for strategy A)"
    ),
    chunk_overlap: Optional[int] = Form(
        default=None,
        description="Chunk overlap (for strategy A)"
    ),
    db: Session = Depends(get_db)
):
    """
    Ingest a document (PDF or TXT) into the system
    
    - **file**: The document file to upload (.pdf or .txt)
    - **chunking_strategy**: Choose between 'strategy_a' (fixed-size) or 'strategy_b' (semantic)
    - **chunk_size**: Optional chunk size for strategy A
    - **chunk_overlap**: Optional chunk overlap for strategy A
    
    Returns:
    - **document_id**: Unique identifier for the document
    - **chunks**: Number of chunks created
    - **status**: Status of the operation
    """
    # Validate file type
    allowed_extensions = [".pdf", ".txt"]
    file_extension = "." + file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )

    try:
        # Read file content
        file_content = await file.read()
        file_io = io.BytesIO(file_content)

        # Process document
        service = DocumentIngestionService(db)
        document_id, num_chunks = await service.ingest_document(
            filename=file.filename,
            file_content=file_io,
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        return DocumentIngestResponse(
            document_id=document_id,
            chunks=num_chunks,
            status="success"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
    finally:
        await file.close()
