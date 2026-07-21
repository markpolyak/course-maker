---
name: course-maker
description: >
  Pipeline for preparing university course materials: lecture slides, visualizations,
  Python figure scripts, LaTeX/Beamer presentations, speaker notes, and lab assignments.
  Use this skill whenever the user works on lecture or lab preparation,
  mentions commands like /lecture, /seminar, /lab, /course, /quiz, or asks to prepare slides, figures,
  speaker notes, course plans, lab notebooks, quizzes/exams, or grading infrastructure.
  Also trigger when the user wants to update a course plan, check lecture/lab status,
  or continue work on a lecture or lab from a previous session.
---

# course-maker Skill

A structured workflow for preparing complete lecture materials from a course plan.
State is stored in Markdown files — no database needed, works with git.

Each command has a thin dispatcher below that names the reference file with the
full workflow. **Always read the named reference file before executing the
workflow.** Repository layout and state file formats: `references/repository_layout.md`.

---

## Inviolable rules

These rules apply to every command in this skill, regardless of which reference
file you did or did not read. Violating any of them is a hard error.

### Observability

- **In the first chat message of every step, list which `references/*.md` files
  you read and which top-level sections of each you consulted.** Silent skips
  are not allowed — if you proceed without reading the named reference, say so
  explicitly.

### Grading invariants (lab)

- When a lab uses per-student variants (`lab_variants: true`), the variant
  formula is a verbatim invariant wherever it appears (Block 0 and the grade
  reporter) — see `extensions/variants/README.md`. With
  `lab_variants: false` there is no such formula.
- When a lab uses a grade reporter (`grade_reporter` not `none`), keep its
  grade-output `print()` layout fixed — an external CI may grep it. Only the
  labels (course/language) and the numerator (bonus) change. See
  `extensions/reporters/README.md`.
- NEVER give students `quizzes/NN/quiz_questions.md` — it holds answers. Before
  marking a quiz `published`, verify the exported student file has no answer
  markers (`grep` for `✓`/answer lines returns nothing).

### Validation isolation (lab)

- During `/course-maker lab validate`: NEVER read `lab_spec.md`, `tests.py`,
  `conftest.py`, `tests_template.py`, or `history.md` until all student tasks
  are complete. The simulation must reflect what a real student sees.
- NEVER start `lab validate` if `<LAB_DIR>starter/` has uncommitted changes —
  the notebook will be modified during validation and the clean version will be
  lost. Stop and ask the user to commit first.
- NEVER skip the fresh-context prompt before `lab validate`. The current session
  contains `lab_spec.md` and `tests.py` from prior steps; without a clean context
  the simulation is invalid. (Claude Code: `/clear`; Codex CLI / Cursor: a new
  chat/session.)

### Slides & figures

- NEVER reference PNG files in `slides.tex` that do not exist in `figures/`.
  List the directory before generating slides.
- NEVER mark `figures → ✅` without running `figures.py` and verifying that the
  expected PNG files were created.
- NEVER add forward references to later slides. At most one mention of the next
  lecture, only on the closing slide, only if it flows naturally.
- Output for `slides`, `notes`, `quiz generate`, and `seminar practice` is ALWAYS
  chunked (blocks of 5 slides, or one quiz block / notebook section per chunk).
  Never generate the entire file in one shot — a full file exceeds a single
  generation/context budget and stalls the agent.

### Process

- The **course-context file is `AGENTS.md`** (course name, audience, style,
  language, `Profile:`, `Slides format:`, `## Lab context`, recurring rules).
  Codex CLI and Cursor read it directly; Claude Code loads it via the
  `@AGENTS.md` import in `CLAUDE.md`, which otherwise holds only Claude Code-only
  overrides.
- NEVER overwrite existing files in init wizards (`course init`,
  `lab course-init`). They are idempotent by design.
- NEVER auto-advance to the next step after the user approves the current one —
  wait for the next explicit command.
- NEVER suggest short-form commands (`/lecture …`, `/lab …`); always the full
  form `/course-maker …`.
- NEVER cite numerical dataset characteristics (size, sampling rate, value
  range, number of classes) without verification via web search.
- ALWAYS read `lectures/NN/history.md` (or `<LAB_DIR>history.md`) before
  starting any step for that lecture/lab. It is the memory of past iterations
  and prevents re-proposing rejected ideas.
- ALWAYS update `COURSE_STATE.md` at the end of every command, even if the
  step is only partially done.
- ALWAYS present output for review and wait for explicit approval before
  saving to the file and updating state.
- ALWAYS check `git diff` on the prerequisite file at the start of a subsequent
  step. If the user manually edited it, log the edit in `history.md` before
  proceeding.
- ALWAYS read `AGENTS.md` → `## Course context` → `Profile:` field at the
  start of `course init`, `lab course-init`, and `lab publish`. Default
  profile is `local-zip` if the field is absent. The profile is the LMS
  adapter only; instructor preferences come from
  `$COURSE_MAKER_HOME/defaults.yaml` (fallback `~/.course-maker/defaults.yaml`).

---

## Quick reference: commands

**Lecture commands:**

| Command | What it does |
|---|---|
| `/course-maker` | Show project status (all lectures + labs) |
| `/course-maker help` | Show this command reference |
| `/course-maker course init` | Scaffold a new course repository |
| `/course-maker course plan` | Create, fill, or update course_plan.md (interactive) |
| `/course-maker course status` | Show status of all lectures/labs |
| `/course-maker course update` | Detect manual plan changes, flag affected lectures |
| `/course-maker doctor` | Check course for state drift, missing files, config gaps (read-only) |
| `/course-maker stats` | Show course progress bars (lectures/labs complete, hours) |
| `/course-maker syllabus [pdf\|latex\|docx]` | Generate/update student syllabus.md from course_plan.md; optional export |
| `/course-maker plan N` | Step 1 — detailed slide-by-slide plan for lecture N |
| `/course-maker visuals N` | Step 2 — list of visualizations, TikZ feasibility |
| `/course-maker figures N` | Step 3 — Python script to generate PNG figures |
| `/course-maker slides N [format]` | Step 4 — deck chunk 0 (beamer→slides.tex / slidev→slides.md); format from AGENTS.md or arg |
| `/course-maker slides N next` | Step 4 — next block of 5 slides (format detected from the existing file) |
| `/course-maker slides N export [pdf\|png]` | Export the existing deck to a file (beamer→PDF, slidev→pdf/png) |
| `/course-maker notes N` | Step 5 — speaker notes, chunk 0 (slides 1–5) |
| `/course-maker notes N next` | Step 5 — next block of 5 slides |
| `/course-maker status N` | Show state + history summary for lecture N |

**Seminar commands** (seminar = lecture deck + practical part, in seminars/NN/):

| Command | Description |
|---|---|
| `/course-maker seminar plan\|visuals\|figures\|slides\|notes N` | Deck steps — reuse lecture step references, target seminars/NN/ |
| `/course-maker seminar practice N` | Practical live code-demo notebook (practice.ipynb) |
| `/course-maker seminar status N` | Status + last 3 history entries for seminar N |

**Lab commands:**

| Command | Description |
|---|---|
| `/course-maker lab course-init` | Create labs/shared/, copy base templates |
| `/course-maker lab init N <url> [slug]` | Scaffold lab N; dir = labs/slug/ or labs/labN/ |
| `/course-maker lab plan N` | Step 1a — interactive planning until approved |
| `/course-maker lab notebook N` | Step 1b — generate exercises.ipynb |
| `/course-maker lab spec N` | Step 1b — generate lab_spec.md (auto plan/notebook mode) |
| `/course-maker lab datasets N` | Step 1b — generate datasets_info.md (optional) |
| `/course-maker lab tests N` | Step 2 — tests.py, requirements.txt, README (+ grade_report.py if a reporter is used) |
| `/course-maker lab validate N <id>` | Step 3 — validate as student (new session required) |
| `/course-maker lab triage N` | After a ⚠️ validation: diagnose which step to revisit (read-only) |
| `/course-maker lab publish N` | Run the LMS publish workflow from `lms_adapter.md` |
| `/course-maker lab update N` | Re-publish after post-release fix |
| `/course-maker lab status N` | Status + last 3 history entries |

**Quiz commands** (quizzes / tests / exams):

| Command | Description |
|---|---|
| `/course-maker quiz plan N` | Step 1 — interactive quiz plan (blocks, types, variants) |
| `/course-maker quiz generate N [next]` | Step 2 — generate question bank (chunked by block) |
| `/course-maker quiz publish N [format]` | Step 3 — export student-facing version (markdown) |

**Homework commands** (manually graded take-home assignment; brief + rubric, no autograding):

| Command | Description |
|---|---|
| `/course-maker homework plan N [dir]` | Step 1 — interactive brief + rubric; dir default homework/NN/ (may nest, e.g. seminars/<name>/homework/) |
| `/course-maker homework publish N [format]` | Step 2 — assemble student handout; markdown default, pdf/latex/docx via pandoc |
| `/course-maker homework status N` | Status + last 3 history entries |

**If invoked with no arguments** (`/course-maker` alone): read `COURSE_STATE.md`
and print a summary of all lectures, seminars, labs, quizzes, and homework with their
current step statuses (✅ / 🔄 / ❌ / ⚠️). End with: "Run `/course-maker help` for
available commands."

**`/course-maker help`**: print the five command tables (Lecture, Seminar, Lab,
Quiz, Homework) into the chat — the user cannot see `SKILL.md` — then stop.

---

## Lecture workflows

### `/course-maker course init`
Read: `references/course_init.md`.

### `/course-maker course plan`
Read: `references/course_plan.md`.

### `/course-maker course update`
Read: `references/course_update.md`.

### `/course-maker doctor`
Read: `references/doctor.md`. Read-only: runs `scripts/validate_state.py` for the
facts layer, adds semantic checks (plan TODOs, profile/adapter consistency,
generated config files), and reports each finding with the command that fixes
it. Never edits files.

### `/course-maker stats`
Read: `references/stats.md`. Read-only: progress bars across pipelines from
`course_plan.md` (planned totals) and `COURSE_STATE.md` (completion).

### `/course-maker syllabus [pdf|latex|docx]`
Read: `references/syllabus.md`. Generates/updates student-facing `syllabus.md`
from `course_plan.md`; with a format arg, exports it via pandoc. No state row.

### `/course-maker plan N` (Step 1)
Read: `references/step1_plan.md`.

### `/course-maker visuals N` (Step 2)
Read: `references/step2_visuals.md`.

### `/course-maker figures N` (Step 3)
Read: `references/step3_figures.md`.

**CRITICAL — even if reference was skipped:**
- After saving `figures.py`, run it: `cd lectures/NN && python figures/figures.py`.
- If the script fails: show the error, fix, re-save, re-run until clean.
- After a clean run: verify expected PNGs in `lectures/NN/figures/`; list them.
- Mark `figures → ✅` ONLY after a clean run with PNGs verified. Otherwise → 🔄.

### `/course-maker slides N [format]` (Step 4)
Resolve the slide format, then read the matching reference:
- `beamer` → `references/step4_slides.md` (produces `slides.tex`).
- `slidev` → `references/step4_slides_slidev.md` (produces `slides.md`).

Format resolution: an explicit `format` arg (`beamer`|`slidev`) wins; else the
`Slides format:` field in `AGENTS.md` → `## Course context` (default `beamer`).
When resuming (`slides N next`), ignore the field and detect from the existing
file: `slides.tex` → beamer, `slides.md` → slidev. (`pptx` is not implemented;
if requested, say so and stop.)

**CRITICAL — even if reference was skipped:**
- Output is ALWAYS chunked, for either format. A full deck is 600–900 lines;
  one-shot generation exceeds a single generation/context budget and stalls the agent.
- Chunk 0 = preamble/headmatter + title. Chunk K (K≥1) = slides [5K-4 … 5K].
  Chunk last = closing slide (beamer also appends `\end{document}`).
- Append each chunk to the deck file (`slides.tex` or `slides.md`) immediately;
  do not pause between chunks.
- Use the course's preamble verbatim: `slides_preamble.tex` (beamer) or
  `slides_headmatter.md` (slidev). If missing, stop and tell the user to run
  `/course-maker course init`.
- Only reference PNG files that actually exist in `lectures/NN/figures/`.
- If any PNG is older than `figures.py`, warn that figures may be stale and
  offer to re-run `/course-maker figures N` first. Warning, not a hard block.

**Resuming:** `/course-maker slides N next` reads the existing deck file, finds
the last completed slide, continues from there (auto-chains remaining chunks).

**Revising:** "fix slide 7" → identify which chunk it belongs to, regenerate
only that chunk, show diff, append corrected version after approval.

### `/course-maker slides N export [pdf|png]`
Read: `references/slides_export.md`. Mechanical export of the existing deck — no
approval, no state change. Detect the deck format from the file present
(`slides.tex` → beamer PDF, `slides.md` → slidev pdf/png). If the export tool (a
LaTeX engine, or Node for Slidev) is missing, say how to install it — never fail
silently. Presenting a Slidev deck live (`npx slidev`) is the user's job; never
launch it.

### `/course-maker notes N` (Step 5)
Read: `references/step5_notes.md`.

**CRITICAL — even if reference was skipped:**
- Output is ALWAYS chunked, same protocol as slides.
- Chunk 0 = header + slides 1–5. Chunk K = slides [5K-4 … min(5K, total)].
  Chunk last = timing table + cut candidates.
- Append each chunk to `speaker_notes.md` immediately; do not pause between chunks (no per-chunk approval — auto-chain to the end).
- Generate in the course language (from `AGENTS.md` → Course context).

**Resuming:** `/course-maker notes N next` reads the file, continues from the
last completed slide (auto-chains remaining chunks).

### `/course-maker status N`

Print: row from `COURSE_STATE.md` for lecture N, last 3 entries from
`lectures/NN/history.md`, any ⚠️ warnings with explanation.

---

## Seminar workflows

A seminar = a lecture deck + a practical part, in `seminars/NN/`.

### `/course-maker seminar plan|visuals|figures|slides|notes N`
Use the matching lecture step reference (`step1_plan.md` … `step5_notes.md`),
applied to `seminars/NN/`. For `slides`, resolve the format exactly as the
lecture slides dispatcher does (beamer → `step4_slides.md`, slidev →
`step4_slides_slidev.md`). All lecture CRITICAL rules apply with paths under
`seminars/NN/` (chunking for slides/notes; run `figures.py` before figures ✅).

### `/course-maker seminar practice N`
Read: `references/seminar_practice.md`.
**CRITICAL — even if reference was skipped:** generate `practice.ipynb` chunked
by section; it is runnable code — execute it top to bottom and fix until clean
before marking `practice → ✅`; it is a demo (no conftest/tests).

### `/course-maker seminar status N`
Like `/course-maker status N` but for the `## Seminars` row and `seminars/NN/`.

---

## Lab workflows

### `/course-maker lab course-init`
Read: `references/lab_course_init.md`.

### `/course-maker lab init N <url> [slug]`
Read: `references/lab_init.md`.

### `/course-maker lab plan N` (Step 1a)
Read: `references/lab_context.md` AND `references/lab_step1a_plan.md`.

### `/course-maker lab notebook N` (Step 1b-1)
Read: `references/lab_context.md` AND `references/lab_step1b_notebook.md`.

### `/course-maker lab spec N` (Step 1b-2)
Read: `references/lab_context.md` AND `references/lab_step1b_spec.md`.

**Auto-detection:** if `<LAB_DIR>history.md` contains an approved plan → plan
mode. Otherwise → notebook mode (deviations report appended to the spec file).

**Protocol:** write the file directly (never dump YAML in chat), then show a
brief human-readable summary and ask the user for confirmation. Update state
only after approval.

### `/course-maker lab datasets N` (Step 1b-3, optional)
Read: `references/lab_context.md` AND `references/lab_step1b_datasets.md`.

### `/course-maker lab tests N` (Step 2)
Read: `references/lab_context.md` AND `references/lab_step2_tests.md`.

After saving:
```bash
git add <LAB_DIR>starter/
git commit -m "lab N: add tests and conftest"
```

### `/course-maker lab validate N <student_id>`
Read: `references/lab_step3_validate.md`.

**CRITICAL — see also Inviolable rules above. Highlights:**
- Show the isolation warning, stop, wait for the user to confirm a fresh
  session/context (Claude Code: `/clear`; Codex CLI / Cursor: a new chat/session).
- Check `git status <LAB_DIR>starter/`; stop with commit-first message if dirty.
- Do NOT read `history.md`, `lab_spec.md`, `tests.py`, `conftest.py`, or
  `tests_template.py` until all student tasks are complete.
- Download the dataset from the source in Block 0; never invent or skip data.
- After all tasks: `jupyter nbconvert --to python exercises.ipynb && pytest tests.py -v`;
  show full output.
- After validation: ask whether to save the solution to a branch, then
  `git restore <LAB_DIR>starter/exercises.ipynb` to remove student solutions.

### `/course-maker lab triage N`
Read: `references/lab_triage.md`. Read-only diagnostic after a ⚠️ validation; maps each issue from the latest Step 3 `history.md` entry to its root-cause step and names the command to run next. Edits nothing; reading `lab_spec.md`/`tests.py`/notebook is allowed (validation is done).

### `/course-maker lab publish N`
Read: `references/lab_publish.md`.

### `/course-maker lab update N`
Read: `references/lab_update.md`.

### `/course-maker lab status N`

Print: row from `COURSE_STATE.md` Labs table for lab N (including `Dir`),
last 3 entries from `<LAB_DIR>history.md`, any ⚠️ warnings.

---

## Quiz workflows

A quiz/test/exam pipeline. The bank `quizzes/NN/quiz_questions.md` holds questions
with answers inline (it is also the key); `quiz publish` exports a student copy
with answers stripped. Artifacts in `quizzes/NN/`; state in the `## Quizzes` section.
See also the Inviolable rules on chunking and answer-leak.

### `/course-maker quiz plan N` (Step 1)
Read: `references/quiz_plan.md`.

### `/course-maker quiz generate N` (Step 2)
Read: `references/quiz_generate.md`. Chunked one block per chunk; resume with
`/course-maker quiz generate N next`.

### `/course-maker quiz publish N [format]` (Step 3)
Read: `references/quiz_publish.md`. Only `markdown` is implemented for now.

---

## Homework workflows

A homework is a manually graded take-home assignment: a task brief plus an
instructor-only grading rubric. No `starter/`, autograder, CI, or `validate` —
that is what a lab is for. Artifacts live in `HW_DIR` (default `homework/NN/`,
resolved from the `## Homework` table's `Dir` column, which is a full path from
the course root and may nest under a seminar); state in the `## Homework`
section. Needs `course init` only — not `lab course-init`.

### `/course-maker homework plan N [dir]` (Step 1)
Read: `references/lab_context.md` AND `references/homework.md`. Writes `task.md`
+ `rubric.md`. Ask once whether the rubric goes into the student handout and
record it, so `publish` need not re-ask.

### `/course-maker homework publish N [format]` (Step 2)
Read: `references/homework.md`. Assembles `homework_student.md` (task + rubric
only if opted in at plan time); markdown default, pdf/latex/docx via pandoc.

**CRITICAL — even if reference was skipped:** when the rubric is NOT opted into
the handout, after writing `homework_student.md` verify no instructor-only
content leaked (`grep -nE "<!-- instructor|<!-- rubric_in_handout"` prints
nothing, and the rubric text is absent). Fix and re-check until clean.

### `/course-maker homework status N`
Print: row from `COURSE_STATE.md` `## Homework` for homework N (incl. `Dir`),
last 3 entries from `HW_DIR/history.md`, any ⚠️ warnings.
