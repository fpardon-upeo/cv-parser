"""
Pydantic schemas for CV Parser models.

This module defines the input and output schemas for the parser and anonymizer models.
"""
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ContactDetails(BaseModel):
    """Contact details schema."""
    
    name: str = Field(..., description="Full name of the candidate")
    email: str = Field(..., description="Email address of the candidate")
    phone: str = Field(..., description="Phone number of the candidate")
    location: Optional[str] = Field(None, description="Location of the candidate")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    other_urls: Optional[List[str]] = Field(None, description="Other relevant URLs (GitHub, portfolio, etc.)")


class WorkExperience(BaseModel):
    """Work experience schema."""
    
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    start_date: str = Field(..., description="Start date (YYYY-MM format)")
    end_date: str = Field(..., description="End date (YYYY-MM format or 'Present')")
    description: Optional[str] = Field(None, description="Job description")
    achievements: Optional[List[str]] = Field(None, description="Key achievements")
    skills_used: Optional[List[str]] = Field(None, description="Skills used in this role")


class Education(BaseModel):
    """Education schema."""
    
    degree: str = Field(..., description="Degree or certification name")
    institution: str = Field(..., description="Institution name")
    location: Optional[str] = Field(None, description="Institution location")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM format)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM format)")
    details: Optional[str] = Field(None, description="Additional details (GPA, honors, etc.)")


class Language(BaseModel):
    """Language proficiency schema."""
    
    language: str = Field(..., description="Language name")
    proficiency: str = Field(..., description="Proficiency level (e.g., Native, Fluent, Intermediate, Basic)")


class Candidate(BaseModel):
    """Candidate schema with structured resume information."""
    
    contact_details: ContactDetails = Field(..., description="Contact information")
    work_experience: List[WorkExperience] = Field(..., description="Work experience")
    education: List[Education] = Field(..., description="Education history")
    languages: Optional[List[Language]] = Field(None, description="Language proficiencies")
    skills: List[str] = Field(..., description="Technical and soft skills")
    summary: Optional[str] = Field(None, description="Professional summary or objective")


class ParserInput(BaseModel):
    """Input schema for the parser model."""
    
    resume_text: str = Field(..., description="Text content of the resume")
    file_type: str = Field(..., description="Original file format (pdf, docx, txt)")


class ParserOutput(BaseModel):
    """Output schema for the parser model."""
    
    candidate: Candidate = Field(..., description="Structured candidate information")


class AnonymizationLevel(str, Enum):
    """Anonymization level enum."""
    
    BASIC = "basic"
    MODERATE = "moderate"
    THOROUGH = "thorough"


class AnonymizerInput(BaseModel):
    """Input schema for the anonymizer model."""
    
    parsed_resume: Dict = Field(..., description="Parsed resume data (output from parser)")
    anonymization_level: AnonymizationLevel = Field(
        AnonymizationLevel.MODERATE, 
        description="Level of anonymization to apply"
    )


class AnonymizerOutput(BaseModel):
    """Output schema for the anonymizer model."""
    
    anonymized_resume: Dict = Field(..., description="Anonymized resume data") 