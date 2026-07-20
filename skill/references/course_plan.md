# Command: `/course-maker course plan`

Create, fill, or update `course_plan.md`. Safe to re-run — detects the current
state and picks up where you left off.

---

## Phase 1 — Detect state

Check `course_plan.md`:
- **Missing** → go to Phase 2 (creation).
- **Partial** — file exists but has `<!-- TODO -->` sections → go to Phase 3
  (fill missing).
- **Complete** — file exists with no TODO sections → show a one-line summary of
  sessions and ask: "Would you like to change anything?" If yes → Phase 4 (update).
  If no → done.

---

## Phase 2 — Create `course_plan.md`

Ask the user to choose (one message):

> "`course_plan.md` not found. How would you like to proceed?
> [1] I have an existing plan file — provide the path or paste the content
> [2] I know my sessions and topics — let's structure them together
> [3] Help me figure out what to cover"

---

### Option [1] — Import existing plan

Accept either a file path or pasted content. Read it fully, then extract:

- Session list: types (lecture, seminar, lab, quiz, homework, other), titles,
  week/order
- Per-lecture topics (bullet lists, numbered lists, or prose)
- Lab assignments mentioned
- Course-level prerequisites (prior disciplines)
- Grading/scoring breakdown
- Self-study materials
- Instructor info

Create a draft `course_plan.md` in the structured format (see below). Where
information was not found, insert `<!-- TODO -->`. Show the draft and ask:
> "Here's what I extracted. What should I correct or add?"

Iterate until the user approves. Save the original file as `course_plan_source.*`
(preserve extension). Write approved draft to `course_plan.md`.

---

### Options [2] and [3] — Dialog creation

Both options use the same dialog. The difference: [2] assumes the user has
content ready; [3] means the agent will propose based on subject knowledge after
collecting the basics. Ask one question at a time, wait for each answer:

1. *(skip if known from CLAUDE.md)* "What is this course about?"
2. "What should students be able to do after completing this course?
   One or two concrete outcomes."
3. "What types of sessions does the course have?
   (e.g. lectures only / lectures + seminars / lectures + labs / all types)"
4. "How many of each type? How many weeks total?"
5. "Standard session duration? (or different per type — specify)"
6. *(option [2])* "List your session titles, one per line. You can add a few
   topics after each title separated by a dash. Skip types you haven't planned yet."
   *(option [3])* the agent generates a full proposed outline using knowledge of
   typical university curricula for this subject and audience. Show it, ask:
   "What would you change?" — iterate until approved. Be explicit this is based
   on general knowledge; the professor's judgment takes precedence.
7. "Any course-level prerequisites — prior disciplines students must have
   completed? Or is this professional development / open to all? (press Enter
   to skip)"
8. "Grading breakdown — point weights for each session type?
   (press Enter to skip — can fill later)"
9. "Self-study materials — textbooks, papers, online resources?
   (press Enter to skip — can fill later)"
10. "Instructor name(s) and contact info?
    (press Enter to skip — can fill later)"

After collecting answers, generate a draft `course_plan.md`, show it, iterate, save.

---

## Phase 3 — Fill missing sections

Show a list of TODO sections found in the existing `course_plan.md`.
For each missing section, offer to fill it now or skip.
Fill approved sections through focused dialog (1–3 questions per section).
Save after each section approved.

---

## Phase 4 — Update existing plan

1. Ask: "What needs to change?" — accept free-form description.
2. Propose the specific edits to make, wait for approval.
3. Apply approved edits to `course_plan.md`.
4. Cross-check with `COURSE_STATE.md` — **only for structural/content changes**
   (Sessions table rows, Lectures subsections, topic lists). Skip cascade for
   metadata-only changes (grading weights, instructor info, prerequisites,
   self-study):
   - For every lecture whose Sessions row, Lectures subsection, or topic list
     changed: mark `plan`, `visuals`, `figures`, `slides`, `notes` as ⚠️ in
     `COURSE_STATE.md`.
   - For every lab whose Sessions row changed: mark all lab columns as ⚠️.
   - Append a note to each affected `history.md`.
5. Report: what was changed, which materials are now marked ⚠️ and need review.
   If no structural changes — report what was updated, no ⚠️ flags.

---

## `course_plan.md` format

```markdown
# Course Plan — {Course Name}

## Overview

**Weeks:** {N}  **Lectures:** {N}  **Seminars:** {N}  **Labs:** {N}
**Quizzes:** {N}  **Standard duration:** {time} min

## Sessions

| # | Week | Type | Title / Topic | Notes |
|---|------|------|---------------|-------|
| 1 | 1 | Lecture | Introduction to HMMs | |
| 2 | 1 | Seminar | Practice: HMM basics | no pipeline |
| 3 | 2 | Lecture | Forward algorithm | |
| 4 | 2 | Lab | Lab 1 — HMM from scratch | |
| 5 | 4 | Quiz | Midterm | quizzes/01/ |
| 6 | 5 | Homework | HW 1 — Viterbi | no pipeline |

## Lectures

### Lecture 1 — Introduction to HMMs

**Topics:**
- Motivation and applications
- Formal definition: states, observations, parameters
- Comparison with Markov chains

**Estimated time:** 90 min
**Prerequisites within course:** none
**Announce-only sections:** continuous HMMs (covered in Lecture 5)

### Lecture 2 — Forward algorithm
...

## Labs

### Lab 1 — HMM from scratch
*(managed by `/course-maker lab` pipeline — see `labs/lab1/`)*

## Prerequisites

<!-- TODO: list prior disciplines or note "no formal prerequisites" -->

## Grading

<!-- TODO: e.g. Labs 40% · Midterm 20% · Final 30% · Homework 10% -->

## Self-study Materials

<!-- TODO: textbooks, papers, online resources -->

## Instructors

<!-- TODO: name, email, office hours -->
```

**Rules for the Sessions table:**
- Every session of every type appears in the table — even those without a pipeline.
- Sessions without a skill pipeline are marked `no pipeline` in Notes.
- Labs managed by the lab pipeline are marked with the lab directory in Notes
  (e.g. `labs/lab1/`); quizzes managed by the quiz pipeline likewise (e.g.
  `quizzes/01/`).
- Row order = chronological order of sessions.

**Rules for the Lectures section:**
- One subsection per lecture session from the Sessions table.
- `Prerequisites within course` — which earlier lectures must be completed first.
- `Announce-only sections` — topics mentioned briefly but not taught fully in
  this lecture.

**Rules for the Labs section:**
- One subsection per lab session; content is a one-line pointer to the lab
  directory.
- Full lab content lives in `labs/labN/` and is managed by the lab pipeline.
