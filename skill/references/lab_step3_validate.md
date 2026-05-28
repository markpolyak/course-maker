# Lab Step 3 — Validation

---

## IMPORTANT: Run in a New Isolated Claude Code Session

This step simulates a student solving the lab. Claude must not have access to `lab_spec.md`
or the test files before completing all tasks.

When the user runs `/lab validate N <student_id>`, show this message first:
```
Этап валидации рекомендуется запускать в новой изолированной сессии Claude Code.
Откройте новую сессию, перейдите в корень курсового репо,
и запустите команду снова.

Это обязательно, чтобы Claude не имел доступа к lab_spec.md,
tests.py и conftest.py до завершения всех заданий.
```

If the user confirms they want to run in the current session, proceed with strict enforcement
of the file access rules below.

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

You are a master's student. You have been given a lab assignment — `exercises.ipynb`.
Your task is to complete all tasks for variant `Student_ID = <provided number>`.

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
  "комментарий" or "TODO"
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
