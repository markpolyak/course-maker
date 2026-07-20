# Lab Step 3 — Validation

---

## IMPORTANT: Pre-validation checklist

Before anything else, run:
```bash
git status <LAB_DIR>starter/
```

If there are **uncommitted changes** in `<LAB_DIR>starter/`, **stop immediately** and show:
```
Cannot start validation: labs/<dir>/starter/ has uncommitted changes.
Commit them first — otherwise the clean notebook will be lost after validation.

  git add <LAB_DIR>starter/
  git commit -m "lab N: ..."

After committing, run validation again.
```

Do not proceed until the working tree for `<LAB_DIR>starter/` is clean.

---

## IMPORTANT: Clear context before validation

This step simulates a student solving the lab. The agent must not have access to `lab_spec.md`
or the test files before completing all tasks. The current session likely has all of that
in context from the preceding steps.

When the user runs `/course-maker lab validate N <student_id>`, show this message first
and **stop — do not proceed until the user confirms**:
```
Context must be cleared before validation — otherwise the agent will know the
contents of lab_spec.md and tests.py and cannot objectively simulate a student.

Start a fresh session/context, then run the command again:
  /course-maker lab validate N <student_id>
(Claude Code: run /clear in this chat. Codex CLI / Cursor: open a new
chat/session at the course repo root and run the command there.)
```

Only proceed after the user has confirmed they started a fresh session/context.

---

## Files Available During Validation

**ALLOWED to read:**
- `labs/labN/starter/exercises.ipynb`
- `labs/labN/starter/datasets_info.md` (if exists)
- Public library documentation (web search allowed)

**NOT ALLOWED to read until all tasks are complete:**
- `labs/labN/starter/tests.py`
- `labs/labN/starter/conftest.py`
- `labs/shared/tests_template.py`

**NEVER allowed to read:**
- `labs/labN/lab_spec.md`

---

## Validation Prompt

You are a student in this course. You have been given a lab assignment — `exercises.ipynb`.
Complete all tasks. When `lab_variants: true`, solve the variant for
`Student_ID = <provided number>`; when `lab_variants: false`, there are no variants and the
provided number (if any) is ignored.

**Rules (mandatory, non-negotiable):**

**Information sources:**
- Use only `exercises.ipynb`, `datasets_info.md` (if exists), and public library documentation
- Files `tests.py`, `conftest.py`, `tests_template.py` — do not read or open until all tasks
  are complete. They are used only in the final step for running tests
- `lab_spec.md` — never read under any circumstances
- If a test fails on a correct solution after running tests — do NOT fix the test.
  Log in the summary: which test failed, why the solution is correct, what is wrong with the test.
  Fixing tests is a Stage 2 task, not a validation task

**Data:**
- Dataset must be loaded from the source specified in Block 0 of the notebook
- If the dataset fails to download — report this explicitly, describe the error, do not continue
  with invented data
- Never generate synthetic data instead of the real dataset under any pretext

**Task completion:**
- Complete ALL tasks from the notebook — not just those checked by tests
- Do not skip tasks even if they seem optional or decorative
- Text comments (string variables) must be filled substantively, not with stubs like
  "TODO", "comment", or any equivalent placeholder in the course language
- Do not reverse-engineer results to match expected values manually — computations must
  follow from the data

**What to log:**
- If a task formulation is ambiguous — note this explicitly
- If a task is technically infeasible (broken link, incompatible requirements) — describe the issue
- If a result looks suspicious (anomalous values, empty graphs, zero metrics) — do not hide it

---

## After Completing All Tasks

1. Run the self-check cell at the end of the notebook and show its output.

2. Convert the notebook to `.py` and run tests:
```bash
jupyter nbconvert --to python exercises.ipynb
pytest tests.py -v
```

3. Show the full pytest output.

4. Give a short summary:
   - Which tasks completed without issues
   - Which tasks caused difficulty or required non-standard solutions
   - Any suspected bugs in formulations or tests
   - Are all `required_vars` defined

---

## After Validation

**Step 1 — offer to save the solution:**

Ask the user:
```
Validation complete. Save the solution to a separate branch?
Enter a branch name (e.g. validate-lab1-student7) or press Enter to skip.
```

If the user provides a branch name:
```bash
git checkout -b <branch-name>
git add <LAB_DIR>starter/exercises.ipynb
git commit -m "lab N: validation solution Student_ID=<id>"
git checkout -
```
Confirm to the user: "Solution saved to branch `<branch-name>`. Back on previous branch."

**Step 2 — restore the notebook to its clean state:**
```bash
git restore <LAB_DIR>starter/exercises.ipynb
```

This removes the student's solutions from the working copy.
The validation results are preserved in `history.md` — the notebook itself must not be committed with student solutions on the main branch.

Append to `labs/labN/history.md`:
```markdown
## [YYYY-MM-DD] Step 3: Validation — Student_ID=<N>

**All tasks completed:** yes / no
**Issues found:** <list or "none">
**Test results:** X passed, Y failed
**Ambiguous formulations:** <list or "none">
**Action required:** <"return to Stage 1/2 with specific issue" or "ready to publish">
```

Update `COURSE_STATE.md` Labs table:
- `validated` → ✅ if all tests pass and no issues
- `validated` → ⚠️ if issues found (needs Stage 1 or 2 revision)
