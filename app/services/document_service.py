from typing import BinaryIO, Tuple
from sqlalchemy.orm import Session
import os

from app.repositories.document_repository import DocumentRepository
from app.utils.document_parser import DocumentParser
from app.utils.chunking import get_chunking_strategy
from app.utils.embeddings import embedding_manager
from app.utils.qdrant_manager import qdrant_manager
from app.schemas import ChunkingStrategy


class DocumentIngestionService:
    """Service for handling document ingestion"""

    def __init__(self, db: Session):
        self.db = db
        self.document_repo = DocumentRepository(db)

    async def ingest_document(
        self,
        filename: str,
        file_content: BinaryIO,
        chunking_strategy: ChunkingStrategy,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> Tuple[str, int]:
        """
        Process and ingest a document
        
        Args:
            filename: Name of the file
            file_content: Binary file content
            chunking_strategy: Chunking strategy to use
            chunk_size: Optional chunk size
            chunk_overlap: Optional chunk overlap
            
        Returns:
            Tuple of (document_id, number_of_chunks)
        """
        # 1. Parse document to extract text
        text = DocumentParser.parse_file(filename, file_content)

        if not text:
            raise ValueError("No text could be extracted from the document")

        # 2. Chunk the text using selected strategy
        chunker = get_chunking_strategy(
            strategy_name=chunking_strategy.value,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = chunker.chunk_text(text)

        if not chunks:
            raise ValueError("No chunks created from document")

        # 3. Generate embeddings for all chunks
        embeddings = embedding_manager.embed_batch(chunks)

        # 4. Store document metadata in MySQL
        document = self.document_repo.create_document(
            filename=filename,
            total_chunks=len(chunks)
        )

        # 5. Store chunks and embeddings in Qdrant
        try:
            stored_count = qdrant_manager.store_vectors(
                document_id=document.document_id,
                chunks=chunks,
                embeddings=embeddings
            )

            if stored_count != len(chunks):
                raise ValueError(f"Mismatch in stored vectors: {stored_count} vs {len(chunks)}")

        except Exception as e:
            # Rollback database changes if Qdrant storage fails
            self.document_repo.delete_document(document.document_id)
            raise ValueError(f"Error storing vectors in Qdrant: {str(e)}")

        return document.document_id, len(chunks)

    def get_document(self, document_id: str):
        """Get document metadata by ID"""
        return self.document_repo.get_document_by_id(document_id)

    def list_documents(self):
        """List all documents"""
        return self.document_repo.get_all_documents()

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its vectors"""
        # Delete from Qdrant
        qdrant_manager.delete_by_document_id(document_id)
        
        # Delete from MySQL
        return self.document_repo.delete_document(document_id)
