"""
Model trainer for CV Parser.

This module provides functionality for training the CV parser and anonymizer models.
"""
import os
from typing import Dict, Any, Optional, Tuple, List

try:
    import smolmodels as sm
except ImportError:
    # Fall back to mock implementation
    from app.models import mock_smolmodels as sm

from app.models.parser_model import CVParserModel
from app.models.anonymizer_model import CVAnonymizerModel


class ModelTrainer:
    """Trainer for CV parser and anonymizer models."""
    
    def __init__(self, parser_model: CVParserModel = None, anonymizer_model: CVAnonymizerModel = None):
        """Initialize the model trainer.
        
        Args:
            parser_model: CV parser model instance
            anonymizer_model: CV anonymizer model instance
        """
        self.parser_model = parser_model or CVParserModel()
        self.anonymizer_model = anonymizer_model or CVAnonymizerModel()
    
    def train_models(self, parser_dataset=None, anonymizer_dataset=None, force_retrain: bool = False) -> Tuple[bool, bool]:
        """Train the CV parser and anonymizer models.
        
        Args:
            parser_dataset: Dataset for training the parser model
            anonymizer_dataset: Dataset for training the anonymizer model
            force_retrain: Whether to force retraining even if models exist
            
        Returns:
            Tuple of (parser_trained, anonymizer_trained) indicating which models were trained
        """
        parser_trained = self._train_parser_model(parser_dataset, force_retrain)
        anonymizer_trained = self._train_anonymizer_model(anonymizer_dataset, force_retrain)
        
        return parser_trained, anonymizer_trained
    
    def _train_parser_model(self, dataset=None, force_retrain: bool = False) -> bool:
        """Train the CV parser model.
        
        Args:
            dataset: Dataset for training the model
            force_retrain: Whether to force retraining even if model exists
            
        Returns:
            Whether the model was trained
        """
        # Check if model exists and force_retrain is False
        if not force_retrain and self._check_model_exists(self.parser_model.model_path):
            print("Parser model already exists. Skipping training.")
            return False
        
        # Build the model
        print("Training parser model...")
        self.parser_model.build_model(dataset)
        
        return True
    
    def _train_anonymizer_model(self, dataset=None, force_retrain: bool = False) -> bool:
        """Train the CV anonymizer model.
        
        Args:
            dataset: Dataset for training the model
            force_retrain: Whether to force retraining even if model exists
            
        Returns:
            Whether the model was trained
        """
        # Check if model exists and force_retrain is False
        if not force_retrain and self._check_model_exists(self.anonymizer_model.model_path):
            print("Anonymizer model already exists. Skipping training.")
            return False
        
        # Build the model
        print("Training anonymizer model...")
        self.anonymizer_model.build_model(dataset)
        
        return True
    
    def _check_model_exists(self, model_path: str) -> bool:
        """Check if a model exists at the given path.
        
        Args:
            model_path: Path to the model file
            
        Returns:
            Whether the model exists
        """
        return os.path.exists(f"{model_path}.json")


# Singleton instance
model_trainer = ModelTrainer() 