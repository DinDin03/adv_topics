#!/usr/bin/env python3
"""
Analyze prompt experiment results in detail
"""

import json
import re

def load_experiment(filepath):
    """Load experiment JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_for_adult_diagnoses(text):
    """Check if text contains inappropriate adult diagnoses"""
    adult_conditions = [
        'osteoarthritis', 'degenerative', 'rotator cuff',
        'degenerative disc', 'age-related', 'wear and tear'
    ]

    found = []
    text_lower = text.lower()

    for condition in adult_conditions:
        if condition in text_lower:
            found.append(condition)

    return found

def analyze_experiment(exp_filepath):
    """Comprehensive analysis of prompt experiment"""

    exp = load_experiment(exp_filepath)

    print("="*80)
    print("PROMPT EXPERIMENT DETAILED ANALYSIS")
    print("="*80)
    print(f"\nDate: {exp['experiment_date']}")
    print(f"Model: {exp['model']}")
    print(f"Reports tested: {exp['total_reports']}")
    print(f"Versions tested: {len(exp['versions_tested'])}")

    # Calculate metrics per version
    version_stats = {}

    for version in exp['versions_tested']:
        version_stats[version] = {
            'times': [],
            'lengths': [],
            'adult_diagnoses_count': 0,
            'adult_diagnoses_found': [],
            'total_cases': 0
        }

    # Collect data
    for report in exp['results']:
        for version, data in report['versions'].items():
            stats = version_stats[version]
            stats['times'].append(data['processing_time'])
            stats['lengths'].append(data['response_length'])
            stats['total_cases'] += 1

            # Check for adult diagnoses
            adult_found = check_for_adult_diagnoses(data['response'])
            if adult_found:
                stats['adult_diagnoses_count'] += 1
                stats['adult_diagnoses_found'].extend(adult_found)

    # Print comparison table
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON")
    print("="*80)
    print(f"\n{'Version':<20} {'Avg Time':<12} {'Avg Length':<15} {'Speed Rank':<12}")
    print("-"*80)

    # Sort by time
    sorted_by_time = sorted(version_stats.items(), key=lambda x: sum(x[1]['times'])/len(x[1]['times']))

    for rank, (version, stats) in enumerate(sorted_by_time, 1):
        avg_time = sum(stats['times']) / len(stats['times'])
        avg_length = sum(stats['lengths']) / len(stats['lengths'])
        print(f"{version:<20} {avg_time:<12.2f} {avg_length:<15.0f} {rank:<12}")

    # Pediatric appropriateness
    print("\n" + "="*80)
    print("PEDIATRIC APPROPRIATENESS (CRITICAL METRIC)")
    print("="*80)
    print(f"\n{'Version':<20} {'Cases with':<15} {'Appropriateness':<18} {'Grade':<10}")
    print(f"{'':20} {'Adult Dx':<15} {'Rate':<18}")
    print("-"*80)

    # Sort by appropriateness (fewer adult diagnoses = better)
    sorted_by_appropriate = sorted(
        version_stats.items(),
        key=lambda x: x[1]['adult_diagnoses_count']
    )

    for version, stats in sorted_by_appropriate:
        cases_with_adult = stats['adult_diagnoses_count']
        total = stats['total_cases']
        appropriateness = ((total - cases_with_adult) / total) * 100

        if appropriateness == 100:
            grade = "A+ ✓✓✓"
        elif appropriateness >= 66:
            grade = "B"
        elif appropriateness >= 33:
            grade = "C"
        else:
            grade = "F ✗"

        print(f"{version:<20} {cases_with_adult}/{total:<12} {appropriateness:<18.1f}% {grade:<10}")

    # Detailed findings
    print("\n" + "="*80)
    print("INAPPROPRIATE DIAGNOSES DETECTED")
    print("="*80)

    for version, stats in sorted_by_appropriate:
        if stats['adult_diagnoses_found']:
            print(f"\n{version}:")
            # Count unique occurrences
            from collections import Counter
            counts = Counter(stats['adult_diagnoses_found'])
            for diagnosis, count in counts.most_common():
                print(f"  - {diagnosis}: {count} occurrences")
        else:
            print(f"\n{version}: ✓ No inappropriate diagnoses (PERFECT!)")

    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)

    best_appropriate = sorted_by_appropriate[0]
    fastest = sorted_by_time[0]

    print(f"\n🏆 BEST for Pediatric Appropriateness: {best_appropriate[0]}")
    print(f"   - {best_appropriate[1]['adult_diagnoses_count']}/{best_appropriate[1]['total_cases']} cases with adult diagnoses")

    print(f"\n⚡ FASTEST: {fastest[0]}")
    print(f"   - Average time: {sum(fastest[1]['times'])/len(fastest[1]['times']):.2f}s")

    # Overall recommendation
    print("\n" + "-"*80)
    print("OVERALL RECOMMENDATION FOR YOUR PAPER:")
    print("-"*80)

    if best_appropriate[0] == fastest[0]:
        print(f"\n✓ Use {best_appropriate[0]} - Best on both speed AND quality!")
    else:
        best_app_time = sum(best_appropriate[1]['times'])/len(best_appropriate[1]['times'])
        fastest_time = sum(fastest[1]['times'])/len(fastest[1]['times'])
        time_diff = best_app_time - fastest_time

        print(f"\n⚖️  Trade-off decision:")
        print(f"   - {best_appropriate[0]}: Better quality but {time_diff:.1f}s slower")
        print(f"   - {fastest[0]}: Faster but {fastest[1]['adult_diagnoses_count']} inappropriate diagnoses")
        print(f"\n   RECOMMENDATION: Use {best_appropriate[0]}")
        print(f"   Reason: Clinical accuracy > speed for medical applications")

    # Calculate improvement
    current_version_stats = version_stats.get('v1_current', {})
    if current_version_stats:
        current_inappropriate = current_version_stats['adult_diagnoses_count']
        best_inappropriate = best_appropriate[1]['adult_diagnoses_count']

        if current_inappropriate > best_inappropriate:
            improvement = ((current_inappropriate - best_inappropriate) / current_inappropriate) * 100
            print(f"\n📈 IMPROVEMENT OVER CURRENT:")
            print(f"   Current (v1): {current_inappropriate}/{current_version_stats['total_cases']} inappropriate")
            print(f"   Best ({best_appropriate[0]}): {best_inappropriate}/{best_appropriate[1]['total_cases']} inappropriate")
            print(f"   ✓ {improvement:.1f}% reduction in errors!")
            print(f"\n   >> USE THIS IN YOUR PAPER!")

    return version_stats, best_appropriate, fastest


if __name__ == "__main__":
    # Analyze most recent experiment
    import os

    results_folder = "results"
    exp_files = [f for f in os.listdir(results_folder) if f.startswith('prompt_experiment_')]

    if exp_files:
        latest_exp = sorted(exp_files)[-1]
        exp_path = os.path.join(results_folder, latest_exp)

        print(f"Analyzing: {latest_exp}\n")
        analyze_experiment(exp_path)
    else:
        print("No prompt experiment results found!")
