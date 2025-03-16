# CV Parser/Anonymizer

A Python service for parsing and anonymizing CVs/resumes using small language models.

## Project Overview

This project involves building a Python service that can parse and anonymize CVs/resumes using small language models. The service consists of two main components:
1. A REST API application with endpoints for parsing and anonymizing resumes
2. An implementation using the smolmodels library to create and utilize compact language models

## Features

- Parse CVs/resumes in various formats (PDF, DOCX, TXT)
- Extract structured information including contact details, work experience, education, skills, etc.
- Anonymize personal information with configurable anonymization levels
- REST API for integration with other systems
- Small, efficient language models for parsing and anonymization

## Installation

```bash
# Clone the repository
git clone https://github.com/fpardon-upeo/cv-parser.git
cd cv-parser

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Start the API server
cd app
python main.py
```

The API will be available at http://localhost:8000

## API Endpoints

- `POST /parse` - Extract structured information from a resume
- `POST /anonymize` - Create an anonymized version of a resume
- `GET /health` - Health check endpoint
- `GET /version` - Version information
- `GET /docs` - API documentation (Swagger/OpenAPI)

## Project Structure

- `app/` - Main application code
  - `api/` - API endpoints and routes
  - `core/` - Core application functionality
  - `models/` - Data models and schemas
  - `services/` - Business logic services
  - `utils/` - Utility functions
  - `data/` - Sample data for testing
  - `output/` - Output files
- `build-plan/` - Project planning documents
- `tests/` - Test cases

## License

MIT 