# course-maker

A structured pipeline for preparing complete university course materials with AI assistance.
From a course plan to finished slides, figures, speaker notes, lab assignments, and more —
with state tracking and minimal iteration.

> The skill is a cross-tool [Agent Skill](https://agentskills.io) (`SKILL.md`),
> so it runs on **Claude Code**, **OpenAI Codex CLI**, and **Cursor** — one skill,
> installed per tool (see [Installation](#installation)). Deeper cross-tool parity
> is tracked in [docs/MULTI_HARNESS_PLAN.md](docs/MULTI_HARNESS_PLAN.md).

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

For lab assignments there is a parallel pipeline (`plan → notebook → spec →
[datasets] → tests → validate → publish`) with optional pytest autograding, and
publishing driven by a pluggable LMS adapter (GitHub Classroom, local zip, …).
Seminars, quizzes, and homework have their own pipelines too — see
[Commands](#commands).

---

## Installation

**Requirements:** one of Claude Code / OpenAI Codex CLI / Cursor, plus git. For
local Beamer compilation: a LaTeX distribution. For lab tests: Python 3.11+.

The same skill (`SKILL.md` + `references/`) works in every tool; only how you
install it differs. Pick one of two ways.

### Option A — release zip (any tool; the only way for Cowork)

Download `course-maker-vX.Y.Z.zip` from the
[latest release](https://github.com/markpolyak/course-maker/releases/latest). It
is a self-contained, versioned copy of the skill — a single `course-maker/`
folder — with the version stamped into it.

- **claude.ai / Claude Cowork:** upload the zip as-is via **Settings → Features**
  (Skills). Do not unzip.
- **Claude Code / Codex / Cursor:** unzip it into the tool's skills directory.
  The archive already contains the `course-maker/` folder, so it lands in the
  right place:

  ```bash
  unzip course-maker-v1.3.0.zip -d ~/.claude/skills/   # Claude Code
  unzip course-maker-v1.3.0.zip -d ~/.agents/skills/   # Codex CLI
  unzip course-maker-v1.3.0.zip -d ~/.cursor/skills/   # Cursor (only if not using the above)
  ```

  Re-download and re-unzip to update.

### Option B — clone + symlink (for development / tracking `main`)

Best if you want a `git pull` to update every tool at once, or you're editing
the skill. Not applicable to Cowork. Run from the PARENT directory of the clone:

```bash
git clone https://github.com/markpolyak/course-maker

# Claude Code:
ln -s "$(pwd)/course-maker/skill" ~/.claude/skills/course-maker

# Codex CLI:
mkdir -p ~/.agents/skills
ln -s "$(pwd)/course-maker/skill" ~/.agents/skills/course-maker
```

Replace `ln -s` with `cp -r` for a self-contained copy (re-copy after updates).

**Cursor needs no separate install** — it also reads the Claude Code and Codex
skill directories, so it picks up either symlink above. (Only using Cursor? Put
the link in `~/.cursor/skills/course-maker`.)

Then create a course and initialize it in your agent:

```bash
# Create a new course repository
mkdir my-course && cd my-course && git init

# Open in Claude Code / Codex / Cursor and initialize
> /course-maker course init
> /course-maker course plan
```

`course init` creates `AGENTS.md` (course context), `course_conventions.md`,
`slides_preamble.tex`, and the directory layout. `course plan` walks you through
filling in `course_plan.md` (or imports an existing one).

---

## Quick start (5 minutes to first slide plan)

1. Run `/course-maker course init` — fills in `AGENTS.md` (course context) and
   per-course templates from your answers (course name, audience, style, language,
   slides format, LaTeX engine).
2. Run `/course-maker course plan` — interactively creates `course_plan.md`,
   or imports yours if you already have one.
3. Run `/course-maker plan 1` and review the output.
4. When satisfied, run `/course-maker visuals 1`.

Full walkthrough: [docs/getting-started.md](docs/getting-started.md).

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

A third source — Claude silently skipping a `references/*.md` file mentioned in
the dispatcher — is addressed by the `## Inviolable rules` block in `SKILL.md`,
which is always loaded and lists the critical rules that survive any skip.

---

## Repository layout (per course)

```
my-course/
  AGENTS.md               ← course context (audience, style, language, profile)
  course_plan.md          ← master plan (source of truth)
  syllabus.md             ← student-facing syllabus (generated from course_plan.md)
  COURSE_STATE.md         ← status of all pipelines: ✅ 🔄 ❌ ⚠️
  course_conventions.md   ← terminology + language rules (generated by course init)
  slides_preamble.tex     ← LaTeX/Beamer preamble (generated by course init)
  lab_templates.md        ← lab notebook/test templates (generated by lab course-init)
  lms_adapter.md          ← LMS publish workflow (copied from the profile by lab course-init)
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
  labs/
    shared/               ← per-course base templates
    lab1/
      lab_spec.md         ← instructor-only contract (not published to students)
      history.md
      starter/            ← student-facing files (delivery depends on the LMS adapter)
        exercises.ipynb
        conftest.py
        tests.py
        ...
  seminars/               ← per-seminar decks + practical notebooks
  quizzes/                ← quiz/exam banks + student exports
  homework/               ← homework briefs + rubrics (or nested under a seminar)
```

---

## Commands

**Lecture pipeline:**

| Command | Description |
|---|---|
| `/course-maker` | Project status (all pipelines) |
| `/course-maker help` | Command reference |
| `/course-maker course init` | Scaffold a new course repository |
| `/course-maker course plan` | Create, fill, or update course_plan.md (interactive) |
| `/course-maker course status` | Status table for all pipelines |
| `/course-maker course update` | Detect manual edits to course_plan.md, flag affected lectures |
| `/course-maker doctor` | Check for state drift, missing files, config gaps (read-only) |
| `/course-maker stats` | Progress bars across pipelines (read-only) |
| `/course-maker syllabus [pdf\|latex\|docx]` | Generate/update student syllabus.md; optional export |
| `/course-maker plan N` | Step 1: detailed slide plan for lecture N |
| `/course-maker visuals N` | Step 2: visualization list |
| `/course-maker figures N` | Step 3: Python figure generation script |
| `/course-maker slides N` | Step 4: Beamer slides, chunk 0 (preamble + title) |
| `/course-maker slides N next` | Step 4: next chunk of 5 slides |
| `/course-maker notes N` | Step 5: speaker notes, slides 1–5 |
| `/course-maker notes N next` | Step 5: next chunk of 5 slides |
| `/course-maker status N` | State + history summary for lecture N |

**Seminar pipeline** (a lecture deck + a practical part, in seminars/NN/):

| Command | Description |
|---|---|
| `/course-maker seminar plan\|visuals\|figures\|slides\|notes N` | Deck steps — reuse the lecture step pipeline, targeting seminars/NN/ |
| `/course-maker seminar practice N` | Practical live code-demo notebook (practice.ipynb) |
| `/course-maker seminar status N` | Status + last 3 history entries |

**Lab pipeline:**

| Command | Description |
|---|---|
| `/course-maker lab course-init` | One-time setup: create labs/shared/ with templates; install the LMS adapter |
| `/course-maker lab init N [url] [slug]` | Scaffold lab N (starter setup per the LMS adapter; url used only by remote-starter profiles) |
| `/course-maker lab plan N` | Step 1a: interactive planning until approved |
| `/course-maker lab notebook N` | Step 1b: generate exercises.ipynb |
| `/course-maker lab spec N` | Step 1b: generate lab_spec.md (auto plan/notebook mode) |
| `/course-maker lab datasets N` | Step 1b: generate datasets_info.md (optional) |
| `/course-maker lab tests N` | Step 2: tests.py, requirements.txt, README (+ grade_report.py if a reporter is used) |
| `/course-maker lab validate N <id>` | Step 3: validate as student (new session required) |
| `/course-maker lab publish N` | Run the publish workflow from lms_adapter.md (LMS-specific) |
| `/course-maker lab update N` | Re-publish after post-release fix |
| `/course-maker lab status N` | Status + last 3 history entries |

**Quiz pipeline** (quizzes / tests / exams):

| Command | Description |
|---|---|
| `/course-maker quiz plan N` | Step 1: interactive quiz plan (blocks, types, variants) |
| `/course-maker quiz generate N [next]` | Step 2: generate question bank (chunked by block) |
| `/course-maker quiz publish N [format]` | Step 3: export student-facing version (markdown) |

**Homework pipeline** (manually graded take-home assignment — no autograding):

| Command | Description |
|---|---|
| `/course-maker homework plan N [dir]` | Step 1: interactive task brief + grading rubric (dir default homework/NN/) |
| `/course-maker homework publish N [format]` | Step 2: assemble student handout; markdown default, pdf/latex/docx via pandoc |
| `/course-maker homework status N` | Status + last 3 history entries |

---

## Examples

The `examples/` directory is reserved for example courses. It is currently
empty — see [examples/README.md](examples/README.md) for what is planned and
how to contribute your own. Examples must be produced by running the skill,
not hand-assembled.

---

## Roadmap

Active roadmap with execution plan: [docs/IMPROVEMENT_PLAN.md](docs/IMPROVEMENT_PLAN.md).

Quick status:

- [x] Claude Code skill (`~/.claude/skills/`)
- [x] Chunked generation for slides and speaker notes
- [x] State tracking (`COURSE_STATE.md` + `history.md`)
- [x] Lab assignment pipeline (`/course-maker lab *` commands)
- [x] Seminar, quiz, and homework pipelines
- [x] Working out-of-the-box templates (`conftest_base.py`, `tests.yaml`)
- [x] `## Inviolable rules` block in `SKILL.md` (critical rules survive skipped references)
- [x] Profile layer: pluggable LMS adapters + user defaults + opt-in grading extensions
- [x] Syllabus auto-generation from `course_plan.md`
- [x] Course health & progress tooling: `doctor`, `stats`, state drift checker, bulky-history warning
- [ ] Additional slide formats: Slidev and pptx (in addition to Beamer)
- [ ] Overleaf integration (cloud LaTeX compilation)
- [~] Cross-tool support: skill installs on Claude Code, Codex CLI, and Cursor (Agent Skills standard); full parity (declaudize wording, `AGENTS.md` course layer) tracked in [docs/MULTI_HARNESS_PLAN.md](docs/MULTI_HARNESS_PLAN.md)
- [ ] Multi-agent harness support (similar to GSD Redux)

---

## Contributing

See [docs/contributing.md](docs/contributing.md).

The best contributions right now: examples from real courses (any discipline),
and bug reports from the Beamer compilation step with the specific error + fix.

---

## License

MIT
