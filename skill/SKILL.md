---
name: course-maker
description: >
  Pipeline for preparing lecture materials: detailed slide plans, visualizations,
  Python figure scripts, LaTeX/Beamer presentations, and speaker notes.
  Use this skill whenever the user works on lecture or course preparation,
  mentions commands like /lecture, /course, or asks to prepare slides, figures,
  speaker notes, or course plans. Also trigger when the user wants to update
  a course plan, check lecture status, or continue work on a lecture from a
  previous session.
---

# course-maker Skill

A structured workflow for preparing complete lecture materials from a course plan.
State is stored in Markdown files — no database needed, works with git.

## Quick reference: commands

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
  labs/                   ← future: lab assignments pipeline
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
