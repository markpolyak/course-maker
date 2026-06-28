# Lab Step 1b-2 — Lab Spec Generation

Read `references/lab_context.md` before starting.

This step handles two cases automatically — no separate command needed:
- **Plan mode:** `history.md` contains an approved plan → plan is the primary source.
- **Notebook mode:** no approved plan in `history.md` (or file absent) → notebook is the
  sole source; add a deviations report.

---

## Context to Read Before Generating

1. Read `labs/labN/starter/exercises.ipynb`.
2. Read `labs/labN/history.md` — check whether an approved plan exists.
3. Read `course_conventions.md` from the course root — language and terminology.
4. Read `lab_templates.md` from the course root — notebook structure and task formatting.

---

## Step 1: Analyze the Notebook

Regardless of mode, extract from `exercises.ipynb`:

- Lab title, course, goal (from the first cell)
- Presence of `theory.md` / peer review
- When `lab_variants: true`: dataset list from Block 0 (`datasets` array, variant
  parameters) and the Block 0 variant variables (`Student_ID`, `DATASET_TYPE`,
  `SOURCE`, etc.). When `lab_variants: false`: skip — there is no `datasets` array.
- All tasks: variables, functions, classes — names, signatures, types
- Text variables (`str`) the student fills manually
- Artifacts: files the student saves to disk
- `required_vars` and `bonus_vars` from the self-check cell
- Scoring: points per task, bonus tasks

---

## Step 2: Fill the Spec

Generate `labs/labN/lab_spec.md` — the machine-readable contract between Stage 1 and Stage 2.
This file is used in Stage 2 (test generation). Students never see it.
It lives only in the course repo, NOT in the starter repo.

Fill all sections strictly per the template below.

**If plan exists (plan mode):** use the approved plan as the primary source of truth.
Take numbers and structure from the plan; the notebook confirms them.
Do NOT invent data not present in either.

**If no plan (notebook mode):** the notebook is the sole source. For each task,
**formulate checks from the task logic** — they are absent from the notebook and must be derived:
- Variables: type, shape, absence of NaN, value range, dependencies
- Functions: return type, correct output on a known input
- Classes: attribute presence, method behavior, test inputs as executable Python
- Artifacts: file existence, structure, numeric values with tolerances

For every check ask: "Does this pass for ALL dataset variants when correctly implemented?"
If no — add `DATASET_TYPE` condition or set `manual_check: true`.

**What to fill (both modes):**

- **Metadata:** title, topic, presence of theory.md / peer review
- **Infrastructure:** environment, CI, nbconvert, graded_markers
- **Datasets:** download method, known issues, expected shape, key columns, value range, normalization
- **Variant variables:** all variables defined in Block 0
- **Tasks:** type, interface (exactly as in notebook), concrete checks, tolerance, points, bonus,
  class attributes/methods/test inputs, notes for non-standard logic
- **Text answers:** all `str` variables the student fills manually
- **Artifacts:** format, save method, content checks with tolerances
- **Scoring table:** block — task — points — bonus
- **Notes for Stage 2:** dependencies, pitfalls, non-standard test logic

---

## Step 3: Deviations Report (notebook mode only)

Skip this step in plan mode.

After the spec body, append a section `## Deviations from Current Standards`
(translate the heading into the course language).

For each deviation note:
- What exactly does not conform (notebook structure, task formatting, terminology,
  missing goal, non-standard Block 0, etc.)
- Severity: `critical` / `recommended`
  (`critical` = blocks tests or unification; `recommended` = quality improvement)
- What needs to be fixed and where (notebook, `conftest.py`, `README.md`)

This section helps decide whether to fix the notebook before Stage 2 or generate tests as-is.

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

# Only when lab_variants: true. Omit this section entirely when the lab has no
# per-student variants.
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

# Only when lab_variants: true. Omit this section entirely when the lab has no
# per-student variants.
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

## Output Protocol

**Do NOT output the spec YAML in chat.** Write the file directly, then:

1. Show a human-readable summary in chat:
   - Lab title and ID
   - Mode used: plan mode or notebook mode
   - Number of tasks per block (e.g. "Block 1: 3 tasks, Block 2: 2 tasks + 1 bonus")
   - Total scoring: mandatory points + bonus points
   - Datasets used (names only)
   - (Notebook mode only) Deviations found: count of critical and recommended, with a brief list
   - Any non-obvious decisions made (tolerances, variant-dependent checks, skipped checks)
2. Ask: "Does the spec look correct? Any edits needed?"
3. Wait for user confirmation before updating `history.md` and `COURSE_STATE.md`.
   If the user requests edits — apply them to the file, then re-show the summary and ask again.
   Only after the user confirms (or explicitly says "done", "ok", "proceed") — run the state updates below.

---

## After Confirmation

Append to `labs/labN/history.md`:

**Plan mode:**
```markdown
## [YYYY-MM-DD] Step 1b-2: Lab spec generated

**File:** labs/labN/lab_spec.md
**Tasks count:** <number>
**Scoring:** <mandatory> mandatory + <bonus> bonus
**Notes:** <any non-obvious decisions in the spec>
```

**Notebook mode:**
```markdown
## [YYYY-MM-DD] Step 1b-2: Lab spec generated from existing notebook

**Source:** labs/labN/starter/exercises.ipynb
**Tasks count:** <number>
**Scoring:** <mandatory> mandatory + <bonus> bonus
**Deviations found:** <count> critical, <count> recommended
**Notes:** <any non-obvious decisions in the spec>
```

Update `COURSE_STATE.md` Labs table: set `spec` column for lab N to ✅.
