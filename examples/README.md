# Examples

This directory holds example courses produced by `course-maker` — a genuine
example must come from actually running the skill, not be hand-assembled by
Claude, otherwise the artifacts don't reflect what the pipeline generates
(tone, format, `history.md` evolution, cross-step coherence).

## `regularization-course/`

A real 2-lecture course ("Regularization in Machine Learning") produced end
to end by the skill. Shows every lecture-pipeline artifact for two lectures
(`plan.md`, `visuals.md`, `figures/figures.py` + generated PNGs, `slides.tex`
+ compiled `slides.pdf`, `speaker_notes.md`, `history.md`), plus a lab
(`labs/lab1/`) through the `plan → notebook → spec → tests` steps, and the
top-level course files (`AGENTS.md`/`CLAUDE.md`, `course_plan.md`,
`course_conventions.md`, `lab_templates.md`, `COURSE_STATE.md`,
`lms_adapter.md` for the `local-zip` profile).

**What it does not cover:** the lab is not yet `validated`/`published`
(`labs/lab1/history.md` stops before Step 3), and the course has no seminars,
quizzes, or homework, so those pipelines aren't demonstrated here.
`lectures/*/history.md` is the most useful part to read — it's real iteration
history (rejected drafts, fixes, reasoning), not a fresh one-shot run.

## Planned content

### `minimal-course/` (planned)

A single-lecture demo course, smaller than `regularization-course/`, meant to
be the fastest thing to skim end to end. Not yet produced.

How to produce it: run `/course-maker course init` in a fresh `minimal-course/`
directory, fill in a tiny `course_plan.md` (one 45-min lecture on any
intuitive topic), then run the full pipeline. Commit the resulting tree here.

## Contributing your own example

If you've used `course-maker` for a real course and are willing to share, open
a PR with the course directory under `examples/<course-slug>/`. Strip:

- Student identifiers and grades
- Internal repository URLs (replace with `https://github.com/your-org/...`)
- Email addresses and office hours
- Anything else PII-sensitive

The most valuable examples are ones that show real iteration history in
`lectures/NN/history.md` — that's the part of the skill that's hardest to
demonstrate from a fresh run. Also worth including: any pipeline
`regularization-course/` doesn't cover (seminars, quizzes, homework, a
`validated`/`published` lab, a non-`local-zip` LMS profile).
