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

4. **Read the grade-reporting config from `CLAUDE.md` → `## Lab context`
   → `### Lab grading`.**
   - `grade_reporter` — default `none`.
   - `lab_variants` — default `false`.
   `conftest_base.py` ships as a real, universal harness (no placeholder); it
   needs no per-course substitution. Any grade output is supplied by an
   optional reporter (Phase 2a), not by editing the conftest.

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

### Phase 2a — Install the grade reporter (optional)

The universal `conftest_base.py` prints no grade output on its own. Any
scoring / grade-output is supplied by an optional reporter dropped next to the
conftest as `grade_report.py` (see `skill/extensions/reporters/README.md`).

Read `grade_reporter` from `CLAUDE.md` → `## Lab context` → `### Lab grading`
(default `none`):

- **`none`** → do nothing. Labs run plain pytest (pass/fail only).
- **`<name>`** (e.g. `scoring_ci`):
  1. Copy `skill/extensions/reporters/<name>.py` → `labs/shared/grade_report.py`.
  2. Substitute the labels at the top of `grade_report.py`. Resolve each label
     by precedence — **user_defaults → lab_templates.md → reporter default**:
     - `SCORING_HEADER` ← `default_scoring_header` (user_defaults), else
       `lab_templates.md` § "Scoring header", else leave the reporter default.
     - `TASKID_LABEL` ← `default_taskid_label`, else § "TASKID label", else default.
     - `GRADE_OUTPUT_LABEL` ← `default_grade_output_label`, else § "Grade output
       label", else default.

     Read user_defaults from `$COURSE_MAKER_HOME/defaults.yaml` (fallback
     `~/.course-maker/defaults.yaml`); use a field only when it is non-empty.
     This keeps an instructor's autograder phrase in their personal config
     rather than in the shared course-language templates. If neither
     user_defaults nor `lab_templates.md` provides a value (e.g. `lab_templates.md`
     is created later in Phase 5), leave the reporter default and re-run this
     command after Phase 5.
  3. If `<name>.py` is missing, warn: "grade_reporter `<name>` not found in
     skill/extensions/reporters/ — labs will run plain pytest."

This way the course-language grade strings live in the reporter, not in the
universal conftest, and every per-lab `grade_report.py` copied from
`labs/shared/` inherits them without per-lab editing.

`lab_variants` (default `false`) is read by `/course-maker lab notebook N` and
`lab tests N`: when `true`, Block 0 includes the variant cells from
`skill/extensions/variants/block0_snippet.md` and the reporter's `DATASETS`
list is populated; when `false`, neither is present.

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
