#!/usr/bin/env python3
"""
Interactive annotation helper for creating ground truth cases
Makes it easy to annotate radiology reports
"""

import json
import os
from process_reports import extract_report_sections

class AnnotationHelper:
    """Interactive tool for creating ground truth annotations"""

    def __init__(self, ground_truth_path="data/ground_truth.json", reports_folder="all"):
        self.ground_truth_path = ground_truth_path
        self.reports_folder = reports_folder
        self.ground_truth = self.load_ground_truth()

        # Common pediatric diagnoses for quick selection
        self.common_diagnoses = [
            "Septic arthritis",
            "Juvenile Idiopathic Arthritis (JIA)",
            "JIA flare",
            "Osteomyelitis",
            "Soft tissue infection",
            "Cellulitis",
            "Abscess",
            "Traumatic effusion",
            "Fracture",
            "Normal examination",
            "Enthesitis-related arthritis",
            "Reactive arthritis",
            "Transient synovitis"
        ]

        self.inappropriate_diagnoses = [
            "Osteoarthritis",
            "Degenerative changes",
            "Rotator cuff tear",
            "Degenerative disc disease",
            "Age-related changes"
        ]

        self.common_recommendations = [
            "MRI if clinical suspicion persists",
            "Ultrasound for effusion/abscess localization",
            "Blood cultures",
            "ESR, CRP, CBC",
            "Joint aspiration if effusion develops",
            "Rheumatology referral",
            "Infectious disease consult",
            "Orthopedics consult",
            "Clinical correlation required",
            "Follow-up imaging in 1-2 weeks",
            "Antibiotic therapy"
        ]

    def load_ground_truth(self):
        """Load existing ground truth"""
        if os.path.exists(self.ground_truth_path):
            with open(self.ground_truth_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_ground_truth(self):
        """Save ground truth to file"""
        with open(self.ground_truth_path, 'w', encoding='utf-8') as f:
            json.dump(self.ground_truth, f, indent=2, ensure_ascii=False)
        print(f"\nSaved to {self.ground_truth_path}")

    def get_unannotated_reports(self):
        """Get list of reports not yet annotated"""
        annotated_files = {gt['filename'] for gt in self.ground_truth if gt.get('annotated', False)}

        all_reports = [f for f in os.listdir(self.reports_folder) if f.endswith('.txt')]
        unannotated = [f for f in all_reports if f not in annotated_files]

        return sorted(unannotated)

    def display_report(self, filename):
        """Display report in readable format"""
        filepath = os.path.join(self.reports_folder, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        sections = extract_report_sections(content)

        print("\n" + "="*80)
        print(f"REPORT: {filename}")
        print("="*80)

        print(f"\nEXAMINATION:")
        print(f"   {sections.get('examination', 'N/A')[:150]}...")

        print(f"\nCLINICAL HISTORY:")
        print(f"   {sections.get('clinical_details', 'N/A')}")

        print(f"\nFINDINGS:")
        findings = sections.get('findings', 'N/A')
        # Print first 300 chars
        print(f"   {findings[:300]}{'...' if len(findings) > 300 else ''}")

        print(f"\nCONCLUSION/IMPRESSION:")
        print(f"   {sections.get('conclusion', 'None provided')}")

        return sections

    def get_input_with_options(self, prompt, options, allow_custom=True):
        """Get user input with numbered options"""
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        if allow_custom:
            print(f"  0. Enter custom value")
            print(f"  -1. Skip/Done")

        while True:
            choice = input("\nYour choice (number): ").strip()

            if choice == '-1':
                return None

            if choice == '0' and allow_custom:
                custom = input("Enter custom value: ").strip()
                return custom if custom else None

            try:
                idx = int(choice)
                if 1 <= idx <= len(options):
                    return options[idx - 1]
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")

    def annotate_report(self, filename):
        """Interactive annotation for a single report"""

        # Display report
        sections = self.display_report(filename)

        print("\n" + "="*80)
        print("START ANNOTATION")
        print("="*80)

        # Extract clinical history for reference
        clinical_history = sections.get('clinical_details', 'Not provided')

        annotation = {
            'filename': filename,
            'patient_info': {
                'age_category': 'pediatric',
                'clinical_history': clinical_history
            },
            'ground_truth': {
                'primary_diagnosis': '',
                'differential_diagnoses': [],
                'inappropriate_diagnoses': [],
                'key_findings': [],
                'appropriate_recommendations': [],
                'notes': ''
            },
            'annotated': True
        }

        # 1. Primary diagnosis
        print("\n1. PRIMARY DIAGNOSIS")
        print("What is the most likely diagnosis based on the findings?")
        primary = input("Enter primary diagnosis: ").strip()
        annotation['ground_truth']['primary_diagnosis'] = primary

        # 2. Differential diagnoses
        print("\n2. DIFFERENTIAL DIAGNOSES")
        print("Select expected differential diagnoses (can choose multiple)")
        differentials = []

        while True:
            dx = self.get_input_with_options(
                "Add differential diagnosis:",
                self.common_diagnoses,
                allow_custom=True
            )
            if dx is None:
                break
            differentials.append(dx)
            print(f"   Added: {dx}")

        annotation['ground_truth']['differential_diagnoses'] = differentials

        # 3. Key findings
        print("\n3. KEY FINDINGS")
        print("Enter key imaging findings (one at a time, -1 when done)")
        findings = []

        count = 1
        while True:
            finding = input(f"Finding {count} (-1 to finish): ").strip()
            if finding == '-1':
                break
            if finding:
                findings.append(finding)
                count += 1

        annotation['ground_truth']['key_findings'] = findings

        # 4. Appropriate recommendations
        print("\n4. APPROPRIATE RECOMMENDATIONS")
        recommendations = []

        while True:
            rec = self.get_input_with_options(
                "Add recommendation:",
                self.common_recommendations,
                allow_custom=True
            )
            if rec is None:
                break
            recommendations.append(rec)
            print(f"   Added: {rec}")

        annotation['ground_truth']['appropriate_recommendations'] = recommendations

        # 5. Notes
        print("\n5. NOTES (optional)")
        notes = input("Any special notes about this case? ").strip()
        annotation['ground_truth']['notes'] = notes

        # Summary
        print("\n" + "="*80)
        print("ANNOTATION SUMMARY")
        print("="*80)
        print(f"File: {filename}")
        print(f"Primary Dx: {annotation['ground_truth']['primary_diagnosis']}")
        print(f"Differentials: {len(differentials)} listed")
        print(f"Key Findings: {len(findings)} listed")
        print(f"Recommendations: {len(recommendations)} listed")

        # Confirm
        confirm = input("\nSave this annotation? (y/n): ").strip().lower()

        if confirm == 'y':
            # Remove any existing annotation for this file
            self.ground_truth = [gt for gt in self.ground_truth if gt['filename'] != filename]
            # Add new annotation
            self.ground_truth.append(annotation)
            self.save_ground_truth()
            print("Annotation saved!")
            return True
        else:
            print("Annotation discarded")
            return False

    def quick_annotate_mode(self):
        """Quick annotation mode with AI assistance"""
        print("\n" + "="*80)
        print("QUICK ANNOTATION MODE")
        print("="*80)
        print("\nThis mode shows you the AI's diagnosis and you can:")
        print("  1. Accept if it looks good")
        print("  2. Modify if needed")
        print("  3. Skip if unsure")

        unannotated = self.get_unannotated_reports()

        if not unannotated:
            print("\nAll reports are annotated!")
            return

        print(f"\nFound {len(unannotated)} unannotated reports")

        # Check if we have batch results
        batch_results = None
        if os.path.exists('results'):
            result_files = [f for f in os.listdir('results')
                          if f.startswith('batch_results_') and f.endswith('.json')]
            if result_files:
                latest = sorted(result_files)[-1]
                with open(os.path.join('results', latest), 'r', encoding='utf-8') as f:
                    batch_results = json.load(f)

        for i, filename in enumerate(unannotated[:10], 1):  # First 10
            print(f"\n{'='*80}")
            print(f"ANNOTATING {i}/10: {filename}")
            print(f"{'='*80}")

            # Display report
            sections = self.display_report(filename)

            # Show AI diagnosis if available
            if batch_results:
                ai_result = next((r for r in batch_results if r['filename'] == filename), None)
                if ai_result:
                    print(f"\nAI DIAGNOSIS (for reference):")
                    print(f"{ai_result['ai_diagnosis'][:400]}...")

            choice = input("\n[1] Annotate  [2] Skip  [3] Quit: ").strip()

            if choice == '1':
                self.annotate_report(filename)
            elif choice == '3':
                break
            else:
                print("Skipped")

        print(f"\nQuick annotation session complete!")
        print(f"Total annotated: {len([gt for gt in self.ground_truth if gt.get('annotated')])}")

    def batch_import_mode(self):
        """Import multiple annotations from a simplified format"""
        print("\n" + "="*80)
        print("BATCH IMPORT MODE")
        print("="*80)
        print("\nCreate a file 'batch_annotations.txt' with this format:")
        print("""
FILE: 000d1e6f-b04c-402f-83c7-df146ae03eb2.txt
PRIMARY: Normal radiographic examination
DIFFERENTIAL: Septic arthritis, Soft tissue infection, MRSA infection
FINDINGS: Normal chest, Normal shoulder alignment, No swelling
RECOMMENDATIONS: Clinical correlation, Consider ultrasound/MRI, Blood cultures
NOTES: MRSA positive - focus on infectious workup
---
        """)

        batch_file = "batch_annotations.txt"
        if os.path.exists(batch_file):
            print(f"\nFound {batch_file}")
            # Implementation would parse the file
            print("Feature coming soon! Use interactive mode for now.")
        else:
            print(f"\nNo {batch_file} found")

    def show_statistics(self):
        """Show annotation statistics"""
        annotated = [gt for gt in self.ground_truth if gt.get('annotated', False)]
        total_reports = len([f for f in os.listdir(self.reports_folder) if f.endswith('.txt')])

        print("\n" + "="*80)
        print("ANNOTATION STATISTICS")
        print("="*80)
        print(f"\nTotal reports in folder: {total_reports}")
        print(f"Annotated reports: {len(annotated)}")
        print(f"Remaining: {total_reports - len(annotated)}")
        print(f"Completion: {(len(annotated)/total_reports)*100:.1f}%")

        if annotated:
            print(f"\nAnnotated files:")
            for gt in annotated[:10]:
                print(f"  - {gt['filename']}")
            if len(annotated) > 10:
                print(f"  ... and {len(annotated)-10} more")

    def interactive_menu(self):
        """Main interactive menu"""

        while True:
            print("\n" + "="*80)
            print("GROUND TRUTH ANNOTATION HELPER")
            print("="*80)

            unannotated = self.get_unannotated_reports()
            annotated_count = len([gt for gt in self.ground_truth if gt.get('annotated', False)])

            print(f"\nAnnotated: {annotated_count} | Remaining: {len(unannotated)}")

            print("\nOptions:")
            print("  1. Annotate next report (full mode)")
            print("  2. Quick annotate (show AI suggestions)")
            print("  3. Choose specific report")
            print("  4. Show statistics")
            print("  5. Exit")

            choice = input("\nChoice: ").strip()

            if choice == '1':
                if unannotated:
                    self.annotate_report(unannotated[0])
                else:
                    print("\nAll reports annotated!")

            elif choice == '2':
                self.quick_annotate_mode()

            elif choice == '3':
                if unannotated:
                    print("\nAvailable reports:")
                    for i, f in enumerate(unannotated[:20], 1):
                        print(f"  {i}. {f}")

                    try:
                        idx = int(input("\nChoose number: ")) - 1
                        if 0 <= idx < len(unannotated):
                            self.annotate_report(unannotated[idx])
                    except ValueError:
                        print("Invalid choice")
                else:
                    print("\nAll reports annotated!")

            elif choice == '4':
                self.show_statistics()

            elif choice == '5':
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    helper = AnnotationHelper()
    helper.interactive_menu()
