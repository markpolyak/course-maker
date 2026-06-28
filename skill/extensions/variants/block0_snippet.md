# Block 0 variant cells (used only when `lab_variants: true`)

These are the Block 0 cells that assign each student a dataset. Include them in
`exercises.ipynb` only when the course enables variants. When `lab_variants`
is `false`, Block 0 is plain setup (imports / dependency install) with none of
the cells below.

The **prose** (cell titles, instructions to the student) is localized — take its
wording from the course `lab_templates.md` / `course_conventions.md`. The
**code and the formula** below are canonical and language-neutral.

## Block 0 divider (markdown)

```markdown
---
## Block 0: Variant Setup
```

## Task 0.1 — Student_ID (markdown + code)

Markdown: instruct the student to enter their row number from the course roster.

```python
Student_ID = None  # Enter your row number, e.g.: Student_ID = 7
```

## Task 0.2 — variant assignment (markdown + code)

Markdown: tell the student to run the cell; it picks their dataset and parameters.

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

## Invariants

- `dataset_id = (Student_ID - 1) % len(datasets)` — verbatim. This is the
  canonical variant formula; see `README.md`. If a grade reporter displays the
  variant (e.g. `../reporters/scoring_ci.py`), its `DATASETS` list must match
  this `datasets` list exactly, or the displayed variant will not match the
  student's.
- Block 0 has **zero points** — it is a mandatory technical step, not graded
  work.
- The required-variables self-check must list `Student_ID`, `DATASET_TYPE`,
  `SOURCE` among the Block 0 variables (per `lab_templates.md`).
