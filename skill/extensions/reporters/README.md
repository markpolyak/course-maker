# Grade reporters (opt-in)

A **grade reporter** turns the raw pass/fail outcomes of a lab's pytest run into
whatever end-of-session output a course needs: a points summary, an
autograder-readable grade line, a JSON blob, or nothing at all.

The universal harness (`templates/conftest_base.py`) deliberately has no
opinion on grading. At the end of the test session it looks for a
`grade_report.py` next to the `conftest.py` and, if found, calls:

```python
report(outcomes: dict[str, str]) -> None
```

`outcomes` maps each test function name to `"passed"`, `"failed"`, or
`"skipped"`. If no `grade_report.py` exists, nothing extra is printed — plain
pytest output. So a course that grades manually needs no reporter at all.

## When a reporter is installed

A reporter is installed only when the course opts in. In the course `AGENTS.md`:

```
### Lab grading
grade_reporter: scoring_ci   # none | scoring_ci | <your own>
```

During `/course-maker lab course-init`, the named reporter is copied from
`extensions/reporters/<name>.py` into the lab scaffold as
`starter/grade_report.py`. `grade_reporter: none` (the default) copies nothing.

## Available reporters

### `scoring_ci.py`

Prints a boxed scoring block: per-block pass/fail markers and a grade line
(`PRELIMINARY GRADE: earned / total`, plus a bonus tally when present). The
grade line is intended to be greppable by an external autograder/CI.

Customize:

- **Labels** — `SCORING_HEADER`, `TASKID_LABEL`, `GRADE_OUTPUT_LABEL`. Set them
  to your language and to whatever exact phrase your CI greps. Change the
  labels, not the `print()` layout, unless your CI agrees.
- **Per-lab data** — `TEST_POINTS`, `TEST_BLOCKS`, `DATASETS`. Filled by
  `/course-maker lab tests N` from `lab_spec.md`.

Conditional invariant: when the lab uses per-student variants (`DATASETS`
non-empty), the variant id is computed as
`dataset_id = (student_id - 1) % len(DATASETS)` and printed as the TASKID line.
Keep that formula verbatim when variants are in use — it must match Block 0 of
the notebook (see `../variants/README.md`). When `DATASETS` is empty, the TASKID
line is omitted and the formula is irrelevant.

## Writing your own reporter

Create `extensions/reporters/<name>.py` exposing `report(outcomes)`,
reference it as `grade_reporter: <name>` in the course `AGENTS.md`. Keep the
file self-contained (no imports from other extensions) — it is copied verbatim
into each lab and edited there per lab.
