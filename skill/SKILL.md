---
name: course-maker
description: >
  Pipeline for preparing university course materials: lecture slides, visualizations,
  Python figure scripts, LaTeX/Beamer presentations, speaker notes, and lab assignments.
  Use this skill whenever the user works on lecture or lab preparation,
  mentions commands like /lecture, /lab, /course, or asks to prepare slides, figures,
  speaker notes, course plans, lab notebooks, tests, or grading infrastructure.
  Also trigger when the user wants to update a course plan, check lecture/lab status,
  or continue work on a lecture or lab from a previous session.
---

# course-maker Skill

A structured workflow for preparing complete lecture materials from a course plan.
State is stored in Markdown files — no database needed, works with git.

## Quick reference: commands

**Lecture commands:**

| Command | What it does |
|---|---|
| `/course init` | Scaffold a new course repository |
| `/course status` | Show status of all lectures/labs |
| `/course update` | Update course_plan.md and flag affected lectures |
| `/lecture plan N` | Step 1 — detailed slide-by-slide plan for lecture N |
| `/lecture visuals N` | Step 2 — list of visualizations, TikZ feasibility |
| `/lecture figures N` | Step 3 — Python script to generate PNG figures |
| `/lecture slides N` | Step 4 — LaTeX/Beamer, chunk 0 (preamble + title) |
| `/lecture slides N next` | Step 4 — next block of 5 slides |
| `/lecture notes N` | Step 5 — speaker notes, chunk 0 (slides 1–5) |
| `/lecture notes N next` | Step 5 — next block of 5 slides |
| `/lecture status N` | Show state + history summary for lecture N |

**Lab commands:**

| Command | Description |
|---|---|
| `/lab course-init` | Create labs/shared/, copy base templates |
| `/lab init N <url> [slug]` | Scaffold lab N; dir = labs/slug/ or labs/labN/ |
| `/lab plan N` | Step 1a — interactive planning until approved |
| `/lab notebook N` | Step 1b — generate exercises.ipynb |
| `/lab spec N` | Step 1b — generate lab_spec.md |
| `/lab datasets N` | Step 1b — generate datasets_info.md (optional) |
| `/lab tests N` | Step 2 — tests.py, conftest.py, requirements.txt, README |
| `/lab validate N <id>` | Step 3 — validate as student (new session recommended) |
| `/lab publish N` | Push to starter repo + sync GHC via gh API |
| `/lab update N` | Re-publish after post-release fix |
| `/lab reverse-spec N` | Generate lab_spec.md from existing notebook |
| `/lab status N` | Status + last 3 history entries |

When the user types one of these commands, read this skill and execute the
corresponding workflow below. Always read `COURSE_STATE.md` and the relevant
`lectures/NN/history.md` before starting any step.

---

## Repository layout

```
<course-root>/
  CLAUDE.md               ← this skill + course-specific context
  course_plan.md          ← master course plan (source of truth)
  COURSE_STATE.md         ← status table for all lectures/labs
  lectures/
    01/
      plan.md             ← detailed slide plan (Step 1 output)
      visuals.md          ← visualization list (Step 2 output)
      figures/
        figures.py        ← figure generation script (Step 3 output)
        fig01_name.png    ← generated figures
        ...
      slides.tex          ← Beamer presentation (Step 4 output)
      speaker_notes.md    ← speaker text (Step 5 output)
      history.md          ← decision log for this lecture
    02/
      ...
  labs/
    shared/
      tests_template.py   ← style reference for Stage 2 (never edit)
      conftest_base.py    ← base conftest, copied per-lab then scoring updated
      tests.yaml          ← GitHub Actions CI (never modify)
    lab1/
      lab_spec.md         ← Stage 1 output, instructor-only (not in starter repo)
      history.md          ← decision log, same role as lectures/NN/history.md
      starter/            ← git subtree → public starter repo (GitHub Classroom template)
        exercises.ipynb
        conftest.py
        tests.py
        requirements.txt
        README.md
        datasets_info.md  ← if needed
        .github/workflows/tests.yaml
    lab2/
      ...
  seminars/               ← future: seminar materials
```

---

## State files

### COURSE_STATE.md

Maintain this file after every command that changes state.
Format:

```markdown
# Course State

**Course:** <name>
**Last updated:** YYYY-MM-DD

## Lectures

| # | Title | plan | visuals | figures | slides | notes | Updated |
|---|-------|------|---------|---------|--------|-------|---------|
| 01 | ... | ✅ | ✅ | ✅ | 🔄 | ❌ | 2024-03-15 |
| 02 | ... | ✅ | ❌ | ❌ | ❌ | ❌ | 2024-03-10 |

## Labs

| # | Dir | Title | plan | notebook | spec | tests | validated | published | Updated |
|---|-----|-------|------|----------|------|-------|-----------|-----------|---------|
| 01 | lab1-backprop | Backpropagation | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — |

Legend: ✅ done · 🔄 in progress · ❌ not started · ⚠️ needs review
```

Mark a step ⚠️ (needs review) when:
- `course_plan.md` was updated and this lecture's content may be affected
- the user manually edited a file without going through the pipeline

### history.md

Every `lectures/NN/history.md` is the memory of that lecture.
**Always read it before starting any step for that lecture.**
It prevents re-proposing ideas the user already rejected.

Append to history after each completed step or meaningful iteration.
Format:

```markdown
# Lecture N — History

## [YYYY-MM-DD] Step 1: Plan — iteration 1
**Result:** plan.md created
**User feedback:** "Too much time on section 3, compress to 1 slide"
**Decision:** Merged slides 8–10 into one overview slide

## [YYYY-MM-DD] Step 1: Plan — iteration 2
**Result:** plan.md updated
**User feedback:** Approved

## [YYYY-MM-DD] Manual edit
**What changed:** User rewrote slide 5 description directly in plan.md
**Detected via:** git diff at start of Step 2
```

---

## Workflows

### `/course init`

1. Ask for: course name, slug, audience description, style preference
   (strict/formal vs intuition-first), language for slide labels.
2. Scaffold the directory structure above.
3. Create `CLAUDE.md` with this skill embedded + a `## Course context` section
   filled with the provided info. The course context section is what makes
   prompts precise — it should include:
   - Audience background (what they already know)
   - Preferred balance: rigor vs intuition
   - Language of slides and speaker notes
   - Any recurring style rules (e.g. "always give intuition before formula")
4. Create empty `COURSE_STATE.md`.
5. Tell the user: copy their `course_plan.md` into the root, then run
   `/course status` to initialize the state table.

---

### `/course update`

Run this when the user has edited `course_plan.md` or wants to.

1. If the user wants Claude to make changes: propose the edit, wait for approval,
   then apply to `course_plan.md`.
2. If the user edited manually: run `git diff course_plan.md` to detect changes.
3. Compare changed sections against `COURSE_STATE.md`. For any lecture whose
   source section in the plan changed:
   - Mark `plan`, `visuals`, `figures`, `slides`, `notes` as ⚠️ if they exist.
   - Append a note to that lecture's `history.md`.
4. Update `COURSE_STATE.md`.
5. Report: which lectures are now marked ⚠️ and why.

---

### `/lecture plan N`  (Step 1)

**Goal:** produce `lectures/NN/plan.md` — a numbered list of slides with
content descriptions, timing, and a timing table at the end.

**Before writing anything:**
1. Read `course_plan.md` section for lecture N.
2. Read `lectures/NN/history.md` if it exists — note any rejected structures
   or decisions already made.
3. Read `## Course context` from `CLAUDE.md`.

**Then produce the plan.** See `references/step1_plan.md` for the full prompt
template, constraints, and output format.

After the user approves:
- Save to `lectures/NN/plan.md`
- Append to `history.md`
- Update `COURSE_STATE.md` (plan → ✅)

---

### `/lecture visuals N`  (Step 2)

**Goal:** produce `lectures/NN/visuals.md` — a table of all visualizations
with TikZ feasibility assessment.

**Before writing anything:**
1. Read `lectures/NN/plan.md`.
2. Read `lectures/NN/history.md`.

**Then produce the list.** See `references/step2_visuals.md` for format and
TikZ feasibility criteria.

After approval:
- Save to `lectures/NN/visuals.md`
- Append to `history.md`
- Update `COURSE_STATE.md` (visuals → ✅)

---

### `/lecture figures N`  (Step 3)

**Goal:** produce `lectures/NN/figures/figures.py` — a single script that
generates all non-TikZ figures as PNG files.

**Before writing anything:**
1. Read `lectures/NN/visuals.md` — extract rows where TikZ = "no" or "hard".
2. Read `lectures/NN/history.md`.

**Then write the script.** See `references/step3_figures.md` for coding
standards, style rules, and file naming conventions.

After approval:
- Save to `lectures/NN/figures/figures.py`
- Append to `history.md`
- Update `COURSE_STATE.md` (figures → ✅ or 🔄 if user is still iterating)

---

### `/lecture slides N`  (Step 4)

**Goal:** produce `lectures/NN/slides.tex` — a compilable LaTeX/Beamer file.

**Output is always chunked — never generate the entire file at once.**
A 20-slide Beamer file is ~600–900 lines. Generating it in one shot causes
timeouts. Always split into preamble + blocks of 5 slides.

**Before writing anything:**
1. Read `lectures/NN/plan.md` — count total slides, note slide titles.
2. Read `lectures/NN/visuals.md`.
3. List files in `lectures/NN/figures/` — use only PNG files that exist.
4. Read `lectures/NN/history.md` — note any layout issues from prior iterations.
5. Read `references/step4_slides.md` — Beamer template and anti-overfull rules.

**Chunked generation protocol:**

**Chunk 0 — Preamble + title slide (always first):**
Generate and show to user:
```latex
\documentclass[...]{beamer}
% packages, colors, title info
\begin{document}
\begin{frame}\titlepage\end{frame}
\begin{frame}{План лекции}\tableofcontents\end{frame}
```
Wait for approval. Then create `lectures/NN/slides.tex` with this content.

**Chunk K — slides [5K-4 … 5K] (K = 1, 2, …):**
Generate 5 slides, show to user. After approval, **append** to `slides.tex`.
Tell the user: "Chunk K/M done. Type `/lecture slides N next` to continue,
or give feedback to revise this chunk first."

**Chunk last — closing slide + `\end{document}`:**
Generate final summary slide + `\end{document}`. Append after approval.

**Resuming after a break:**
If the user runs `/lecture slides N next` and `slides.tex` already exists,
read the file to find the last completed slide number, then continue from there.

**Revising a specific chunk:**
If the user says "fix slide 7", identify which chunk it belongs to,
regenerate only that chunk, show diff, append corrected version after approval.

After all chunks are done:
- Append to `history.md`
- Update `COURSE_STATE.md` (slides → ✅)

See `references/step4_slides.md` for Beamer template, layout rules, and
anti-overfull checklist. Read it before writing Chunk 0.

---

### `/lecture notes N`  (Step 5)

**Goal:** produce `lectures/NN/speaker_notes.md` — live spoken text, not a
summary. The lecturer reads/adapts this aloud.

**Output is always chunked — never generate the entire file at once.**
Speaker notes for a 20-slide lecture run to ~2000–3000 words. Generate in
blocks of 5 slides to avoid timeouts.

**Before writing anything:**
1. Read `lectures/NN/plan.md` — slide list, timing.
2. Read `lectures/NN/slides.tex` if it exists — match slide order exactly.
3. Read `lectures/NN/history.md`.
4. Read `## Course context` from `CLAUDE.md` — tone, audience, language.
5. Read `references/step5_notes.md` — format and tone rules.

**Chunked generation protocol:**

**Chunk 0 — Header + slides 1–5:**
Generate and show to user:
```markdown
# Лекция N — Текст для лектора
**Общее время:** 85–90 мин
---
## Слайд 1 — [Title]
...
## Слайд 5 — [Title]
...
```
Wait for approval. Create `lectures/NN/speaker_notes.md` with this content.

**Chunk K — slides [5K-4 … min(5K, total)] (K = 1, 2, …):**
Generate 5 slides of notes, show to user. After approval, **append** to
`speaker_notes.md`. Tell the user: "Chunk K/M done. Type
`/lecture notes N next` to continue, or give feedback to revise this chunk."

**Chunk last — timing table + cut candidates:**
Generate the timing table and "что можно сократить" section from
`references/step5_notes.md`. Append after approval.

**Resuming after a break:**
If the user runs `/lecture notes N next` and `speaker_notes.md` already exists,
read the file to find the last completed slide, then continue from there.

After all chunks are done:
- Append to `history.md`
- Update `COURSE_STATE.md` (notes → ✅)

---

### `/lecture status N`

Print:
1. Row from `COURSE_STATE.md` for lecture N.
2. Last 3 entries from `lectures/NN/history.md`.
3. Any ⚠️ warnings with explanation.

---

## Lab Workflows

### `/lab course-init`

This command is a setup wizard. It detects what is already in place and asks only for
what it cannot determine on its own. Do not ask questions whose answers are already in the files.

#### Phase 1 — Auto-detect existing state

Run these checks silently before asking anything:

1. **Scan `labs/` for existing lab directories.**
   A directory counts as an existing lab if it contains `starter/` or `history.md`.
   Record each found dir and its contents.

2. **Check `CLAUDE.md` for `## Lab context`.**
   The section is "missing" if it does not exist.
   It is "placeholder" if it contains strings like `[org-name]`, `[classroom-org]`, `[org]`.
   It is "filled" if none of the above apply.

3. **Check `COURSE_STATE.md` for a `## Labs` table.**
   It is "missing" if there is no such section.

4. **Check `skill/templates/conftest_base.py` for placeholder content.**
   It is a placeholder if it contains `# PLACEHOLDER` or `PLACEHOLDER — paste`.
   Also look for a real `conftest.py` in any existing lab's `starter/`.

5. **Check `skill/templates/tests.yaml` similarly.**
   Also look for a real `tests.yaml` in any existing lab's `starter/.github/workflows/`.

#### Phase 2 — Populate shared templates

Create `labs/shared/` if it does not exist.

For each of the three files (`tests_template.py`, `conftest_base.py`, `tests.yaml`):
- If the skill template is a placeholder AND a real file exists in an existing lab's `starter/`
  (or `starter/.github/workflows/` for tests.yaml):
  → Copy the real file to `labs/shared/` directly. Do not use the placeholder.
  → Tell the user: "Found real `<file>` in `<source path>` — using it."
- Else if the skill template is not a placeholder:
  → Copy it to `labs/shared/`.
- Else (placeholder and no real file found):
  → Create the placeholder in `labs/shared/` and tell the user:
  "Could not find a real `<file>`. Placeholder written to `labs/shared/<file>` —
  replace it before running `/lab tests N`."

#### Phase 3 — Dialog: CLAUDE.md `## Lab context`

Skip this phase if the section is already "filled".

If "missing" or "placeholder", announce:
"Filling in `## Lab context` in `CLAUDE.md`. I'll ask one question at a time."

Ask in sequence (stop and wait for each answer before asking the next):

1. "GitHub org where starter repos live?"
2. "GitHub Classroom org? (press Enter if same as GitHub org)"
   If blank — use GitHub org value.
3. "GHC repo naming pattern? (e.g. `sp2026-lab{N}-{slug}` or `lab{N}-{slug}-{student}`)"
4. For each existing lab found in Phase 1:
   "Starter repo URL for lab {N} (dir: `{dir}`)?"
   If the existing lab's `starter/` has its own `.git`, suggest reading the remote URL:
   run `git -C labs/{dir}/starter remote get-url origin` and show the result as the default.
5. "Title and slug for the next lab? (e.g. `2, lab2-arima`)" — only if the user ran
   this command to set up a new lab, not just to initialise an existing course.

Then write the complete `## Lab context` section into `CLAUDE.md`.

#### Phase 4 — Dialog: COURSE_STATE.md Labs table

Skip this phase if the table already exists.

If missing, announce: "Creating Labs table in `COURSE_STATE.md`."

For each existing lab found in Phase 1:
- Extract what can be read from files:
  - `dir` — the directory name
  - Title — from the first cell of `starter/exercises.ipynb` if it exists, else ask
  - Status columns — if `lab_spec.md` exists → spec ✅; if `tests.py` exists → tests ✅;
    if `history.md` has "Validation" entry → validated ✅; etc. For columns that cannot
    be inferred, set ❌ and note what was assumed.
- Ask only: "Lab {N} ({dir}): I inferred {summary}. Does that look right?"
  Allow the user to correct individual columns.

Then write the Labs table into `COURSE_STATE.md`.

#### Phase 5 — Summary

Print a compact summary:
- What was auto-detected and filled without questions
- What was filled based on dialog answers
- What remains as placeholders (if any) and what to do about them
- "Done. Run `/lab init N <url> [slug]` to scaffold the next lab."

---

### `/lab init N <url> [slug]`

`slug` is optional. If provided, the lab directory is `labs/<slug>/`.
If omitted, the directory is `labs/labN/` (e.g. `labs/lab1/`).

Example: `/lab init 1 https://github.com/org/lab1-backprop lab1-backprop`

Let `LAB_DIR = labs/<slug>/` if slug given, else `labs/labN/`.

1. Create `<LAB_DIR>` directory.
2. Create `<LAB_DIR>history.md`:
   ```markdown
   # Lab N — History

   (no entries yet)
   ```
3. Create empty `<LAB_DIR>lab_spec.md` placeholder:
   ```markdown
   # Lab N Spec — placeholder
   # Run /lab spec N to generate this file.
   ```
4. Add starter repo as git subtree:
   ```bash
   git subtree add --prefix=<LAB_DIR>starter <url> main --squash
   ```
5. Copy CI file:
   ```bash
   mkdir -p <LAB_DIR>starter/.github/workflows
   cp labs/shared/tests.yaml <LAB_DIR>starter/.github/workflows/tests.yaml
   ```
6. Copy base conftest:
   ```bash
   cp labs/shared/conftest_base.py <LAB_DIR>starter/conftest.py
   ```
7. Add lab N row to `COURSE_STATE.md` Labs table (fill `Dir` = `<slug or labN>`, all status columns ❌).
8. Commit:
   ```bash
   git add -A && git commit -m "lab N: init starter subtree"
   ```

---

### Resolving lab directory

**Every `/lab N` command starts with this step:**

Read `COURSE_STATE.md` Labs table, find the row where `#` = N, read the `Dir` column.
That value is `LAB_DIR` — use it as `labs/<Dir>/` for all file operations in this command.

Example: if row for lab 1 has `Dir = lab1-backprop`, then `LAB_DIR = labs/lab1-backprop/`.
If the `Dir` column is absent or empty, fall back to `labs/labN/`.

---

### `/lab plan N`  (Step 1a)

**Goal:** iterative planning conversation → approved plan logged in `<LAB_DIR>history.md`.

Read: `references/lab_step1a_plan.md` for the full prompt, requirements, and format.

Input files: `course_plan.md` (lab N section), `<LAB_DIR>history.md`, `CLAUDE.md` (Lab context).
Output: iterative planning conversation → approved plan.
State: update `<LAB_DIR>history.md`, `COURSE_STATE.md` plan → ✅ after approval.

---

### `/lab notebook N`  (Step 1b-1)

**Goal:** produce `<LAB_DIR>starter/exercises.ipynb`.

Read: `references/lab_step1b_notebook.md` before writing anything.

Input files: `<LAB_DIR>history.md` (approved plan), `course_plan.md`.
State: update `<LAB_DIR>history.md`, `COURSE_STATE.md` notebook → ✅.

---

### `/lab spec N`  (Step 1b-2)

**Goal:** produce `<LAB_DIR>lab_spec.md` — the contract between Stage 1 and Stage 2.
This file is NOT published to students.

Read: `references/lab_step1b_spec.md` before writing anything.

Input files: `<LAB_DIR>starter/exercises.ipynb`, `<LAB_DIR>history.md`.
State: update `<LAB_DIR>history.md`, `COURSE_STATE.md` spec → ✅.

---

### `/lab datasets N`  (Step 1b-3, optional)

**Goal:** produce `<LAB_DIR>starter/datasets_info.md` — student reference for datasets.

Read: `references/lab_step1b_datasets.md`.

Input files: `<LAB_DIR>lab_spec.md`, `<LAB_DIR>starter/exercises.ipynb`.
State: update `<LAB_DIR>history.md`.

---

### `/lab tests N`  (Step 2)

**Goal:** produce `tests.py`, `conftest.py`, `requirements.txt`, `README.md` in `<LAB_DIR>starter/`.

Read: `references/lab_step2_tests.md` before writing anything.

Input files: `<LAB_DIR>lab_spec.md`, `<LAB_DIR>starter/exercises.ipynb`,
`labs/shared/conftest_base.py`, `labs/shared/tests_template.py`.
State: update `<LAB_DIR>history.md`, `COURSE_STATE.md` tests → ✅.
Commit:
```bash
git add <LAB_DIR>starter/
git commit -m "lab N: add tests and conftest"
```

---

### `/lab validate N <student_id>`  (Step 3)

Read: `references/lab_step3_validate.md`.

Show the isolation warning first. Recommend running in a new Claude Code session.
If proceeding: simulate student solving `<LAB_DIR>starter/exercises.ipynb` for `Student_ID = <student_id>`.
State: update `<LAB_DIR>history.md`, `COURSE_STATE.md` validated → ✅ or ⚠️.

---

### `/lab publish N`

Read `CLAUDE.md` → `## Lab context` to get GHC org and repo naming.

**Step 1 — push to starter repo (git subtree):**
```bash
# Get url from CLAUDE.md Lab context → Starter repos table for lab N
git subtree push --prefix=<LAB_DIR>starter <url> main
```

**Step 2 — sync GHC repo via gh API:**
Read `CLAUDE.md` to find GHC repo name for lab N.
For each student-facing file in `<LAB_DIR>starter/`:
`exercises.ipynb`, `conftest.py`, `tests.py`, `requirements.txt`,
`README.md`, `datasets_info.md` (if exists), `.github/workflows/tests.yaml`

Run for each file:
```bash
SHA=$(gh api repos/$GHC_REPO/contents/$FILE --jq '.sha // empty' 2>/dev/null)
CONTENT=$(base64 < <LAB_DIR>starter/$FILE)
if [ -n "$SHA" ]; then
  gh api repos/$GHC_REPO/contents/$FILE --method PUT \
    --field message="sync: lab N update" \
    --field content="$CONTENT" \
    --field sha="$SHA"
else
  gh api repos/$GHC_REPO/contents/$FILE --method PUT \
    --field message="sync: lab N initial publish" \
    --field content="$CONTENT"
fi
```

Note: `lab_spec.md` and `history.md` are explicitly NOT in the sync list.

**Step 3 — update course repo:**
```bash
git add <LAB_DIR>
git commit -m "lab N: publish"
git push
```

**Step 4 — update state:**
- Update `COURSE_STATE.md`: published → ✅
- Append to `<LAB_DIR>history.md`:
  ```markdown
  ## [YYYY-MM-DD] Published

  **Starter repo:** <url>
  **GHC repo:** <ghc_repo>
  **Files synced:** exercises.ipynb, conftest.py, tests.py, requirements.txt, README.md, ...
  ```

---

### `/lab update N`

Use when a lab needs to be updated AFTER publishing (fix tests, fix notebook).

1. Make needed changes in `<LAB_DIR>starter/`.
2. Run `/lab validate N <student_id>` to verify fix doesn't break correct solutions.
3. Run `/lab publish N` to sync changes.
4. Append to `<LAB_DIR>history.md`:
   ```markdown
   ## [YYYY-MM-DD] Post-publish update

   **Changed:** <files>
   **Reason:** <why update was needed>
   **Validated:** Student_ID=<N>
   ```
5. Update `COURSE_STATE.md`: set validated → 🔄 if re-validation needed.

---

### `/lab reverse-spec N`

Use when you have an existing `exercises.ipynb` but no `lab_spec.md`.
Generates the spec from the notebook. Pipeline continues with `/lab tests N`.

Read: `references/lab_reverse_spec.md`.

Input files: `<LAB_DIR>starter/exercises.ipynb`, `<LAB_DIR>history.md` (if exists).
Output: `<LAB_DIR>lab_spec.md` + deviations report.
State: update `<LAB_DIR>history.md`, `COURSE_STATE.md` spec → ✅.

---

### `/lab status N`

Print:
1. Row from `COURSE_STATE.md` Labs table for lab N (including `Dir`).
2. Last 3 entries from `<LAB_DIR>history.md`.
3. Any ⚠️ warnings with explanation.

---

## General rules

- **Never skip reading `history.md`** before starting a step. If it doesn't
  exist yet, create it when writing the first output.
- **Peer review on every output.** Present the result, wait for explicit
  approval or feedback before saving to the file and updating state.
- **Detect manual edits.** At the start of Steps 2–5, check if the prerequisite
  file was manually edited since the last pipeline run (via git diff or
  by asking). If yes, log it in `history.md` before proceeding.
- **One step at a time.** Don't auto-advance to the next step after approval.
  Wait for the user to issue the next command.
- **COURSE_STATE.md is always up to date.** Update it at the end of every
  command, even if the step is only partially done.
