# Document Parser Usage Guide

## Overview
The Document Parser library provides a unified interface for parsing various document formats (PDF, DOCX, and TXT) into a structured format. This guide explains how to use the library effectively.

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from src.parsers.parser_factory import DocumentParserFactory

# Create a parser factory
factory = DocumentParserFactory()

# Get the appropriate parser for your file
parser = factory.create_parser('resume.pdf')  # or .docx, .txt

# Parse the document
result = parser.parse('path/to/your/document')

# Access the parsed content
content = result['content']
metadata = result['metadata']
```

## Supported Formats

### PDF Files
- Handles both text-based and scanned PDFs
- Extracts text, metadata, and structure
- Supports encrypted PDFs (with password)

```python
pdf_parser = factory.create_parser('document.pdf')
result = pdf_parser.parse('document.pdf', password='optional_password')
```

### DOCX Files
- Extracts formatted text and styles
- Preserves document structure
- Handles tables and lists

```python
docx_parser = factory.create_parser('document.docx')
result = docx_parser.parse('document.docx')
```

### TXT Files
- Auto-detects text encoding
- Identifies document structure
- Handles various line endings

```python
txt_parser = factory.create_parser('document.txt')
result = txt_parser.parse('document.txt')
```

## Output Format

All parsers return a standardized dictionary with the following structure:

```python
{
    'content': {
        'text': str,          # Full document text
        'sections': List[str], # Document sections
        'metadata': {         # Document metadata
            'title': str,
            'author': str,
            'created_date': str,
            'modified_date': str
        }
    },
    'metadata': {
        'format': str,        # Original file format
        'size': int,         # File size in bytes
        'pages': int,        # Number of pages (if applicable)
        'encoding': str      # Text encoding (for TXT files)
    }
}
```

## Error Handling

The library provides comprehensive error handling:

```python
from src.parsers.exceptions import (
    ParserError,
    FileNotFoundError,
    InvalidFormatError,
    EncryptedFileError
)

try:
    result = parser.parse('document.pdf')
except FileNotFoundError:
    print("File not found")
except InvalidFormatError:
    print("Invalid file format")
except EncryptedFileError:
    print("File is encrypted")
except ParserError as e:
    print(f"Parsing error: {str(e)}")
```

## Performance Considerations

- All parsers are optimized for memory usage
- Processing time scales linearly with document size
- Large files (>100MB) are processed in chunks
- Caching is implemented for frequently accessed documents

## Best Practices

1. Always use the factory to create parsers
2. Handle exceptions appropriately
3. Close parsers when done (they implement context managers)
4. Use batch processing for multiple files
5. Monitor memory usage for large documents

## Examples

### Batch Processing

```python
documents = ['doc1.pdf', 'doc2.docx', 'doc3.txt']
results = []

for doc in documents:
    parser = factory.create_parser(doc)
    results.append(parser.parse(doc))
```

### Using Context Managers

```python
with factory.create_parser('document.pdf') as parser:
    result = parser.parse('document.pdf')
```

### Custom Configuration

```python
parser = factory.create_parser('document.pdf', config={
    'chunk_size': 1024 * 1024,  # 1MB chunks
    'cache_enabled': True,
    'max_memory': '512MB'
})
``` 