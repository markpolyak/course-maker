# /course-maker quiz publish N [format] — Step 3

Export the canonical bank `quizzes/NN/quiz_questions.md` to a student-facing
artifact in a chosen format. This is **export**, distinct from `lab publish`
(which syncs to an LMS). `markdown` is the default and is always produced first
— it is the file the answer-leak check runs against. `pdf` / `latex` / `docx`
convert that checked file via `references/doc_export.md`.

```
/course-maker quiz publish N            → markdown (default)
/course-maker quiz publish N markdown   → markdown
/course-maker quiz publish N pdf|latex|docx → markdown, leak check, then convert
/course-maker quiz publish N moodle     → not implemented yet; stop
```

LMS-native formats (Moodle XML/GIFT, Canvas QTI) are not implemented. If one is
requested, say so and stop — do not improvise an exporter.

## Context to read first

1. `quizzes/NN/quiz_questions.md` — the canonical bank (the source).
2. `quizzes/NN/quiz_plan.md` — variant count M and header metadata.
3. `quizzes/NN/history.md`.

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
- Pool mode: `quizzes/NN/quiz_student.md`.
- Per-variant mode: `quizzes/NN/quiz_variant_<letter>.md` per variant.

The bank (`quiz_questions.md`) itself remains the answer key — do not produce a
separate key file unless asked.

## CRITICAL — answer-leak check (do not skip)

A single missed answer exposes the key to students. After writing each export
file, verify no answer survived:

```bash
grep -nE "✓|Answer/criteria" quizzes/NN/quiz_student.md   # must print nothing
```

If the count is not zero, the export is invalid: show the offending lines, fix
the stripping, rewrite, and re-check until the grep is empty. Only then report
success and set `published → ✅` in the `## Quizzes` section of `COURSE_STATE.md`;
append an entry to `quizzes/NN/history.md`.

**The check gates the conversion, not just the Markdown.** A `pdf`/`docx` export
of a file that still contains answers is exactly the leak this section exists to
prevent. Never convert before the grep is clean.

## Converting to pdf / latex / docx

Read `references/doc_export.md` and convert the **checked** student file(s) —
`quiz_student.md`, or every `quiz_variant_<letter>.md` in per-variant mode —
with the backend the course configured. Never convert `quiz_questions.md`: it is
the answer key.
