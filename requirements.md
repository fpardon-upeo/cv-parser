# CV Parser/Anonymizer: Developer Requirements Document

## Project Overview
This project involves building a Python service that can parse and anonymize CVs/resumes using small language models. The service consists of two main components:
1. A REST API application with endpoints for parsing and anonymizing resumes
2. An implementation using the smolmodels library to create and utilize compact language models

https://github.com/plexe-ai/smolmodels

## API Application Specifications

### Security Requirements
- Implement basic authentication/authorization
- Use API keys or JWT tokens for endpoint access
- Rate limiting to prevent abuse
- Input validation and sanitization
- Secure handling of uploaded files

### Endpoints

#### `POST /parse`
**Purpose:** Extract structured information from a resume

**Request:**
```json
{
  "resume": "base64_encoded_file_content",
  "file_type": "pdf|docx|txt" // Optional, can be inferred
}
```

**Response:**
```json
{
  "candidate": {
    "contact_details": {
      "name": "string",
      "email": "string",
      "phone": "string",
      "location": "string",
      "linkedin": "string",
      "other_urls": ["string"]
    },
    "work_experience": [
      {
        "title": "string",
        "company": "string",
        "location": "string",
        "start_date": "string",
        "end_date": "string",
        "description": "string",
        "achievements": ["string"],
        "skills_used": ["string"]
      }
    ],
    "education": [
      {
        "degree": "string",
        "institution": "string",
        "location": "string",
        "start_date": "string",
        "end_date": "string",
        "details": "string"
      }
    ],
    "languages": [
      {
        "language": "string",
        "proficiency": "string"
      }
    ],
    "skills": ["string"],
    "summary": "string"
  },
  "metadata": {
    "confidence_score": "float",
    "processing_time": "float"
  }
}
```

**Implementation Details:**
- Use appropriate Python libraries for document parsing (PyPDF2, python-docx, etc.)
- If document parsing proves challenging, implement a fallback using OpenAI APIs
- Use the "parser" small model for information extraction
- Implement error handling for malformed documents
- Log parsing attempts and success/failure rates

#### `POST /anonymize`
**Purpose:** Create an anonymized version of a resume

**Request:**
```json
{
  "resume": "base64_encoded_file_content",
  "file_type": "pdf|docx|txt", // Optional
  "anonymization_level": "basic|moderate|thorough" // Optional, defaults to "moderate"
}
```

**Response:**
```json
{
  "anonymized_resume": "base64_encoded_file_content",
  "file_type": "pdf|docx|txt",
  "metadata": {
    "fields_anonymized": ["name", "contact", "dates", etc.],
    "processing_time": "float"
  }
}
```

**Implementation Details:**
- Use the parsing functionality internally first to extract structured data
- Pass the structured data to the "anonymizer" small model
- Convert the anonymized structured data back to the original document format
- Maintain document formatting and structure where possible
- Implement customizable anonymization levels

### Additional API Features
- Error handling and meaningful error messages
- Request validation
- Logging and monitoring
- Health check endpoint (`GET /health`)
- Version endpoint (`GET /version`)
- Documentation endpoint (Swagger/OpenAPI, `GET /docs`)

## Small Model Application

### Parser Model

**Intent Definition:**
```python
parser_model = sm.Model(
    intent="Extract structured information from a resume or CV document, including contact details, work experience, education, language proficiency, and skills.",
    input_schema={
        "resume_text": str,
        "file_type": str  # original format: pdf, docx, txt
    },
    output_schema={
        "candidate": {
            "contact_details": dict,
            "work_experience": list,
            "education": list,
            "languages": list,
            "skills": list,
            "summary": str
        }
    }
)
```

### Anonymizer Model

**Intent Definition:**
```python
anonymizer_model = sm.Model(
    intent="Anonymize resume data by removing or replacing personally identifiable information while preserving the professional value of the document.",
    input_schema={
        "parsed_resume": dict,  # The structured output from the parser
        "anonymization_level": str  # basic, moderate, or thorough
    },
    output_schema={
        "anonymized_resume": dict  # Same structure as input, with PII removed/replaced
    }
)
```

### Model Building and Training

1. **Data Preparation:**
   - Collect sample resumes in various formats (PDF, DOCX, TXT)
   - Create labeled datasets with manually extracted information
   - Define anonymization rules and examples

2. **Model Building:**
   ```python
   parser_model.build(
       datasets=[parsed_cv_dataset],
       provider="openai/gpt-4o-mini",
       timeout=3600,
       max_iterations=10
   )
   
   anonymizer_model.build(
       datasets=[anonymized_cv_dataset],
       provider="openai/gpt-4o-mini",
       timeout=3600,
       max_iterations=10
   )
   ```

3. **Model Storage:**
   - Implement model versioning
   - Save models using `sm.save_model()`
   - Add capability to load models using `sm.load_model()`

## Technical Requirements

### Project Folder Structure
- Logical and meaningful folder structure for the code organization

### Environment and Dependencies
- Python 3.9+ compatibility
- Requirements file listing all dependencies
- Docker containerization
- Environment variable configuration

### Testing
- Unit tests for core functionality
- Integration tests for API endpoints
- Test cases using sample resumes
- Performance testing

### Documentation
- API documentation with examples
- Setup and deployment instructions
- Model training documentation
- Code documentation

### DevOps Considerations
- Monitoring and logging setup
- Scalability considerations
- Error reporting

## Project Timeline and Milestones
1. Setup project structure and environment
2. Implement document parsing functionality
3. Create and train initial "parser" model
4. Implement parsing API endpoint
5. Create and train "anonymizer" model
6. Implement anonymizing API endpoint
7. Add security features
8. Testing and debugging
9. Documentation
10. Deployment

## Success Criteria
- API endpoints correctly parse and anonymize at least 90% of test resumes
- Response time under 5 seconds for parsing and 10 seconds for anonymization
- Secure authentication/authorization implementation
- Comprehensive test coverage
- Complete documentation