# Plan: populate `examples/minimal-course/`

**Date:** 2026-07-09
**Goal:** produce the `examples/minimal-course/` demo course by a *real* pipeline
run (never hand-authored), so the repo shows exactly what every artifact looks like.

This plan is executed by the instructor (running the pipeline), with Claude
acting as the `/course-maker` command executor on individual steps.

## Principles

1. **Everything from a real run.** No artifact (`plan.md`, `slides.tex`,
   `history.md`, `COURSE_STATE.md`) is hand-written. The whole point of the
   example is to show what the pipeline actually produces.
2. **Self-contained.** LMS profile = `local-zip` (no GitHub Classroom, no
   external CI, no `gh api`). No external URLs or tokens.
3. **No PII.** Toy course, no real students — but no URLs / e-mails / student
   IDs should ever appear.
4. **Build outside the repo**, then copy the sanitized tree into `examples/`.
   Reason: running directly inside `examples/minimal-course/` makes Claude pick
   up the repo-root `CLAUDE.md` (dev conventions, "skill English-only") as
   instructions, which conflicts with the course `CLAUDE.md`; and `course init`
   may `git init` → nested repo. A separate folder avoids both.

## Decisions to lock before starting (recommendations)

| Question | Recommendation | Why |
|---|---|---|
| Example language | English | Public-repo example, read by everyone. (Downside: real courses are Russian, and authentic `history.md` evolution is Russian. Pick Russian if authenticity matters more.) |
| Topic | Linear regression | Intuitive, good figures (scatter + line, MSE), easy to test in the lab |
| Scope | 2 lectures + 1 lab | Shows cross-lecture coherence + full lab pipeline. Absolute minimum: 1 lecture + 1 lab |
| LMS profile | `local-zip` | Self-contained, no external services |
| Lab data | Synthetic, fixed seed | No web download, deterministic — `validate` is reproducible |

---

## Phase 0. Prepare working directory

Outside the repo, e.g.:

```
mkdir -p ~/cm-example/minimal-course && cd ~/cm-example/minimal-course
```

Run all `/course-maker` commands from this folder (open a fresh Claude Code
session there, or set it as the working directory).

## Phase 1. Course scaffold

```
/course-maker course init
```
Answers: language English (or Russian); LMS profile **local-zip**; audience
e.g. "undergraduate, intro-level"; LaTeX engine pdflatex.

```
/course-maker course plan
```
Dictate a short plan: 2 lectures + 1 lab, e.g.:
- Lecture 1 — "Linear Regression: intuition and least squares" (45 min)
- Lecture 2 — "Fitting by gradient descent" (45 min)
- Lab 1 — "Implement linear regression from scratch"

Check: `CLAUDE.md`, `course_plan.md`, `COURSE_STATE.md`, `slides_preamble.tex`,
`course_conventions_*.md`, `lms_adapter.md` exist.

## Phase 2. Lecture 1 (full pipeline)

One command at a time; review + explicit approval after each:

```
/course-maker plan 1
/course-maker visuals 1
/course-maker figures 1        # figures.py is run; PNGs verified
/course-maker slides 1
/course-maker slides 1 next    # repeat until the deck ends
/course-maker notes 1
```

Check: `lectures/01/` has `plan.md`, `visuals.md`, `figures/figures.py` + PNGs,
`slides.tex`, `speaker_notes.md`, non-empty `history.md`.

Optional: compile the PDF (pdflatex) to confirm the deck builds — but do NOT
commit the PDF (heavy binary).

## Phase 3. Lecture 2 (optional, recommended)

Same cycle for lecture 2. Value: `history.md` and cross-lecture references show
how the pipeline keeps coherence between lectures.

## Phase 4. Lab bootstrap

```
/course-maker lab course-init
```
Creates `labs/shared/` with real (not placeholder) `conftest_base.py`,
`tests.yaml`. `local-zip` → no git-subtree/starter repo. Keep grade reporter
**none** (simplest for the example — plain pytest, no external CI string).

## Phase 5. Lab 1 (full pipeline)

```
/course-maker lab init 1 lab1-linreg
```
(No URL — `local-zip`; `lab1-linreg` is the slug.)

```
/course-maker lab plan 1
```
Dictate: student implements `fit(X, y)` (least squares via normal equation) and
`predict(X)`; data is **synthetic, generated in Block 0 with a fixed seed** (no
web download). Tests check coefficients against the known answer within a
tolerance.

```
/course-maker lab notebook 1
/course-maker lab spec 1
/course-maker lab tests 1      # creates tests.py, requirements.txt, README; commits starter/
```

Skip `lab datasets 1` — data is synthetic, no separate `datasets_info.md`.

## Phase 6. Lab validation (fresh session required)

1. Ensure `labs/lab1-linreg/starter/` is committed (no uncommitted changes).
2. Open a clean session (`/clear`).
3. Run:
```
/course-maker lab validate 1 1
```
(second arg = student_id = 1). Claude works the lab "as a student", runs
`nbconvert` + `pytest`, shows full output, then `git restore` removes the
solution from `starter/exercises.ipynb`.

Check: `COURSE_STATE.md` marks the lab `validated → ✅`; the lab `history.md`
has a Step 3 entry.

## Phase 7. Sanitize and move into the repo

1. PII scan (should be empty for a toy course):
```
grep -rniE "markpolyak|@gmail|@itmo|github.com/|student[_-]?id.*[0-9]{4}" \
  ~/cm-example/minimal-course --include=*.md --include=*.py --include=*.tex --include=*.ipynb
```
Clean anything found (replace with `https://github.com/your-org/...`, generalize
the audience).

2. Decide on heavy/non-reproducible artifacts. Commit sources, not binaries:
exclude deck PDFs and `__pycache__`. Keep PNG figures (small, illustrative).

3. Copy the tree without the nested `.git`:
```
rsync -a --exclude='.git' --exclude='__pycache__' --exclude='*.pdf' \
  ~/cm-example/minimal-course/ examples/minimal-course/
```

4. Update `examples/README.md`: mark `minimal-course/` as done; describe what the
example shows and which commands produced it.

5. Consistency check from the repo root:
```
python skill/scripts/validate_state.py examples/minimal-course
```
(or `/course-maker doctor` from the example folder) — so `COURSE_STATE.md`
matches the real files.

6. Commit:
```
git add examples/minimal-course examples/README.md
git commit -m "examples: add minimal-course produced by a real pipeline run"
```

## Gotchas

- Do NOT run `validate` in the same session that generated `spec`/`tests` — the
  context holds the solution and the simulation becomes invalid. Hence the
  mandatory `/clear`.
- `starter/` must be committed before `validate` — otherwise the clean notebook
  version is lost.
- `.gitignore` for the example: keep `__pycache__`, PDFs, `.ipynb_checkpoints`
  out of the commit (exclude at the rsync step or add a local `.gitignore`).
- Synthetic data with a fixed seed is critical: without it `validate` is not
  reproducible and tests drift.
