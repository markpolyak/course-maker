# Getting Started

This guide takes you from zero to a complete first lecture (plan + figures + slides + notes)
in a single session.

---

## Prerequisites

- One agent that supports the [Agent Skills](https://agentskills.io) standard:
  - Claude Code (`npm install -g @anthropic-ai/claude-code`), or
  - OpenAI Codex CLI, or
  - Cursor
- git
- LaTeX distribution for compiling slides locally (TeX Live or MiKTeX)
- Python 3.8+ with numpy, matplotlib, scipy, statsmodels

---

## Step 0: Install the skill

The skill is a single cross-tool Agent Skill (`SKILL.md` + `references/`). Clone
once, then symlink it into your agent's skills directory — a `git pull` in the
repo then keeps every tool up to date.

```bash
# Clone the repository
git clone https://github.com/markpolyak/course-maker

# Claude Code — global (~/.claude/skills):
ln -s "$(pwd)/course-maker/skill" ~/.claude/skills/course-maker

# OpenAI Codex CLI — global (~/.agents/skills; legacy ~/.codex/skills also works):
mkdir -p ~/.agents/skills
ln -s "$(pwd)/course-maker/skill" ~/.agents/skills/course-maker
```

For **Claude Code** and **Codex CLI** the skill is global — available in every
project. **Cursor has no global skills directory**, so the skill is project-scoped:
symlink it into each course repo (created in Step 1) and gitignore the link:

```bash
mkdir -p my-course/.cursor/skills
ln -s "$(pwd)/course-maker/skill" my-course/.cursor/skills/course-maker
echo ".cursor/skills/" >> my-course/.gitignore
```

---

## Step 1: Create a course repository

```bash
mkdir my-course && cd my-course && git init
cp ~/.claude/skills/course-maker/COURSE_CLAUDE_TEMPLATE.md CLAUDE.md
```

---

## Step 2: Fill in course context

Open `CLAUDE.md` and fill in `## Course context`. This is the most important step —
it's what makes every subsequent prompt precise without you having to repeat yourself.

Key things to specify:

**Audience.** What do your students already know?
```
Masters students. Strong background in probability theory and linear algebra.
Familiar with Python and basic ML. No prior experience with time series.
```

**Style.** How do you prefer to teach?
```
Intuition before formulas. Every equation must have a verbal interpretation.
Proofs only when they build understanding, not for completeness.
```

**Language.** Any language is supported — specify it explicitly:
```
Slides: French. Speaker notes: French. Code comments and axis labels: English.
```
Or all in one language:
```
All materials in Japanese.
```

**Recurring rules.** Anything that applies across all lectures:
```
- Always connect new material to applications in engineering/system analysis
- For every new distribution: show PDF shape, typical use case, parameter meaning
- Sections marked "announce-only" in course plan: 1–2 slides max, no derivations
```

---

## Step 3: Add your course plan

```bash
cp /path/to/your/course_plan.md .
git add . && git commit -m "init course"
```

The course plan is a Markdown file describing all lectures, seminars, and labs.
It doesn't need to follow any special format — Claude reads it and extracts what it needs.

---

## Step 4: Open in Claude Code

```bash
claude
```

Initialize the state file:
```
/course-maker course status
```

This reads `course_plan.md` and creates `COURSE_STATE.md` with a status table for all lectures.

---

## Step 5: Prepare lecture 1

### Plan (Step 1)

```
/course-maker plan 1
```

Claude reads your course plan section for lecture 1, reads your course context,
and produces a numbered slide-by-slide plan with timing.

Review it. Give feedback in plain text:
```
Slide 5 and 6 cover the same thing, merge them.
Section on characteristic functions is announce-only, compress to 1 slide.
```

When satisfied, Claude saves `lectures/01/plan.md` and updates `COURSE_STATE.md`.

### Visualizations (Step 2)

```
/course-maker visuals 1
```

Claude produces a table of all figures needed, with a TikZ feasibility assessment.
Figures marked "No — needs data/simulation" will be generated as PNG by Python.

### Figures (Step 3)

```
/course-maker figures 1
```

Claude writes `lectures/01/figures/figures.py`. Run it locally:

```bash
cd lectures/01 && python figures/figures.py
```

Check the PNGs. Give feedback:
```
fig02 — font too small on axis labels, increase to 12pt
fig03 — remove the legend, it's obvious from the colors
```

Iterate until satisfied, then commit the PNGs.

### Slides (Step 4)

Slides are generated in chunks of 5 to avoid timeouts.

```
/course-maker slides 1
```

This generates the preamble + title slide. Review, then continue:

```
/course-maker slides 1 next   # slides 1–5
/course-maker slides 1 next   # slides 6–10
/course-maker slides 1 next   # slides 11–15
/course-maker slides 1 next   # slides 16–20 + \end{document}
```

After each chunk Claude pauses for your feedback before continuing.

Compile locally to check:
```bash
cd lectures/01 && pdflatex slides.tex
```

If there are overfull boxes or layout issues, describe them to Claude:
```
Slide 8: image overflows the bottom of the frame
Slide 12: three blocks don't fit, text is cut off
```

Claude reads `history.md` to avoid repeating the same mistake in the next lecture.

### Speaker notes (Step 5)

```
/course-maker notes 1
/course-maker notes 1 next   # repeat until done
```

Notes are live spoken text, not a summary. They include pacing cues, emphasis marks,
and checkpoint timings. Generated in chunks of 5 slides.

---

## Step 6: Commit everything

```bash
git add lectures/01/ COURSE_STATE.md
git commit -m "lecture 01: all materials done"
```

---

## Continuing next week

When you come back to prepare lecture 2, Claude Code reads `history.md` from lecture 1
and `COURSE_STATE.md` — so it already knows what worked and what didn't.

If you've updated `course_plan.md` in the meantime:
```
/course-maker course update
```

This diffs the plan, marks affected lectures as ⚠️, and tells you which materials
need to be reviewed.

---

---

## Creating lab assignments

Lab assignments use a separate pipeline with `/course-maker lab *` commands.
Full workflow for a single lab:

```
/course-maker lab course-init                                            # one-time: create labs/shared/ with templates
/course-maker lab init 1 https://github.com/org/lab1-backprop lab1-backprop  # scaffold lab 1 in labs/lab1-backprop/

/course-maker lab plan 1        # Stage 1a: iterate until plan is approved
/course-maker lab notebook 1    # Stage 1b: generate exercises.ipynb
/course-maker lab spec 1        # Stage 1b: generate lab_spec.md (instructor-only)
/course-maker lab datasets 1    # Stage 1b: generate datasets_info.md (optional)

/course-maker lab tests 1       # Stage 2: generate tests.py, requirements.txt, README (+ grade_report.py if a reporter is used)

/course-maker lab validate 1 7  # Stage 3: validate as student 7 (new session recommended)

/course-maker lab publish 1     # push to starter repo + sync GitHub Classroom repo via gh API
```

For labs that already have a notebook but no spec, skip `lab plan 1` and run
`lab spec 1` directly — it auto-detects notebook mode and generates `lab_spec.md`
from the existing `exercises.ipynb`:
```
/course-maker lab spec 1        # auto-detects: no plan → notebook mode
/course-maker lab tests 1       # then continue normally
```

After post-release fixes:
```
/course-maker lab update 1      # fix → re-validate → re-publish
```

**Before running `/course-maker lab course-init`:** fill in `## Lab context` in `CLAUDE.md` with
your GitHub org, GitHub Classroom org, and starter repo URLs.

**Before running `/course-maker lab init N`:** for a profile that uses a remote starter repo
(e.g. `github-classroom`), create the starter repo first and pass its URL. For a local profile
(e.g. `local-zip`), no remote repo is needed — the `starter/` is just a local folder. The skill
ships with working `conftest_base.py` and `tests.yaml`, so labs scaffold out-of-the-box.

### Lab grading and per-student variants

By **default, labs are deliberately minimal**: the test harness
(`conftest_base.py`) runs the lab's pytest tests and reports plain pass/fail.
There is no scoring block, no autograder grade line, and no per-student variant
scheme — so a course that grades manually or has no variants needs no setup at
all.

Two opt-in features are controlled from `CLAUDE.md` → `## Lab context` →
`### Lab grading`:

```
grade_reporter: none      # none | scoring_ci | <your own reporter>
lab_variants: false       # true if each student gets a different dataset
```

- **`grade_reporter`** — selects an optional *grade reporter* that turns the
  raw pytest outcomes into end-of-run output. `none` (default) prints nothing
  extra. `scoring_ci` prints a points summary and a grade line designed to be
  read by an external autograder/CI. You can add your own reporter under
  `skill/extensions/reporters/`. See that folder's `README.md` for the contract.
- **`lab_variants`** — when `true`, each student is assigned a different dataset
  via a fixed formula in Block 0 of the notebook (so solutions can't be copied
  verbatim). When `false` (default), every student gets the same task and there
  is no variant code. See `skill/extensions/variants/README.md`.

The two are independent — you can use either, both, or neither.

**To run an autograded course with per-student variants** (a common STEM
setup), set both flags:

```
grade_reporter: scoring_ci
lab_variants: true
```

Then the pipeline wires it up for you:

1. `/course-maker lab course-init` installs the reporter into `labs/shared/`
   (as `grade_report.py`) and substitutes your course-language grade labels into
   it from `lab_templates.md`.
2. `/course-maker lab notebook N` includes the Block 0 variant cells.
3. `/course-maker lab tests N` fills the reporter's `TEST_POINTS`,
   `TEST_BLOCKS`, and `DATASETS` from the lab spec.
4. `/course-maker lab init N` copies `grade_report.py` into each lab's
   `starter/`, and the CI workflow captures the grade line from the test logs.

If your autograder greps the grade line for an exact phrase, put that phrase in
your personal `user_defaults` (`default_grade_output_label` in
`~/.course-maker/defaults.yaml`) so it stays in your config rather than in the
shared course-language templates. It takes precedence over the generic label
from `lab_templates.md` and is substituted into `grade_report.py` automatically.
(You can still override per course by editing `lab_templates.md`.)

---

## Tips for fewer iterations

- **Fill in course context thoroughly.** Vague context → vague output → more rounds.
- **Don't skip Steps 1–3 before running Step 4.** Generating slides without a plan
  and without existing PNGs leads to hallucinated figure filenames and incoherent structure.
- **Commit PNGs before running `/course-maker slides`.** Claude checks which files
  actually exist in `figures/` — missing files cause compilation errors.
- **Give specific feedback.** "Slide 7 is too dense" → Claude guesses. "Slide 7 has
  5 bullet points and a figure, move the figure to slide 8" → Claude executes.
