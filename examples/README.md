# Examples

This directory is reserved for example courses produced by `course-maker`.

## Status

**Empty at the moment.** Wave 2 of the improvement plan created this directory
but did not populate it: a genuine example must be produced by running the
skill on a real course, not hand-assembled by Claude — otherwise the artifacts
do not reflect what the pipeline actually generates (tone, format, history.md
evolution, cross-step coherence).

## Planned content

### `minimal-course/` (planned)

A single-lecture demo course. Goal: anyone reading the repo can `cd` into this
directory and see exactly what every pipeline artifact looks like
(`plan.md`, `visuals.md`, `figures/figures.py`, `slides.tex`,
`speaker_notes.md`, `history.md`, `COURSE_STATE.md`).

How to produce it: run `/course-maker course init` in a fresh `minimal-course/`
directory, fill in a tiny `course_plan.md` (one 45-min lecture on any
intuitive topic), then run the full pipeline. Commit the resulting tree here.

### Full-scale example (planned)

A real multi-lecture course (e.g. an 8-lecture course with labs). The author
has such materials available; adding them here is gated on PII cleanup
(student identifiers, internal repository URLs, contact info).

## Contributing your own example

If you've used `course-maker` for a real course and are willing to share, open
a PR with the course directory under `examples/<course-slug>/`. Strip:

- Student identifiers and grades
- Internal repository URLs (replace with `https://github.com/your-org/...`)
- Email addresses and office hours
- Anything else PII-sensitive

The most valuable examples are ones that show real iteration history in
`lectures/NN/history.md` — that's the part of the skill that's hardest to
demonstrate from a fresh run.
