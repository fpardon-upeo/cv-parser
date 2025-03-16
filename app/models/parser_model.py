"""
Parser model implementation for CV Parser.

This module implements the parser model using smolmodels (or mock implementation).
"""
import os
from typing import Dict, Any, Optional

try:
    import smolmodels as sm
except ImportError:
    # Fall back to mock implementation
    from app.models import mock_smolmodels as sm

from app.models.schemas import ParserInput, ParserOutput


class CVParserModel:
    """CV Parser model implementation."""
    
    def __init__(self):
        """Initialize the parser model."""
        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), "saved_models", "cv_parser_model.tar.gz")
        
    def initialize(self, force_rebuild: bool = False) -> None:
        """Initialize the model, loading from disk or building if necessary.
        
        Args:
            force_rebuild: Whether to force rebuilding the model
        """
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        if os.path.exists(f"{self.model_path}.json") and not force_rebuild:
            self.load_model()
        else:
            self.build_model()
    
    def build_model(self, dataset=None) -> None:
        """Build the parser model.
        
        Args:
            dataset: Optional dataset for training
        """
        # Define the model intent
        intent = """
        Extract structured information from a resume or CV document, including contact details, 
        work experience, education, language proficiency, and skills. The model should identify 
        and structure all relevant information from the resume text into a consistent format.
        """
        
        # Create the model with input and output schemas
        self.model = sm.Model(
            intent=intent,
            input_schema=ParserInput.model_json_schema(),
            output_schema=ParserOutput.model_json_schema()
        )
        
        # Build the model
        datasets = [dataset] if dataset else []
        self.model.build(
            datasets=datasets,
            provider="openai/gpt-4o-mini",
            timeout=3600,
            max_iterations=10
        )
        
        # Save the model
        sm.save_model(self.model, self.model_path)
    
    def load_model(self) -> None:
        """Load the model from disk."""
        self.model = sm.load_model(self.model_path)
    
    def parse(self, resume_text: str, file_type: str) -> Dict[str, Any]:
        """Parse a resume into structured data.
        
        Args:
            resume_text: Text content of the resume
            file_type: Original file format (pdf, docx, txt)
            
        Returns:
            Structured resume data
        """
        if self.model is None:
            self.initialize()
        
        # Prepare input data
        input_data = {
            "resume_text": resume_text,
            "file_type": file_type
        }
        
        # Print some debug info
        print(f"Parsing resume text ({len(resume_text)} chars) from {file_type} file")
        print(f"First 100 chars: {resume_text[:100]}...")
        
        # Make prediction
        result = self.model.predict(input_data)
        
        # If we're using the mock model, let's enhance the output with actual data
        # This is a simple extraction logic that tries to extract real information from the text
        if "mock_smolmodels" in str(type(self.model)):
            # Extract name (look for patterns at the beginning of the resume)
            name_lines = resume_text.split('\n')[:5]  # First 5 lines often contain the name
            name = "Unknown"
            for line in name_lines:
                line = line.strip()
                if line and len(line) < 50 and not line.startswith("http") and "@" not in line:
                    name = line
                    break
            
            # Extract email (look for @ symbol)
            email = None
            for line in resume_text.split('\n'):
                words = line.split()
                for word in words:
                    if '@' in word and '.' in word.split('@')[1]:
                        email = word.strip('.,;:()"\'')
                        break
                if email:
                    break
            
            # Extract phone (look for number patterns)
            phone = None
            for line in resume_text.split('\n'):
                if any(c.isdigit() for c in line) and ('+' in line or '(' in line or '-' in line):
                    words = line.split()
                    for word in words:
                        if any(c.isdigit() for c in word) and len(word) >= 7:
                            phone = word.strip('.,;:()"\'')
                            break
                    if phone:
                        break
            
            # Extract skills (look for common programming languages and technologies)
            skills = []
            skill_keywords = ["python", "javascript", "java", "c++", "react", "angular", "vue", 
                            "node.js", "express", "django", "flask", "aws", "azure", "gcp", 
                            "docker", "kubernetes", "sql", "nosql", "mongodb", "postgresql"]
            
            for skill in skill_keywords:
                if skill.lower() in resume_text.lower():
                    skills.append(skill.title() if skill != "gcp" and skill != "aws" else skill.upper())
            
            # Extract summary (first paragraph that's longer than 100 characters)
            summary = None
            paragraphs = resume_text.split('\n\n')
            for para in paragraphs:
                if len(para) > 100 and len(para.split()) > 15:
                    summary = para.strip()
                    break
            
            # Update the result with extracted information
            if "candidate" in result:
                if name and "contact_details" in result["candidate"]:
                    result["candidate"]["contact_details"]["name"] = name
                if email and "contact_details" in result["candidate"]:
                    result["candidate"]["contact_details"]["email"] = email
                if phone and "contact_details" in result["candidate"]:
                    result["candidate"]["contact_details"]["phone"] = phone
                if skills:
                    result["candidate"]["skills"] = skills
                if summary:
                    result["candidate"]["summary"] = summary
        
        return result


# Singleton instance
parser_model = CVParserModel() 