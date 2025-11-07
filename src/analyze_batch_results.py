import json
import os
from datetime import datetime
from typing import Dict, List
import statistics

class BatchResultsAnalyzer:
    """Analyzes batch processing results to extract performance statistics"""

    def __init__(self, results_folder="results"):
        self.results_folder = results_folder
        self.batch_files = self._discover_batch_files()

    def _discover_batch_files(self) -> List[str]:
        """Find all batch result JSON files"""
        if not os.path.exists(self.results_folder):
            return []

        files = [f for f in os.listdir(self.results_folder)
                 if f.startswith('batch_results_') and f.endswith('.json')]
        return sorted(files)

    def load_batch(self, filename: str) -> List[Dict]:
        """Load a single batch result file"""
        path = os.path.join(self.results_folder, filename)
        with open(path, 'r') as f:
            return json.load(f)

    def analyze_processing_times(self, batch_data: List[Dict]) -> Dict:
        """Analyze processing time statistics"""
        times = [result.get('processing_time', 0) for result in batch_data if 'processing_time' in result]

        if not times:
            return {'error': 'No processing time data'}

        return {
            'count': len(times),
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'min': min(times),
            'max': max(times),
            'total': sum(times)
        }

    def analyze_output_lengths(self, batch_data: List[Dict]) -> Dict:
        """Analyze AI response length statistics"""
        lengths = [len(result.get('ai_diagnosis', '')) for result in batch_data]

        if not lengths:
            return {'error': 'No output data'}

        return {
            'mean_chars': statistics.mean(lengths),
            'median_chars': statistics.median(lengths),
            'min_chars': min(lengths),
            'max_chars': max(lengths)
        }

    def extract_diagnoses_mentioned(self, batch_data: List[Dict]) -> Dict[str, int]:
        """Extract and count diagnoses mentioned across all reports"""

        # Common pediatric and general diagnoses to track
        diagnosis_keywords = [
            'septic arthritis', 'juvenile idiopathic arthritis', 'jia',
            'osteomyelitis', 'abscess', 'cellulitis', 'fracture',
            'effusion', 'inflammation', 'infection', 'normal',
            'osteoarthritis', 'rotator cuff', 'degenerative'
        ]

        diagnosis_counts = {keyword: 0 for keyword in diagnosis_keywords}

        for result in batch_data:
            diagnosis_text = result.get('ai_diagnosis', '').lower()

            for keyword in diagnosis_keywords:
                if keyword in diagnosis_text:
                    diagnosis_counts[keyword] += 1

        return diagnosis_counts

    def analyze_single_batch(self, filename: str) -> Dict:
        """Comprehensive analysis of a single batch file"""

        batch_data = self.load_batch(filename)

        analysis = {
            'filename': filename,
            'total_reports': len(batch_data),
            'processing_times': self.analyze_processing_times(batch_data),
            'output_lengths': self.analyze_output_lengths(batch_data),
            'diagnosis_frequency': self.extract_diagnoses_mentioned(batch_data)
        }

        return analysis

    def analyze_all_batches(self) -> List[Dict]:
        """Analyze all batch files in the results folder"""

        if not self.batch_files:
            print("No batch files found in results folder")
            return []

        analyses = []

        for batch_file in self.batch_files:
            print(f"Analyzing {batch_file}...")
            analysis = self.analyze_single_batch(batch_file)
            analyses.append(analysis)

        return analyses

    def generate_summary_report(self, output_file: str = None):
        """Generate a comprehensive summary report of all batches"""

        analyses = self.analyze_all_batches()

        if not analyses:
            print("No batch data to analyze")
            return

        print("\n" + "="*80)
        print("BATCH PROCESSING ANALYSIS REPORT")
        print("="*80)

        for analysis in analyses:
            print(f"\n{'='*80}")
            print(f"BATCH: {analysis['filename']}")
            print(f"{'='*80}")
            print(f"Total Reports Processed: {analysis['total_reports']}")

            # Processing times
            if 'error' not in analysis['processing_times']:
                pt = analysis['processing_times']
                print(f"\nProcessing Time Statistics:")
                print(f"  Mean:     {pt['mean']:.2f}s")
                print(f"  Median:   {pt['median']:.2f}s")
                print(f"  Std Dev:  {pt['stdev']:.2f}s")
                print(f"  Range:    {pt['min']:.2f}s - {pt['max']:.2f}s")
                print(f"  Total:    {pt['total']:.2f}s ({pt['total']/60:.1f} minutes)")
                print(f"  Throughput: {pt['count']/(pt['total']/60):.1f} reports/minute")

            # Output lengths
            if 'error' not in analysis['output_lengths']:
                ol = analysis['output_lengths']
                print(f"\nAI Output Length Statistics:")
                print(f"  Mean:     {ol['mean_chars']:.0f} characters")
                print(f"  Median:   {ol['median_chars']:.0f} characters")
                print(f"  Range:    {ol['min_chars']} - {ol['max_chars']} characters")

            # Diagnosis frequency
            print(f"\nDiagnosis Mention Frequency:")
            # Sort by frequency
            sorted_diagnoses = sorted(analysis['diagnosis_frequency'].items(),
                                     key=lambda x: x[1], reverse=True)

            # Print top mentions
            for diagnosis, count in sorted_diagnoses[:10]:
                if count > 0:
                    pct = (count / analysis['total_reports']) * 100
                    print(f"  {diagnosis.title():<30} {count:>4} ({pct:>5.1f}%)")

            # Flag inappropriate diagnoses
            inappropriate = ['osteoarthritis', 'rotator cuff', 'degenerative']
            inappropriate_counts = {k: v for k, v in analysis['diagnosis_frequency'].items()
                                   if k in inappropriate and v > 0}

            if inappropriate_counts:
                print(f"\nWARNING - INAPPROPRIATE PEDIATRIC DIAGNOSES DETECTED:")
                for diagnosis, count in inappropriate_counts.items():
                    pct = (count / analysis['total_reports']) * 100
                    print(f"  {diagnosis.title()}: {count} cases ({pct:.1f}%)")

        # Save to JSON if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump({
                    'generated_at': datetime.now().isoformat(),
                    'total_batches_analyzed': len(analyses),
                    'batches': analyses
                }, f, indent=2)
            print(f"\n\nDetailed analysis saved to: {output_file}")

        return analyses

    def compare_batches(self, batch1_name: str, batch2_name: str):
        """Compare two specific batch files side-by-side"""

        analysis1 = self.analyze_single_batch(batch1_name)
        analysis2 = self.analyze_single_batch(batch2_name)

        print("\n" + "="*80)
        print(f"COMPARISON: {batch1_name} vs {batch2_name}")
        print("="*80)

        # Compare processing times
        if 'error' not in analysis1['processing_times'] and 'error' not in analysis2['processing_times']:
            pt1 = analysis1['processing_times']
            pt2 = analysis2['processing_times']

            print(f"\n{'Metric':<30} {batch1_name:<25} {batch2_name:<25}")
            print("-"*80)
            print(f"{'Total Reports':<30} {analysis1['total_reports']:<25} {analysis2['total_reports']:<25}")
            print(f"{'Mean Processing Time':<30} {pt1['mean']:.2f}s{'':<20} {pt2['mean']:.2f}s")
            print(f"{'Median Processing Time':<30} {pt1['median']:.2f}s{'':<20} {pt2['median']:.2f}s")
            print(f"{'Throughput':<30} {pt1['count']/(pt1['total']/60):.1f} reports/min{'':<11} {pt2['count']/(pt2['total']/60):.1f} reports/min")

        # Compare output lengths
        if 'error' not in analysis1['output_lengths'] and 'error' not in analysis2['output_lengths']:
            ol1 = analysis1['output_lengths']
            ol2 = analysis2['output_lengths']

            print(f"\n{'Mean Output Length':<30} {ol1['mean_chars']:.0f} chars{'':<16} {ol2['mean_chars']:.0f} chars")

        return analysis1, analysis2

    def export_for_paper(self, output_csv: str = "results/batch_analysis_summary.csv"):
        """Export analysis in CSV format suitable for paper tables"""

        analyses = self.analyze_all_batches()

        if not analyses:
            print("No data to export")
            return

        # Create CSV content
        csv_lines = []
        csv_lines.append("Batch,Total_Reports,Mean_Time,Median_Time,Throughput_Reports_Per_Min,Mean_Output_Length")

        for analysis in analyses:
            batch_name = analysis['filename'].replace('batch_results_', '').replace('.json', '')
            total = analysis['total_reports']

            if 'error' not in analysis['processing_times']:
                pt = analysis['processing_times']
                mean_time = f"{pt['mean']:.2f}"
                median_time = f"{pt['median']:.2f}"
                throughput = f"{pt['count']/(pt['total']/60):.2f}"
            else:
                mean_time = median_time = throughput = "N/A"

            if 'error' not in analysis['output_lengths']:
                mean_length = f"{analysis['output_lengths']['mean_chars']:.0f}"
            else:
                mean_length = "N/A"

            csv_lines.append(f"{batch_name},{total},{mean_time},{median_time},{throughput},{mean_length}")

        # Write to file
        csv_content = "\n".join(csv_lines)

        with open(output_csv, 'w') as f:
            f.write(csv_content)

        print(f"\nCSV exported to: {output_csv}")
        print("\nPreview:")
        print(csv_content)

        return csv_content


if __name__ == "__main__":
    analyzer = BatchResultsAnalyzer()

    # Generate comprehensive report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analyzer.generate_summary_report(f"results/analysis_summary_{timestamp}.json")

    print("\n" + "="*80)
    print("Exporting data for paper...")
    print("="*80)
    analyzer.export_for_paper()
