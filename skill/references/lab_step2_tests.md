# Lab Step 2 — Test Generation

---

## Context to Read FIRST (mandatory)

1. Read `labs/labN/lab_spec.md` — full specification.
2. Read `labs/labN/starter/exercises.ipynb` — notebook structure, variable names, Block 0.
3. Read `labs/shared/conftest_base.py` — universal harness (DO NOT modify).
4. Read `labs/shared/tests_template.py` — style reference (do not copy logic, only patterns).
5. If the course uses a grade reporter (`grade_reporter` not `none`): read
   `lab_templates.md` from the course root — scoring/grade labels for `grade_report.py`.
6. Read `course_conventions.md` from the course root — course language for error messages.

---

## Prompt to Execute

Prepare autotests for lab N.

### Step 1: Read files

Read `lab_spec.md`, `exercises.ipynb`, `labs/shared/conftest_base.py`, and
`labs/shared/tests_template.py` fully before writing any code.

### Step 2: Update `requirements.txt`

Check which packages are needed for `exercises.ipynb`. If `requirements.txt` is missing
any — add them. Do not remove existing dependencies without explicit reason.

**Library versions — CRITICAL:**
- Do NOT take version from the local machine — it may be outdated
- For every package being added or updated: find the current version on PyPI via web search
  and write the exact found version as `package==X.Y.Z`
- Do not round down, do not choose an arbitrary lower bound — only what the search shows
- Flag libraries not updated in more than one year (e.g. hmmlearn): notify the professor,
  propose alternatives or justify the choice

### Step 3: Update `README.md` in `labs/labN/starter/`

Take the existing `README.md` from the starter directory (or `labs/shared/` if first time)
and adapt for this lab. Change only:
- Lab and course name (from `lab_spec.md` metadata)
- Lab goal (from the goal field in the first `exercises.ipynb` cell — field name per `lab_templates.md`)
- Repository structure: add `datasets_info.md` if `lab_spec.md` lists it; add `theory.md`
  if `theory_md: true` in metadata
- Task structure table: fill from the scoring table in `lab_spec.md`

Do NOT touch: submission instructions, Colab setup, contact section.

### Step 4: Update the grade reporter (only if the course uses one)

`conftest.py` is the universal harness and needs **no per-lab edit**. Whether a
lab produces any scoring output depends on `grade_reporter` in `AGENTS.md` →
`## Lab context` → `### Lab grading`:

- **`grade_reporter: none`** → there is no `grade_report.py`; labs run plain
  pytest (pass/fail). Skip this step entirely.
- **`grade_reporter: <name>`** → `lab init` copied
  `labs/shared/grade_report.py` into `labs/labN/starter/`. Edit only its data
  block (the reporter's contract is in `skill/extensions/reporters/README.md`):

  - `TEST_POINTS` — test function names → points from `lab_spec.md`.
  - `TEST_BLOCKS` — TestClass name → primary test function from `lab_spec.md`.
  - `DATASETS` — **only when `lab_variants: true`** — dataset list verbatim from
    Block 0 of `exercises.ipynb`. Leave empty when the lab has no variants.

  Labels (`TASKID_LABEL`, `GRADE_OUTPUT_LABEL`, `SCORING_HEADER`) were
  substituted from `lab_templates.md` at `lab course-init`; if still defaults,
  substitute them now. Do not change the `print()` layout — only the labels and
  the data block are course/lab-specific.

  **When `lab_variants: true`:** the variant formula in the reporter is verbatim
  — see `skill/extensions/variants/README.md`. Never modify it, and keep the
  reporter's `DATASETS` identical to Block 0's `datasets`.

### Step 5: Write `tests.py` in `labs/labN/starter/`

Use `labs/shared/tests_template.py` as a style and structure reference.
Write tests per `lab_spec.md` — copy patterns, not logic.

**`tests.py` requirements:**
- One class per task (class name: `TestTask{N}_{name}`)
- Fixture `student_module` from `conftest.py` — use everywhere student code access is needed
- Tests in order per task: existence → type → value/behavior
- For classes: test class existence, test attributes, test each method separately
- For artifacts: test file existence, test loading, test structure, test values
- Bonus tests: in a class named `TestBonus{N}` (one class per bonus task),
  skip via `pytest.skip` if variable not defined or is `None`
- When a grade reporter is used, test function names MUST exactly match keys in
  `TEST_POINTS` in `grade_report.py`
- Error messages in course language (per `course_conventions.md`), specific (what was expected, what was received)
- Heavy operations (model training) — via `scope='module'` fixture, not repeated per test

**Matplotlib tests — CRITICAL:**
- NEVER check internal matplotlib objects: `ax.collections`, `ax.patches`, `QuadMesh`,
  `AxesImage`, etc. — these change between library versions
- Check ONLY observable behavior:
  - Return type: `isinstance(fig, matplotlib.figure.Figure)`
  - Title: `ax.get_title() != ''`
  - Axis labels: `ax.get_xlabel()`, `ax.get_ylabel()`
  - Legend: `ax.get_legend() is not None`
- `plt.colorbar()` / seaborn heatmap with colorbar add extra axes — this is standard behavior,
  not a student error
- Correct check for "main axes only" (excludes colorbars):
  ```python
  main_axes = [ax for ax in fig.axes if ax.get_subplotspec() is not None]
  assert len(main_axes) == 2
  ```
- If multiple standard methods solve correctly (`imshow`, `pcolormesh`, `heatmap`,
  `axvspan`, `fill_between`) — test must not prefer one over others

**Critical prohibition (when `lab_variants: true`):** keep the variant formula
verbatim everywhere it appears (Block 0 and the grade reporter) — see
`skill/extensions/variants/README.md`. When `lab_variants: false`, there is no
such formula.

### Step 6: Verify Compatibility

After writing, verify (when a grade reporter is used; skip if `grade_reporter: none`):
- All keys in `TEST_POINTS` (`grade_report.py`) match test function names in `tests.py`
- All tests in `TEST_BLOCKS` (`grade_report.py`) exist in `tests.py`
- Sum of `TEST_POINTS` matches the scoring table in `lab_spec.md`

### Step 7: Do NOT Touch

- `exercises.ipynb` — may read, **do not modify**
- `tests.yaml` — do not read, do not modify
- `datasets_info.md` — do not read, do not modify
- `tests_template.py` — do not modify, read only as reference

---

## After Saving

Append to `labs/labN/history.md`:
```markdown
## [YYYY-MM-DD] Step 2: Tests generated

**Files changed:** tests.py, requirements.txt, README.md (+ grade_report.py if a reporter is used)
**Test count:** <number> tests, <number> bonus tests
**Compatibility check:** TEST_POINTS ✅ / TEST_BLOCKS ✅ / scoring total ✅
**Notes:** <any non-obvious test decisions>
```

Update `COURSE_STATE.md` Labs table: set `tests` column for lab N to ✅.

Commit:
```bash
git add labs/labN/starter/
git commit -m "lab N: add tests and conftest"
```
