"""
Dataset processor for CV Parser.

This module provides functionality for processing CV data for model training.
"""
import os
import json
from typing import Dict, List, Any, Optional, Tuple

try:
    import smolmodels as sm
except ImportError:
    # Fall back to mock implementation
    from app.models import mock_smolmodels as sm

from app.services.document_parser import DocumentParserFactory


class CVDatasetProcessor:
    """Processor for CV datasets."""
    
    def __init__(self, data_dir: str = None):
        """Initialize the dataset processor.
        
        Args:
            data_dir: Directory containing CV data files
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.parser_factory = DocumentParserFactory()
        
    def process_cv_files(self) -> List[Dict[str, Any]]:
        """Process CV files in the data directory.
        
        Returns:
            List of processed CV data
        """
        processed_data = []
        
        # Ensure data directory exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            print(f"Created data directory: {self.data_dir}")
            return processed_data
        
        # Get all files in the data directory
        try:
            files = [f for f in os.listdir(self.data_dir) if os.path.isfile(os.path.join(self.data_dir, f))]
        except Exception as e:
            print(f"Error listing files in {self.data_dir}: {str(e)}")
            return processed_data
        
        for file_name in files:
            file_path = os.path.join(self.data_dir, file_name)
            file_ext = os.path.splitext(file_name)[1].lower().replace(".", "")
            
            # Skip non-document files
            if file_ext not in ["pdf", "docx", "txt"]:
                continue
            
            try:
                # Parse the document
                with open(file_path, "rb") as f:
                    content = f.read()
                
                parser = self.parser_factory.create_parser(file_ext)
                parsed_doc = parser.parse(content)
                
                # Extract text content
                text_content = parsed_doc.get("content", "")
                
                # Add to processed data
                processed_data.append({
                    "file_name": file_name,
                    "file_type": file_ext,
                    "resume_text": text_content
                })
                
                print(f"Processed {file_name}")
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")
        
        # If no files were processed, add a mock sample
        if not processed_data:
            print("No files processed. Adding mock sample.")
            processed_data.append({
                "file_name": "mock_resume.pdf",
                "file_type": "pdf",
                "resume_text": "Mock resume content for testing purposes."
            })
        
        return processed_data
    
    def create_parser_dataset(self, processed_data: List[Dict[str, Any]]) -> sm.DatasetGenerator:
        """Create a dataset for the parser model.
        
        Args:
            processed_data: List of processed CV data
            
        Returns:
            Dataset generator for the parser model
        """
        # Define schema for the dataset
        schema = {
            "resume_text": str,
            "file_type": str
        }
        
        # Create dataset generator
        dataset = sm.DatasetGenerator(schema=schema, data=processed_data)
        
        return dataset
    
    def create_anonymizer_dataset(self, parser_results: List[Dict[str, Any]]) -> sm.DatasetGenerator:
        """Create a dataset for the anonymizer model.
        
        Args:
            parser_results: List of parser model results
            
        Returns:
            Dataset generator for the anonymizer model
        """
        # Define schema for the dataset
        schema = {
            "parsed_resume": dict,
            "anonymization_level": str
        }
        
        # Create dataset with different anonymization levels
        anonymizer_data = []
        for result in parser_results:
            for level in ["basic", "moderate", "thorough"]:
                anonymizer_data.append({
                    "parsed_resume": result,
                    "anonymization_level": level
                })
        
        # Create dataset generator
        dataset = sm.DatasetGenerator(schema=schema, data=anonymizer_data)
        
        return dataset
    
    def prepare_datasets(self) -> Tuple[sm.DatasetGenerator, sm.DatasetGenerator]:
        """Prepare datasets for both parser and anonymizer models.
        
        Returns:
            Tuple of (parser_dataset, anonymizer_dataset)
        """
        # Process CV files
        processed_data = self.process_cv_files()
        
        # Create parser dataset
        parser_dataset = self.create_parser_dataset(processed_data)
        
        # For demonstration purposes, we'll use the mock parser results
        # In a real implementation, we would use actual parser results
        parser_results = []
        for data in processed_data[:5]:  # Limit to 5 samples for demonstration
            mock_result = {
                "candidate": {
                    "contact_details": {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone": "+1 (555) 123-4567",
                        "location": "New York, NY",
                        "linkedin": "linkedin.com/in/johndoe",
                        "other_urls": ["github.com/johndoe"]
                    },
                    "work_experience": [
                        {
                            "title": "Senior Software Engineer",
                            "company": "Tech Company Inc.",
                            "location": "New York, NY",
                            "start_date": "2018-01",
                            "end_date": "Present",
                            "description": "Led development of key features",
                            "achievements": ["Increased performance by 30%"],
                            "skills_used": ["Python", "JavaScript", "AWS"]
                        }
                    ],
                    "education": [
                        {
                            "degree": "Bachelor of Science in Computer Science",
                            "institution": "University of Example",
                            "location": "Boston, MA",
                            "start_date": "2010-09",
                            "end_date": "2014-05",
                            "details": "GPA: 3.8/4.0"
                        }
                    ],
                    "languages": [
                        {
                            "language": "English",
                            "proficiency": "Native"
                        },
                        {
                            "language": "Spanish",
                            "proficiency": "Intermediate"
                        }
                    ],
                    "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
                    "summary": "Experienced software engineer with a focus on web development and cloud technologies."
                }
            }
            parser_results.append(mock_result)
        
        # Create anonymizer dataset
        anonymizer_dataset = self.create_anonymizer_dataset(parser_results)
        
        return parser_dataset, anonymizer_dataset


# Singleton instance
dataset_processor = CVDatasetProcessor() 