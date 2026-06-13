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

Ask in sequence (stop and wait for each answer before asking the next):

1. "GitHub org where starter repos live?"
2. "GitHub Classroom org? (press Enter if same as GitHub org)"
   If blank — use GitHub org value.
3. "GHC repo naming pattern? (e.g. `sp2026-lab{N}-{slug}` or `lab{N}-{slug}-{student}`)"
4. For each existing lab found in Phase 1:
   "Starter repo URL for lab {N} (dir: `{dir}`)?"
   If the existing lab's `starter/` has its own `.git`, suggest reading the
   remote URL: run `git -C labs/{dir}/starter remote get-url origin` and show
   the result as the default.
5. "Title and slug for the next lab? (e.g. `2, lab2-arima`)" — only if the user
   ran this command to set up a new lab, not just to initialise an existing course.

Then write the complete `## Lab context` section into `CLAUDE.md`.

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

## Phase 6 — Summary

Print a compact summary:
- What was auto-detected and filled without questions
- What was filled based on dialog answers
- What remains as placeholders (if any) and what to do about them
- "Done. Run `/course-maker lab init N <url> [slug]` to scaffold the next lab."
