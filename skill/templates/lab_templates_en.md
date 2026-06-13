# Lab Templates — English

This file is copied to `lab_templates.md` in the course root by `/course-maker lab course-init`
when the course language is English. Edit after generation if your conventions differ.

---

## Notebook Header Cell (markdown)

```markdown
# Lab Assignment {N}
## {Full Title}

**Course:** {Course Name}
**Goal:** {Lab goal — one concise sentence}
**Topic:** {Topic}
**Deadline:** see the grade tracking table

---

### Instructions

1. **Variant:** enter your `Student_ID` in Task 0.1 — it determines your dataset and parameters
2. **Variable naming:** strictly follow the specified names — they are used for auto-grading
3. **Functions:** implement each function with the given signature; do not rename functions or parameters
4. **Visualizations:** all graphs must have a title and axis labels
5. **Submission:** before submitting run `Kernel → Restart & Run All` and verify there are no errors
```

---

## Block 0 Divider Cell (markdown)

```markdown
---
## Block 0: Variant Setup
```

---

## Task 0.1 (markdown)

```markdown
### Task 0.1: Enter your Student_ID

Find your row number (field "No.") in the course grade tracking table and enter it below.
```

## Task 0.1 (code)

```python
Student_ID = None  # Enter your row number, e.g.: Student_ID = 7
```

---

## Task 0.2 (markdown)

```markdown
### Task 0.2: Variant Assignment

Run the cell below — it will determine your dataset and task parameters.
```

## Task 0.2 (code)

```python
# (dataset_type, description, source)
datasets = [
    ('sp500', 'S&P 500 Index, ticker ^GSPC, 2010–2023, yfinance (https://pypi.org/project/yfinance/)', '^GSPC'),
    ...
]

if Student_ID is None:
    print("ERROR! Student_ID is not set. Go back to Task 0.1.")
else:
    dataset_id = (Student_ID - 1) % len(datasets)   # NEVER change this formula
    DATASET_TYPE, DATASET_DESC, SOURCE = datasets[dataset_id]
    print(f"Your variant: dataset #{dataset_id + 1}")
    print(f"Dataset:      {DATASET_DESC}")
```

---

## Task 0.3 (markdown)

```markdown
### Task 0.3: Install Dependencies
```

## Task 0.3 (code, two cells)

```python
# Install required libraries (run once)
# !pip install {library1}
```

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# ... other imports for this lab

print("Libraries loaded.")
```

---

## Final Checklist Cell (markdown, second-to-last)

```markdown
---
## Final Checks

Before submitting make sure:
- ✅ All cells executed (`Kernel → Restart & Run All`)
- ✅ All required variables defined and not `None`
- ✅ All graphs have a title and axis labels
- ✅ Text comments ({list text variables for this lab}) filled in
```

---

## Self-Check Cell (code, last)

```python
required_vars = [
    # Block 0
    'Student_ID', 'DATASET_TYPE', 'SOURCE',
    # Block 1
    'variable_name',
]

print("=" * 60)
print("CHECKING REQUIRED VARIABLES:")
print("=" * 60)
all_ok = True
for var in required_vars:
    value = globals().get(var)
    if value is not None:
        print(f"  ✓ {var}")
    else:
        print(f"  ✗ {var} — NOT DEFINED!")
        all_ok = False

bonus_vars = [
    # Block {N} (bonus)
    'bonus_variable_name',
]

print()
print("=" * 60)
print("CHECKING BONUS VARIABLES:")
print("=" * 60)
for var in bonus_vars:
    value = globals().get(var)
    if value is not None:
        print(f"  ✓ {var}")
    else:
        print(f"  ○ {var} — not completed (bonus)")

print()
if all_ok:
    print("✅ All required variables defined. Work is ready to submit!")
else:
    print("⚠️  Some required variables are not defined. Check your code.")
```

---

## Task Formatting

### Function stub

```python
def function_name(param: type) -> ReturnType:
    """Brief description.

    Parameters:
        param — type and meaning of the parameter

    Returns:
        type and meaning of the return value
    """
    # TODO: your code
    raise NotImplementedError
```

### Variable stub

```python
# Part A: brief description
# TODO: compute variable_name
variable_name: np.ndarray = None  # shape (n,) or explanation
```

### Task title format

```
### Task N.M — Title
```

### Hint format

```markdown
> 💡 **Hint:** ...
```

### Bonus task marker

```markdown
**Bonus:**
```

---

## conftest.py Strings

The lab tests step (`/course-maker lab tests N`) reads these values from this
file and uses them as the customizable strings at the top of `conftest.py`
(`TASKID_LABEL`, `GRADE_OUTPUT_LABEL`, `SCORING_HEADER`). The print() format
in `conftest_base.py` is fixed — only the labels change per course/language.

If your external CI expects a specific exact phrase in the grade-output line
(e.g. for autograding), put it here verbatim — the skill substitutes it into
`conftest.py` during lab init.

### Scoring header (printed inside the LAB SCORING SYSTEM block)

```
LAB SCORING SYSTEM
```

### TASKID label (printed as `TASKID is {n}` — read by external CI)

```
TASKID
```

### Grade output label (printed as `PRELIMINARY GRADE: {earned} / {total}` — read by external CI)

```
PRELIMINARY GRADE
```

---

## datasets_info.md

### Common issues section title

```
Common Issues and Solutions
```

---

## Error Messages

Error messages in tests: English.
