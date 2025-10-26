import json
import os
import time
from datetime import datetime
from process_reports import extract_report_sections
from ask_ai import ask_medical_ai

class PromptExperiment:
    """Framework for testing and comparing different prompt variations"""

    def __init__(self):
        self.prompts = {}
        self._load_prompt_versions()

    def _load_prompt_versions(self):
        """Define different prompt versions to test"""

        # CURRENT VERSION (from process_reports.py)
        self.prompts['v1_current'] = """
You are an experienced **pediatric radiologist** analyzing a case.
Your role is to provide a structured diagnostic assessment tailored to children.

EXAMINATION: {examination}
CLINICAL HISTORY: {clinical_details}
COMPARISON: {comparison}
RADIOLOGY FINDINGS: {findings}

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

        # ENHANCED VERSION - More explicit age emphasis
        self.prompts['v2_age_emphasis'] = """
You are a **pediatric radiologist** evaluating a CHILD (NOT an adult).
CRITICAL: This patient is a CHILD. Adult conditions like osteoarthritis, degenerative disc disease, and rotator cuff tears DO NOT occur in children.

PATIENT: PEDIATRIC (child/infant)
EXAMINATION: {examination}
CLINICAL HISTORY: {clinical_details}
COMPARISON: {comparison}
RADIOLOGY FINDINGS: {findings}

Provide a structured assessment:

1. **CLINICAL ASSESSMENT** (2-3 sentences)
   - Key imaging findings and significance

2. **DIFFERENTIAL DIAGNOSIS** (list 3-5 diagnoses)
   - ONLY pediatric conditions
   - Prioritize: JIA, septic arthritis, osteomyelitis, trauma
   - Explain reasoning for top diagnosis

3. **CLINICAL CORRELATION** (2-3 sentences)
   - How findings relate to clinical history
   - JIA vs septic arthritis differentiation

4. **RECOMMENDATIONS** (2-3 specific next steps)
   - Diagnostic tests needed
   - Specialist referrals (rheumatology, infectious disease, orthopedics)

REMEMBER: THIS IS A PEDIATRIC CASE. NO ADULT DEGENERATIVE CONDITIONS.
"""

        # SIMPLIFIED VERSION - Shorter, more direct
        self.prompts['v3_simplified'] = """
Pediatric radiology case assessment:

PATIENT AGE: Child
EXAMINATION: {examination}
HISTORY: {clinical_details}
PRIOR IMAGING: {comparison}
FINDINGS: {findings}

Provide:
1. ASSESSMENT: What are the key findings?
2. DIFFERENTIAL (pediatric only): Most likely diagnoses? Consider JIA and septic arthritis.
3. CORRELATION: How do findings match the history?
4. NEXT STEPS: What should be done next?

Keep concise. No adult conditions (no osteoarthritis, rotator cuff, etc).
"""

        # CHECKLIST VERSION - Explicit constraints
        self.prompts['v4_checklist'] = """
You are a pediatric radiologist. This is a PEDIATRIC patient.

CASE INFORMATION:
- Examination: {examination}
- Clinical History: {clinical_details}
- Comparison: {comparison}
- Findings: {findings}

PROVIDE STRUCTURED ASSESSMENT:

1. CLINICAL ASSESSMENT
   What are the key findings and their significance?

2. DIFFERENTIAL DIAGNOSIS
   List 3-5 most likely diagnoses:
   - Must be age-appropriate pediatric conditions
   - Consider: JIA, septic arthritis, osteomyelitis, trauma, infection
   - Rank by likelihood

3. CLINICAL CORRELATION
   - How do imaging findings support or refute JIA?
   - How do imaging findings support or refute septic arthritis?
   - What clinical features are most relevant?

4. RECOMMENDATIONS
   - Laboratory tests needed
   - Additional imaging
   - Specialist referrals

CONSTRAINTS:
✓ Only pediatric conditions
✗ NO osteoarthritis
✗ NO degenerative disc disease
✗ NO rotator cuff pathology
✗ NO age-related changes
"""

    def create_prompt(self, version: str, sections: dict) -> str:
        """Generate a specific prompt version with report sections"""

        if version not in self.prompts:
            raise ValueError(f"Unknown prompt version: {version}")

        template = self.prompts[version]

        return template.format(
            examination=sections.get('examination', 'Not provided'),
            clinical_details=sections.get('clinical_details', 'Not provided'),
            comparison=sections.get('comparison', 'Not provided'),
            findings=sections.get('findings', 'Not provided')
        )

    def test_prompt_version(self, version: str, report_text: str, model_name: str = "llama2:7b") -> dict:
        """Test a single prompt version on a report"""

        # Extract sections
        sections = extract_report_sections(report_text)

        # Create prompt
        prompt = self.create_prompt(version, sections)

        # Send to AI
        start_time = time.time()
        response = ask_medical_ai(prompt, model_name=model_name)
        processing_time = time.time() - start_time

        return {
            'version': version,
            'model': model_name,
            'prompt': prompt,
            'response': response,
            'processing_time': processing_time,
            'response_length': len(response)
        }

    def run_experiment(self, test_reports: list, versions: list = None,
                      model_name: str = "llama2:7b") -> dict:
        """Run experiment comparing multiple prompt versions"""

        if versions is None:
            versions = list(self.prompts.keys())

        print(f"Running prompt experiment with {len(versions)} versions on {len(test_reports)} reports")
        print("="*70)

        results = []

        for i, report_file in enumerate(test_reports):
            print(f"\nProcessing report {i+1}/{len(test_reports)}: {report_file}")

            # Read report
            with open(report_file, 'r', encoding='utf-8') as f:
                report_text = f.read()

            report_results = {
                'report_file': report_file,
                'versions': {}
            }

            # Test each prompt version
            for version in versions:
                print(f"  Testing {version}...")
                result = self.test_prompt_version(version, report_text, model_name)
                report_results['versions'][version] = result

            results.append(report_results)

        return {
            'experiment_date': datetime.now().isoformat(),
            'model': model_name,
            'versions_tested': versions,
            'total_reports': len(test_reports),
            'results': results
        }

    def save_experiment(self, experiment_data: dict, output_path: str):
        """Save experiment results to JSON"""
        with open(output_path, 'w') as f:
            json.dump(experiment_data, f, indent=2)
        print(f"\nExperiment results saved to: {output_path}")

    def compare_versions(self, experiment_data: dict):
        """Analyze and compare prompt version performance"""

        versions = experiment_data['versions_tested']

        print("\n" + "="*70)
        print("PROMPT VERSION COMPARISON")
        print("="*70)

        # Calculate average metrics per version
        version_stats = {v: {'times': [], 'lengths': []} for v in versions}

        for report_result in experiment_data['results']:
            for version, data in report_result['versions'].items():
                version_stats[version]['times'].append(data['processing_time'])
                version_stats[version]['lengths'].append(data['response_length'])

        # Print comparison table
        print(f"\n{'Version':<20} {'Avg Time (s)':<15} {'Avg Length (chars)':<20}")
        print("-"*70)

        for version in versions:
            avg_time = sum(version_stats[version]['times']) / len(version_stats[version]['times'])
            avg_length = sum(version_stats[version]['lengths']) / len(version_stats[version]['lengths'])
            print(f"{version:<20} {avg_time:<15.2f} {avg_length:<20.0f}")

        print("\n" + "="*70)
        print("SAMPLE RESPONSES")
        print("="*70)

        # Show first report's responses for comparison
        if experiment_data['results']:
            first_report = experiment_data['results'][0]
            print(f"\nReport: {first_report['report_file']}")

            for version in versions:
                print(f"\n{'-'*70}")
                print(f"VERSION: {version}")
                print(f"{'-'*70}")
                response = first_report['versions'][version]['response']
                # Print first 500 chars
                print(response[:500] + "..." if len(response) > 500 else response)

    def export_prompts_documentation(self, output_path: str = "config/prompt_versions.md"):
        """Export all prompt versions as documentation for paper"""

        doc_lines = ["# Prompt Engineering Iterations\n"]
        doc_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        doc_lines.append("---\n")

        for version, prompt_template in self.prompts.items():
            doc_lines.append(f"\n## {version.upper()}\n")
            doc_lines.append("```")
            doc_lines.append(prompt_template)
            doc_lines.append("```\n")

        doc_content = "\n".join(doc_lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)

        print(f"Prompt documentation saved to: {output_path}")


def quick_experiment():
    """Run a quick experiment on a few test cases"""

    # Get some test reports
    all_folder = "all"
    if not os.path.exists(all_folder):
        print("Error: 'all' folder not found")
        return

    files = [os.path.join(all_folder, f) for f in os.listdir(all_folder) if f.endswith('.txt')]

    # Use first 3 files for quick test
    test_files = files[:30]

    print(f"Quick experiment with {len(test_files)} reports")

    # Initialize experiment
    experiment = PromptExperiment()

    # Test all versions
    results = experiment.run_experiment(test_files)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"results/prompt_experiment_{timestamp}.json"
    experiment.save_experiment(results, output_path)

    # Compare versions
    experiment.compare_versions(results)

    # Export documentation
    experiment.export_prompts_documentation()

    return results


if __name__ == "__main__":
    # Run quick experiment
    quick_experiment()
