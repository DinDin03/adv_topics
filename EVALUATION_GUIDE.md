# Evaluation Framework - Usage Guide

This guide explains how to use the evaluation tools created for your Advanced Topics project.

## 📁 New Files Created

```
project/
├── src/
│   ├── evaluate_system.py          # Main evaluation framework
│   ├── analyze_batch_results.py    # Batch results analyzer
│   ├── prompt_experiments.py       # Prompt testing framework
│   └── generate_paper_figures.py   # Paper tables generator
├── data/
│   └── ground_truth.json           # Ground truth annotations (4 cases done, add more)
└── paper_outputs/                  # Generated tables and figures (auto-created)
```

## 🚀 Quick Start

### 1. Evaluate Your Existing Results

```bash
cd src
python evaluate_system.py
```

**What it does:**
- Loads ground truth from `data/ground_truth.json`
- Evaluates your most recent batch results
- Checks for:
  - Section completeness (4 required sections)
  - Differential diagnosis coverage
  - Inappropriate adult diagnoses
  - Pediatric appropriateness
- Generates detailed evaluation report
- Saves results to `results/evaluation_TIMESTAMP.json`

### 2. Analyze All Batch Results

```bash
python analyze_batch_results.py
```

**What it does:**
- Analyzes ALL batch result files in `results/` folder
- Calculates:
  - Processing time statistics (mean, median, std dev)
  - Output length distributions
  - Diagnosis frequency counts
  - Throughput (reports/minute)
- Flags inappropriate diagnoses
- Exports CSV for paper tables
- Saves to `results/analysis_summary_TIMESTAMP.json`

### 3. Run Prompt Experiments

```bash
python prompt_experiments.py
```

**What it does:**
- Tests 4 different prompt versions:
  - `v1_current`: Your current prompt
  - `v2_age_emphasis`: Enhanced pediatric emphasis
  - `v3_simplified`: Shorter, direct format
  - `v4_checklist`: Explicit constraints
- Runs on 3 test reports (quick test)
- Compares performance metrics
- Saves to `results/prompt_experiment_TIMESTAMP.json`
- Exports prompt documentation to `config/prompt_versions.md`

### 4. Generate Paper Tables

```bash
python generate_paper_figures.py
```

**What it does:**
- Creates formatted tables for your paper:
  - Table 1: System performance metrics
  - Table 2: Evaluation metrics
  - Table 3: Diagnosis frequency
  - Table 4: Prompt version comparison
  - Table 5: Example case evaluations
- Generates both Markdown and LaTeX formats
- Creates summary statistics document
- Saves everything to `paper_outputs/` folder

## 📊 Understanding the Metrics

### Completeness Score
- Checks if AI output contains all 4 required sections
- Score: 0.0 to 1.0 (higher is better)
- Target: ≥ 0.75

### Differential Coverage
- % of expected diagnoses mentioned by AI
- Score: 0.0 to 1.0 (higher is better)
- Target: ≥ 0.60

### Pediatric Appropriateness Rate
- % of cases WITHOUT adult diagnoses
- Score: 0.0 to 1.0 (higher is better)
- Target: 1.0 (100%)

**Red Flags (adult conditions that shouldn't appear):**
- Osteoarthritis
- Rotator cuff tears
- Degenerative disc disease
- Age-related changes

## 📝 Adding More Ground Truth Cases

Edit `data/ground_truth.json`:

```json
{
  "filename": "YOUR_REPORT.txt",
  "patient_info": {
    "age_category": "pediatric",
    "clinical_history": "Brief history"
  },
  "ground_truth": {
    "primary_diagnosis": "Most likely diagnosis",
    "differential_diagnoses": [
      "Diagnosis 1",
      "Diagnosis 2",
      "Diagnosis 3"
    ],
    "inappropriate_diagnoses": [
      "Adult conditions to avoid"
    ],
    "key_findings": [
      "Finding 1",
      "Finding 2"
    ],
    "appropriate_recommendations": [
      "Recommendation 1",
      "Recommendation 2"
    ],
    "notes": "Any special notes"
  },
  "annotated": true
}
```

**Recommendation:** Annotate 15-20 cases for robust evaluation.

## 🔬 Running a Complete Evaluation Workflow

```bash
# 1. Analyze existing batch results
python analyze_batch_results.py

# 2. Evaluate against ground truth
python evaluate_system.py

# 3. Test prompt variations
python prompt_experiments.py

# 4. Generate all paper tables
python generate_paper_figures.py
```

All outputs will be timestamped and saved automatically.

## 📈 Using Results in Your Paper

### For Methods Section:
- Describe evaluation metrics (from `evaluate_system.py`)
- Show prompt iterations (from `config/prompt_versions.md`)

### For Results Section:
- Use tables from `paper_outputs/paper_tables_*.md`
- Include processing time statistics
- Show diagnosis frequency distribution

### For Discussion Section:
- Reference inappropriate diagnosis findings
- Discuss prompt optimization results
- Use `paper_outputs/summary_statistics_*.txt`

## 🎯 Model Comparison (Llama2 vs Meditron)

If you have results from different models:

```python
from evaluate_system import compare_models

compare_models(
    "results/batch_results_llama2.json",
    "results/batch_results_meditron.json"
)
```

This will generate a side-by-side comparison table.

## ⚠️ Important Notes

1. **Ground Truth**: Currently has 4 annotated cases. Add more for better statistics.
2. **Prompt Experiments**: Quick test uses 3 reports. Increase for production testing.
3. **Model Selection**: Default is `llama2:7b`. Change model in code if using Meditron.
4. **Ollama Required**: Make sure Ollama is running (`ollama serve`) for prompt experiments.

## 🐛 Troubleshooting

**"No ground truth found"**: Add more annotated cases to `data/ground_truth.json`

**"No batch files found"**: Check that `results/` folder contains `batch_results_*.json` files

**"Cannot connect to Ollama"**: Start Ollama server with `ollama serve`

**Empty tables**: Run analyzers first to generate required JSON files

## 📊 Expected Output Files

After running all tools:

```
results/
├── evaluation_TIMESTAMP.json          # Evaluation metrics
├── analysis_summary_TIMESTAMP.json    # Batch analysis
├── prompt_experiment_TIMESTAMP.json   # Prompt tests
├── batch_analysis_summary.csv         # CSV for Excel/paper

paper_outputs/
├── paper_tables_TIMESTAMP.md          # All tables in Markdown
├── performance_table_TIMESTAMP.tex    # LaTeX table
└── summary_statistics_TIMESTAMP.txt   # Key statistics

config/
└── prompt_versions.md                 # Prompt documentation
```

## 🎓 For Your Paper

**Key statistics to report:**
1. Total reports processed
2. Mean processing time
3. System throughput
4. Completeness score
5. Differential coverage
6. Pediatric appropriateness rate
7. Prompt optimization improvements
8. Most frequent inappropriate diagnoses

Good luck with your paper! 🚀
