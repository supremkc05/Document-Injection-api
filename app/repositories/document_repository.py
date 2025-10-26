from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from app.database import Document


class DocumentRepository:
    """Repository for document-related database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_document(
        self,
        filename: str,
        total_chunks: int,
        file_path: Optional[str] = None
    ) -> Document:
        """Create a new document record"""
        document = Document(
            document_id=str(uuid.uuid4()),
            filename=filename,
            total_chunks=total_chunks,
            file_path=file_path
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by document_id"""
        return self.db.query(Document).filter(
            Document.document_id == document_id
        ).first()

    def get_all_documents(self) -> List[Document]:
        """Get all documents"""
        return self.db.query(Document).all()

    def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        document = self.get_document_by_id(document_id)
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        return False
