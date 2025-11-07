import re
from ask_ai import ask_medical_ai
import os 

def extract_report_sections(report_text):
    """
    Extract key sections from a radiology report using regex patterns
    """
    sections = {}
    
    # EXAMINATION section
    exam_pattern = r'EXAMINATION:\s*(.*?)(?=CLINICAL DETAILS:|COMPARISON:|FINDINGS:|$)'
    exam_match = re.search(exam_pattern, report_text, re.DOTALL | re.IGNORECASE)
    sections['examination'] = exam_match.group(1).strip() if exam_match else ""
    
    # CLINICAL DETAILS section  
    clinical_pattern = r'CLINICAL DETAILS:\s*(.*?)(?=COMPARISON:|FINDINGS:|$)'
    clinical_match = re.search(clinical_pattern, report_text, re.DOTALL | re.IGNORECASE)
    sections['clinical_details'] = clinical_match.group(1).strip() if clinical_match else ""
    
    # COMPARISON section
    comparison_pattern = r'COMPARISON:\s*(.*?)(?=FINDINGS:|$)'
    comparison_match = re.search(comparison_pattern, report_text, re.DOTALL | re.IGNORECASE)
    sections['comparison'] = comparison_match.group(1).strip() if comparison_match else ""
    
    # FINDINGS section
    findings_pattern = r'(?:FINDINGS|REPORT):\s*(.*?)(?=CONCLUSION:|IMPRESSION:|REPORTED BY:|$)'
    findings_match = re.search(findings_pattern, report_text, re.DOTALL | re.IGNORECASE)
    sections['findings'] = findings_match.group(1).strip() if findings_match else ""

    # CONCLUSION/IMPRESSION section
    conclusion_pattern = r'(?:CONCLUSION|IMPRESSION):\s*(.*?)(?=REPORTED BY:|$)'
    conclusion_match = re.search(conclusion_pattern, report_text, re.DOTALL | re.IGNORECASE)
    sections['conclusion'] = conclusion_match.group(1).strip() if conclusion_match else ""
    
    return sections

def create_medical_prompt(sections):
    prompt = f"""You are a pediatric radiologist. Analyze this case with focus on AGE-APPROPRIATE diagnoses only.

EXAMINATION: {sections['examination']}
CLINICAL HISTORY: {sections['clinical_details']}
COMPARISON: {sections['comparison']}
RADIOLOGY FINDINGS: {sections['findings']}

Provide your assessment:

1. **Key Findings**: What do you see?

2. **Differential Diagnosis (PEDIATRIC ONLY)**: List most likely pediatric conditions. Do NOT include adult conditions like osteoarthritis, degenerative disease, or rotator cuff tears.

3. **Clinical Correlation**: How do findings match the patient history?

4. **Recommendations**: What are the next steps?

Remember: This is a PEDIATRIC patient. All diagnoses must be age-appropriate."""
    return prompt

def process_single_report(report_text):

    sections = extract_report_sections(report_text)

    prompt = create_medical_prompt(sections)

    ai_response = ask_medical_ai(prompt)
    
    return {
        'extracted_sections': sections,
        'ai_diagnosis': ai_response
    }

if __name__ == "__main__":
    all_folder = "all"
    
    if os.path.exists(all_folder):
        files = os.listdir(all_folder)
        print(f"Found {len(files)} files in the /all folder")
        print("First 5 files:")
        for i, file in enumerate(files[:5]):
            print(f"{i+1}. {file}")
        
        if files:
            test_file = files[0]
            print(f"\nTesting with: {test_file}")
            print("="*50)
            
            with open(os.path.join(all_folder, test_file), 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            result = process_single_report(report_content)
            
            print("EXTRACTED SECTIONS:")
            for section, content in result['extracted_sections'].items():
                print(f"{section.upper()}: {content}")
                print("-" * 30)
            
            print("\nAI DIAGNOSIS:")
            print(result['ai_diagnosis'])
    else:
        print("Error: /all folder not found. Please check the folder path.")