# CV Parser Architecture Overview

## System Architecture

The CV Parser is built as a modern web service with the following key components:

### 1. API Layer
- FastAPI framework for REST API
- API key authentication
- Rate limiting
- CORS support
- Input validation
- Error handling

### 2. Core Services
- Document Parser Service
  - PDF parsing
  - DOCX parsing
  - TXT parsing
- ML Model Service
  - Parser model (information extraction)
  - Anonymizer model (PII removal)
- File Management Service
  - File upload/download
  - Format conversion

### 3. ML Models
Built using smolmodels library:
- Parser Model: Extracts structured information from resumes
- Anonymizer Model: Removes/replaces personal information

### 4. Data Flow
1. Client uploads resume → API endpoint
2. Document parsing → Structured text
3. ML processing → Structured data/Anonymized content
4. Response formatting → JSON response

### 5. Security
- API key authentication
- Rate limiting per API key
- Input validation
- Secure file handling
- CORS configuration

### 6. Monitoring
- Health checks
- Error logging
- Performance metrics
- Rate limit tracking

## Technology Stack

- **Framework**: FastAPI
- **ML Library**: smolmodels
- **Document Processing**: PyPDF2, python-docx
- **Security**: python-jose, passlib
- **Logging**: loguru
- **Testing**: pytest
- **Code Quality**: black, flake8, isort

## Deployment

The application is containerized using Docker and can be deployed to any container orchestration platform. 