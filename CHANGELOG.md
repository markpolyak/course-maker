# Changelog

## [2026-06-14] — Improvement wave 6 (QoL & observability)

Scope decisions for this wave (from design discussion): the lock-file step was
**dropped** (single-user git-backed repo; a stale `.lock` from a crashed session
causes more harm than the rare concurrent-run it prevents), and `history.md`
compaction was **deferred** (no real large `history.md` exists to design against;
folding it on spec risks losing the rejected-ideas memory that is its whole
value). `doctor` is **read-only** this iteration — it reports and names the fix
command, never edits.

### Added

**`scripts/validate_state.py`** — the skill's first executable artifact. Facts
layer for drift detection: parses `COURSE_STATE.md` and cross-checks every `✅`
status against the artifact that should exist on disk. Lenient Markdown parser
(maps columns by header name, agnostic to order/spacing), pure stdlib. Findings
are prefixed `DRIFT` (done but missing) / `STALE` (figures older than
`figures.py`) / `UNTRACKED` (artifact exists, status ❌) / `SKIP` (unparseable
row). Exit code 1 on drift/stale so it is usable standalone in external CI. The
step→file mapping is kept in sync with `references/repository_layout.md`.

**`/course-maker doctor`** (`references/doctor.md`) — read-only diagnostic.
Step 1 runs `validate_state.py` (mechanical facts). Step 2 adds semantic checks
Claude does itself: leftover `<!-- TODO -->` in `course_plan.md`,
profile↔`lms_adapter.md` consistency, presence of generated config files
(`course_conventions.md`, `slides_preamble.tex`, `lab_templates.md`). Step 3
reports each finding with the exact command that fixes it. The split — script
for deterministic facts, instructions for judgement — is the deliberate hybrid
chosen for this wave.

**`/course-maker stats`** (`references/stats.md`) — read-only progress bars.
Planned totals from `course_plan.md` (Overview/Sessions + per-lecture estimated
time); completion from `COURSE_STATE.md` (lecture complete = all 5 steps ✅, lab
complete = tests+validated+published ✅). 10-cell bars per pipeline, optional
hours line, in-progress list; flags plan/state count mismatches toward `doctor`.

### Changed

**Slides stale-figure guard** (`references/step4_slides.md`, `SKILL.md`). The
slides step now lists PNGs *with timestamps* and warns when any PNG is older
than `figures.py` (figures may be out of date), offering to re-run
`/course-maker figures N` first. A warning, not a hard block. Same fact the
`validate_state.py` `STALE` finding surfaces, applied inline at slide time.

**`SKILL.md`**: `doctor` and `stats` added to the command table and as thin
dispatchers (now 299 lines — still under the 300 target, but tight; the next
addition should prompt extracting something).

---

## [2026-06-13] — Improvement waves 1–3

### Added

**`IMPROVEMENT_PLAN.md`** (`docs/IMPROVEMENT_PLAN.md`) — comprehensive skill
review and 7-wave execution roadmap. Each wave has atomic steps and
completion criteria. Recommended execution order: 1 (SKILL.md compaction) →
2 (bootstrap) → 3 (doc drift) → 4 (profiles) → 6 (QoL) → 5 (new pipelines)
→ 7 (alternative formats).

**`## Inviolable rules` block in `SKILL.md`** — 15 rules grouped into
Observability, Grading invariants, Validation isolation, Slides & figures,
and Process. They apply regardless of which reference file was read. The
first rule is the observability rule: every step must list which
`references/*.md` files were read in the first chat message — silent skips
become detectable. Rationale: critical rules buried in 100-line workflows
are skipped as often as instructions in external reference files; sticky
rules require short, high-visibility, negatively framed statements that
survive any path.

**New reference files** extracted from the bloated `SKILL.md`:
`references/course_init.md`, `course_plan.md`, `lab_course_init.md`,
`lab_init.md`, `lab_publish.md`, `repository_layout.md`. The `lab_publish.md`
file additionally documents recovery from `git subtree push` failures caused
by GitHub Classroom squashed-history divergence.

**Working out-of-the-box templates** (`skill/templates/`):
- `conftest_base.py` — real pytest conftest (~210 lines): IPython mocking,
  nbformat-based student notebook importer, `student_module` fixture,
  outcome tracking, session finalizer with parameterized labels
  (`TASKID_LABEL`, `GRADE_OUTPUT_LABEL`, `SCORING_HEADER`). Substitutes
  the previous placeholder that required pasting from a real lab.
- `tests.yaml` — real GitHub Actions workflow: checkout, setup-python,
  install requirements + pytest + nbformat + jupyter, nbconvert, pytest.
  `STUDENT_ID` read from a repo variable so external CI can override per-fork.

**`.gitignore`** for `__pycache__/`, editor caches, OS metadata.

**`examples/`** stub with an honest README (`examples/README.md`).
Hand-assembled artifacts labelled as "produced by the skill" would diverge
from real pipeline output in tone, history.md evolution, and cross-step
coherence — so the directory stays empty until a genuine example is produced
by running the skill.

**`docs/contributing.md`** — minimal contribution guide (priorities, skill
conventions, PR checklist).

**`docs/archive/`** — completed planning documents moved here:
`TEMPLATE_MIGRATION_PLAN.md` (template language abstraction — done) and
`LAB_PIPELINE_PLAN.md` (labforge integration — done). The archive README
explains what was implemented for each.

### Changed

**`SKILL.md` compacted from 978 → 280 lines** (target ≤300). Full
workflows for `course init`, `course plan`, `lab course-init`, `lab init`,
and `lab publish` moved out to dedicated reference files. Each command in
`SKILL.md` is now a thin dispatcher (`Read: references/X.md`) plus, for
steps with a history of silent skips (`figures`, `slides`, `notes`,
`lab validate`), a short `**CRITICAL — even if reference was skipped:**`
block. Repository layout and state file formats extracted to
`references/repository_layout.md`.

**`tests_template.py` translated from Russian to English.** The file is
the universal style reference for generated `tests.py`; per-language strings
(error messages in the course language) are substituted at generation time
from `course_conventions.md`.

**Grade output strings are now parameters, not invariants.** The Russian
phrases `СИСТЕМА ПОДСЧЁТА БАЛЛОВ ДЛЯ ЛАБОРАТОРНОЙ РАБОТЫ` and
`ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА В ЖУРНАЛ` (read by external CI) used to be hardcoded
"critical invariants" in `conftest_base.py` and `lab_step2_tests.md`. They
are now values in `lab_templates_ru.md` (and English equivalents in
`lab_templates_en.md`) under `SCORING_HEADER`, `TASKID_LABEL`,
`GRADE_OUTPUT_LABEL`. `conftest_base.py` parameterizes the print() format
once; per-course labels are substituted during `lab course-init` (new
Phase 2a). The print() format itself is fixed, so external CI still
matches; the labels become a course/language configuration knob.

**`COURSE_CLAUDE_TEMPLATE.md` no longer embeds `SKILL.md`.** Removed the
`SKILL:START`/`SKILL:END` markers and the reference to the non-existent
`/skill update` command. The skill is loaded globally from
`~/.claude/skills/course-maker/` and discovered automatically — embedding
it in course-level `CLAUDE.md` was redundant and went stale on every
skill update.

**`docs/PROJECT_CONTEXT.md` updated**:
- Layout corrected (`course-maker/skill/SKILL.md` not `course-maker/SKILL.md`)
  and expanded to list all current files in `skill/`, `docs/`, `examples/`.
- "Known issues" updated: chunked-generation is no longer "in v2", Inviolable
  rules and out-of-the-box templates marked fixed in waves 1 and 2.
- Roadmap pointed to `IMPROVEMENT_PLAN.md` as the authoritative source;
  original design intent preserved for context.
- Agent-agnostic core and Overleaf integration kept as separate items
  (different goals, different consumers).

**`docs/getting-started.md` updated**: the lab `reverse-spec` example
replaced with the new `lab spec` auto-detect notebook-mode flow.
Pre-init manual file copy step removed (handled by `course init`).

**`README.md` updated**: command tables now match `SKILL.md` (added
missing commands: `/course-maker` (no-arg status), `/course-maker help`,
`/course-maker course plan`, `lab datasets`, `lab update`, `lab status`;
split into two tables: Lecture pipeline and Lab pipeline). Repository
layout now lists `course_conventions.md`, `slides_preamble.tex`,
`lab_templates.md`, and `labs/`. Roadmap aligned with `IMPROVEMENT_PLAN.md`.
"Examples" section honest about the empty stub state.

### Fixed

**Reference dispatchers reorganized** so that lab `spec` reflects the
auto-detection of plan vs notebook mode (no separate `reverse-spec`
command — the previous merge is now consistently documented).

---

## [2026-06-04] — Per-course preamble, hardened validate, slide numbering

### Added

**Per-course LaTeX preamble template** (`skill/templates/slides_preamble_pdflatex.tex`,
`slides_preamble_xelatex.tex`). The engine choice (pdflatex / xelatex /
lualatex) is asked during `course init`; the correct preamble template is
copied to `slides_preamble.tex` in the course root. Removes the hardcoded
engine assumption.

### Changed

**Slide numbering convention** (`skill/references/step1_plan.md`,
`skill/references/step4_slides.md`): title = slide 1, outline = slide 2,
first content slide = 3. Slide numbers are absolute and never restart.
Comments in `slides.tex` (e.g. `% Slide 07`) match `plan.md` exactly.

### Fixed

**`lab validate`: inline critical rules to prevent silent skips**
(`skill/SKILL.md`, `skill/references/lab_step3_validate.md`). Even when
`references/lab_step3_validate.md` is skipped (which happens under heavy
context), the inline `**CRITICAL rules — apply regardless of whether the
reference file was read:**` block enforces: never read `history.md` during
the student simulation; never open `tests.py`, `conftest.py`, or
`tests_template.py` until tasks are complete; download the dataset from
Block 0; run `nbconvert + pytest tests.py -v` and show full output.

---

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
