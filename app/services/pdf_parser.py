"""PDF document parsing service.

This module provides the implementation for parsing PDF documents.
"""
import io
import re
import PyPDF2
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.services.document_parser import (
    DocumentParser,
    DocumentParsingError,
    ValidationError,
    DocumentParserFactory
)


class PDFParsingError(DocumentParsingError):
    """Raised when PDF parsing fails."""
    pass


class PDFEncryptedError(DocumentParsingError):
    """Raised when an encrypted PDF is encountered."""
    pass


class PDFDamagedError(DocumentParsingError):
    """Raised when a damaged PDF is encountered."""
    pass


class PDFParser(DocumentParser):
    """Parser for PDF documents."""
    
    def __init__(self):
        super().__init__()
        self._pdf_reader = None
        self._structure = None
    
    def parse(self, content: bytes) -> Dict[str, Any]:
        """Parse a PDF document and extract its content and structure.
        
        Args:
            content: Raw PDF file content as bytes
            
        Returns:
            Dict containing parsed content, structure, and metadata
            
        Raises:
            PDFParsingError: If any parsing error occurs
            PDFEncryptedError: If the PDF is encrypted
            PDFDamagedError: If the PDF is damaged
            ValidationError: If the content fails validation
        """
        try:
            self._set_content(content)
            
            # Convert bytes to file-like object
            file_stream = io.BytesIO(content)
            self._pdf_reader = PyPDF2.PdfReader(file_stream)
            
            if self._pdf_reader.is_encrypted:
                raise PDFEncryptedError("Cannot parse encrypted PDF")
            
            parsed_content = self._extract_text()
            structure = self._extract_structure()
            metadata = self.extract_metadata()
            
            return {
                "content": parsed_content,
                "structure": structure,
                "metadata": metadata
            }
            
        except PyPDF2.errors.PdfReadError as e:
            raise PDFDamagedError(f"Failed to read PDF: {str(e)}")
        except (AttributeError, ValueError, TypeError) as e:
            if "seek" in str(e):
                raise PDFDamagedError(f"Invalid PDF format: {str(e)}")
            raise PDFParsingError(f"PDF parsing failed: {str(e)}")
        except Exception as e:
            raise PDFParsingError(f"PDF parsing failed: {str(e)}")
    
    def extract_metadata(self) -> Dict[str, Any]:
        """Extract document metadata.
        
        Returns:
            Dict containing document metadata
            
        Raises:
            PDFParsingError: If metadata extraction fails
        """
        if not self._pdf_reader:
            raise PDFParsingError("No PDF loaded for metadata extraction")
        
        try:
            info = self._pdf_reader.metadata
            if info is None:
                return {}
                
            metadata = {}
            
            # Extract standard metadata fields
            if info.get('/Title'):
                metadata['title'] = info.get('/Title')
            if info.get('/Author'):
                metadata['author'] = info.get('/Author')
            if info.get('/Subject'):
                metadata['subject'] = info.get('/Subject')
            if info.get('/Keywords'):
                metadata['keywords'] = info.get('/Keywords')
            if info.get('/Producer'):
                metadata['producer'] = info.get('/Producer')
            if info.get('/Creator'):
                metadata['creator'] = info.get('/Creator')
                
            # Handle dates
            if info.get('/CreationDate'):
                creation_date = self._parse_pdf_date(info.get('/CreationDate'))
                if creation_date:
                    metadata['creation_date'] = creation_date
                    
            if info.get('/ModDate'):
                mod_date = self._parse_pdf_date(info.get('/ModDate'))
                if mod_date:
                    metadata['modification_date'] = mod_date
            
            # Add document structure information
            metadata['page_count'] = len(self._pdf_reader.pages)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting PDF metadata: {str(e)}")
            return {}
    
    def validate(self) -> bool:
        """Validate PDF content.
        
        Returns:
            bool: True if document is valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not self._get_content():
            raise PDFParsingError("No content has been set for validation")
            
        try:
            # Check if content starts with PDF signature
            if not self._content.startswith(b'%PDF-'):
                raise ValidationError("Not a valid PDF file (missing PDF signature)")
                
            # Check if we can read the PDF
            file_stream = io.BytesIO(self._content)
            reader = PyPDF2.PdfReader(file_stream)
            
            # Check if PDF has pages
            if len(reader.pages) == 0:
                raise ValidationError("PDF has no pages")
                
            return True
            
        except PyPDF2.errors.PdfReadError as e:
            raise ValidationError(f"Invalid PDF structure: {str(e)}")
        except Exception as e:
            raise ValidationError(f"PDF validation failed: {str(e)}")
    
    def _extract_text(self) -> str:
        """Extract text content from PDF.
        
        Returns:
            str: Extracted text content
            
        Raises:
            PDFParsingError: If text extraction fails
        """
        if not self._pdf_reader:
            raise PDFParsingError("No PDF loaded for text extraction")
            
        try:
            text_content = []
            
            for page_num, page in enumerate(self._pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                except Exception as e:
                    self.logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            raise PDFParsingError(f"Failed to extract text: {str(e)}")
    
    def _extract_structure(self) -> Dict[str, Any]:
        """Extract document structure from PDF.
        
        Returns:
            Dict containing document structure
            
        Raises:
            PDFParsingError: If structure extraction fails
        """
        if not self._pdf_reader:
            raise PDFParsingError("No PDF loaded for structure extraction")
            
        try:
            structure = {
                'pages': [],
                'sections': [],
                'images': []
            }
            
            # Extract page information
            for page_num, page in enumerate(self._pdf_reader.pages):
                page_info = {
                    'number': page_num + 1,
                    'size': (page.mediabox.width, page.mediabox.height),
                    'rotation': page.get('/Rotate', 0)
                }
                structure['pages'].append(page_info)
            
            # Try to extract outline/bookmarks if available
            if hasattr(self._pdf_reader, 'outline') and self._pdf_reader.outline:
                structure['outline'] = self._extract_outline(self._pdf_reader.outline)
            
            return structure
            
        except Exception as e:
            self.logger.error(f"Error extracting PDF structure: {str(e)}")
            return {'pages': [], 'sections': [], 'images': []}
    
    def _extract_outline(self, outline) -> List[Dict[str, Any]]:
        """Extract outline/bookmarks from PDF.
        
        Args:
            outline: PDF outline object
            
        Returns:
            List of outline entries
        """
        result = []
        
        if isinstance(outline, list):
            for item in outline:
                if isinstance(item, dict) and '/Title' in item:
                    entry = {'title': item['/Title']}
                    if '/Page' in item:
                        entry['page'] = item['/Page']
                    if '/Kids' in item:
                        entry['children'] = self._extract_outline(item['/Kids'])
                    result.append(entry)
                elif isinstance(item, list):
                    result.extend(self._extract_outline(item))
        
        return result
    
    def _parse_pdf_date(self, date_str: str) -> Optional[str]:
        """Parse PDF date format to ISO format.
        
        Args:
            date_str: PDF date string (e.g., "D:20200101120000+01'00'")
            
        Returns:
            ISO formatted date string or None if parsing fails
        """
        try:
            # Remove 'D:' prefix if present
            if date_str.startswith('D:'):
                date_str = date_str[2:]
                
            # Basic format: YYYYMMDDHHmmSS
            if len(date_str) >= 14:
                year = int(date_str[0:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                hour = int(date_str[8:10])
                minute = int(date_str[10:12])
                second = int(date_str[12:14])
                
                dt = datetime(year, month, day, hour, minute, second)
                return dt.isoformat()
        except:
            return ""

# Register the PDF parser with the factory
DocumentParserFactory.register_parser("pdf", PDFParser) 