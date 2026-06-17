# /course-maker syllabus [pdf|latex|docx]

Produce a student-facing syllabus from `course_plan.md`. Two actions in one
command:

- `/course-maker syllabus` — generate or update the canonical `syllabus.md` in
  the course root.
- `/course-maker syllabus pdf|latex|docx` — export the existing `syllabus.md` to
  that format via pandoc (generate `syllabus.md` first if it is missing).

The syllabus is a derived view of `course_plan.md` — regenerate it whenever the
plan changes. It has no state row and no `history.md`.

## Context to read first

1. `course_plan.md` — the source of all content.
2. `CLAUDE.md` → `## Course context` — course name, program, institution,
   audience, and language; and a short description if the plan lacks one.
3. `course_conventions.md` — terminology and language rules.

This reference is English; **write the syllabus itself in the course language.**

## Generation: `syllabus.md`

A clean, student-facing document. Map from `course_plan.md`, omitting anything
internal to the skill:

- **Title block:** course name, program/institution (from `CLAUDE.md`),
  term/year if present.
- **Instructors:** names and contacts (from `## Instructors`).
- **Description / objectives:** from `CLAUDE.md` course context and the plan's
  topics. Keep it short.
- **Prerequisites:** from `## Prerequisites`.
- **Schedule:** render `## Sessions` as a human-readable table (Week, Type,
  Title). **Drop the Notes column's pipeline pointers** (`labs/lab1/`,
  `quizzes/01/`, `no pipeline`) — these are internal and meaningless to students.
- **Grading:** from `## Grading`.
- **Materials:** from `## Self-study Materials`.

Do not invent policies or sections that are not in the plan or course context.

### Unfilled sections (do not leak)

If a source section is `<!-- TODO -->` or empty, **omit it from `syllabus.md`** —
never emit a raw `TODO` marker into a student document. After writing the file,
report to the instructor in chat: "Not yet in course_plan.md, so omitted from the
syllabus: <list>." This is the instructor's cue to fill the plan and regenerate.

## Export: `syllabus.{pdf,tex,docx}`

All three formats go through pandoc — one tool, three targets:

```bash
pandoc syllabus.md -o syllabus.pdf     # needs a LaTeX engine installed
pandoc -s syllabus.md -o syllabus.tex  # standalone LaTeX source
pandoc syllabus.md -o syllabus.docx
```

- If `syllabus.md` does not exist, generate it first (the generation step above).
- If `pandoc` is not installed: stop, leave `syllabus.md` in place, and tell the
  user it is ready to convert and how to install pandoc. Do not fail silently.
- For `pdf`, if pandoc reports no LaTeX engine, say so and suggest `latex` or
  `docx` as alternatives (or installing a TeX distribution).
- After a successful export, list the produced file for the user.

## Protocol

Generation writes `syllabus.md` directly, then shows a brief summary and the
omitted-sections report. Export is a mechanical conversion — no approval needed.
Neither action touches `COURSE_STATE.md`.
