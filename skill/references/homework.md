# Homework pipeline

A **homework** is a manually graded take-home assignment. It is deliberately
lighter than a lab: a task **brief** (authored in markdown, handed out as
markdown or exported to PDF) plus an instructor-only grading **rubric**. The
deliverable is open — a notebook, a report, an archive of files — the brief
states what to submit. There is **no** `starter/`, autograder, `conftest`,
`tests.py`, CI workflow, or `validate` step; that machinery is what a lab is
for. Grading is done by hand.

Manual grading is this pipeline's default, not a universal law — some courses do
autograde homework. If a course needs autograding, that is a lab, not homework.

This reference is English; **write the brief and rubric in the course language.**

---

## Directory and files

`HW_DIR` is resolved from `COURSE_STATE.md` → `## Homework` table: find the row
where `#` = N, read the `Dir` column — that value is a **path from the course
root**. Default for a new homework is `homework/NN/` (N zero-padded to two
digits). Unlike labs (where `Dir` is a slug under `labs/`), homework `Dir` is a
full relative path, so a homework can live anywhere — e.g. under a seminar in a
seminar-centric course: `seminars/<seminar>/homework/`.

Files in `HW_DIR`:

- `task.md` — the assignment brief. Instructor source; its content is
  student-facing.
- `rubric.md` — grading criteria. Instructor-only unless the author opts to
  include it in the handout (asked at plan time).
- `homework_student.md` — the assembled student handout (`publish` output; the
  `.pdf` / `.tex` / `.docx` exports are derived from it on demand).
- `history.md` — decision log, same role as `lectures/NN/history.md`.

Only `homework_student.md` (and its exports) is given to students. `task.md`,
`rubric.md`, and `history.md` stay with the instructor.

`N` is the homework's own index. `Dir` decouples the physical location, so
homework `N` need not correspond to lecture/seminar `N` — the two are linked
only if the author points `Dir` at that unit's folder.

---

## `/course-maker homework plan N [dir]` (Step 1)

Read `references/lab_context.md` for the shared authoring rules (audience level
from `CLAUDE.md`, terminology from `course_conventions.md`, factual-claims and
library-currency discipline). Homework does not use `lab_templates.md` (no
notebook/test scaffolding).

### Context to read first

1. `course_plan.md` — the section for homework N (topic, objectives) if present.
2. `HW_DIR/history.md` if it exists — rejected ideas, prior decisions.
3. `CLAUDE.md` → `## Course context` — audience and language.
4. `course_conventions.md` — terminology and language rules.

Homework needs only `course init` to have run (for `CLAUDE.md` and
`course_conventions.md`). It does **not** require `lab course-init`.

### Resolve `HW_DIR`

- If a `## Homework` row for N exists, use its `Dir`.
- Otherwise this is a new homework: `HW_DIR` = the `[dir]` argument if given,
  else `homework/NN/`. Create the directory and a `HW_DIR/history.md`
  (`# Homework N — History` / `(no entries yet)`).

### Interactive planning

Ask for any parameter not supplied with the command:

- Total points (and any per-task split).
- Deliverable format(s): notebook / report / archive / other, and how to submit.
- Deadline, if the course tracks one.
- Any constraints (allowed tools, page/length limits, individual vs group).
- **Whether the grading rubric is included in the student handout.** Record the
  answer — `publish` reads it and must not re-ask.

Then iterate on the task content. Do **not** write the files until the user
approves the draft (any clear confirmation, in any language).

### Write `task.md` (student-facing content)

In the course language:

- Title, topic, one-sentence goal (the final result, not a list of steps — see
  `course_conventions.md` for good/bad examples).
- Numbered tasks / subtasks with the points for each. Bonus tasks marked per the
  course's convention.
- **Deliverable** section: exactly what to submit and in what form; submission
  channel and deadline if provided.
- Constraints, if any.

Record the rubric-in-handout decision as a metadata comment on the first line so
`publish` can read it without asking:

```
<!-- rubric_in_handout: true -->
```

Mark any instructor-only aside (a hint you keep for yourself, a reference
answer) with `<!-- instructor: ... -->` so `publish` can strip it.

### Write `rubric.md` (instructor-only)

Per-task grading criteria: what earns full vs partial credit, point breakdown
matching `task.md`, and common-mistake notes. This file is always produced — you
grade by hand and need it regardless of whether students see it.

### Protocol

Write both files directly (never dump their contents in chat), then show a brief
human-readable summary and wait for approval. Only after approval:

- Append to `HW_DIR/history.md` (topics, points, deliverable, rubric-in-handout
  decision, key/rejected choices).
- In `COURSE_STATE.md` → `## Homework`, set `task` and `rubric` to ✅ for row N
  (adding the row with its `Dir` if new).

Do not auto-advance to `publish`.

---

## `/course-maker homework publish N [format]` (Step 2)

Assemble the student handout, then optionally export it. Default and always-run
target is `markdown` (the assembly itself); `pdf` / `latex` / `docx` go through
pandoc, mirroring `/course-maker syllabus`.

```
/course-maker homework publish N            → markdown (assemble handout)
/course-maker homework publish N markdown   → same
/course-maker homework publish N pdf|latex|docx → assemble, then pandoc export
```

### Context to read first

1. `HW_DIR/task.md` — the source, including the `rubric_in_handout` metadata.
2. `HW_DIR/rubric.md` — only needed when the metadata says to include it.
3. `HW_DIR/history.md` — fallback for the rubric-in-handout decision if the
   metadata comment is absent.

### Assemble `homework_student.md`

Copy `task.md` and:

- Strip the `<!-- rubric_in_handout: ... -->` metadata line.
- Strip every `<!-- instructor: ... -->` aside.
- If `rubric_in_handout` is **true**, append `rubric.md` under a course-language
  "Grading criteria" heading. If **false**, do not include the rubric.

Write the result to `HW_DIR/homework_student.md`.

### CRITICAL — rubric-leak check (do not skip)

When `rubric_in_handout` is **false**, the rubric must not reach students. After
writing the handout, verify no instructor-only content survived:

```bash
grep -nE "<!-- instructor|<!-- rubric_in_handout" HW_DIR/homework_student.md  # must print nothing
```

Also confirm the handout does not contain the rubric text. If anything leaked,
the export is invalid: show the offending lines, fix the assembly, rewrite, and
re-check until clean.

### Export (pdf / latex / docx)

```bash
pandoc HW_DIR/homework_student.md -o HW_DIR/homework_student.pdf     # needs a LaTeX engine
pandoc -s HW_DIR/homework_student.md -o HW_DIR/homework_student.tex  # standalone LaTeX
pandoc HW_DIR/homework_student.md -o HW_DIR/homework_student.docx
```

- If `homework_student.md` is missing, assemble it first.
- If `pandoc` is not installed: stop, leave the markdown in place, and tell the
  user how to install pandoc. Do not fail silently.
- For `pdf`, if pandoc reports no LaTeX engine, say so and suggest `latex` or
  `docx` (or installing a TeX distribution).
- After a successful export, list the produced file.

### After publish

Set `published → ✅` for row N in `## Homework`; append an entry to
`HW_DIR/history.md` noting the format(s) produced.

---

## `/course-maker homework status N`

Print: the row from `COURSE_STATE.md` → `## Homework` for homework N (including
`Dir`), the last 3 entries from `HW_DIR/history.md`, and any ⚠️ warnings with an
explanation.
