# Per-student dataset variants (opt-in)

Some labs assign each student a different dataset (and, optionally, different
parameters) so that solutions cannot be copied verbatim. This is the **variant**
system. It is **not** universal — many labs give every student the same task —
so it lives here as an opt-in extension rather than in the core pipeline.

## Enabling

In the course `CLAUDE.md`:

```
### Lab grading
lab_variants: true      # default: false
```

When `false` (default):

- Block 0 of the notebook is plain setup (imports, dependency install); there is
  no `Student_ID`, no `datasets` list, no variant assignment.
- `lab_spec.md` has no variant variables.
- `/course-maker lab validate N <id>` ignores the id (or it is not required).
- A grade reporter, if any, prints no TASKID line.

When `true`:

- Block 0 includes the variant-selection cells from `block0_snippet.md`.
- `lab_spec.md` records the `datasets` list and variant variables.
- Validation is run per `Student_ID`.
- A grade reporter that supports variants (e.g. `../reporters/scoring_ci.py`)
  prints the assigned variant.

## The variant formula (invariant when enabled)

Every place that maps a student to a dataset MUST use exactly this formula:

```python
dataset_id = (Student_ID - 1) % len(datasets)
```

It appears in two places that must agree:

1. Block 0 of `exercises.ipynb` (the student computes their own variant);
2. the grade reporter, if it displays the variant id, and the validation step.

Changing it in one place but not the other silently misassigns datasets and
breaks grading for everyone. When `lab_variants: true`, treat this line as
verbatim. When `lab_variants: false`, the formula is irrelevant and absent.

## Files

- `block0_snippet.md` — the Block 0 variant cells (Task 0.1 Student_ID, Task 0.2
  variant assignment). Localized prose comes from the course `lab_templates.md`
  / `course_conventions.md`; the code and the formula come from here.
