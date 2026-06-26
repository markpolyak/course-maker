# /course-maker lab triage N

Use after a validation that surfaced problems (`validated → ⚠️`) to diagnose
what went wrong and recommend which pipeline step to return to.

**Read-only and advisory.** Triage edits nothing and changes no state. The fix
happens in the recommended step's own command, which logs its own `history.md`
entry. There is no `triage` row in `COURSE_STATE.md`.

## When to run

After `/course-maker lab validate N <id>` left `validated → ⚠️`, or whenever a
validation run reported failing tests, ambiguous tasks, or a broken dataset and
it is unclear which step to revisit.

## Isolation note

Validation is already complete, so the validate-time isolation rules no longer
apply: triage MAY read `lab_spec.md`, `tests.py`, `conftest.py`, `history.md`,
and the notebook — it needs all of them to find the root cause. Do not confuse
this with `lab validate`, where those files are off-limits until tasks are done.

## Inputs to read

1. `<LAB_DIR>history.md` — the most recent `## [date] Step 3: Validation` entry.
   Use its fields: *All tasks completed* / *Issues found* / *Test results* /
   *Ambiguous formulations* / *Action required*.
2. `COURSE_STATE.md` Labs row N — confirm `validated` is ⚠️. If it is ✅, there is
   nothing to triage: say so and stop.
3. For each reported issue, the source that confirms its root cause:
   `tests.py` + `conftest.py` (test logic), `starter/exercises.ipynb`
   (scaffolding, Block 0, self-check), `lab_spec.md` (intended task),
   `starter/datasets_info.md` (data facts), `starter/requirements.txt` (versions).

If `history.md` has no Step 3 entry, tell the user to run
`/course-maker lab validate N <id>` first, then stop.

## Diagnosis taxonomy

Map each reported issue to its root-cause step. Confirm the cause against the
source file before recommending — do not classify from the report wording alone.

| Symptom in the validation report | Root cause | Return to | Command |
|---|---|---|---|
| Test fails on a solution the report argues is correct | Wrong expected value / tolerance / assertion in the test | Stage 2 | `lab tests N` |
| Import error, version conflict, package not found | `requirements.txt` (lives in Stage 2 output) | Stage 2 | `lab tests N` |
| `required_vars` missing, wrong variable name, broken self-check cell | Notebook scaffolding | Step 1b | `lab notebook N` |
| Task wording ambiguous / contradictory / under-specified | Notebook wording (what students read); spec must follow | Step 1b | `lab notebook N`, then `lab spec N` |
| Dataset fails to download, Block 0 URL wrong, dataset facts incorrect | Notebook Block 0 + `datasets_info.md` | Step 1b | `lab datasets N` and `lab notebook N` |
| Task infeasible for the scope, wrong difficulty, off-topic | Plan-level (forces downstream regen) | Step 1a | `lab plan N` |

When the report flags a test as wrong, never recommend "fix the test to pass" —
recommend revisiting Stage 2 to confirm whether the test or the expectation is
at fault. A genuinely correct test exposing a wrong solution is not a lab defect.

## Ordering rule

When issues map to multiple steps, recommend fixing the EARLIEST pipeline step
first. Pipeline order: plan (1a) → notebook (1b) → spec (1b) → datasets (1b) →
tests (2). A change upstream can force regenerating downstream artifacts, so
fixing tests before a pending notebook change wastes work.

## Output

Print a triage report in chat, then stop:

1. **Summary line:** validation date, `X passed / Y failed`, count of distinct
   issues.
2. **Findings table:** one row per issue — issue → category → return-to step →
   exact command → one-line why.
3. **Recommended order:** an ordered list of the commands to run, earliest
   pipeline step first.
4. **Re-validate:** after the recommended step(s), run
   `/course-maker lab validate N <id>` to confirm the fix.

Do not edit files and do not change `validated`. The user runs the recommended
command next.

## Nothing to triage

If the latest validation entry says *All tasks completed: yes*, `0 failed`, and
no issues, report that `validated` should be ✅ and suggest
`/course-maker lab status N`. Do not invent issues.
