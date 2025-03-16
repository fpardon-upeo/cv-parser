# Document Parsing Guide

This guide explains how to use the CV Parser's document parsing functionality to extract content and metadata from various document formats.

## Supported Formats

The CV Parser currently supports the following document formats:

- PDF (`.pdf`) - Using PyPDF2
- Microsoft Word (`.docx`) - Using python-docx
- Plain Text (`.txt`) - With encoding detection

## Basic Usage

### Step 1: Choose the Right Parser

The first step is to select the appropriate parser for your document format. The `DocumentParserFactory` makes this easy:

```python
from app.services.document_parser import DocumentParserFactory

# Create a parser based on file extension
parser = DocumentParserFactory.create_parser('pdf')  # or 'docx', 'txt'
```

### Step 2: Load Document Content

Next, load the document content as bytes:

```python
# From a file
with open('document.pdf', 'rb') as f:
    content = f.read()

# Or from a request/upload
content = request.files['document'].read()
```

### Step 3: Parse the Document

Use the parser to extract content and metadata:

```python
result = parser.parse(content)
```

The `result` dictionary contains:

- `content`: The extracted text content
- `structure`: Document structure information (varies by format)
- `metadata`: Document metadata (title, author, etc.)

## Error Handling

The parsing system uses a hierarchy of exceptions for different error types:

```python
from app.services.document_parser import DocumentParsingError, ValidationError, EncodingError

try:
    result = parser.parse(content)
except ValidationError as e:
    # Handle validation errors (invalid format, etc.)
except EncodingError as e:
    # Handle encoding issues (for TXT files)
except DocumentParsingError as e:
    # Handle general parsing errors
```

Format-specific errors are also available:

```python
from app.services.pdf_parser import PDFEncryptedError, PDFDamagedError
from app.services.docx_parser import DOCXCorruptedError
from app.services.txt_parser import TXTEncodingError

try:
    result = parser.parse(content)
except PDFEncryptedError:
    # Handle encrypted PDF
except PDFDamagedError:
    # Handle damaged PDF
except DOCXCorruptedError:
    # Handle corrupted DOCX
except TXTEncodingError:
    # Handle TXT encoding issues
```

## Working with Parsed Results

### Text Content

The `content` field contains the extracted text:

```python
text = result['content']
print(f"Document contains {len(text)} characters")
```

### Metadata

The `metadata` field contains document properties:

```python
metadata = result['metadata']

# Common metadata fields
title = metadata.get('title', 'Untitled')
author = metadata.get('author', 'Unknown')
creation_date = metadata.get('creation_date')

# Format-specific metadata
if 'page_count' in metadata:  # PDF
    print(f"PDF has {metadata['page_count']} pages")
    
if 'paragraph_count' in metadata:  # DOCX
    print(f"DOCX has {metadata['paragraph_count']} paragraphs")
    
if 'encoding' in metadata:  # TXT
    print(f"TXT encoding: {metadata['encoding']}")
```

### Document Structure

The `structure` field contains format-specific structural information:

```python
structure = result['structure']

# PDF structure
if 'pages' in structure:
    for page in structure['pages']:
        print(f"Page {page['number']}: {page['size']}")
        
# DOCX structure
if 'headings' in structure:
    for heading in structure['headings']:
        print(f"Heading (level {heading['level']}): {heading['text']}")
        
# TXT structure
if 'headers' in structure:
    for header in structure['headers']:
        print(f"Header: {header['text']}")
```

## Performance Considerations

- For large documents, consider processing in chunks
- Monitor memory usage when parsing large files
- Use validation before full parsing for quick format checks

## Best Practices

1. **Always use error handling**: Wrap parsing code in try/except blocks
2. **Validate before parsing**: Use `parser.validate()` for quick format checks
3. **Check content type**: Ensure you're using the correct parser for the file type
4. **Handle encoding issues**: Especially important for TXT files
5. **Extract metadata separately**: Use `parser.extract_metadata()` if you only need metadata 