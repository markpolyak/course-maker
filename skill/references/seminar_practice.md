# /course-maker seminar practice N

Generate the practical part of seminar N: a runnable Jupyter notebook,
`seminars/NN/practice.ipynb`, used for live code demonstration during the
seminar. The deck (plan/visuals/figures/slides/notes) is produced by the seminar
mirror of the lecture pipeline; this step adds the hands-on notebook.

What the practical part is varies by course. Here it is an **instructor-driven
demo notebook** — code shown and run live to reinforce the seminar's theory. It
is **not autograded** and has no `conftest.py`/`tests.py` (that is a lab).

## Context to read first

1. `seminars/NN/history.md` — past iterations for this seminar (read first).
2. `seminars/NN/plan.md` — the seminar's content; identify which points are meant
   to be shown live / practised (vs pure lecture).
3. `course_plan.md` — seminar N row (title, topic).
4. `AGENTS.md` → `## Course context` and `course_conventions.md` — audience,
   tone, language, terminology. The notebook **content is in the course
   language**; this reference is English.

## Output: `seminars/NN/practice.ipynb`

A notebook that runs top to bottom without errors (`Restart & Run All` clean):

- **Header markdown cell:** seminar title and what will be demonstrated.
- **Sections** matching the seminar's practical points: a markdown cell that
  explains what and why, then code cell(s) that demonstrate it, then a short
  takeaway. Keep cells small and readable — this is shown on screen live.
- **Optional in-seminar exercises:** a "try it yourself" cell with a prompt and a
  stub, immediately followed by a worked answer cell (this is a demo, not a
  graded task — the answer is shown).
- Minimal dependencies; reuse the course's usual stack. Fix the random seed where
  output must be reproducible.

Generate large notebooks **section by section** (chunked, same reason as slides),
appending cells as you go; do not emit the whole notebook in one shot.

## Verification (do not skip)

The notebook is runnable code — treat it as unverified until it has run:

```bash
cd seminars/NN && jupyter nbconvert --to notebook --execute --inplace practice.ipynb
```

If execution fails: show the error, fix the offending cell, re-run until clean.
Only after a clean top-to-bottom run, list the sections for the user to confirm.

## Protocol and state

After a clean run and user approval: append an entry to `seminars/NN/history.md`
and set `practice → ✅` in the `## Seminars` row of `COURSE_STATE.md`. Mark
`practice → 🔄` if it was generated but not yet cleanly executed. Do not
auto-advance to another step.
