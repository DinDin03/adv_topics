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

    prompt = f"""
You are an experienced **pediatric radiologist** analyzing a case. 
Your role is to provide a structured diagnostic assessment tailored to children.

EXAMINATION: {sections['examination']}
CLINICAL HISTORY: {sections['clinical_details']}
COMPARISON: {sections['comparison']}
RADIOLOGY FINDINGS: {sections['findings']}

Please provide:

1. **CLINICAL ASSESSMENT**  
   - Summarize the key imaging findings and their clinical significance.  

2. **DIFFERENTIAL DIAGNOSIS**  
   - Prioritize pediatric conditions.  
   - Specifically consider **Juvenile Idiopathic Arthritis (JIA)** and **septic arthritis**.  
   - If another diagnosis is more likely, justify why.  
   - Avoid adult-only conditions (e.g., osteoarthritis, rotator cuff degeneration).  

3. **CLINICAL CORRELATION**  
   - Relate the imaging findings to the clinical history (symptoms, MRSA status, age).  
   - Explicitly explain what supports or argues against JIA vs septic arthritis.  

4. **RECOMMENDATIONS**  
   - Suggest next diagnostic steps (e.g., labs, joint aspiration, MRI, referral).  
   - Suggest management only in general terms (e.g., antibiotics vs rheumatology referral).  

Keep each section **concise (2–4 sentences)** and clinically focused.
"""

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