# Lab Step 1b-2 — Lab Spec Generation

Read `references/lab_context.md` before starting.

---

## Context to Read Before Generating

1. Read `labs/labN/starter/exercises.ipynb` — must be generated and approved before this step.
2. Read `labs/labN/history.md` — find the approved plan.

---

## Prompt to Execute

Generate `labs/labN/lab_spec.md` — the machine-readable contract between Stage 1 and Stage 2.
This file is used in Stage 2 (test generation). Students never see it.
It lives only in the course repo, NOT in the starter repo.

Fill all sections strictly per the template below. Take data from the approved plan
and generated notebook — do NOT invent numbers or hallucinate dataset characteristics.

**What to fill:**

- **Metadata:** title, topic, presence of theory.md / peer review
- **Infrastructure:** environment, CI, nbconvert, graded_markers
- **Datasets:** for each dataset — download method, known issues, expected shape, key columns,
  value range, normalization
- **Variant variables:** all variables defined in Block 0
- **Tasks:** for each task from the plan —
  - type (variable / function / class)
  - interface (exactly as in notebook)
  - concrete checks (not abstract — with variable names, numbers, operators)
  - tolerance (`rtol` / `atol`) if applicable
  - points, bonus
  - for classes: attributes, methods, behavior of each method, test inputs as executable Python
  - notes if non-standard logic
- **Text answers:** all `str` variables the student fills manually
- **Artifacts:** if a task requires saving a file — format, save method, content checks with tolerances
- **Scoring table:** block — task — points — bonus
- **Notes for Stage 2:** dependencies between tasks, pitfalls, non-standard test logic

---

## Rules for Writing Checks

**Tolerances:**
- Values ~order of 1 (model parameters, metrics): `rtol=0.05`
- Values approaching zero (probabilities, fractions, small coefficients): `atol=0.05`
  NOT `rtol` — otherwise tolerance = `rtol * ~0` and any correct implementation fails
- Log-likelihood of continuous distributions: do not check sign — density at mode can exceed 1,
  so log-likelihood can be positive
- Always include `tolerance_notes` with justification

**Robustness:**
- Before any numeric check, ask: "Does this check pass for ALL dataset variants when
  correctly implemented?" If no — either condition on `DATASET_TYPE` or move to oral defense
- Do NOT check internal matplotlib objects (`ax.collections`, `ax.patches`, `QuadMesh`, etc.) —
  they change between library versions
- Check only observable behavior: return type, title, axis labels, legend presence
- If multiple standard methods solve correctly (`imshow`, `pcolormesh`, `heatmap`) — test must
  not prefer one over others

**Axis count:**
- If spec says "figure has exactly 2 subplots" — check main axes only (no colorbars):
  ```python
  main_axes = [ax for ax in fig.axes if ax.get_subplotspec() is not None]
  assert len(main_axes) == 2
  ```
- `plt.colorbar()` / seaborn heatmap with colorbar add extra axes — `len(fig.axes) == 2`
  wrongly forbids colorbars

**Reproducibility:**
- All parameters affecting reproducibility (`random_state`, `covariance_type`, `n_iter`, `n_init`)
  must be explicitly specified for EVERY function and method where they apply, not just the main one
- Especially critical for parameters whose behavior depends on data volume

---

## Lab Spec Template

```yaml
# lab_spec.md — contract between Stage 1 and Stage 2
# NOT published to students. Stored only in course repo (labs/labN/).

## Metadata

lab_id: labN
title: <title>
course: <course name>
theory_md: false        # true — if lab includes peer review
notebook: exercises.ipynb


## Infrastructure

environment: Google Colab (CPU / GPU T4)
ci: pytest + GitHub Actions (tests.yaml)
nbconvert: true         # exercises.ipynb → exercises.py via nbconvert
graded_markers: false   # true — if ### Begin/End graded code markers used


## Datasets

datasets:
  - id: <dataset_id>
    description: <name and source>
    download: <how to download, e.g. "yfinance API, ticker from SOURCE variable">
    known_issues: <or null>
    expected_shape: "<approximate, e.g. (~3300, 6)>"
    key_columns: [col1, col2, ...]
    value_range: "<range description>"
    normalization: <or null>


## Variant Variables

variant_vars:
  - name: Student_ID
    type: int
  - name: DATASET_TYPE
    type: str
    values: [type1, type2, ...]
  - name: SOURCE
    type: str
  # add other variant variables as needed


## Tasks

# --- Variables ---

- id: task_N_M
  block: N
  title: <task title>
  variable: <variable_name>
  type: <pd.DataFrame | np.ndarray | int | float | str | ...>
  points: <number>
  bonus: false
  checks:
    - "<description: len(variable) > 0>"
    - "<description: variable.isnull().sum() == 0>"
  tolerance: null
  notes: >
    <any non-standard logic, dataset-specific behavior>

# --- Functions ---

- id: task_N_M
  block: N
  title: <task title>
  function: <function_name>
  signature: "<function_name(param: type) -> ReturnType>"
  points: <number>
  bonus: false
  checks:
    - "returns matplotlib.figure.Figure"
    - "does not raise on valid inputs"
    - "graph has title and axis labels"
  tolerance: null
  notes: >
    <notes>

# --- Classes ---

- id: task_N_M
  block: N
  title: <task title>
  class: <ClassName>
  points: <number>
  bonus: false
  attributes:
    - name: <attr_name>
      type: <type>
      description: <description>
  methods:
    - name: <method_name>
      signature: "<method_name(self, param: type) -> ReturnType>"
      behavior: >
        <what the method does>
      test_inputs:
        <param>: "<Python expression to create test input>"
      checks:
        - "<check description>"
  notes: >
    <notes>

# --- Bonus Tasks ---

- id: task_N_M
  block: N
  title: <task title>
  function: <function_name>
  signature: "<signature>"
  points: <number>
  bonus: true
  checks:
    - "returns correct type"
    - "does not raise on valid inputs"
  notes: >
    Bonus task. Test skips via pytest.skip if variable not defined or None.


## Text Answers

text_vars:
  - name: <variable_name>
    type: str
    block: N
    points: <number>
    checks:
      - "defined and not None"
      - "not empty string"
      - "length > 50"


## Artifacts

artifacts:
  - filename: <file.ext>
    format: <pickle | csv | json | pytorch>
    saved_by: "<Python code that saves the file>"
    checks:
      - "file exists: os.path.exists('<file.ext>')"
      - "loads without error"
      - "<content checks>"

# If no artifacts: artifacts: []


## Scoring Table

| Block | Task | Points | Bonus |
|-------|------|--------|-------|
| 1 | <task title> | <points> | — |
| ... | ... | ... | ... |
| N | <bonus task> | <points> | ✓ |
| **Total** | | **<mandatory> + <bonus> bonus** | |


## Notes for Stage 2

notes:
  - "<dependency: task X must run before task Y>"
  - "<dataset-specific: for ECG variants, signal may contain artifacts at start>"
  - "<non-standard logic description>"
```

---

## After Saving

Append to `labs/labN/history.md`:
```markdown
## [YYYY-MM-DD] Step 1b-2: Lab spec generated

**File:** labs/labN/lab_spec.md
**Tasks count:** <number>
**Scoring:** <mandatory> mandatory + <bonus> bonus
**Notes:** <any non-obvious decisions in the spec>
```

Update `COURSE_STATE.md` Labs table: set `spec` column for lab N to ✅.
