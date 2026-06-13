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
     course name, slug, language, audience, style preferences, **`Profile:`**.

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

### Phase 2a — Load user_defaults

The skill supports a user-level defaults file that pre-fills the content
questions across all of an instructor's courses (language, latex engine,
audience template, style template, instructor name).

Determine the path:
- If the environment variable `$COURSE_MAKER_HOME` is set → use
  `$COURSE_MAKER_HOME/defaults.yaml`.
- Otherwise → use `~/.course-maker/defaults.yaml`.

If the file exists, read it. Its values are used as **suggested defaults**
for the questions below. Empty strings mean "no default, ask fresh". If
the file does not exist, no defaults are pre-filled (every question is
asked fresh).

The format of `defaults.yaml` is documented in
`skill/profiles/README.md` § user_defaults.

### Phase 2b — Resolve profile (LMS adapter)

Before asking content questions, determine which LMS profile to use:

- If `CLAUDE.md` has `Profile:` filled → use that.
- Otherwise → ask: "Which LMS profile? (default: `local-zip`.
  Available profiles: list directory names under `skill/profiles/` —
  read each `<name>/README.md` first line for a one-sentence summary.)
  Press Enter for `local-zip`."
- Record the chosen profile; it will be written to `CLAUDE.md` in Phase 3.

The LMS-related defaults (`skill/profiles/<profile>/lms_defaults.yaml`)
are read by `lab course-init`, not here. Phase 2 only asks content
questions.

### Phase 2c — Collect missing info

Skip any question whose answer is already in `CLAUDE.md` (filled state).
Ask only what is needed to fill the missing pieces. Ask one question at
a time. Use user_defaults values as suggested defaults where available.

Questions (ask only if not already known):

1. Course name? *(no default — always asked)*
2. Slug (short identifier, e.g. `ml-systems`)? *(no default)*
3. Institution name (for title slide)? *(no user_default — per-course;
   if you teach at multiple institutions, this answer differs per course)*
4. Audience description — what students already know?
   *(default: `default_audience` from user_defaults)*
5. Style preference: strict/formal vs intuition-first?
   *(default: `default_style` from user_defaults)*
6. Language for slides and speaker notes?
   *(default: `default_language` from user_defaults)*
7. LaTeX engine for slide compilation? (`pdflatex` / `xelatex` / `lualatex`)
   *(default: `default_latex_engine` from user_defaults)*
   Note: xelatex and lualatex support Unicode fonts natively; pdflatex
   requires T2A/inputenc for Cyrillic.

### Phase 2d — Offer to save user_defaults

After all content questions are answered, if there are answers that look
reusable across courses (language, latex engine, audience, style,
instructor name), and they differ from the current user_defaults (or
user_defaults does not exist), ask:

> "Save these answers as your user_defaults for future courses? Future
> `course init` runs will pre-fill them. Press Enter to skip, or type a
> comma-separated list of fields to save (e.g.
> `language, latex_engine, instructor`)."

If the user provides fields:
- Resolve the target path (`$COURSE_MAKER_HOME/defaults.yaml` if the
  env var is set, otherwise `~/.course-maker/defaults.yaml`).
- Create the parent directory if missing.
- If `defaults.yaml` exists, merge: update only the requested fields,
  preserve others.
- If it does not exist, create it with all standard keys (empty if not
  requested) so the file is self-documenting.
- Confirm: "Saved {fields} to {path}."

---

## Phase 3 — Create missing files

For each file, act only if it is `missing` (skip if it already exists):

- **`CLAUDE.md`** — create from `skill/COURSE_CLAUDE_TEMPLATE.md` with all
  collected info embedded in the `## Course context` section, including
  `Profile: <name>` (default `local-zip`).
  If `placeholder` — fill in the placeholder fields, preserve everything else.
  Do NOT embed the skill content in `CLAUDE.md` — the skill is installed
  globally in `~/.claude/skills/course-maker/` and is discovered automatically.

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
