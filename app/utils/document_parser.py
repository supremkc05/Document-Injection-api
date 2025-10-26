from typing import BinaryIO
import pypdf
from pathlib import Path


class DocumentParser:
    """Parser for extracting text from different document types"""

    @staticmethod
    def parse_pdf(file_content: BinaryIO) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_content: Binary file content
            
        Returns:
            Extracted text
        """
        try:
            pdf_reader = pypdf.PdfReader(file_content)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")

    @staticmethod
    def parse_txt(file_content: BinaryIO) -> str:
        """
        Extract text from TXT file
        
        Args:
            file_content: Binary file content
            
        Returns:
            Extracted text
        """
        try:
            text = file_content.read()
            if isinstance(text, bytes):
                text = text.decode('utf-8')
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing TXT: {str(e)}")

    @staticmethod
    def parse_file(filename: str, file_content: BinaryIO) -> str:
        """
        Parse file based on extension
        
        Args:
            filename: Name of the file
            file_content: Binary file content
            
        Returns:
            Extracted text
        """
        extension = Path(filename).suffix.lower()
        
        if extension == '.pdf':
            return DocumentParser.parse_pdf(file_content)
        elif extension == '.txt':
            return DocumentParser.parse_txt(file_content)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
