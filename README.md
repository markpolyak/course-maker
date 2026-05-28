# course-maker

A structured pipeline for preparing complete university course materials with AI assistance.
From a course plan to finished slides, figures, speaker notes, lab assignments, and more —
with state tracking and minimal iteration.

> Currently supports **Claude Code**. Cursor, Codex, and other agents — planned (see [Roadmap](#roadmap)).

---

## What it does

You describe your course once. Then for each lecture you run five commands:

```
/course-maker plan 3        # detailed slide-by-slide plan
/course-maker visuals 3     # list of visualizations, TikZ vs Python
/course-maker figures 3     # Python script to generate PNG figures
/course-maker slides 3      # LaTeX/Beamer presentation (chunked)
/course-maker slides 3 next # ...next 5 slides
/course-maker notes 3       # speaker notes (chunked)
```

Each step reads the outputs of previous steps and a `history.md` that logs every
decision and rejected idea — so Claude doesn't re-propose what you already turned down,
and each new lecture benefits from lessons learned in previous ones.

---

## Installation

**Requirements:** Claude Code, git.

```bash
# 1. Clone the skill
git clone https://github.com/markpolyak/course-maker ~/.claude/skills/course-maker

# 2. Create a new course repository
mkdir my-course && cd my-course && git init

# 3. Copy the course template
cp ~/.claude/skills/course-maker/COURSE_CLAUDE_TEMPLATE.md CLAUDE.md

# 4. Add your course plan
cp /path/to/your/course_plan.md .

# 5. Open in Claude Code and initialize
claude
> /course-maker course init
```

---

## Quick start (5 minutes to first slide plan)

1. Fill in `CLAUDE.md` → `## Course context`: audience background, style preference, language.
2. Put your `course_plan.md` in the repo root.
3. Run `/course-maker plan 1` and review the output.
4. When satisfied, run `/course-maker visuals 1`.

Full walkthrough: [docs/getting-started.md](docs/getting-started.md)

---

## How it reduces iteration

The two main sources of wasted rounds in lecture prep:

**Problem 1: Claude doesn't remember what you rejected.**
Each session starts fresh. You say "compress section 3", Claude does it, next week
it's back. → `history.md` per lecture fixes this: every decision is logged and re-read
at the start of each step.

**Problem 2: Beamer slides time out or overflow.**
A 20-slide `.tex` file is 600–900 lines. Generating it in one shot causes Claude Code
to hang. → Slides and speaker notes are generated in chunks of 5, with approval between
each chunk.

---

## Repository layout (per course)

```
my-course/
  CLAUDE.md               ← skill + course context (audience, style, language)
  course_plan.md          ← master plan (source of truth)
  COURSE_STATE.md         ← status of all lectures: ✅ 🔄 ❌ ⚠️
  lectures/
    01/
      plan.md             ← slide-by-slide plan
      visuals.md          ← visualization list with TikZ feasibility
      figures/
        figures.py        ← generates all PNG figures
        fig01_name.png
      slides.tex          ← Beamer presentation
      speaker_notes.md    ← live spoken text for the lecturer
      history.md          ← decision log
    02/
      ...
```

---

## Commands

| Command | Description |
|---|---|
| `/course-maker course init` | Scaffold a new course repository |
| `/course-maker course status` | Status table for all lectures |
| `/course-maker course update` | Update course plan, flag affected lectures |
| `/course-maker plan N` | Step 1: detailed slide plan for lecture N |
| `/course-maker visuals N` | Step 2: visualization list |
| `/course-maker figures N` | Step 3: Python figure generation script |
| `/course-maker slides N` | Step 4: Beamer slides, chunk 0 (preamble + title) |
| `/course-maker slides N next` | Step 4: next chunk of 5 slides |
| `/course-maker notes N` | Step 5: speaker notes, slides 1–5 |
| `/course-maker notes N next` | Step 5: next chunk of 5 slides |
| `/course-maker status N` | State + history summary for lecture N |

---

## Example

The `examples/stochastic-processes/` directory contains a real course
("Случайные процессы и временные ряды", 8 lectures) with completed materials
for lectures 1–2: `plan.md`, `visuals.md`, `slides.tex`, `speaker_notes.md`.

---

## Roadmap

- [x] Claude Code skill (`.claude/skills/`)
- [x] Chunked generation for slides and speaker notes
- [x] State tracking (`COURSE_STATE.md` + `history.md`)
- [ ] Lab assignment pipeline (`/lab-pipeline`)
- [ ] Syllabus auto-generation
- [ ] pptx output (in addition to Beamer)
- [ ] Overleaf integration
- [ ] Cursor / Codex / Cline adapter (agent-agnostic `AGENTS.md` core)
- [ ] Multi-agent harness support (similar to GSD Redux)

---

## Contributing

See [docs/contributing.md](docs/contributing.md).

The best contributions right now: examples from real courses (any discipline),
and bug reports from the Beamer compilation step with the specific error + fix.

---

## License

MIT
