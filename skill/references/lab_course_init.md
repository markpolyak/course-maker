# Command: `/course-maker lab course-init`

Setup wizard for the lab pipeline. Detects what is already in place and asks
only for what it cannot determine on its own. Do not ask questions whose answers
are already in the files.

---

## Phase 1 — Auto-detect existing state

Run these checks silently before asking anything:

1. **Scan `labs/` for existing lab directories.**
   A directory counts as an existing lab if it contains `starter/` or
   `history.md`. Record each found dir and its contents.

2. **Check `CLAUDE.md` for `## Lab context`.**
   - `missing` — section does not exist.
   - `placeholder` — contains strings like `[org-name]`, `[classroom-org]`, `[org]`.
   - `filled` — none of the above apply.

3. **Check `COURSE_STATE.md` for a `## Labs` table.**
   - `missing` — no such section.

4. **Check `skill/templates/conftest_base.py` for placeholder content.**
   It is a placeholder if it contains `# PLACEHOLDER` or `PLACEHOLDER — paste`.
   Also look for a real `conftest.py` in any existing lab's `starter/`.

5. **Check `skill/templates/tests.yaml` similarly.**
   Also look for a real `tests.yaml` in any existing lab's `starter/.github/workflows/`.

---

## Phase 2 — Populate shared templates

Create `labs/shared/` if it does not exist.

For each of the three files (`tests_template.py`, `conftest_base.py`, `tests.yaml`):

- **If** the skill template is a placeholder **AND** a real file exists in an
  existing lab's `starter/` (or `starter/.github/workflows/` for tests.yaml):
  → Copy the real file to `labs/shared/` directly. Do not use the placeholder.
  → Tell the user: "Found real `<file>` in `<source path>` — using it."

- **Else if** the skill template is not a placeholder:
  → Copy it to `labs/shared/`.

- **Else** (placeholder and no real file found):
  → Create the placeholder in `labs/shared/` and tell the user:
  "Could not find a real `<file>`. Placeholder written to `labs/shared/<file>` —
  replace it before running `/course-maker lab tests N`."

### Phase 2a — Substitute course-specific labels into `conftest_base.py`

After `labs/shared/conftest_base.py` exists, populate the customizable labels
at the top of the file from `lab_templates.md` (if it already exists from a
prior `course init`):

- Read `lab_templates.md` § "Scoring header" → set `SCORING_HEADER`.
- Read `lab_templates.md` § "TASKID label" → set `TASKID_LABEL`.
- Read `lab_templates.md` § "Grade output label" → set `GRADE_OUTPUT_LABEL`.

If `lab_templates.md` does not exist yet (Phase 5 will create it), leave the
defaults in place. Re-run `/course-maker lab course-init` after Phase 5 to
substitute the labels.

This ensures every per-lab conftest.py copied from `labs/shared/` inherits the
course-language grade-output strings without per-lab editing.

---

## Phase 3 — Dialog: CLAUDE.md `## Lab context`

Skip this phase if the section is already `filled`.

If `missing` or `placeholder`, announce:
"Filling in `## Lab context` in `CLAUDE.md`. I'll ask one question at a time."

### Phase 3a — Load profile questions

Read `CLAUDE.md` → `## Course context` → `Profile:` field. Default:
`local-zip`.

Read `skill/profiles/<profile>/lab_questions.yaml`. Each entry describes
one LMS-config question:

```yaml
- id: <key>            # written to CLAUDE.md under ## Lab context
  prompt: "<text>"     # shown to the user verbatim
  default: ""          # may reference lms_defaults.yaml values via ${name}
  required: true|false
  per_lab: true|false  # true → ask once per existing lab
```

Also read `skill/profiles/<profile>/lms_defaults.yaml` — used to resolve
`${name}` references inside `default` fields.

### Phase 3b — Ask the profile's questions

For each entry in `lab_questions.yaml`:

- If `per_lab: false`: ask once.
- If `per_lab: true`: ask once per existing lab found in Phase 1.
  Substitute `{N}` and `{dir}` into the prompt from the lab's row.
  For each lab where `labs/{dir}/starter/.git` exists, run
  `git -C labs/{dir}/starter remote get-url origin` and offer the result
  as the default.
- Resolve `${ghc_repo_naming}` and similar references in `default` against
  `lms_defaults.yaml`.
- If `default` is non-empty, show as `"<prompt> (default: <value>)"`.
  Press Enter accepts; typing replaces.
- If `required: true` and the user provides an empty value, repeat the
  question.

If the user runs this command to also set up a new lab, additionally ask:

- "Title and slug for the next lab? (e.g. `2, lab2-arima`)"

### Phase 3c — Write `## Lab context`

Write the collected answers into `CLAUDE.md` → `## Lab context`. Field
names come from the `id` of each `lab_questions.yaml` entry. For per-lab
questions, write a table: one row per lab, one column per per-lab field
(e.g. `starter_repo_url`).

The actual publish workflow lives in `<course-root>/lms_adapter.md` (copied
in Phase 5a). The `## Lab context` section in `CLAUDE.md` holds only the
identifiers that workflow looks up at publish time.

---

## Phase 4 — Dialog: COURSE_STATE.md Labs table

Skip this phase if the table already exists.

If missing, announce: "Creating Labs table in `COURSE_STATE.md`."

For each existing lab found in Phase 1:

- Extract what can be read from files:
  - `dir` — the directory name
  - Title — from the first cell of `starter/exercises.ipynb` if it exists, else ask
  - Status columns:
    - if `lab_spec.md` exists → spec ✅
    - if `tests.py` exists → tests ✅
    - if `history.md` has "Validation" entry → validated ✅
    - etc.
  - For columns that cannot be inferred, set ❌ and note what was assumed.
- Ask only: "Lab {N} ({dir}): I inferred {summary}. Does that look right?"
  Allow the user to correct individual columns.

Then write the Labs table into `COURSE_STATE.md`.

---

## Phase 5 — Copy lab templates

Read `CLAUDE.md` → `## Course context` → Language field.
Determine the template variant: `ru` for Russian, `en` for English,
or `en` as default if the language is unsupported.

Copy `skill/templates/lab_templates_{lang}.md` → `lab_templates.md` in the
course root.
Confirm: "lab_templates.md created for {language}. Review the self-check cell
and scoring strings before generating notebooks."

---

## Phase 5a — Install the LMS adapter

Read `CLAUDE.md` → `## Course context` → `Profile:` field. Default:
`local-zip`.

If `<course-root>/lms_adapter.md` does not exist (or the user explicitly
asks to refresh it):

1. Verify `skill/profiles/<profile>/lms.md` exists. If not, fall back to
   `skill/profiles/local-zip/lms.md` and warn the user that the chosen
   profile is missing the adapter.
2. Copy `skill/profiles/<profile>/lms.md` → `<course-root>/lms_adapter.md`.
3. Confirm: "lms_adapter.md installed from profile `<profile>`. This is
   the workflow `/course-maker lab publish` will follow. Edit it if your
   setup differs from the profile defaults."

If `<course-root>/lms_adapter.md` already exists, do not overwrite it
without explicit user confirmation — they may have customized it.

---

## Phase 6 — Summary

Print a compact summary:
- What was auto-detected and filled without questions
- What was filled based on dialog answers
- What remains as placeholders (if any) and what to do about them
- "Done. Run `/course-maker lab init N <url> [slug]` to scaffold the next lab."
