# Command: `/course-maker course init`

Scaffold a new course repository, or recover missing files in an existing one.

This command is **idempotent** — safe to re-run on an existing course. It detects
what is already in place and only creates or asks about what is missing.

---

## Phase 1 — Auto-detect existing state

Run these checks silently before asking anything:

1. **Check `CLAUDE.md`.**
   - `missing` — file does not exist.
   - `placeholder` — exists but contains strings like `[Course Name]`, `[course-slug]`,
     `[org-name]`.
   - `filled` — exists with real content. Read the following fields from it if present:
     course name, slug, language, audience, style preferences.

2. **Check `COURSE_STATE.md`.**
   - `missing` — file does not exist.
   - `exists` — do not overwrite.

3. **Check `course_conventions.md`.**
   - `missing` — file does not exist.
   - `exists` — do not overwrite unless the user explicitly asks to reset it.

4. **Check `slides_preamble.tex`.**
   - `missing` — file does not exist.
   - `exists` — do not overwrite.

5. **Check directory structure** (`lectures/`, `labs/`).
   - Note which directories already exist; create only the missing ones.

6. **Check `course_plan.md`.**
   - `exists` — do not overwrite; note that it is already present.
   - `missing` — will be handled in Phase 3 (deferred to `/course-maker course plan`).

---

## Phase 2 — Dialog: collect missing info

Skip any question whose answer is already in `CLAUDE.md` (filled state).
Ask only what is needed to fill the missing pieces. Ask one question at a time.

Questions (ask only if not already known):

1. Course name?
2. Slug (short identifier, e.g. `ml-systems`)?
3. Audience description — what students already know?
4. Style preference: strict/formal vs intuition-first?
5. Language for slides and speaker notes?
6. LaTeX engine for slide compilation? (`pdflatex` / `xelatex` / `lualatex`)
   Note: xelatex and lualatex support Unicode fonts natively; pdflatex requires
   T2A/inputenc for Cyrillic.

---

## Phase 3 — Create missing files

For each file, act only if it is `missing` (skip if it already exists):

- **`CLAUDE.md`** — create from `skill/COURSE_CLAUDE_TEMPLATE.md` with all collected
  info embedded; embed the skill content between `SKILL:START` and `SKILL:END`.
  If `placeholder` — fill in the placeholder fields, preserve everything else.

- **`course_conventions.md`** — determine template variant from the language answer:
  `ru` for Russian, `en` for English, `en` as default for unsupported languages.
  Copy `skill/templates/course_conventions_{lang}.md` → `course_conventions.md`.
  Confirm: "course_conventions.md created for {language}. Review and edit the
  terminology dictionary before starting labs."

- **`slides_preamble.tex`** — determine variant from the engine answer:
  `pdflatex` → `skill/templates/slides_preamble_pdflatex.tex`,
  `xelatex` or `lualatex` → `skill/templates/slides_preamble_xelatex.tex`.
  Default to `pdflatex` if not specified.
  Copy to `slides_preamble.tex` in the course root.
  Confirm: "slides_preamble.tex created for {engine}. Edit it to set your theme,
  colors, and title info before generating slides."

- **`COURSE_STATE.md`** — create empty state file (header + empty Lectures table).

- **Directory structure** — create only directories that do not exist yet
  (`lectures/`, `labs/`).

---

## Phase 4 — Summary

Print a compact summary:
- What already existed and was left untouched.
- What was created in this run.
- If `course_plan.md` is missing: "Run `/course-maker course plan` to create the
  course plan."
- Next step: run `/course-maker course status` to initialize the state table.
