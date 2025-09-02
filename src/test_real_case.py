from ask_ai import ask_medical_ai

clinical_details = "14month old with hx of septic arthritis. Swelling, erythema and tenderness increasing after finishing course of PO abx."

findings = "There is a small knee joint effusion, but has improved since the previous x-ray. Degree of soft tissue swelling has also improved significantly. No fractures identified. No abnormal lucency or periosteal reaction. Normal alignment of the knee joint. No dislocation."

medical_prompt = f"""
You are a pediatric radiologist reviewing a case. Please provide a structured diagnostic assessment.

PATIENT: 14-month-old child
CLINICAL HISTORY: {clinical_details}

RADIOLOGY FINDINGS: {findings}

Please provide:
1. CLINICAL ASSESSMENT (key findings and their significance)
2. DIFFERENTIAL DIAGNOSIS (most likely possibilities)
3. CLINICAL CORRELATION (how findings relate to patient history)
4. RECOMMENDATIONS (next steps for management)

Be specific and clinically focused.
"""

print("Testing AI with real radiology case")
print("="*50)

response = ask_medical_ai(medical_prompt)
print(response)