"""
Anonymizer model implementation for CV Parser.

This module implements the anonymizer model using smolmodels (or mock implementation).
"""
import os
from typing import Dict, Any, Optional

try:
    import smolmodels as sm
except ImportError:
    # Fall back to mock implementation
    from app.models import mock_smolmodels as sm

from app.models.schemas import AnonymizerInput, AnonymizerOutput, AnonymizationLevel


class CVAnonymizerModel:
    """CV Anonymizer model implementation."""
    
    def __init__(self):
        """Initialize the anonymizer model."""
        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), "saved_models", "cv_anonymizer_model.tar.gz")
        
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
        """Build the anonymizer model.
        
        Args:
            dataset: Optional dataset for training
        """
        # Define the model intent
        intent = """
        Anonymize resume data by removing or replacing personally identifiable information (PII) 
        while preserving the professional value of the document. The model should support different 
        levels of anonymization (basic, moderate, thorough) and handle various types of PII including 
        names, contact details, specific locations, and dates.
        """
        
        # Create the model with input and output schemas
        self.model = sm.Model(
            intent=intent,
            input_schema=AnonymizerInput.model_json_schema(),
            output_schema=AnonymizerOutput.model_json_schema()
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
    
    def anonymize(self, parsed_resume: Dict[str, Any], anonymization_level: str = "moderate") -> Dict[str, Any]:
        """Anonymize a parsed resume.
        
        Args:
            parsed_resume: Parsed resume data
            anonymization_level: Level of anonymization to apply (basic, moderate, thorough)
            
        Returns:
            Anonymized resume data
        """
        if self.model is None:
            self.initialize()
        
        # Validate anonymization level
        if anonymization_level not in [level.value for level in AnonymizationLevel]:
            anonymization_level = AnonymizationLevel.MODERATE.value
        
        # Prepare input data
        input_data = {
            "parsed_resume": parsed_resume,
            "anonymization_level": anonymization_level
        }
        
        # Make prediction
        result = self.model.predict(input_data)
        
        return result


# Singleton instance
anonymizer_model = CVAnonymizerModel() 