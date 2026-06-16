# /course-maker test publish N [format] — Step 3

Export the canonical bank `tests/NN/test_questions.md` to a student-facing
artifact in a chosen format. This is **export**, distinct from `lab publish`
(which syncs to an LMS). Default and only currently implemented format:
`markdown`. The dispatcher is designed to grow (LaTeX, docx, Moodle JSON), but
do not implement those until asked — if an unimplemented format is requested,
say so and stop.

```
/course-maker test publish N            → markdown (default)
/course-maker test publish N markdown   → markdown
/course-maker test publish N latex|docx|moodle → not implemented yet; stop
```

## Context to read first

1. `tests/NN/test_questions.md` — the canonical bank (the source).
2. `tests/NN/test_plan.md` — variant count M and header metadata.
3. `tests/NN/history.md`.

## Export modes

- **Pool (default).** Export every question with all its variants, answers
  removed. The instructor hands out / selects from the pool.
- **Per-variant sheets.** If the plan uses M > 1 parametrized variants and the
  instructor wants ready exam sheets, assemble one sheet per variant letter
  (A, B, … in the course-language alphabet), each picking that letter's version
  of every question. Ask which mode if it is not obvious from the request.

## Markdown exporter

Produce the student-facing file(s) by copying the bank and **removing every
trace of the answer**:
- Drop the trailing ` ✓` from every option line, keeping all options.
- For calculation questions, remove the entire answer line (it shows the result);
  keep the problem statement and any given formula.
- For open questions, remove the `**Answer/criteria:** …` line.
- Drop the "trick question" (⚠️) markers — they hint at the answer.

Write to:
- Pool mode: `tests/NN/test_student.md`.
- Per-variant mode: `tests/NN/test_variant_<letter>.md` per variant.

The bank (`test_questions.md`) itself remains the answer key — do not produce a
separate key file unless asked.

## CRITICAL — answer-leak check (do not skip)

A single missed answer exposes the key to students. After writing each export
file, verify no answer survived:

```bash
grep -nE "✓|Answer/criteria" tests/NN/test_student.md   # must print nothing
```

If the count is not zero, the export is invalid: show the offending lines, fix
the stripping, rewrite, and re-check until the grep is empty. Only then report
success and set `published → ✅` in the `## Tests` section of `COURSE_STATE.md`;
append an entry to `tests/NN/history.md`.
