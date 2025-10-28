from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ChunkingStrategy(str, Enum):
    FIXED_SIZE = "fixed_size"  # Fixed-size chunks with overlap
    SEMANTIC = "semantic"  # Semantic/sentence-based chunks


class DocumentIngestRequest(BaseModel):
    chunking_strategy: ChunkingStrategy = Field(
        default=ChunkingStrategy.FIXED_SIZE,
        description="Chunking strategy to use"
    )
    chunk_size: Optional[int] = Field(
        default=None,
        description="Chunk size for strategy A"
    )
    chunk_overlap: Optional[int] = Field(
        default=None,
        description="Chunk overlap for strategy A"
    )


class DocumentIngestResponse(BaseModel):
    document_id: str
    chunks: int
    status: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for the conversation")
    user_message: str = Field(..., description="User's message")


class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: Optional[List[str]] = None


class BookingRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    date: str = Field(..., description="Booking date in YYYY-MM-DD format")
    time: str = Field(..., description="Booking time in HH:MM format")


class BookingResponse(BaseModel):
    booking_id: str
    status: str


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    upload_time: datetime
    total_chunks: int

    class Config:
        from_attributes = True


class BookingMetadata(BaseModel):
    booking_id: str
    name: str
    email: str
    date: str
    time: str
    created_at: datetime

    class Config:
        from_attributes = True
