# Lab Reverse Spec — Generate lab_spec.md from Existing Notebook

Use this when you have a finished `exercises.ipynb` but no `lab_spec.md`.
Generates the spec from the existing notebook, then the pipeline continues with Stage 2
(`/lab tests N`) in the normal way.

Read `references/lab_context.md` and `references/lab_step1b_spec.md` before starting.

---

## Context to Read Before Generating

1. Read `labs/labN/starter/exercises.ipynb` — the existing notebook to analyze.
2. Read `labs/labN/history.md` if it exists — prior decisions.

The `lab_spec.md` template and rules for writing checks are defined in
`references/lab_step1b_spec.md`.

---

## Prompt to Execute

### Step 1: Analyze the Notebook

Read `exercises.ipynb` and extract:

- Lab title, course, goal (from the first cell)
- Presence of `theory.md` / peer review (from instructions or block structure)
- Dataset list from Block 0: `datasets` array, additional variant parameters
- All variables defined in Block 0 (`Student_ID`, `DATASET_TYPE`, `SOURCE`, etc.)
- All tasks: variables, functions, classes — their names, signatures, types
- Text variables (type `str`) the student fills manually
- Artifacts: files the student saves to disk
- `required_vars` and `bonus_vars` from the self-check cell
- Scoring: points per task, bonus tasks

### Step 2: Fill the Spec

Fill all sections per the template in `references/lab_step1b_spec.md`.

Additionally, for each task, **formulate checks** — they may be absent from the notebook
and must be derived from the task logic:
- For variables: type, shape, absence of NaN, value range, dependencies on other variables
- For functions: return type, correct output on a known input
- For classes: attribute presence, method behavior, test inputs
- For artifacts: file existence, structure, numeric values with tolerances

**Tolerances — strictly per rules in `references/lab_step1b_spec.md`.**

**For every check ask:** "Does this pass for all dataset variants when correctly implemented?"
If no — add `DATASET_TYPE` condition or set `manual_check: true`.

**Do not check** internal matplotlib objects — only observable behavior.

**Reproducibility parameters** (`random_state`, etc.) — specify explicitly for every
function/method where they apply.

### Step 3: Note Deviations from Current Standards

After the spec, add a section `## Deviations from Current Standards`
(translate the heading into the course language).

For each deviation note:
- What exactly does not conform (notebook structure, task formatting, terminology,
  missing goal, non-standard Block 0, etc.)
- Severity: `critical` / `recommended` — use course-language equivalents
  (`critical` = blocks tests or unification; `recommended` = quality improvement)
- What needs to be fixed and where (notebook, `conftest.py`, `README.md`)

This section helps decide whether to fix the notebook before Stage 2 or generate tests
from the spec as-is.

---

## After Saving

Append to `labs/labN/history.md`:
```markdown
## [YYYY-MM-DD] Reverse spec: lab_spec.md generated from existing notebook

**Source:** labs/labN/starter/exercises.ipynb
**Deviations found:** <count> critical, <count> recommended
**Next step:** /lab tests N
```

Update `COURSE_STATE.md` Labs table: set `spec` column for lab N to ✅.
