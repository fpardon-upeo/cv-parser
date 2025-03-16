"""
Demo script for CV Parser and Anonymizer models.

This script demonstrates the functionality of the CV parser and anonymizer models.
"""
import os
import sys
import json
from typing import Dict, Any

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.models import CVParserModel, CVAnonymizerModel
from app.services.document_parser import DocumentParserFactory


def parse_cv_file(file_path: str) -> Dict[str, Any]:
    """Parse a CV file.
    
    Args:
        file_path: Path to the CV file
        
    Returns:
        Parsed CV data
    """
    # Get file extension
    file_ext = os.path.splitext(file_path)[1].lower().replace(".", "")
    
    # Read file content
    with open(file_path, "rb") as f:
        content = f.read()
    
    # Parse document
    parser_factory = DocumentParserFactory()
    document_parser = parser_factory.create_parser(file_ext)
    parsed_doc = document_parser.parse(content)
    
    # Extract text content
    text_content = parsed_doc.get("content", "")
    
    # Parse resume with model
    parser_model = CVParserModel()
    parser_model.initialize()
    
    result = parser_model.parse(text_content, file_ext)
    
    return result


def anonymize_cv_data(parsed_data: Dict[str, Any], level: str = "moderate") -> Dict[str, Any]:
    """Anonymize parsed CV data.
    
    Args:
        parsed_data: Parsed CV data
        level: Anonymization level (basic, moderate, thorough)
        
    Returns:
        Anonymized CV data
    """
    # Anonymize resume with model
    anonymizer_model = CVAnonymizerModel()
    anonymizer_model.initialize()
    
    result = anonymizer_model.anonymize(parsed_data, level)
    
    return result


def main():
    """Run the demo."""
    # Check if data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    if not os.path.exists(data_dir):
        print(f"Data directory not found: {data_dir}")
        return
    
    # Get all PDF files in the data directory
    pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"No PDF files found in {data_dir}")
        return
    
    # Select the first PDF file
    file_path = os.path.join(data_dir, pdf_files[0])
    print(f"Processing file: {file_path}")
    
    try:
        # Parse the CV
        print("\n=== Parsing CV ===")
        parsed_data = parse_cv_file(file_path)
        print(json.dumps(parsed_data, indent=2))
        
        # Anonymize the CV at different levels
        for level in ["basic", "moderate", "thorough"]:
            print(f"\n=== Anonymizing CV ({level}) ===")
            anonymized_data = anonymize_cv_data(parsed_data, level)
            print(json.dumps(anonymized_data, indent=2))
    
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main() 