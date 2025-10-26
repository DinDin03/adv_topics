#!/usr/bin/env python3
"""
Run complete evaluation pipeline for paper
Executes all evaluation scripts in sequence
"""

import os
import sys
from datetime import datetime

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def run_evaluation_pipeline():
    """Run all evaluation scripts in order"""

    start_time = datetime.now()

    print_section("STARTING FULL EVALUATION PIPELINE")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check if we're in the right directory
    if not os.path.exists('analyze_batch_results.py'):
        print("❌ Error: Please run this script from the src/ directory")
        print("   Usage: cd src && python run_full_evaluation.py")
        return

    # Step 1: Analyze batch results
    print_section("STEP 1/4: Analyzing Batch Results")
    try:
        import analyze_batch_results
        analyzer = analyze_batch_results.BatchResultsAnalyzer()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analyzer.generate_summary_report(f"../results/analysis_summary_{timestamp}.json")
        analyzer.export_for_paper()
        print("✓ Batch analysis complete")
    except Exception as e:
        print(f"❌ Error in batch analysis: {e}")
        print("   Continuing with other steps...\n")

    # Step 2: Evaluate system
    print_section("STEP 2/4: Evaluating System Performance")
    try:
        import evaluate_system
        evaluator = evaluate_system.DiagnosticEvaluator()

        # Find most recent batch results
        results_folder = "../results"
        if os.path.exists(results_folder):
            result_files = [f for f in os.listdir(results_folder)
                          if f.startswith('batch_results_') and f.endswith('.json')]

            if result_files:
                latest_file = sorted(result_files)[-1]
                results_path = os.path.join(results_folder, latest_file)

                print(f"Evaluating: {latest_file}")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"../results/evaluation_{timestamp}.json"

                evaluator.generate_evaluation_report(results_path, output_path)
                print("✓ System evaluation complete")
            else:
                print("⚠️  No batch result files found - skipping evaluation")
        else:
            print("⚠️  Results folder not found - skipping evaluation")

    except Exception as e:
        print(f"❌ Error in system evaluation: {e}")
        print("   Continuing with other steps...\n")

    # Step 3: Run prompt experiments
    print_section("STEP 3/4: Running Prompt Experiments")
    print("⚠️  This step requires Ollama to be running (ollama serve)")
    print("   Testing 3 reports with 4 prompt versions (may take 2-5 minutes)")

    user_input = input("\nDo you want to run prompt experiments? (y/n): ")

    if user_input.lower() == 'y':
        try:
            import prompt_experiments
            results = prompt_experiments.quick_experiment()
            print("✓ Prompt experiments complete")
        except Exception as e:
            print(f"❌ Error in prompt experiments: {e}")
            print("   Make sure Ollama is running: ollama serve")
    else:
        print("⚠️  Skipping prompt experiments")

    # Step 4: Generate paper figures
    print_section("STEP 4/4: Generating Paper Figures and Tables")
    try:
        import generate_paper_figures
        generator = generate_paper_figures.PaperFigureGenerator()
        generator.generate_all_tables()
        generator.generate_summary_statistics()
        print("✓ Paper figures generated")
    except Exception as e:
        print(f"❌ Error generating figures: {e}")

    # Summary
    end_time = datetime.now()
    duration = end_time - start_time

    print_section("EVALUATION PIPELINE COMPLETE")
    print(f"Start Time:    {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time:      {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Duration: {duration.total_seconds():.1f} seconds")

    print("\n📁 Output Locations:")
    print("   • Batch Analysis:    results/analysis_summary_*.json")
    print("   • System Evaluation: results/evaluation_*.json")
    print("   • Prompt Experiments: results/prompt_experiment_*.json")
    print("   • Paper Tables:      paper_outputs/paper_tables_*.md")
    print("   • Summary Stats:     paper_outputs/summary_statistics_*.txt")

    print("\n📊 Next Steps:")
    print("   1. Review generated tables in paper_outputs/")
    print("   2. Add more ground truth cases to data/ground_truth.json")
    print("   3. If prompt experiments weren't run, execute: python prompt_experiments.py")
    print("   4. Use EVALUATION_GUIDE.md for detailed usage instructions")

    print("\n✅ Ready for paper writing!\n")


if __name__ == "__main__":
    try:
        run_evaluation_pipeline()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
