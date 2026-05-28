# Getting Started

This guide takes you from zero to a complete first lecture (plan + figures + slides + notes)
in a single session.

---

## Prerequisites

- Claude Code installed (`npm install -g @anthropic-ai/claude-code`)
- git
- LaTeX distribution for compiling slides locally (TeX Live or MiKTeX)
- Python 3.8+ with numpy, matplotlib, scipy, statsmodels

---

## Step 0: Install the skill

```bash
# Clone the repository
git clone https://github.com/your-username/course-maker

# Option A — symlink (recommended for development and staying up to date)
# git pull in the repo will automatically update the skill
ln -s $(pwd)/course-maker/skill ~/.claude/skills/course-maker

# Option B — copy (simpler, but requires re-copying after updates)
cp -r course-maker/skill ~/.claude/skills/course-maker
```

The skill lives in `~/.claude/skills/` and is available in all your Claude Code projects.

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

Lab assignments use a separate pipeline with `/lab *` commands.
Full workflow for a single lab:

```
/lab course-init                                            # one-time: create labs/shared/ with templates
/lab init 1 https://github.com/org/lab1-backprop lab1-backprop  # scaffold lab 1 in labs/lab1-backprop/

/lab plan 1        # Stage 1a: iterate until plan is approved
/lab notebook 1    # Stage 1b: generate exercises.ipynb
/lab spec 1        # Stage 1b: generate lab_spec.md (instructor-only)
/lab datasets 1    # Stage 1b: generate datasets_info.md (optional)

/lab tests 1       # Stage 2: generate tests.py, conftest.py, requirements.txt, README

/lab validate 1 7  # Stage 3: validate as student 7 (new session recommended)

/lab publish 1     # push to starter repo + sync GitHub Classroom repo via gh API
```

For labs that already have a notebook but no spec:
```
/lab reverse-spec 1   # generate lab_spec.md from existing exercises.ipynb
/lab tests 1          # then continue normally
```

After post-release fixes:
```
/lab update 1      # fix → re-validate → re-publish
```

**Before running `/lab course-init`:** fill in `## Lab context` in `CLAUDE.md` with
your GitHub org, GitHub Classroom org, and starter repo URLs.

**Before running `/lab init N`:** create the starter repo on GitHub and copy in your
`conftest.py` and `tests.yaml` to `skill/templates/` (these are not auto-generated).

---

## Tips for fewer iterations

- **Fill in course context thoroughly.** Vague context → vague output → more rounds.
- **Don't skip Steps 1–3 before running Step 4.** Generating slides without a plan
  and without existing PNGs leads to hallucinated figure filenames and incoherent structure.
- **Commit PNGs before running `/course-maker slides`.** Claude checks which files
  actually exist in `figures/` — missing files cause compilation errors.
- **Give specific feedback.** "Slide 7 is too dense" → Claude guesses. "Slide 7 has
  5 bullet points and a figure, move the figure to slide 8" → Claude executes.
