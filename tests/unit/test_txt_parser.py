"""Unit tests for TXT parser implementation."""
import pytest
from typing import Dict, Any
import chardet

from app.services.txt_parser import (
    TXTParser,
    TXTParsingError,
    TXTEncodingError
)
from app.services.document_parser import ValidationError


def create_test_txt(content: str, encoding: str = 'utf-8') -> bytes:
    """Create a test TXT file with given content and encoding."""
    return content.encode(encoding)


def create_structured_txt() -> bytes:
    """Create a structured TXT file with various elements."""
    content = """DOCUMENT TITLE
==============

1. Introduction
--------------
This is a sample text document with structured content.
It contains multiple sections and formatting elements.

1.1 Purpose
• First bullet point
• Second bullet point
• Third bullet point

2. Main Content
--------------
2.1 Numbered List
1. First item
2. Second item
3. Third item

2.2 Different Indentation Levels
    This text is indented
        This text is indented more
    Back to first indentation
Back to no indentation

3. Conclusion
============
Final thoughts and summary.
"""
    return create_test_txt(content)


def create_multilingual_txt() -> bytes:
    """Create a text file with content in multiple languages."""
    content = """English Section
-------------
This is a sample text in English with common words like the, and, for, that.

Spanish Section
--------------
Este es un ejemplo en español con palabras comunes como el, la, que, en.

French Section
-------------
C'est un exemple en français avec des mots communs comme le, la, les, des.

German Section
-------------
Dies ist ein Beispiel auf Deutsch mit häufigen Wörtern wie der, die, das, und."""
    return create_test_txt(content)


class TestTXTParser:
    """Test suite for TXTParser class."""
    
    def test_parse_basic_txt(self):
        """Test parsing a basic TXT with simple content."""
        parser = TXTParser()
        content = create_test_txt("Sample text content\nWith multiple lines")
        
        result = parser.parse(content)
        
        assert "content" in result
        assert "Sample text content" in result["content"]
        assert "With multiple lines" in result["content"]
        assert "structure" in result
        assert "metadata" in result
        
    def test_parse_with_different_encodings(self):
        """Test parsing TXT files with different encodings."""
        parser = TXTParser()
        # Test UTF-8
        content_utf8 = create_test_txt("UTF-8 content with unicode: ñáéíóú", 'utf-8')
        result = parser.parse(content_utf8)
        assert "ñáéíóú" in result["content"]
        assert result["metadata"]["encoding"].lower() in ['utf-8', 'utf8']
        
        # Test ASCII
        content_ascii = create_test_txt("ASCII content", 'ascii')
        result = parser.parse(content_ascii)
        assert result["metadata"]["encoding"].lower() in ['ascii', 'utf-8']
        
        # Test ISO-8859-1
        content_iso = create_test_txt("ISO content with special chars: áéíóú", 'iso-8859-1')
        result = parser.parse(content_iso)
        assert "áéíóú" in result["content"]
        
    def test_parse_invalid_encoding(self):
        """Test parsing a TXT file with invalid encoding raises appropriate error."""
        parser = TXTParser()
        # Create invalid UTF-8 sequence
        content = b"Invalid \x80 UTF-8 sequence"
        
        with pytest.raises(TXTEncodingError) as exc_info:
            parser.parse(content)
        assert "Failed to decode" in str(exc_info.value)
        
    def test_extract_structure(self):
        """Test extraction of TXT structure information."""
        parser = TXTParser()
        content = create_structured_txt()
        
        result = parser.parse(content)
        structure = result["structure"]
        
        assert len(structure["sections"]) > 0
        assert structure["paragraphs"] > 0
        assert structure["lists"]["bullet_points"] == 3
        assert structure["lists"]["numbered"] == 3
        assert structure["section_markers"] > 0
        assert len(structure["indentation_levels"]) > 1
        
    def test_validation(self):
        """Test TXT validation."""
        parser = TXTParser()
        content = create_test_txt("Valid content")
        
        # Set content before validation
        parser._set_content(content)
        parser._detect_and_decode_content()
        
        assert parser.validate() is True
        
    def test_validation_empty_content(self):
        """Test validation with empty content raises error."""
        parser = TXTParser()
        content = create_test_txt("")
        
        parser._set_content(content)
        parser._detect_and_decode_content()
        
        with pytest.raises(ValidationError) as exc_info:
            parser.validate()
        assert "Empty content" in str(exc_info.value)
        
    def test_language_detection(self):
        """Test language detection functionality."""
        parser = TXTParser()
        content = create_multilingual_txt()
        
        # Test each section separately
        english_section = create_test_txt("This is a test with the words and that for testing.")
        result = parser.parse(english_section)
        assert result["metadata"]["detected_language"] == "en"
        
        spanish_section = create_test_txt("Este es una prueba con el y la que en español.")
        result = parser.parse(spanish_section)
        assert result["metadata"]["detected_language"] == "es"
        
    def test_text_normalization(self):
        """Test text content normalization."""
        parser = TXTParser()
        content = create_test_txt("Line 1\r\nLine 2\rLine 3\nLine 4\n\n\nLine 5")
        
        result = parser.parse(content)
        
        # Check that different line endings are normalized
        assert result["content"].count("\r") == 0
        # Check that multiple empty lines are reduced to one
        assert result["content"].count("\n\n\n") == 0
        assert "Line 1" in result["content"]
        assert "Line 5" in result["content"] 