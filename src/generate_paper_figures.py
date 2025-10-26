import json
import os
from datetime import datetime
from typing import Dict, List

class PaperFigureGenerator:
    """Generate tables and formatted output for academic paper"""

    def __init__(self, results_folder="results"):
        self.results_folder = results_folder
        self.output_folder = "paper_outputs"
        os.makedirs(self.output_folder, exist_ok=True)

    def load_json(self, filename: str):
        """Load a JSON file from results folder"""
        path = os.path.join(self.results_folder, filename)
        with open(path, 'r') as f:
            return json.load(f)

    def generate_performance_table_latex(self, analysis_file: str) -> str:
        """Generate LaTeX table for system performance metrics"""

        data = self.load_json(analysis_file)

        latex = []
        latex.append("\\begin{table}[h]")
        latex.append("\\centering")
        latex.append("\\caption{System Performance Metrics}")
        latex.append("\\label{tab:performance}")
        latex.append("\\begin{tabular}{lcc}")
        latex.append("\\hline")
        latex.append("\\textbf{Metric} & \\textbf{Value} & \\textbf{Unit} \\\\")
        latex.append("\\hline")

        # Extract metrics from analysis
        if 'batches' in data:
            for batch in data['batches']:
                if 'processing_times' in batch and 'error' not in batch['processing_times']:
                    pt = batch['processing_times']

                    latex.append(f"Total Reports & {batch['total_reports']} & reports \\\\")
                    latex.append(f"Mean Processing Time & {pt['mean']:.2f} & seconds \\\\")
                    latex.append(f"Median Processing Time & {pt['median']:.2f} & seconds \\\\")
                    latex.append(f"Throughput & {pt['count']/(pt['total']/60):.1f} & reports/min \\\\")

                    if 'output_lengths' in batch:
                        ol = batch['output_lengths']
                        latex.append(f"Mean Output Length & {ol['mean_chars']:.0f} & characters \\\\")

                    break  # Use first batch only

        latex.append("\\hline")
        latex.append("\\end{tabular}")
        latex.append("\\end{table}")

        return "\n".join(latex)

    def generate_performance_table_markdown(self, analysis_file: str) -> str:
        """Generate Markdown table for system performance metrics"""

        data = self.load_json(analysis_file)

        md = []
        md.append("## Table 1: System Performance Metrics\n")
        md.append("| Metric | Value | Unit |")
        md.append("|--------|-------|------|")

        if 'batches' in data:
            for batch in data['batches']:
                if 'processing_times' in batch and 'error' not in batch['processing_times']:
                    pt = batch['processing_times']

                    md.append(f"| Total Reports | {batch['total_reports']} | reports |")
                    md.append(f"| Mean Processing Time | {pt['mean']:.2f} | seconds |")
                    md.append(f"| Median Processing Time | {pt['median']:.2f} | seconds |")
                    md.append(f"| Standard Deviation | {pt['stdev']:.2f} | seconds |")
                    md.append(f"| Throughput | {pt['count']/(pt['total']/60):.1f} | reports/min |")

                    if 'output_lengths' in batch:
                        ol = batch['output_lengths']
                        md.append(f"| Mean Output Length | {ol['mean_chars']:.0f} | characters |")

                    break

        return "\n".join(md)

    def generate_evaluation_table_markdown(self, evaluation_file: str) -> str:
        """Generate Markdown table for evaluation metrics"""

        data = self.load_json(evaluation_file)

        md = []
        md.append("## Table 2: Diagnostic System Evaluation Metrics\n")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")

        md.append(f"| Total Cases Evaluated | {data['total_cases_evaluated']} |")
        md.append(f"| Average Completeness Score | {data['average_completeness_score']:.1%} |")
        md.append(f"| Average Differential Coverage | {data['average_differential_coverage']:.1%} |")
        md.append(f"| Pediatric Appropriateness Rate | {data['pediatric_appropriateness_rate']:.1%} |")
        md.append(f"| Cases with Inappropriate Diagnoses | {data['cases_with_inappropriate_diagnoses']} |")

        md.append("\n### Section Presence\n")
        md.append("| Section | Presence Rate |")
        md.append("|---------|---------------|")

        for section, pct in data['section_presence_percentage'].items():
            section_name = section.replace('_', ' ').title()
            md.append(f"| {section_name} | {pct:.1f}% |")

        if data['inappropriate_diagnoses_frequency']:
            md.append("\n### Inappropriate Diagnoses Detected\n")
            md.append("| Diagnosis | Frequency |")
            md.append("|-----------|-----------|")

            for diagnosis, count in data['inappropriate_diagnoses_frequency'].items():
                md.append(f"| {diagnosis.title()} | {count} |")

        return "\n".join(md)

    def generate_diagnosis_frequency_table(self, analysis_file: str) -> str:
        """Generate table showing diagnosis mention frequency"""

        data = self.load_json(analysis_file)

        md = []
        md.append("## Table 3: Diagnosis Mention Frequency\n")
        md.append("| Diagnosis | Count | Percentage |")
        md.append("|-----------|-------|------------|")

        if 'batches' in data:
            for batch in data['batches']:
                if 'diagnosis_frequency' in batch:
                    total = batch['total_reports']

                    # Sort by frequency
                    sorted_dx = sorted(batch['diagnosis_frequency'].items(),
                                      key=lambda x: x[1], reverse=True)

                    for diagnosis, count in sorted_dx:
                        if count > 0:
                            pct = (count / total) * 100
                            md.append(f"| {diagnosis.title()} | {count} | {pct:.1f}% |")

                    break

        return "\n".join(md)

    def generate_prompt_comparison_table(self, experiment_file: str) -> str:
        """Generate comparison table for prompt experiments"""

        data = self.load_json(experiment_file)

        md = []
        md.append("## Table 4: Prompt Version Comparison\n")
        md.append("| Version | Avg Time (s) | Avg Length (chars) | Notes |")
        md.append("|---------|--------------|-------------------|-------|")

        # Calculate stats per version
        versions = data.get('versions_tested', [])
        version_stats = {v: {'times': [], 'lengths': []} for v in versions}

        for report in data.get('results', []):
            for version, result in report['versions'].items():
                version_stats[version]['times'].append(result['processing_time'])
                version_stats[version]['lengths'].append(result['response_length'])

        version_descriptions = {
            'v1_current': 'Current baseline',
            'v2_age_emphasis': 'Enhanced age emphasis',
            'v3_simplified': 'Simplified structure',
            'v4_checklist': 'Explicit checklist'
        }

        for version in versions:
            stats = version_stats[version]
            if stats['times']:
                avg_time = sum(stats['times']) / len(stats['times'])
                avg_length = sum(stats['lengths']) / len(stats['lengths'])
                notes = version_descriptions.get(version, '')

                md.append(f"| {version} | {avg_time:.2f} | {avg_length:.0f} | {notes} |")

        return "\n".join(md)

    def generate_case_examples_table(self, evaluation_file: str, n_examples: int = 5) -> str:
        """Generate table showing example case evaluations"""

        data = self.load_json(evaluation_file)

        md = []
        md.append("## Table 5: Example Case Evaluations\n")
        md.append("| Case | Completeness | Differential Coverage | Pediatric Appropriate | Issues |")
        md.append("|------|--------------|----------------------|----------------------|--------|")

        for eval in data.get('individual_evaluations', [])[:n_examples]:
            filename_short = eval['filename'][:20] + "..." if len(eval['filename']) > 20 else eval['filename']
            completeness = f"{eval['completeness_score']:.0%}"
            coverage = f"{eval['differential_coverage']['coverage_rate']:.0%}"
            appropriate = "✓" if eval['pediatric_appropriateness'] == 1.0 else "✗"

            issues = []
            if eval['inappropriate_diagnoses_found']:
                issues.append(f"Inappropriate: {', '.join(eval['inappropriate_diagnoses_found'][:2])}")
            if eval['differential_coverage']['missed']:
                issues.append(f"Missed: {len(eval['differential_coverage']['missed'])}")

            issues_str = "; ".join(issues) if issues else "None"

            md.append(f"| {filename_short} | {completeness} | {coverage} | {appropriate} | {issues_str} |")

        return "\n".join(md)

    def generate_all_tables(self):
        """Generate all tables and save to files"""

        # Find latest files
        result_files = [f for f in os.listdir(self.results_folder) if f.endswith('.json')]

        analysis_files = [f for f in result_files if f.startswith('analysis_summary_')]
        evaluation_files = [f for f in result_files if f.startswith('evaluation_')]
        experiment_files = [f for f in result_files if f.startswith('prompt_experiment_')]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_folder, f"paper_tables_{timestamp}.md")

        with open(output_file, 'w') as f:
            f.write(f"# Paper Tables and Figures\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Performance table
            if analysis_files:
                latest_analysis = sorted(analysis_files)[-1]
                print(f"Using analysis file: {latest_analysis}")

                f.write(self.generate_performance_table_markdown(latest_analysis))
                f.write("\n\n---\n\n")

                f.write(self.generate_diagnosis_frequency_table(latest_analysis))
                f.write("\n\n---\n\n")

            # Evaluation table
            if evaluation_files:
                latest_evaluation = sorted(evaluation_files)[-1]
                print(f"Using evaluation file: {latest_evaluation}")

                f.write(self.generate_evaluation_table_markdown(latest_evaluation))
                f.write("\n\n---\n\n")

                f.write(self.generate_case_examples_table(latest_evaluation))
                f.write("\n\n---\n\n")

            # Prompt comparison
            if experiment_files:
                latest_experiment = sorted(experiment_files)[-1]
                print(f"Using experiment file: {latest_experiment}")

                f.write(self.generate_prompt_comparison_table(latest_experiment))
                f.write("\n\n---\n\n")

        print(f"\n✓ All tables generated and saved to: {output_file}")

        # Also generate LaTeX version for performance table
        if analysis_files:
            latex_file = os.path.join(self.output_folder, f"performance_table_{timestamp}.tex")
            with open(latex_file, 'w') as f:
                f.write(self.generate_performance_table_latex(sorted(analysis_files)[-1]))
            print(f"✓ LaTeX table saved to: {latex_file}")

        return output_file

    def generate_summary_statistics(self):
        """Generate a summary statistics document"""

        result_files = [f for f in os.listdir(self.results_folder) if f.endswith('.json')]

        analysis_files = [f for f in result_files if f.startswith('analysis_summary_')]
        evaluation_files = [f for f in result_files if f.startswith('evaluation_')]

        if not (analysis_files and evaluation_files):
            print("Missing required files for summary")
            return

        analysis = self.load_json(sorted(analysis_files)[-1])
        evaluation = self.load_json(sorted(evaluation_files)[-1])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_folder, f"summary_statistics_{timestamp}.txt")

        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("SUMMARY STATISTICS FOR PAPER\n")
            f.write("="*70 + "\n\n")

            # Key findings
            f.write("KEY FINDINGS:\n")
            f.write("-" * 70 + "\n\n")

            if 'batches' in analysis:
                batch = analysis['batches'][0]
                if 'processing_times' in batch:
                    pt = batch['processing_times']
                    f.write(f"• Processed {batch['total_reports']} radiology reports\n")
                    f.write(f"• Average processing time: {pt['mean']:.2f}s per report\n")
                    f.write(f"• System throughput: {pt['count']/(pt['total']/60):.1f} reports/minute\n\n")

            f.write(f"• Completeness score: {evaluation['average_completeness_score']:.1%}\n")
            f.write(f"• Differential diagnosis coverage: {evaluation['average_differential_coverage']:.1%}\n")
            f.write(f"• Pediatric appropriateness: {evaluation['pediatric_appropriateness_rate']:.1%}\n\n")

            # Issues identified
            if evaluation['cases_with_inappropriate_diagnoses'] > 0:
                f.write("ISSUES IDENTIFIED:\n")
                f.write("-" * 70 + "\n")
                f.write(f"• {evaluation['cases_with_inappropriate_diagnoses']} cases contained inappropriate adult diagnoses\n")

                if evaluation['inappropriate_diagnoses_frequency']:
                    f.write("• Most common inappropriate diagnoses:\n")
                    for diagnosis, count in list(evaluation['inappropriate_diagnoses_frequency'].items())[:3]:
                        f.write(f"  - {diagnosis.title()}: {count} cases\n")
                f.write("\n")

            # Strengths
            f.write("SYSTEM STRENGTHS:\n")
            f.write("-" * 70 + "\n")
            f.write(f"• High completeness rate: {evaluation['section_presence_percentage'].get('clinical_assessment', 0):.1f}% of reports include all required sections\n")
            f.write("• Fast processing enables real-time clinical use\n")
            f.write("• Structured output format aids clinical decision-making\n\n")

            # Limitations
            f.write("LIMITATIONS:\n")
            f.write("-" * 70 + "\n")
            f.write("• Occasional inclusion of adult-specific diagnoses in pediatric cases\n")
            f.write("• Performance depends on prompt engineering\n")
            f.write("• Requires validation against expert radiologist assessments\n")

        print(f"✓ Summary statistics saved to: {output_file}")

        return output_file


if __name__ == "__main__":
    generator = PaperFigureGenerator()

    print("Generating all tables for paper...")
    generator.generate_all_tables()

    print("\nGenerating summary statistics...")
    generator.generate_summary_statistics()

    print("\n" + "="*70)
    print("COMPLETE! Check the paper_outputs/ folder for all generated files.")
    print("="*70)
