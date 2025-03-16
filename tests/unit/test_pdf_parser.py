"""Unit tests for PDF parser implementation."""
import pytest
from datetime import datetime
from io import BytesIO
from PyPDF2 import PdfWriter, PdfReader
from typing import Dict, Any

from app.services.pdf_parser import (
    PDFParser,
    PDFParsingError,
    PDFEncryptedError,
    PDFDamagedError
)
from app.services.document_parser import ValidationError


def create_test_pdf(content: str = "Test content", metadata: Dict[str, Any] = None) -> bytes:
    """Create a test PDF file with given content and metadata."""
    writer = PdfWriter()
    
    # Add a page with content
    page = writer.add_blank_page(width=612, height=792)
    page.insert_text(text=content, x=50, y=700)
    
    # Add metadata if provided
    if metadata:
        writer.add_metadata(metadata)
    
    # Write to bytes buffer
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def create_encrypted_pdf(password: str = "test123") -> bytes:
    """Create an encrypted test PDF file."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    page.insert_text(text="Encrypted content", x=50, y=700)
    writer.encrypt(password)
    
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


class TestPDFParser:
    """Test suite for PDFParser class."""
    
    def test_parse_basic_pdf(self):
        """Test parsing a basic PDF with text content."""
        parser = PDFParser()
        content = create_test_pdf("Sample PDF content")
        
        result = parser.parse(content)
        
        assert "content" in result
        assert "Sample PDF content" in result["content"]
        assert "structure" in result
        assert "metadata" in result
        
    def test_parse_with_metadata(self):
        """Test parsing PDF with metadata."""
        metadata = {
            "/Title": "Test Document",
            "/Author": "Test Author",
            "/Subject": "Test Subject",
            "/Creator": "Test Creator",
            "/Producer": "Test Producer",
            "/CreationDate": f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        parser = PDFParser()
        content = create_test_pdf("Content", metadata)
        
        result = parser.parse(content)
        
        assert result["metadata"]["title"] == "Test Document"
        assert result["metadata"]["author"] == "Test Author"
        assert result["metadata"]["subject"] == "Test Subject"
        assert result["metadata"]["creator"] == "Test Creator"
        assert result["metadata"]["producer"] == "Test Producer"
        assert "creation_date" in result["metadata"]
        
    def test_parse_encrypted_pdf(self):
        """Test parsing an encrypted PDF raises appropriate error."""
        parser = PDFParser()
        content = create_encrypted_pdf()
        
        with pytest.raises(PDFEncryptedError) as exc_info:
            parser.parse(content)
        assert "Cannot parse encrypted PDF" in str(exc_info.value)
        
    def test_parse_damaged_pdf(self):
        """Test parsing a damaged PDF raises appropriate error."""
        parser = PDFParser()
        content = b"This is not a valid PDF file"
        
        with pytest.raises(PDFDamagedError) as exc_info:
            parser.parse(content)
        assert "Failed to read PDF" in str(exc_info.value)
        
    def test_extract_structure(self):
        """Test extraction of PDF structure information."""
        parser = PDFParser()
        content = create_test_pdf("Page content")
        
        result = parser.parse(content)
        structure = result["structure"]
        
        assert "pages" in structure
        assert len(structure["pages"]) == 1
        assert structure["pages"][0]["page_number"] == 1
        assert structure["pages"][0]["text_length"] > 0
        assert "has_images" in structure
        assert "has_tables" in structure
        
    def test_validation(self):
        """Test PDF validation."""
        parser = PDFParser()
        content = create_test_pdf()
        
        # Set content before validation
        parser._set_content(content)
        parser._pdf_reader = PdfReader(BytesIO(content))
        
        assert parser.validate() is True
        
    def test_validation_no_content(self):
        """Test validation without content raises error."""
        parser = PDFParser()
        
        with pytest.raises(PDFParsingError) as exc_info:
            parser.validate()
        assert "No content to validate" in str(exc_info.value)
        
    def test_parse_pdf_date(self):
        """Test PDF date string parsing."""
        parser = PDFParser()
        
        # Test valid date
        date_str = "D:20240328123456"
        result = parser._parse_pdf_date(date_str)
        assert result == "2024-03-28T12:34:56"
        
        # Test empty date
        assert parser._parse_pdf_date("") == ""
        
        # Test invalid date
        assert parser._parse_pdf_date("invalid") == "" 