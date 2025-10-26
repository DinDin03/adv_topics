# Ground Truth Annotation Guide

## 🎯 Quick Start

```bash
cd "C:\Users\dinet\Desktop\Uni Work\3rd Year\Advanced Topics\adv_topics"
python src/annotation_helper.py
```

## 📋 What is This Tool?

The **Annotation Helper** makes it easy to create ground truth cases by:
- Showing you the radiology report in a clear format
- Providing common diagnosis options to choose from
- Guiding you through what to annotate
- Saving everything automatically

## 🚀 How to Use

### Option 1: Interactive Menu (Recommended for Beginners)

When you run the tool, you'll see:

```
================================================================================
GROUND TRUTH ANNOTATION HELPER
================================================================================

Annotated: 4 | Remaining: 96

Options:
  1. Annotate next report (full mode)
  2. Quick annotate (show AI suggestions)
  3. Choose specific report
  4. Show statistics
  5. Exit
```

**Choose Option 2** - Quick annotate mode (easiest!)

### Option 2: Full Annotation Mode

You'll be asked for:

#### 1️⃣ Primary Diagnosis
The most likely diagnosis based on findings.

**Examples:**
- "Normal radiographic examination"
- "Septic arthritis suspected, radiographically normal"
- "Minimal knee effusion in patient with JIA"

#### 2️⃣ Differential Diagnoses (Select Multiple)
The tool shows common pediatric diagnoses:
```
1. Septic arthritis
2. Juvenile Idiopathic Arthritis (JIA)
3. JIA flare
4. Osteomyelitis
5. Soft tissue infection
6. Cellulitis
7. Abscess
... and more
```

**Just type the number** and press Enter.
Type `-1` when done.

#### 3️⃣ Key Findings
Imaging findings from the report.

**Examples:**
- "Normal chest X-ray"
- "Minimal knee joint effusion"
- "Soft tissue swelling and inflammatory changes"
- "No fracture"

#### 4️⃣ Appropriate Recommendations
What should be done next?

**Common options provided:**
```
1. MRI if clinical suspicion persists
2. Ultrasound for effusion/abscess localization
3. Blood cultures
4. ESR, CRP, CBC
5. Joint aspiration if effusion develops
6. Rheumatology referral
... and more
```

#### 5️⃣ Notes (Optional)
Any special information about the case.

**Examples:**
- "MRSA positive - should focus on infectious workup"
- "Known JIA patient - prioritize JIA-related complications"
- "X-ray cannot exclude osteomyelitis - need MRI"

## ⚡ Quick Annotate Mode (Fastest Way!)

This mode:
1. Shows you the report
2. Shows what the AI diagnosed (if available)
3. Lets you quickly annotate or skip

**Perfect for bulk annotations!**

## 💡 Tips for Fast Annotation

### Use Number Selection
Instead of typing, just select from the numbered lists:
- Faster
- No typos
- Consistent terminology

### Focus on Key Cases
You don't need to annotate all 100 reports!

**For full marks, annotate:**
- 15-20 diverse cases ✓
- Mix of different conditions
- Include both normal and abnormal

### Categories to Cover
Try to get at least 2-3 from each:
- ✓ Septic arthritis cases
- ✓ JIA cases
- ✓ Osteomyelitis cases
- ✓ Normal examinations
- ✓ Traumatic injuries
- ✓ Soft tissue infections

## 📊 Example Annotation Session

```
================================================================================
REPORT: 000d1e6f-b04c-402f-83c7-df146ae03eb2.txt
================================================================================

📋 EXAMINATION:
   XR Chest and XR Shoulder Left

🩺 CLINICAL HISTORY:
   Left shoulder pain. MRSA positive. ? septic arthritis.

🔍 FINDINGS:
   Chest: Normal.
   Left shoulder: Normal alignment, no soft tissue swelling, no bony lesions.

================================================================================
START ANNOTATION
================================================================================

1️⃣ PRIMARY DIAGNOSIS
Enter primary diagnosis: Normal radiographic examination, septic arthritis cannot be excluded clinically

2️⃣ DIFFERENTIAL DIAGNOSES
Select expected differential diagnoses:

1. Septic arthritis
2. Juvenile Idiopathic Arthritis (JIA)
3. Soft tissue infection
...

Your choice: 1
✓ Added: Septic arthritis

Your choice: 5
✓ Added: Soft tissue infection

Your choice: -1

3️⃣ KEY FINDINGS
Finding 1: Normal chest X-ray
Finding 2: Normal shoulder alignment
Finding 3: No soft tissue swelling
Finding 4: -1

4️⃣ APPROPRIATE RECOMMENDATIONS
1. MRI if clinical suspicion persists
2. Blood cultures
3. Rheumatology referral
...

Your choice: 2
✓ Added: Blood cultures

Your choice: 7
✓ Added: Infectious disease consult

Your choice: -1

5️⃣ NOTES
Any special notes? MRSA positive patient - should focus on infectious workup

💾 Save this annotation? (y/n): y
✓ Annotation saved!
```

## ⏱️ Time Estimates

- **Per case (full mode)**: 3-5 minutes
- **Per case (quick mode)**: 1-2 minutes
- **15 cases total**: ~30-45 minutes
- **20 cases total**: ~40-60 minutes

## 🎓 Why Annotate More Cases?

### Current: 4 cases
- Shows concept ✓
- Minimal statistics
- Grade: B range

### With 15-20 cases:
- Robust evaluation ✓
- Credible statistics ✓
- Professional rigor ✓
- Grade: A range ✓

## 📁 Where Annotations Are Saved

All annotations save to:
```
data/ground_truth.json
```

The file updates automatically each time you save an annotation.

## 🔍 Check Your Progress

From the menu, choose **Option 4: Show statistics**

You'll see:
```
================================================================================
ANNOTATION STATISTICS
================================================================================

Total reports in folder: 100
Annotated reports: 4
Remaining: 96
Completion: 4.0%

Annotated files:
  ✓ 000d1e6f-b04c-402f-83c7-df146ae03eb2.txt
  ✓ 0146a6aa-5170-40f9-8067-252777ae8ed0.txt
  ✓ 0222523e-1ea1-4841-9ab0-f433fc9cc45f.txt
  ✓ 03d68077-7a9a-40bd-8265-c6a1208c0f0a.txt
```

## 🎯 Recommended Workflow

### Session 1 (30 mins): Annotate 10 cases
```bash
python src/annotation_helper.py
# Choose Option 2: Quick annotate
# Do 10 cases
```

### Session 2 (30 mins): Annotate 10 more cases
```bash
python src/annotation_helper.py
# Choose Option 2: Quick annotate
# Do 10 more cases
```

### Done! 20 cases = Strong evaluation

Then run:
```bash
python src/evaluate_system.py
```

You'll have robust statistics for your paper!

## 🐛 Troubleshooting

**"File not found error"**
- Make sure you're in the project root directory
- Check that `data/` and `all/` folders exist

**"No reports to annotate"**
- Check that you have .txt files in the `all/` folder

**"Encoding error on Windows"**
- The tool handles UTF-8 automatically, should work fine

**Want to edit an existing annotation?**
- Edit `data/ground_truth.json` directly
- Or re-annotate (it will replace the old one)

## 🌟 Pro Tips

1. **Use the AI suggestions** in quick mode - they're usually good starting points
2. **Don't overthink it** - your clinical judgment is what matters
3. **Be consistent** - use similar terminology across cases
4. **Take breaks** - annotating 20 cases in one go is tiring!

## ✅ Ready to Annotate!

```bash
python src/annotation_helper.py
```

Aim for **15-20 cases** for full marks! 🎓
