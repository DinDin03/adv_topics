#!/usr/bin/env python3
"""
Auto-suggest ground truth annotations from AI results
Speeds up annotation by pre-filling reasonable defaults
"""

import json
import os
import re

def extract_diagnoses_from_ai(ai_diagnosis):
    """Extract potential diagnoses from AI text"""
    diagnoses = []

    # Look for differential diagnosis section
    diff_section = re.search(
        r'(?:differential diagnosis|diagnoses).*?(?=\n\n|clinical|recommendation|$)',
        ai_diagnosis.lower(),
        re.DOTALL
    )

    if diff_section:
        text = diff_section.group()

        # Common patterns
        patterns = [
            r'(?:jia|juvenile idiopathic arthritis)',
            r'septic arthritis',
            r'osteomyelitis',
            r'cellulitis',
            r'abscess',
            r'trauma(?:tic)?',
            r'infection',
            r'effusion',
        ]

        for pattern in patterns:
            if re.search(pattern, text):
                # Clean up the match
                match = re.search(pattern, text).group()
                diagnoses.append(match.title())

    return list(set(diagnoses))  # Remove duplicates

def extract_recommendations_from_ai(ai_diagnosis):
    """Extract recommendations from AI text"""
    recommendations = []

    # Look for recommendations section
    rec_section = re.search(
        r'(?:recommendation|next steps).*?$',
        ai_diagnosis.lower(),
        re.DOTALL
    )

    if rec_section:
        text = rec_section.group()

        # Common recommendations
        if 'mri' in text:
            recommendations.append("MRI if clinical suspicion persists")
        if 'ultrasound' in text or 'us' in text:
            recommendations.append("Ultrasound for effusion/abscess localization")
        if 'blood culture' in text:
            recommendations.append("Blood cultures")
        if 'aspiration' in text:
            recommendations.append("Joint aspiration if effusion develops")
        if 'rheumatolog' in text:
            recommendations.append("Rheumatology referral")
        if 'infectious disease' in text:
            recommendations.append("Infectious disease consult")
        if 'orthopedic' in text:
            recommendations.append("Orthopedics consult")

    return recommendations

def generate_suggestions(batch_results_path, output_path="data/suggested_annotations.json"):
    """Generate suggested annotations from batch results"""

    print("Loading batch results...")
    with open(batch_results_path, 'r', encoding='utf-8') as f:
        batch_results = json.load(f)

    # Load existing ground truth to avoid duplicates
    gt_path = "data/ground_truth.json"
    existing_files = set()
    if os.path.exists(gt_path):
        with open(gt_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
            existing_files = {gt['filename'] for gt in existing if gt.get('annotated')}

    suggestions = []

    print(f"Processing {len(batch_results)} results...")

    for result in batch_results:
        filename = result.get('filename')
        if filename in existing_files:
            continue  # Skip already annotated

        ai_diagnosis = result.get('ai_diagnosis', '')
        sections = result.get('extracted_sections', {})

        # Extract suggestions
        suggested_diagnoses = extract_diagnoses_from_ai(ai_diagnosis)
        suggested_recommendations = extract_recommendations_from_ai(ai_diagnosis)

        suggestion = {
            'filename': filename,
            'patient_info': {
                'age_category': 'pediatric',
                'clinical_history': sections.get('clinical_details', '')
            },
            'ground_truth': {
                'primary_diagnosis': '*** REVIEW AND EDIT ***',
                'differential_diagnoses': suggested_diagnoses,
                'inappropriate_diagnoses': [],
                'key_findings': [
                    '*** REVIEW AND ADD FINDINGS ***'
                ],
                'appropriate_recommendations': suggested_recommendations,
                'notes': '*** AUTO-GENERATED - PLEASE REVIEW ***'
            },
            'annotated': False,  # Mark as not fully annotated
            'auto_suggested': True
        }

        suggestions.append(suggestion)

    # Save suggestions
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(suggestions, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Generated {len(suggestions)} suggested annotations")
    print(f"✓ Saved to: {output_path}")
    print(f"\nNext steps:")
    print(f"1. Review {output_path}")
    print(f"2. Edit the suggestions as needed")
    print(f"3. Copy reviewed cases to data/ground_truth.json")
    print(f"4. Change 'annotated': false to 'annotated': true")

    return suggestions

def merge_suggestions_with_ground_truth(suggestions_path, ground_truth_path):
    """Merge reviewed suggestions into ground truth"""

    with open(suggestions_path, 'r', encoding='utf-8') as f:
        suggestions = json.load(f)

    # Load existing ground truth
    ground_truth = []
    if os.path.exists(ground_truth_path):
        with open(ground_truth_path, 'r', encoding='utf-8') as f:
            ground_truth = json.load(f)

    # Ask user which to merge
    print(f"\nFound {len(suggestions)} suggestions")
    print("Which ones have you reviewed and want to merge?")

    for i, sugg in enumerate(suggestions, 1):
        print(f"\n{i}. {sugg['filename']}")
        print(f"   Primary: {sugg['ground_truth']['primary_diagnosis']}")
        print(f"   Differentials: {len(sugg['ground_truth']['differential_diagnoses'])}")

        merge = input("   Merge this? (y/n/q to quit): ").strip().lower()

        if merge == 'y':
            # Remove if already exists
            ground_truth = [gt for gt in ground_truth if gt['filename'] != sugg['filename']]
            # Mark as annotated
            sugg['annotated'] = True
            sugg.pop('auto_suggested', None)
            # Add to ground truth
            ground_truth.append(sugg)
            print("   ✓ Added!")

        elif merge == 'q':
            break

    # Save updated ground truth
    with open(ground_truth_path, 'w', encoding='utf-8') as f:
        json.dump(ground_truth, f, indent=2, ensure_ascii=False)

    annotated_count = len([gt for gt in ground_truth if gt.get('annotated')])
    print(f"\n✓ Ground truth updated!")
    print(f"✓ Total annotated cases: {annotated_count}")

if __name__ == "__main__":
    import sys

    # Find latest batch results
    results_folder = "results"
    if os.path.exists(results_folder):
        batch_files = [f for f in os.listdir(results_folder)
                      if f.startswith('batch_results_') and f.endswith('.json')]

        if batch_files:
            latest = sorted(batch_files)[-1]
            batch_path = os.path.join(results_folder, latest)

            print(f"Using batch results: {latest}\n")

            if len(sys.argv) > 1 and sys.argv[1] == '--merge':
                # Merge mode
                merge_suggestions_with_ground_truth(
                    "data/suggested_annotations.json",
                    "data/ground_truth.json"
                )
            else:
                # Generate suggestions
                generate_suggestions(batch_path)

        else:
            print("No batch result files found!")
    else:
        print("Results folder not found!")
