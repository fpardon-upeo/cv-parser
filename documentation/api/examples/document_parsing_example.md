# Document Parsing API Examples

## Basic Usage

### Parsing a Document

```python
from app.services.document_parser import DocumentParserFactory

# Create a parser for the appropriate file type
parser = DocumentParserFactory.create_parser('pdf')  # or 'docx', 'txt'

# Read file content
with open('document.pdf', 'rb') as f:
    content = f.read()

# Parse the document
result = parser.parse(content)

# Access parsed content
text_content = result['content']
document_structure = result['structure']
metadata = result['metadata']

print(f"Document title: {metadata.get('title', 'Unknown')}")
print(f"Document author: {metadata.get('author', 'Unknown')}")
print(f"Total text length: {len(text_content)} characters")
```

### Error Handling

```python
from app.services.document_parser import DocumentParserFactory
from app.services.document_parser import DocumentParsingError, ValidationError, EncodingError

try:
    parser = DocumentParserFactory.create_parser('pdf')
    with open('document.pdf', 'rb') as f:
        content = f.read()
    result = parser.parse(content)
    
except ValidationError as e:
    print(f"Document validation failed: {str(e)}")
    
except EncodingError as e:
    print(f"Encoding issue: {str(e)}")
    
except DocumentParsingError as e:
    print(f"Parsing error: {str(e)}")
    
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## Advanced Usage

### Working with PDF Documents

```python
from app.services.document_parser import DocumentParserFactory
from app.services.pdf_parser import PDFParser, PDFEncryptedError, PDFDamagedError

try:
    # Create PDF parser
    parser = DocumentParserFactory.create_parser('pdf')
    
    # Read file content
    with open('document.pdf', 'rb') as f:
        content = f.read()
    
    # Parse the document
    result = parser.parse(content)
    
    # Access PDF-specific structure
    pages = result['structure']['pages']
    print(f"Document has {len(pages)} pages")
    
    # Check for outline/bookmarks
    if 'outline' in result['structure']:
        print("Document has bookmarks/outline")
        
except PDFEncryptedError:
    print("Cannot process encrypted PDF")
    
except PDFDamagedError:
    print("PDF file is damaged or corrupted")
    
except Exception as e:
    print(f"Error: {str(e)}")
```

### Working with DOCX Documents

```python
from app.services.document_parser import DocumentParserFactory
from app.services.docx_parser import DOCXParser, DOCXCorruptedError

try:
    # Create DOCX parser
    parser = DocumentParserFactory.create_parser('docx')
    
    # Read file content
    with open('document.docx', 'rb') as f:
        content = f.read()
    
    # Parse the document
    result = parser.parse(content)
    
    # Access DOCX-specific structure
    headings = result['structure']['headings']
    tables = result['structure']['tables']
    
    print(f"Document has {len(headings)} headings and {len(tables)} tables")
    
except DOCXCorruptedError:
    print("DOCX file is corrupted")
    
except Exception as e:
    print(f"Error: {str(e)}")
```

### Working with TXT Documents

```python
from app.services.document_parser import DocumentParserFactory
from app.services.txt_parser import TXTParser, TXTEncodingError

try:
    # Create TXT parser
    parser = DocumentParserFactory.create_parser('txt')
    
    # Read file content
    with open('document.txt', 'rb') as f:
        content = f.read()
    
    # Parse the document
    result = parser.parse(content)
    
    # Access TXT-specific information
    encoding = result['encoding']
    confidence = result['confidence']
    
    print(f"Document encoding: {encoding} (confidence: {confidence:.2f})")
    
    # Access structure information
    if 'headers' in result['structure']:
        headers = result['structure']['headers']
        print(f"Document has {len(headers)} headers")
    
except TXTEncodingError as e:
    print(f"Encoding error: {str(e)}")
    
except Exception as e:
    print(f"Error: {str(e)}") 