# Changelog

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
