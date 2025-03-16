"""
Visualization module for CV data anonymization.

This module provides functions to create visual representations of CV data
at different anonymization levels for comparison purposes.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def create_comparison_table(original: Dict[str, Any], anonymized_levels: Dict[str, Dict[str, Any]]) -> str:
    """
    Create an HTML table comparing original and anonymized CV data.
    
    Args:
        original: The original parsed CV data
        anonymized_levels: Dictionary of anonymized data at different levels
        
    Returns:
        HTML string containing the comparison table
    """
    try:
        # Extract candidate data from the original parsed CV
        candidate_data = original.get('candidate', {})
        if not candidate_data:
            # If no candidate data is found, create mock data for demonstration
            candidate_data = {
                'contact_details': {
                    'name': 'John Doe',
                    'email': 'john.doe@example.com',
                    'phone': '+1 (555) 123-4567',
                    'location': 'New York, NY',
                    'linkedin': 'linkedin.com/in/johndoe',
                    'other_urls': ['github.com/johndoe']
                },
                'work_experience': [
                    {
                        'title': 'Senior Software Engineer',
                        'company': 'Tech Company Inc.',
                        'location': 'New York, NY',
                        'start_date': '2018-01',
                        'end_date': 'Present',
                        'description': 'Led development of key features'
                    }
                ],
                'education': [
                    {
                        'degree': 'Bachelor of Science in Computer Science',
                        'institution': 'University of Example',
                        'location': 'Boston, MA',
                        'start_date': '2010-09',
                        'end_date': '2014-05'
                    }
                ]
            }
            
        # Create HTML structure
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CV Anonymization Comparison</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }
                h1 {
                    color: #2c3e50;
                    text-align: center;
                    margin-bottom: 30px;
                }
                h2 {
                    color: #3498db;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                    margin-top: 30px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 30px;
                }
                th, td {
                    padding: 12px 15px;
                    border: 1px solid #ddd;
                    text-align: left;
                }
                th {
                    background-color: #f8f9fa;
                    font-weight: bold;
                }
                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                .redacted {
                    color: #e74c3c;
                    font-weight: bold;
                }
                .section {
                    margin-bottom: 40px;
                    background-color: white;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    padding: 20px;
                }
                .level-description {
                    margin-bottom: 20px;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-left: 4px solid #3498db;
                }
            </style>
        </head>
        <body>
            <h1>CV Anonymization Comparison</h1>
            
            <div class="level-description">
                <p><strong>Basic Level:</strong> Redacts only the most direct personal identifiers (name, email, phone).</p>
                <p><strong>Moderate Level:</strong> Redacts personal identifiers plus location information and URLs.</p>
                <p><strong>Thorough Level:</strong> Redacts all identifiable information including company names, institutions, and specific locations.</p>
            </div>
        """
        
        # Contact Details Section
        html += """
            <div class="section">
                <h2>Contact Details</h2>
                <table>
                    <tr>
                        <th>Field</th>
                        <th>Original</th>
                        <th>Basic</th>
                        <th>Moderate</th>
                        <th>Thorough</th>
                    </tr>
        """
        
        # Get contact details
        contact_details = candidate_data.get('contact_details', {})
        
        # Add rows for each contact detail
        for field in ['name', 'email', 'phone', 'location', 'linkedin']:
            original_value = contact_details.get(field, '')
            
            html += f"""
                <tr>
                    <td>{field.capitalize()}</td>
                    <td>{original_value}</td>
            """
            
            # Add anonymized values for each level
            for level in ['basic', 'moderate', 'thorough']:
                if level in anonymized_levels:
                    anon_data = anonymized_levels[level]
                    anon_candidate = anon_data.get('candidate', {})
                    anon_contact = anon_candidate.get('contact_details', {})
                    anon_value = anon_contact.get(field, '')
                    
                    # Highlight redacted values
                    if anon_value != original_value and 'REDACTED' in anon_value:
                        html += f'<td class="redacted">{anon_value}</td>'
                    else:
                        html += f'<td>{anon_value}</td>'
                else:
                    html += '<td>N/A</td>'
            
            html += "</tr>"
        
        html += """
                </table>
            </div>
        """
        
        # Work Experience Section
        html += """
            <div class="section">
                <h2>Work Experience</h2>
                <table>
                    <tr>
                        <th>Field</th>
                        <th>Original</th>
                        <th>Basic</th>
                        <th>Moderate</th>
                        <th>Thorough</th>
                    </tr>
        """
        
        # Get work experience
        work_experience = candidate_data.get('work_experience', [])
        if work_experience:
            work_exp = work_experience[0]  # Take the first work experience for demonstration
            
            # Add rows for each work experience field
            for field in ['title', 'company', 'location', 'start_date', 'end_date']:
                original_value = work_exp.get(field, '')
                
                html += f"""
                    <tr>
                        <td>{field.replace('_', ' ').capitalize()}</td>
                        <td>{original_value}</td>
                """
                
                # Add anonymized values for each level
                for level in ['basic', 'moderate', 'thorough']:
                    if level in anonymized_levels:
                        anon_data = anonymized_levels[level]
                        anon_candidate = anon_data.get('candidate', {})
                        anon_work_exp = anon_candidate.get('work_experience', [])
                        
                        if anon_work_exp:
                            anon_exp = anon_work_exp[0]
                            anon_value = anon_exp.get(field, '')
                            
                            # Highlight redacted values
                            if anon_value != original_value and 'REDACTED' in anon_value:
                                html += f'<td class="redacted">{anon_value}</td>'
                            else:
                                html += f'<td>{anon_value}</td>'
                        else:
                            html += '<td>N/A</td>'
                    else:
                        html += '<td>N/A</td>'
                
                html += "</tr>"
        
        html += """
                </table>
            </div>
        """
        
        # Education Section
        html += """
            <div class="section">
                <h2>Education</h2>
                <table>
                    <tr>
                        <th>Field</th>
                        <th>Original</th>
                        <th>Basic</th>
                        <th>Moderate</th>
                        <th>Thorough</th>
                    </tr>
        """
        
        # Get education
        education = candidate_data.get('education', [])
        if education:
            edu = education[0]  # Take the first education for demonstration
            
            # Add rows for each education field
            for field in ['degree', 'institution', 'location', 'start_date', 'end_date']:
                original_value = edu.get(field, '')
                
                html += f"""
                    <tr>
                        <td>{field.replace('_', ' ').capitalize()}</td>
                        <td>{original_value}</td>
                """
                
                # Add anonymized values for each level
                for level in ['basic', 'moderate', 'thorough']:
                    if level in anonymized_levels:
                        anon_data = anonymized_levels[level]
                        anon_candidate = anon_data.get('candidate', {})
                        anon_edu = anon_candidate.get('education', [])
                        
                        if anon_edu:
                            anon_education = anon_edu[0]
                            anon_value = anon_education.get(field, '')
                            
                            # Highlight redacted values
                            if anon_value != original_value and 'REDACTED' in anon_value:
                                html += f'<td class="redacted">{anon_value}</td>'
                            else:
                                html += f'<td>{anon_value}</td>'
                        else:
                            html += '<td>N/A</td>'
                    else:
                        html += '<td>N/A</td>'
                
                html += "</tr>"
        
        html += """
                </table>
            </div>
        """
        
        # Close HTML
        html += """
        </body>
        </html>
        """
        
        return html
    except Exception as e:
        # Return a simple error message as HTML if something goes wrong
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error in Visualization</title>
        </head>
        <body>
            <h1>Error Creating Visualization</h1>
            <p>An error occurred while creating the visualization: {str(e)}</p>
        </body>
        </html>
        """

def main():
    """
    Main function to demonstrate the visualization capabilities.
    """
    try:
        # Check if data directory exists
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        if not os.path.exists(data_dir):
            print(f"Data directory not found: {data_dir}")
            return
        
        # Find the first PDF file in the data directory
        pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print("No PDF files found in the data directory")
            return
        
        file_path = os.path.join(data_dir, pdf_files[0])
        print(f"Processing file: {file_path}")
        
        # Import here to avoid circular imports
        from app.models.parser_model import CVParserModel
        from app.models.anonymizer_model import CVAnonymizerModel, AnonymizationLevel
        from app.services.document_parser import DocumentParserFactory
        
        # Parse the CV
        print("\n=== Parsing CV ===")
        parser = DocumentParserFactory().create_parser('pdf')
        with open(file_path, 'rb') as f:
            content = f.read()
        
        text_content = parser.parse(content)
        cv_parser = CVParserModel()
        cv_parser.initialize()
        parsed_data = cv_parser.parse(text_content, 'pdf')
        
        # Anonymize at different levels
        cv_anonymizer = CVAnonymizerModel()
        cv_anonymizer.initialize()
        anonymized_levels = {}
        
        for level in [level.value for level in AnonymizationLevel]:
            print(f"\n=== Anonymizing CV ({level}) ===")
            anonymized_data = cv_anonymizer.anonymize(
                parsed_data,
                level
            )
            anonymized_levels[level] = anonymized_data.get("anonymized_resume", {})
        
        # Create comparison table
        html_content = create_comparison_table(parsed_data, anonymized_levels)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the HTML file
        output_file = os.path.join(output_dir, 'anonymization_comparison.html')
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"\nComparison table saved to: {output_file}")
        
    except Exception as e:
        print(f"Error in visualization: {str(e)}")

if __name__ == "__main__":
    main() 