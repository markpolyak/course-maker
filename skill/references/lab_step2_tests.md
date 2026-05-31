# Lab Step 2 — Test Generation

---

## Context to Read FIRST (mandatory)

1. Read `labs/labN/lab_spec.md` — full specification.
2. Read `labs/labN/starter/exercises.ipynb` — notebook structure, variable names, Block 0.
3. Read `labs/shared/conftest_base.py` — existing infrastructure (DO NOT modify the top section).
4. Read `labs/shared/tests_template.py` — style reference (do not copy logic, only patterns).
5. Read `lab_templates.md` from the course root — scoring block marker and grade output string
   for conftest.py.
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

### Step 4: Update `conftest.py` in `labs/labN/starter/`

Copy `labs/shared/conftest_base.py` → `labs/labN/starter/conftest.py` if not already there.
Then update **only** the scoring block (marker from `lab_templates.md`) and below.
Everything above this block — DO NOT TOUCH.

**What to change in the scoring block:**
- `TEST_POINTS` — test function names and points from `lab_spec.md`
- `TEST_BLOCKS` — test-to-task mapping from `lab_spec.md`
- `DATASETS` — dataset list from Block 0 of `exercises.ipynb`

**What NOT to change without explicit reason:**
- `import_student_notebook`, `pytest_runtest_makereport`, `student_module` fixture
- `pytest_sessionfinish` — only change if `lab_spec.md` explicitly calls for it

**Critical prohibitions in `pytest_sessionfinish`:**
- Never delete or modify: `print(f"  TASKID is {dataset_id + 1}")` — read by external CI
- Never modify: `dataset_id = (Student_ID - 1) % len(DATASETS)` — used by external grading
- Never delete student result output blocks — student navigates by them
- Never modify the grade output string format (from `lab_templates.md`) — CI reads it.
  Only the formula inside (numerator) may change: add/remove bonus points

**Permitted changes in `pytest_sessionfinish`:**
- Remove bonus point output if `lab_spec.md` has no bonus tasks
- Add a note if some points are graded manually by the professor
- Update the lab title in the report header

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
- Test function names MUST exactly match keys in `TEST_POINTS` in `conftest.py`
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

**Critical prohibition:** never modify `dataset_id = (Student_ID - 1) % len(DATASETS)` anywhere.

### Step 6: Verify Compatibility

After writing, verify:
- All keys in `TEST_POINTS` (`conftest.py`) match test function names in `tests.py`
- All tests in `TEST_BLOCKS` (`conftest.py`) exist in `tests.py`
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

**Files changed:** conftest.py, tests.py, requirements.txt, README.md
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
