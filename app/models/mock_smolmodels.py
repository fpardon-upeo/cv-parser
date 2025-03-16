"""
Mock implementation of smolmodels for development.

This module provides a mock implementation of the smolmodels library
for development purposes until the environment can be updated to
a compatible Python version.
"""
from typing import Any, Dict, List, Optional, Union
import json
import os


class Model:
    """Mock implementation of smolmodels.Model."""

    def __init__(
        self,
        intent: str,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the model.

        Args:
            intent: Description of the model's purpose
            input_schema: Schema for input data
            output_schema: Schema for output data
        """
        self.intent = intent
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}
        self.is_built = False
        self.model_data = {}

    def build(
        self,
        datasets: Optional[List[Any]] = None,
        provider: str = "openai/gpt-4o-mini",
        timeout: int = 3600,
        max_iterations: int = 10,
    ) -> None:
        """Build the model.

        Args:
            datasets: List of datasets to use for training
            provider: LLM provider to use
            timeout: Maximum time to spend building the model
            max_iterations: Maximum number of iterations to try
        """
        print(f"Mock: Building model with intent: {self.intent}")
        print(f"Mock: Using provider: {provider}")
        print(f"Mock: Timeout: {timeout}, Max iterations: {max_iterations}")
        
        if datasets:
            print(f"Mock: Using {len(datasets)} datasets")
        
        self.is_built = True
        self.model_data = {
            "intent": self.intent,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "provider": provider,
        }

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a prediction using the model.

        Args:
            input_data: Input data for prediction

        Returns:
            Prediction result
        """
        if not self.is_built:
            raise RuntimeError("Model must be built before making predictions")
        
        print(f"Mock: Making prediction with input: {input_data}")
        
        # For parser model, return structured data
        if "resume_text" in input_data:
            return self._mock_parser_prediction(input_data)
        
        # For anonymizer model, return anonymized data
        if "parsed_resume" in input_data:
            return self._mock_anonymizer_prediction(input_data)
        
        # Generic fallback
        return {"result": "Mock prediction result"}

    def _mock_parser_prediction(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock prediction for the parser model."""
        # Extract information from the resume text
        resume_text = input_data.get("resume_text", "")
        file_type = input_data.get("file_type", "")
        
        print(f"Processing resume text ({len(resume_text)} chars) from {file_type} file")
        
        # Simple extraction logic based on the resume text
        # This is a basic implementation that tries to extract real information from the text
        
        # Extract name (look for patterns at the beginning of the resume)
        name_lines = resume_text.split('\n')[:5]  # First 5 lines often contain the name
        name = "Unknown"
        for line in name_lines:
            line = line.strip()
            if line and len(line) < 50 and not line.startswith("http") and "@" not in line:
                name = line
                break
        
        # Extract email (look for @ symbol)
        email = "unknown@example.com"
        for line in resume_text.split('\n'):
            words = line.split()
            for word in words:
                if '@' in word and '.' in word.split('@')[1]:
                    email = word.strip('.,;:()"\'')
                    break
        
        # Extract phone (look for number patterns)
        phone = "+1 (555) 123-4567"  # Default
        for line in resume_text.split('\n'):
            if any(c.isdigit() for c in line) and ('+' in line or '(' in line or '-' in line):
                words = line.split()
                for word in words:
                    if any(c.isdigit() for c in word) and len(word) >= 7:
                        phone = word.strip('.,;:()"\'')
                        break
        
        # Extract skills (look for common programming languages and technologies)
        skills = []
        skill_keywords = ["python", "javascript", "java", "c++", "react", "angular", "vue", 
                         "node.js", "express", "django", "flask", "aws", "azure", "gcp", 
                         "docker", "kubernetes", "sql", "nosql", "mongodb", "postgresql"]
        
        for skill in skill_keywords:
            if skill.lower() in resume_text.lower():
                skills.append(skill.title() if skill != "gcp" and skill != "aws" else skill.upper())
        
        # If no skills found, add some default ones
        if not skills:
            skills = ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"]
        
        # Extract summary (first paragraph that's longer than 100 characters)
        summary = "Experienced professional with relevant skills and background."
        paragraphs = resume_text.split('\n\n')
        for para in paragraphs:
            if len(para) > 100 and len(para.split()) > 15:
                summary = para.strip()
                break
        
        return {
            "candidate": {
                "contact_details": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "location": "Location extracted from resume",
                    "linkedin": "linkedin profile extracted from resume",
                    "other_urls": ["github or other urls extracted from resume"]
                },
                "work_experience": [
                    {
                        "title": "Position extracted from resume",
                        "company": "Company extracted from resume",
                        "location": "Location extracted from resume",
                        "start_date": "Start date extracted from resume",
                        "end_date": "End date extracted from resume",
                        "description": "Description extracted from resume",
                        "achievements": ["Achievement extracted from resume"],
                        "skills_used": skills[:3]  # Use first 3 skills
                    }
                ],
                "education": [
                    {
                        "degree": "Degree extracted from resume",
                        "institution": "Institution extracted from resume",
                        "location": "Location extracted from resume",
                        "start_date": "Start date extracted from resume",
                        "end_date": "End date extracted from resume",
                        "details": "Details extracted from resume"
                    }
                ],
                "languages": [
                    {
                        "language": "English",
                        "proficiency": "Proficiency extracted from resume"
                    }
                ],
                "skills": skills,
                "summary": summary
            }
        }

    def _mock_anonymizer_prediction(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock prediction for the anonymizer model."""
        anonymization_level = input_data.get("anonymization_level", "moderate")
        parsed_resume = input_data.get("parsed_resume", {})
        
        # Create a deep copy to avoid modifying the input
        anonymized_resume = json.loads(json.dumps(parsed_resume))
        
        # Get the candidate data or create an empty dict if it doesn't exist
        candidate = anonymized_resume.get("candidate", {})
        
        # Anonymize contact details
        if "contact_details" in candidate:
            contact = candidate["contact_details"]
            if anonymization_level in ["basic", "moderate", "thorough"]:
                contact["name"] = "REDACTED NAME"
                contact["email"] = "REDACTED EMAIL"
                contact["phone"] = "REDACTED PHONE"
            
            if anonymization_level in ["moderate", "thorough"]:
                contact["location"] = "REDACTED LOCATION"
                contact["linkedin"] = "REDACTED URL"
                contact["other_urls"] = ["REDACTED URL"]
            
        # Anonymize work experience
        if "work_experience" in candidate and anonymization_level == "thorough":
            for exp in candidate["work_experience"]:
                exp["company"] = "REDACTED COMPANY"
                exp["location"] = "REDACTED LOCATION"
                
        # Anonymize education
        if "education" in candidate and anonymization_level in ["moderate", "thorough"]:
            for edu in candidate["education"]:
                edu["institution"] = "REDACTED INSTITUTION"
                edu["location"] = "REDACTED LOCATION"
        
        return {"anonymized_resume": anonymized_resume}


class DatasetGenerator:
    """Mock implementation of smolmodels.DatasetGenerator."""

    def __init__(
        self,
        schema: Dict[str, Any],
        data: Optional[List[Dict[str, Any]]] = None
    ):
        """Initialize the dataset generator.

        Args:
            schema: Schema for the dataset
            data: Existing data to use
        """
        self.schema = schema
        self.data = data or []

    def generate(self, n_samples: int) -> List[Dict[str, Any]]:
        """Generate synthetic data.

        Args:
            n_samples: Number of samples to generate

        Returns:
            Generated data
        """
        print(f"Mock: Generating {n_samples} samples")
        
        # Return existing data if available
        if self.data:
            return self.data
        
        # Generate mock data
        generated_data = []
        for i in range(n_samples):
            sample = {}
            for key, value_type in self.schema.items():
                if key == "resume_text":
                    sample[key] = f"Mock resume text for sample {i}"
                elif key == "file_type":
                    sample[key] = "pdf"
                else:
                    sample[key] = f"Mock {key} for sample {i}"
            generated_data.append(sample)
        
        self.data = generated_data
        return generated_data


def save_model(model: Model, path: str) -> str:
    """Save a model to disk.

    Args:
        model: Model to save
        path: Path to save the model to

    Returns:
        Path to the saved model
    """
    if not model.is_built:
        raise RuntimeError("Model must be built before saving")
    
    # Ensure the path has the correct extension
    if not path.endswith(".tar.gz"):
        path = f"{path}.tar.gz"
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    
    # Mock saving the model
    with open(f"{path}.json", "w") as f:
        json.dump(model.model_data, f)
    
    print(f"Mock: Saved model to {path}")
    return path


def load_model(path: str) -> Model:
    """Load a model from disk.

    Args:
        path: Path to the model

    Returns:
        Loaded model
    """
    # Check if the JSON metadata file exists
    json_path = f"{path}.json"
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Model metadata file not found: {json_path}")
    
    # Load the model metadata
    with open(json_path, "r") as f:
        model_data = json.load(f)
    
    # Create a new model
    model = Model(
        intent=model_data.get("intent", ""),
        input_schema=model_data.get("input_schema", {}),
        output_schema=model_data.get("output_schema", {})
    )
    
    # Mark the model as built
    model.is_built = True
    model.model_data = model_data
    
    print(f"Mock: Loaded model from {path}")
    return model 