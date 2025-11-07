import json
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple

class DiagnosticEvaluator:
    """Evaluates AI diagnostic outputs against ground truth"""

    def __init__(self, ground_truth_path="data/ground_truth.json"):
        with open(ground_truth_path, 'r') as f:
            self.ground_truth = json.load(f)

        # Filter out template and unannotated entries
        self.ground_truth = [gt for gt in self.ground_truth if gt.get('annotated', False)]

        # Adult conditions that should NEVER appear in pediatric reports
        self.adult_only_conditions = [
            'osteoarthritis', 'degenerative', 'rotator cuff',
            'degenerative disc disease', 'age-related',
            'wear and tear', 'arthropathy'
        ]

    def load_batch_results(self, results_path):
        """Load AI-generated results from JSON file"""
        with open(results_path, 'r') as f:
            return json.load(f)

    def check_section_completeness(self, ai_diagnosis: str) -> Dict[str, bool]:
        """Check if AI output contains all required sections"""
        sections = {
            'clinical_assessment': False,
            'differential_diagnosis': False,
            'clinical_correlation': False,
            'recommendations': False
        }

        text_lower = ai_diagnosis.lower()

        # Check for each section (case-insensitive)
        if 'clinical assessment' in text_lower or '1.' in text_lower:
            sections['clinical_assessment'] = True
        if 'differential diagnosis' in text_lower or '2.' in text_lower:
            sections['differential_diagnosis'] = True
        if 'clinical correlation' in text_lower or '3.' in text_lower:
            sections['clinical_correlation'] = True
        if 'recommendation' in text_lower or '4.' in text_lower:
            sections['recommendations'] = True

        return sections

    def detect_inappropriate_diagnoses(self, ai_diagnosis: str) -> List[str]:
        """Detect adult-only conditions mentioned in pediatric reports"""
        found_inappropriate = []
        text_lower = ai_diagnosis.lower()

        for condition in self.adult_only_conditions:
            if condition in text_lower:
                found_inappropriate.append(condition)

        return found_inappropriate

    def check_differential_coverage(self, ai_diagnosis: str, expected_diagnoses: List[str]) -> Dict:
        """Check how many expected differential diagnoses are mentioned"""
        text_lower = ai_diagnosis.lower()

        mentioned = []
        missed = []

        for diagnosis in expected_diagnoses:
            # Simplify diagnosis for matching (e.g., "JIA flare" -> "jia")
            key_terms = diagnosis.lower().split()

            # Check if any key term is in the AI response
            if any(term in text_lower for term in key_terms if len(term) > 3):
                mentioned.append(diagnosis)
            else:
                missed.append(diagnosis)

        coverage_rate = len(mentioned) / len(expected_diagnoses) if expected_diagnoses else 0

        return {
            'mentioned': mentioned,
            'missed': missed,
            'coverage_rate': coverage_rate,
            'total_expected': len(expected_diagnoses)
        }

    def evaluate_single_case(self, filename: str, ai_diagnosis: str) -> Dict:
        """Evaluate a single AI diagnosis against ground truth"""

        # Find ground truth for this file
        gt = next((g for g in self.ground_truth if g['filename'] == filename), None)

        if not gt:
            return {
                'error': 'No ground truth found',
                'filename': filename
            }

        # Perform evaluations
        section_completeness = self.check_section_completeness(ai_diagnosis)
        inappropriate = self.detect_inappropriate_diagnoses(ai_diagnosis)
        differential_coverage = self.check_differential_coverage(
            ai_diagnosis,
            gt['ground_truth']['differential_diagnoses']
        )

        # Calculate scores
        completeness_score = sum(section_completeness.values()) / len(section_completeness)
        pediatric_appropriateness = 1.0 if len(inappropriate) == 0 else 0.0

        return {
            'filename': filename,
            'section_completeness': section_completeness,
            'completeness_score': completeness_score,
            'differential_coverage': differential_coverage,
            'inappropriate_diagnoses_found': inappropriate,
            'pediatric_appropriateness': pediatric_appropriateness,
            'ground_truth_info': {
                'primary_diagnosis': gt['ground_truth']['primary_diagnosis'],
                'expected_differentials': gt['ground_truth']['differential_diagnoses']
            }
        }

    def evaluate_batch(self, batch_results_path: str) -> Dict:
        """Evaluate an entire batch of results"""

        batch_results = self.load_batch_results(batch_results_path)

        evaluations = []

        for result in batch_results:
            filename = result.get('filename')
            ai_diagnosis = result.get('ai_diagnosis', '')

            if filename and ai_diagnosis:
                eval_result = self.evaluate_single_case(filename, ai_diagnosis)
                # Only add if we have valid evaluation (not an error)
                if 'error' not in eval_result:
                    eval_result['processing_time'] = result.get('processing_time', 0)
                    evaluations.append(eval_result)

        # Calculate aggregate statistics
        total_cases = len(evaluations)

        if total_cases == 0:
            return {'error': 'No cases to evaluate'}

        # Aggregate metrics
        avg_completeness = sum(e['completeness_score'] for e in evaluations) / total_cases
        avg_coverage = sum(e['differential_coverage']['coverage_rate'] for e in evaluations) / total_cases
        pediatric_appropriate_count = sum(e['pediatric_appropriateness'] for e in evaluations)
        pediatric_appropriateness_rate = pediatric_appropriate_count / total_cases

        # Count section presence
        section_presence = {
            'clinical_assessment': 0,
            'differential_diagnosis': 0,
            'clinical_correlation': 0,
            'recommendations': 0
        }

        for eval in evaluations:
            for section, present in eval['section_completeness'].items():
                if present:
                    section_presence[section] += 1

        # Convert to percentages
        section_presence_pct = {
            section: (count / total_cases) * 100
            for section, count in section_presence.items()
        }

        # Collect all inappropriate diagnoses
        all_inappropriate = []
        for eval in evaluations:
            all_inappropriate.extend(eval['inappropriate_diagnoses_found'])

        inappropriate_frequency = {}
        for diagnosis in all_inappropriate:
            inappropriate_frequency[diagnosis] = inappropriate_frequency.get(diagnosis, 0) + 1

        summary = {
            'total_cases_evaluated': total_cases,
            'average_completeness_score': round(avg_completeness, 3),
            'average_differential_coverage': round(avg_coverage, 3),
            'pediatric_appropriateness_rate': round(pediatric_appropriateness_rate, 3),
            'cases_with_inappropriate_diagnoses': total_cases - pediatric_appropriate_count,
            'section_presence_percentage': section_presence_pct,
            'inappropriate_diagnoses_frequency': inappropriate_frequency,
            'individual_evaluations': evaluations
        }

        return summary

    def generate_evaluation_report(self, batch_results_path: str, output_path: str = None):
        """Generate a comprehensive evaluation report"""

        evaluation = self.evaluate_batch(batch_results_path)

        if 'error' in evaluation:
            print(f"Error: {evaluation['error']}")
            return

        # Print summary
        print("="*70)
        print("EVALUATION REPORT")
        print("="*70)
        print(f"\nBatch Results File: {batch_results_path}")
        print(f"Total Cases Evaluated: {evaluation['total_cases_evaluated']}")
        print("\n" + "-"*70)
        print("OVERALL METRICS")
        print("-"*70)
        print(f"Average Completeness Score: {evaluation['average_completeness_score']:.1%}")
        print(f"Average Differential Coverage: {evaluation['average_differential_coverage']:.1%}")
        print(f"Pediatric Appropriateness Rate: {evaluation['pediatric_appropriateness_rate']:.1%}")
        print(f"Cases with Inappropriate Diagnoses: {evaluation['cases_with_inappropriate_diagnoses']}")

        print("\n" + "-"*70)
        print("SECTION PRESENCE (% of cases)")
        print("-"*70)
        for section, pct in evaluation['section_presence_percentage'].items():
            print(f"{section.replace('_', ' ').title()}: {pct:.1f}%")

        if evaluation['inappropriate_diagnoses_frequency']:
            print("\n" + "-"*70)
            print("INAPPROPRIATE DIAGNOSES FOUND")
            print("-"*70)
            for diagnosis, count in evaluation['inappropriate_diagnoses_frequency'].items():
                print(f"{diagnosis}: {count} cases")

        print("\n" + "-"*70)
        print("INDIVIDUAL CASE DETAILS")
        print("-"*70)
        for eval in evaluation['individual_evaluations']:
            print(f"\n{eval['filename']}:")
            print(f"  Completeness: {eval['completeness_score']:.1%}")
            print(f"  Differential Coverage: {eval['differential_coverage']['coverage_rate']:.1%} "
                  f"({len(eval['differential_coverage']['mentioned'])}/{eval['differential_coverage']['total_expected']})")
            if eval['inappropriate_diagnoses_found']:
                print(f"  WARNING - Inappropriate: {', '.join(eval['inappropriate_diagnoses_found'])}")
            if eval['differential_coverage']['missed']:
                print(f"  Missed: {', '.join(eval['differential_coverage']['missed'][:3])}")

        # Save to file if output path provided
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(evaluation, f, indent=2)
            print(f"\n\nDetailed evaluation saved to: {output_path}")

        return evaluation


def compare_models(llama_results_path: str, meditron_results_path: str):
    """Compare Llama2 vs Meditron performance side-by-side"""

    evaluator = DiagnosticEvaluator()

    print("Evaluating Llama2 results...")
    llama_eval = evaluator.evaluate_batch(llama_results_path)

    print("Evaluating Meditron results...")
    meditron_eval = evaluator.evaluate_batch(meditron_results_path)

    print("\n" + "="*70)
    print("MODEL COMPARISON: Llama2 vs Meditron")
    print("="*70)

    metrics = [
        ('Average Completeness', 'average_completeness_score'),
        ('Differential Coverage', 'average_differential_coverage'),
        ('Pediatric Appropriateness', 'pediatric_appropriateness_rate')
    ]

    print(f"\n{'Metric':<30} {'Llama2':<15} {'Meditron':<15} {'Winner':<10}")
    print("-"*70)

    for metric_name, metric_key in metrics:
        llama_val = llama_eval[metric_key]
        meditron_val = meditron_eval[metric_key]
        winner = "Llama2" if llama_val > meditron_val else "Meditron" if meditron_val > llama_val else "Tie"
        print(f"{metric_name:<30} {llama_val:.1%}{'':>8} {meditron_val:.1%}{'':>8} {winner:<10}")

    return {
        'llama2': llama_eval,
        'meditron': meditron_eval
    }


if __name__ == "__main__":
    # Example usage
    evaluator = DiagnosticEvaluator()

    # Find the most recent batch results
    results_folder = "results"
    if os.path.exists(results_folder):
        result_files = [f for f in os.listdir(results_folder) if f.endswith('.json')]

        if result_files:
            # Use the most recent file
            latest_file = sorted(result_files)[-1]
            results_path = os.path.join(results_folder, latest_file)

            print(f"Evaluating: {results_path}\n")

            # Generate report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"results/evaluation_{timestamp}.json"

            evaluator.generate_evaluation_report(results_path, output_path)
        else:
            print("No batch result files found in results/ folder")
    else:
        print("results/ folder not found")
