import pytest
import os
from typing import List, Dict
from app.services.document_parser import DocumentParser
from app.services.document_parser import DocumentParserFactory
from app.services.pdf_parser import PDFParser
from app.services.docx_parser import DOCXParser
from app.services.txt_parser import TXTParser

@pytest.fixture
def sample_files() -> Dict[str, str]:
    """Fixture to provide paths to sample test files."""
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'test_data')
    return {
        'pdf': os.path.join(base_dir, 'sample_resume.pdf'),
        'docx': os.path.join(base_dir, 'sample_resume.docx'),
        'txt': os.path.join(base_dir, 'sample_resume.txt')
    }

@pytest.fixture
def parser_factory() -> DocumentParserFactory:
    """Fixture to provide a parser factory instance."""
    return DocumentParserFactory()

def get_file_extension(file_path: str) -> str:
    """Extract the file extension from a file path."""
    _, ext = os.path.splitext(file_path)
    return ext.lower().lstrip('.')

def test_factory_creates_correct_parser(parser_factory):
    """Test that factory creates the correct parser for each file type."""
    pdf_parser = parser_factory.create_parser('pdf')
    docx_parser = parser_factory.create_parser('docx')
    txt_parser = parser_factory.create_parser('txt')

    assert isinstance(pdf_parser, PDFParser)
    assert isinstance(docx_parser, DOCXParser)
    assert isinstance(txt_parser, TXTParser)

def test_cross_format_consistency(parser_factory, sample_files):
    """Test that parsing results are consistent across different formats."""
    results = {}
    
    for file_type, file_path in sample_files.items():
        parser = parser_factory.create_parser(file_type)
        with open(file_path, 'rb') as f:
            content = f.read()
        results[file_type] = parser.parse(content)
        
        # Basic structure checks
        assert 'content' in results[file_type]
        assert 'metadata' in results[file_type]
        
    # Compare content structure across formats
    first_format = next(iter(results))
    first_content = results[first_format]['content']
    
    # Check that all formats have similar content
    for file_type, result in results.items():
        if file_type != first_format:
            # Check for key phrases that should be present in all formats
            assert "JOHN DOE" in result['content']
            assert "Software Engineer" in result['content']
            assert "WORK EXPERIENCE" in result['content']
            assert "EDUCATION" in result['content']

def test_error_handling_across_formats(parser_factory):
    """Test error handling consistency across different parsers."""
    invalid_content = b"This is not a valid document"
    
    for file_type in ['pdf', 'docx', 'txt']:
        parser = parser_factory.create_parser(file_type)
        
        # All parsers should handle invalid content gracefully
        try:
            parser.parse(invalid_content)
            assert False, f"Expected {file_type} parser to raise an exception"
        except Exception as e:
            # Verify that the error is of the expected type
            assert "error" in str(e).lower() or "invalid" in str(e).lower() or "fail" in str(e).lower()

def test_performance_benchmarks(parser_factory, sample_files):
    """Test performance benchmarks for each parser."""
    import time
    performance_results = {}
    
    for file_type, file_path in sample_files.items():
        parser = parser_factory.create_parser(file_type)
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # Measure parsing time
        start_time = time.time()
        parser.parse(content)
        end_time = time.time()
        
        performance_results[file_type] = end_time - start_time
        
        # Basic performance check - parsing should be reasonably fast
        assert performance_results[file_type] < 2.0, f"{file_type} parsing took too long"
    
    # Log performance results
    print("\nPerformance benchmarks:")
    for file_type, duration in performance_results.items():
        print(f"{file_type}: {duration:.4f} seconds")

def test_memory_usage(parser_factory, sample_files):
    """Test memory usage for each parser."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_results = {}
    
    for file_type, file_path in sample_files.items():
        parser = parser_factory.create_parser(file_type)
        
        # Measure memory before parsing
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        with open(file_path, 'rb') as f:
            content = f.read()
        parser.parse(content)
        
        # Measure memory after parsing
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_results[file_type] = memory_after - memory_before
        
        # Basic memory check - parsing should not use excessive memory
        assert memory_results[file_type] < 100, f"{file_type} parsing used too much memory"
    
    # Log memory results
    print("\nMemory usage:")
    for file_type, usage in memory_results.items():
        print(f"{file_type}: {usage:.2f} MB") 