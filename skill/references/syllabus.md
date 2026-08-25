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
2. `AGENTS.md` → `## Course context` — course name, program, institution,
   audience, and language; and a short description if the plan lacks one.
3. `course_conventions.md` — terminology and language rules.

This reference is English; **write the syllabus itself in the course language.**

## Generation: `syllabus.md`

A clean, student-facing document. Map from `course_plan.md`, omitting anything
internal to the skill:

- **Title block:** course name, program/institution (from `AGENTS.md`),
  term/year if present.
- **Instructors:** names and contacts (from `## Instructors`).
- **Description / objectives:** from `AGENTS.md` course context and the plan's
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

Read `references/doc_export.md` and convert `syllabus.md` with the backend the
course configured (`Doc export:` in `AGENTS.md`, default pandoc).

If `syllabus.md` does not exist, generate it first (the generation step above),
then export.

## Protocol

Generation writes `syllabus.md` directly, then shows a brief summary and the
omitted-sections report. Export is a mechanical conversion — no approval needed.
Neither action touches `COURSE_STATE.md`.
