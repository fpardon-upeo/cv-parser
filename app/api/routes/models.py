"""
API routes for model training and prediction.

This module provides API endpoints for training models and making predictions.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse, HTMLResponse
import os
import sys
from typing import Optional, Dict, Any
import json

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.models import CVParserModel, CVAnonymizerModel, model_trainer
from app.models.schemas import ParserInput, ParserOutput, AnonymizerInput, AnonymizerOutput, AnonymizationLevel
from app.services.document_parser import DocumentParserFactory
from app.models.parser_model import CVParserModel
from app.models.anonymizer_model import CVAnonymizerModel, AnonymizationLevel
from app.models.dataset_processor import CVDatasetProcessor
from app.models.model_trainer import ModelTrainer
from app.models.visualization import create_comparison_table

router = APIRouter(prefix="/models", tags=["models"])

# Initialize models
cv_parser_model = CVParserModel()
cv_anonymizer_model = CVAnonymizerModel()
dataset_processor = CVDatasetProcessor()
model_trainer = ModelTrainer()

@router.post("/train", response_model=Dict[str, bool])
async def train_models(force_retrain: bool = False):
    """Train the CV parser and anonymizer models.
    
    Args:
        force_retrain: Whether to force retraining even if models exist
        
    Returns:
        Dictionary indicating which models were trained
    """
    try:
        # Process the dataset
        parser_dataset, anonymizer_dataset = dataset_processor.create_datasets()
        
        # Train the models
        model_trainer.train_models(parser_dataset, anonymizer_dataset)
        
        return {"message": "Models trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training models: {str(e)}")

@router.post("/parse", response_model=ParserOutput)
async def parse_resume(file: UploadFile = File(...)):
    """Parse a resume file.
    
    Args:
        file: The resume file to parse
        
    Returns:
        Structured resume data
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Get the file type from the filename
        file_type = file.filename.split('.')[-1].lower()
        
        # Create a parser for the file type
        parser = DocumentParserFactory().create_parser(file_type)
        
        # Parse the document
        text_content = parser.parse(content)
        
        # Print debug info
        print(f"Extracted text length: {len(text_content)}")
        print(f"First 100 chars: {text_content[:100]}...")
        
        # Use the CV parser model to extract structured data
        cv_parser_model.initialize()
        parsed_data = cv_parser_model.parse(text_content, file_type)
        
        return parsed_data
    except Exception as e:
        print(f"Error in parse_resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")

@router.post("/anonymize", response_model=AnonymizerOutput)
async def anonymize_resume(input_data: AnonymizerInput):
    """Anonymize parsed resume data.
    
    Args:
        input_data: Parsed resume data and anonymization level
        
    Returns:
        Anonymized resume data
    """
    try:
        # Validate the anonymization level
        if input_data.anonymization_level not in [level.value for level in AnonymizationLevel]:
            input_data.anonymization_level = AnonymizationLevel.MODERATE.value
            
        # Use the CV anonymizer model to anonymize the data
        anonymized_data = cv_anonymizer_model.predict({
            "parsed_resume": input_data.parsed_resume,
            "anonymization_level": input_data.anonymization_level
        })
        
        return anonymized_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error anonymizing resume: {str(e)}")

@router.post("/parse-and-anonymize")
async def parse_and_anonymize_resume(
    file: UploadFile = File(...),
    anonymization_level: str = Form("moderate")
):
    """Parse and anonymize a resume file in one step.
    
    Args:
        file: The resume file to parse and anonymize
        anonymization_level: Level of anonymization to apply
        
    Returns:
        Anonymized resume data
    """
    try:
        # Validate the anonymization level
        if anonymization_level not in [level.value for level in AnonymizationLevel]:
            anonymization_level = AnonymizationLevel.MODERATE.value
            
        # Read the file content
        content = await file.read()
        
        # Get the file type from the filename
        file_type = file.filename.split('.')[-1].lower()
        
        try:
            # Create a parser for the file type
            parser_factory = DocumentParserFactory()
            parser = parser_factory.create_parser(file_type)
            
            # Parse the document
            text_content = parser.parse(content)
            
            # Print debug info
            print(f"Extracted text length: {len(text_content)}")
            print(f"First 100 chars: {text_content[:100]}...")
            
            # Initialize the parser model
            cv_parser_model.initialize()
            
            # Parse the resume
            parsed_data = cv_parser_model.parse(text_content, file_type)
            
            # Initialize the anonymizer model
            cv_anonymizer_model.initialize()
            
            # Anonymize the resume
            anonymized_data = cv_anonymizer_model.anonymize(
                parsed_data,
                anonymization_level
            )
            
            return {
                "original": parsed_data,
                "anonymized": anonymized_data
            }
        except Exception as inner_e:
            # Log the specific error
            print(f"Error in parse-and-anonymize: {str(inner_e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing resume: {str(inner_e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        # Log the outer error
        print(f"Unexpected error in parse-and-anonymize: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error processing resume: {str(e)}"
        )

@router.post("/visualization")
async def generate_visualization(file: UploadFile = File(...)):
    """
    Generate a visualization comparing different anonymization levels for a CV
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Get the file type from the filename
        file_type = file.filename.split('.')[-1].lower()
        
        # Create a parser for the file type
        parser = DocumentParserFactory().create_parser(file_type)
        
        # Parse the document
        text_content = parser.parse(content)
        
        # Print debug info
        print(f"Visualization - Extracted text length: {len(text_content)}")
        print(f"Visualization - First 100 chars: {text_content[:100]}...")
        
        # Use the CV parser model to extract structured data
        cv_parser_model.initialize()
        parsed_data = cv_parser_model.parse(text_content, file_type)
        
        # Generate anonymized versions at different levels
        anonymized_levels = {}
        
        cv_anonymizer_model.initialize()
        for level in [level.value for level in AnonymizationLevel]:
            anonymized_data = cv_anonymizer_model.anonymize(
                parsed_data,
                level
            )
            anonymized_levels[level] = anonymized_data.get("anonymized_resume", {})
        
        # Create the comparison table
        html_content = create_comparison_table(parsed_data, anonymized_levels)
        
        # Return the HTML content
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        print(f"Error in generate_visualization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating visualization: {str(e)}") 