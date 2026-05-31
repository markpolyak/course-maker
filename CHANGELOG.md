# Changelog

## [2026-05-31] (2)

### Added

**`/course-maker course plan` — dedicated command for course plan creation and filling**
(`skill/SKILL.md`, `skill/references/step1_plan.md`)

`course_plan.md` is now a first-class artifact with its own command. The command is
idempotent: detects whether the plan is missing, partial (has `<!-- TODO -->` sections),
or complete, and picks up from the right place.

**Three creation modes:**

- **[1] Import existing plan** — accepts a file path or pasted content in any format.
  Claude extracts sessions, lecture topics, labs, prerequisites, grading, and instructor
  info; fills a structured template; marks anything not found as `<!-- TODO -->`.
  Original file saved as `course_plan_source.*`. Iterates until approved.

- **[2] Structure known content** — 10-question dialog (one at a time) covering session
  types and counts, schedule, topics, prerequisites, grading, self-study materials,
  instructor info. Skips questions the user presses Enter on (filled with TODO).

- **[3] Help determine content** — same dialog, but after collecting basics Claude
  generates a full proposed outline using knowledge of typical university curricula
  for the subject and audience. Iterates with open-ended feedback until approved.
  Claude is explicit that the proposal is based on general knowledge.

**`course_plan.md` format** now includes:
- `## Overview` — session type counts and standard duration
- `## Sessions` table — all sessions of all types in chronological order; sessions
  without a skill pipeline marked `no pipeline`
- `## Lectures` — one subsection per lecture with topics, time, within-course
  prerequisites, and announce-only sections
- `## Labs` — one-line pointer per lab to the lab pipeline directory
- `## Prerequisites`, `## Grading`, `## Self-study Materials`, `## Instructors` —
  optional sections with `<!-- TODO -->` until filled

**`/course-maker course plan update`** — dedicated command for intentional plan edits
(session removed, topic shifted, schedule compressed). Applies edits, then cross-checks
`COURSE_STATE.md` and flags affected lectures/labs as ⚠️.

**`/course-maker course update`** — narrowed to detecting *manual* edits (git diff)
and flagging affected materials. No longer handles intentional edits (use `course plan update`).

**`course init`** no longer runs a plan dialog — just reports if `course_plan.md` is
missing and points to `/course-maker course plan`.

`step1_plan.md` updated to read from the new `## Sessions` table and `## Lectures`
subsection format.

---

## [2026-05-31]

### Fixed

**lab validate: no /clear prompt before validation** (`skill/references/lab_step3_validate.md`, `skill/SKILL.md`)

The current session context contains `lab_spec.md`, `tests.py`, and `conftest.py` from
prior steps, which would compromise the student simulation. The skill now shows a blocking
message asking the user to run `/clear` (or open a new session) and re-run the command.
Validation does not proceed until the user confirms the context has been cleared.

**lab validate: no guard against uncommitted changes, notebook not restored after validation** (`skill/SKILL.md`, `skill/references/lab_step3_validate.md`)

Validation simulates a student solving `exercises.ipynb`, which modifies the file.
If the notebook wasn't committed before validation, the clean version was lost permanently.
After validation the notebook was left with student solutions in the working tree.

Now the workflow:
- Runs `git status <LAB_DIR>starter/` before starting; stops with an error message if there
  are uncommitted changes, asking the user to commit first
- After validation completes, runs `git restore <LAB_DIR>starter/exercises.ipynb` to remove
  student solutions from the working copy

**figures step marked ✅ without running the script** (`skill/SKILL.md`, `skill/references/step3_figures.md`)

After generating `figures.py` and getting user approval, the skill saved the file and
immediately marked the step done — without running the script or verifying that PNG files
were created. Code that has never been run must be treated as unverified.

Now the workflow after approval:
1. Saves `figures.py`
2. Runs `python figures/figures.py` from the lecture directory
3. If errors: shows traceback, fixes the script, re-runs until clean
4. After clean run: lists generated PNGs for the user to confirm
5. Only then marks figures → ✅

### Changed

**Skill reference files made language-agnostic** (`skill/references/step4_slides.md`, `skill/references/step5_notes.md`)

Russian strings in the lecture pipeline reference files were replaced with English equivalents
and annotated with "translate to course language" instructions. The skill now works with any
course language; the output language is determined at generation time from the course context
in CLAUDE.md.

Changes:
- `step4_slides.md`: `\subtitle{Лекция N. [Title]}` → annotated placeholder that reads
  the course-language word for "Lecture" at generation time; outline frame title
  `План лекции` likewise replaced with a language-neutral placeholder
- `step5_notes.md`: entire output template translated from Russian to English;
  all Russian section headers, table headers, stage directions, and example speech replaced
  with English equivalents; each heading annotated "(translate to course language)" so the
  generated notes are still produced in the correct course language

### Added

**Language-specific template files** (`skill/templates/`)

Four new source files that serve as the language-specific content layer for each course:

- `lab_templates_ru.md` / `lab_templates_en.md` — notebook header cell, Block 0 cells
  (tasks 0.1–0.3 with code), final checklist cell, self-check cell, function/variable stub
  format, task title format, hint format, bonus marker, conftest scoring block marker,
  grade output string, datasets_info section title
- `course_conventions_ru.md` / `course_conventions_en.md` — language rule, terminology
  dictionary (English ↔ course language), "never use" list, lab goal writing rule with
  bad/good examples

These files are copied to the course root by the init wizards and edited by the professor
to match the course. The skill references read from the course-root copies, not from
`skill/templates/` directly.

### Changed

**Skill reference files made fully language-agnostic** (all `skill/references/lab_*.md`,
`skill/references/step1_plan.md`, `skill/references/step4_slides.md`,
`skill/references/step5_notes.md`, `skill/SKILL.md`, `skill/COURSE_CLAUDE_TEMPLATE.md`)

All language-specific content (Russian notebook templates, terminology dictionary,
docstring format, TODO comment style, scoring strings, section titles) has been moved
out of skill reference files into the new `skill/templates/` source files. Reference
files now point to `course_conventions.md` and `lab_templates.md` in the course root
instead of embedding the content directly.

Specific changes:
- `lab_context.md`: removed "Language and Terminology", "Notebook Structure", and
  "Notebook Task Formatting" sections; added "Required reading" block directing the
  skill to read `course_conventions.md` and `lab_templates.md` before any lab command;
  "What NOT to do" examples now reference `course_conventions.md` instead of hardcoding
  Russian examples
- `lab_step1b_notebook.md`, `lab_step2_tests.md`, `lab_step1b_datasets.md`,
  `lab_step1a_plan.md`, `lab_step1b_spec.md`, `lab_reverse_spec.md`: added
  `course_conventions.md` and/or `lab_templates.md` to "Context to Read" lists;
  replaced hardcoded Russian strings with references to the template files
- `step1_plan.md`, `step4_slides.md`, `step5_notes.md`: added `course_conventions.md`
  to "Context to gather before writing"

**`/course-maker course init` is now idempotent** (`skill/SKILL.md`)

The command can be safely re-run on an existing course — to recover missing files or
after accidental re-invocation. Restructured into four phases mirroring `lab course-init`:

- Phase 1: auto-detects `CLAUDE.md` (missing / placeholder / filled), `COURSE_STATE.md`,
  `course_conventions.md`, and directory structure
- Phase 2: asks only the questions whose answers are not already in `CLAUDE.md`
- Phase 3: creates only the files that are missing; never overwrites existing files
- Phase 4: prints a summary of what existed, what was created, and what to do next

`course_conventions.md` is created in Phase 3 (language template copied from
`skill/templates/course_conventions_{lang}.md`).

**`/course-maker lab course-init` Phase 5 creates both template files** (`skill/SKILL.md`)

Phase 5 now creates `lab_templates.md` if it does not exist (previously undocumented).
Acts as a fallback for existing courses that were set up before template files were
introduced — re-running `lab course-init` is enough to get `lab_templates.md` without
going through `course init`.

**Repository layout updated** (`skill/SKILL.md`)

Added `course_conventions.md` and `lab_templates.md` to the documented course root layout.

**`COURSE_CLAUDE_TEMPLATE.md` updated**

Added a note below the Language field explaining that `course_conventions.md` and
`lab_templates.md` are generated automatically by the init wizards and should be
edited after generation if the course conventions differ from language defaults.

---

## [2026-05-29]

### Fixed

**Wrong command suggestions after each step** (`skill/SKILL.md`, `docs/getting-started.md`, `README.md`)

Claude Code was suggesting non-existent short-form commands to the user after completing each pipeline step:
- After `/course-maker plan N`, Claude suggested `/lecture visuals N` → unknown command error
- After completing a lab step, Claude suggested `/lab tests N` → unknown command error

Root cause: `SKILL.md` documented commands in a short form (`/lecture plan N`, `/lab plan N`) that
predates the `course-maker` skill name. Claude Code resolves slash commands by looking up a skill with
that exact name — since no `lecture` or `lab` skill exists, it reports "unknown command."

Changes:
- Updated Quick reference tables (lecture and lab commands) to use full invocation form
- Updated all workflow section headers (`### /lecture plan N` → `### /course-maker plan N`, etc.)
- Updated in-text references to commands inside workflow descriptions
- Fixed chunked-generation suggestions in slides and notes workflows:
  `Type /lecture slides N next` → `Type /course-maker slides N next`
- Fixed `/course-maker lab course-init` completion message
- Added General rule: "Always use the full invocation form when suggesting next commands"
- `docs/getting-started.md`: updated all lab command examples to `/course-maker lab *` form
- `README.md`: added lab commands to the Commands table

**Command format reference (after this fix):**

| Before (broken) | After (correct) |
|---|---|
| `/lecture plan N` | `/course-maker plan N` |
| `/lecture visuals N` | `/course-maker visuals N` |
| `/lecture figures N` | `/course-maker figures N` |
| `/lecture slides N` | `/course-maker slides N` |
| `/lecture notes N` | `/course-maker notes N` |
| `/lecture status N` | `/course-maker status N` |
| `/course init` | `/course-maker course init` |
| `/course status` | `/course-maker course status` |
| `/course update` | `/course-maker course update` |
| `/lab course-init` | `/course-maker lab course-init` |
| `/lab init N` | `/course-maker lab init N` |
| `/lab plan N` | `/course-maker lab plan N` |
| `/lab notebook N` | `/course-maker lab notebook N` |
| `/lab spec N` | `/course-maker lab spec N` |
| `/lab tests N` | `/course-maker lab tests N` |
| `/lab validate N` | `/course-maker lab validate N` |
| `/lab publish N` | `/course-maker lab publish N` |
| `/lab update N` | `/course-maker lab update N` |
| `/lab reverse-spec N` | `/course-maker lab reverse-spec N` |
| `/lab status N` | `/course-maker lab status N` |

---

## [fa115d0] — 2026-05-28

### Added

- Lab assignment pipeline (`/course-maker lab *` commands):
  - Steps: plan → notebook → spec → datasets → tests → validate → publish
  - `references/lab_step1a_plan.md`, `lab_step1b_notebook.md`, `lab_step1b_spec.md`,
    `lab_step1b_datasets.md`, `lab_step2_tests.md`, `lab_step3_validate.md`, `lab_context.md`
  - `references/lab_reverse_spec.md` — generate spec from existing notebook
  - `skill/templates/`: `conftest_base.py`, `tests_template.py`, `tests.yaml`
  - `docs/LAB_PIPELINE_PLAN.md` — design document for the lab pipeline

## [cc12be7] — 2026-05-28

### Added

- `docs/LAB_PIPELINE_PLAN.md` — planning document for the lab pipeline integration

## [9af9002] — 2026-05-28

### Changed

- Updated installation instructions in README

## [cba4c8b] — 2026-05-28

### Changed

- Renamed project from `lecture-pipeline` to `course-maker`

## [70dc5d7] — 2026-05-28

### Added

- Initial release: lecture pipeline (steps 1–5: plan, visuals, figures, slides, notes)
- `skill/SKILL.md` with full workflow descriptions
- `skill/COURSE_CLAUDE_TEMPLATE.md`
- `skill/references/`: `step1_plan.md` through `step5_notes.md`
- `docs/getting-started.md`, `docs/PROJECT_CONTEXT.md`
