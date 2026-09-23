# /course-maker lab defense N [next]

Prepare the instructor's question bank for the oral defense of lab N. At the
defense the instructor picks a question from the bank, asks it, judges the
answer against the criteria, and asks the follow-ups to probe deeper.

**Premise.** Students may use AI assistants to do the lab. A passing notebook
and green tests therefore say little about what the student knows. The defense
questions are what does: they check the theory behind the lab, the task and why
it is posed this way, the student's own solution, and the problem area the lab
belongs to. A question that a chatbot answers as well as a student who
understands the work does not do this job — see "Question design" below.

The bank is **instructor-only**: it holds the answer criteria and is never
handed to students. A shorter student-facing list for self-study is not part of
this command.

Reuses the quiz pipeline's answer encoding: every question carries an
`**Answer/criteria:**` block, as open questions do in
`references/quiz_generate.md`. There is no plan or publish step — the bank is
not an exam sheet, it is the instructor's material for a conversation.

---

## Prerequisites

- `<LAB_DIR>` resolved from the `COURSE_STATE.md` Labs table (see
  `references/repository_layout.md`).
- `notebook` is ✅ (or `starter/exercises.ipynb` exists) and `spec` is ✅. The
  bank is built from the tasks the student actually gets; without them, stop
  and name the missing step.
- Best run after `validate`: a validation solution gives concrete expected
  answers for the solution questions. Not a hard requirement.

## Context to read first

1. `<LAB_DIR>history.md` — past iterations, rejected questions, and the latest
   `Step 3: Validation` entry (tasks that caused difficulty are good defense
   material).
2. `<LAB_DIR>lab_spec.md` — tasks, expected outputs, points, learning goals.
3. `<LAB_DIR>starter/exercises.ipynb` — the tasks as the student sees them:
   wording, stubs, the goal line.
4. The validation solution, if `history.md` names a branch for it:
   `git show <branch>:<LAB_DIR>starter/exercises.ipynb`. Read-only; do not
   check the branch out.
5. `course_plan.md` — which lectures/seminars the lab relies on; then the
   `plan.md` (and, if present, `speaker_notes.md`) of those sessions. Theory
   questions stay within what was taught, using the course's own notation.
6. `AGENTS.md` → `## Course context` and `course_conventions.md` — language,
   audience, terminology, `Never Use`. The question content is in the course
   language; this reference and all structural labels stay English.
7. Existing `<LAB_DIR>defense_questions.md`, if any — extend or revise it
   rather than regenerate from scratch, unless the user asks to.

Validate-time isolation does not apply here: the lab is built, and this command
needs the spec and the solution to write answer criteria.

---

## Dialog (one question at a time)

Skip any question already answered in `AGENTS.md` → `## Lab context`,
`history.md`, or the command itself. Offer the default in each question so the
user can accept it with one word.

1. **Format and time.** Oral by default. Minutes per student (default 10) and
   how many main questions a student gets (default 5: 1 theory, 1 task,
   2 solution, 1 domain).
2. **Number of students.** How many students defend this lab (all groups
   together), and how many may get the same question (default 3). Together with
   the questions per student these set the bank size — see "Bank size".
3. **Hands-on questions.** May the instructor ask the student to change and
   re-run their code during the defense (student has the notebook open)?
   Default: yes, with changes that take at most 2–3 minutes.
4. **Grading.** How the defense outcome is recorded: pass/fail, points (how
   many), or a multiplier on the lab score. Default: pass/fail.

Record the answers in the bank header.

---

## Question design

### The four areas

Every bank covers all four. Default balance for a bank: about 20% theory, 20%
task, 40% solution, 20% domain. The solution area is the largest because it is
the hardest to answer without having done the work.

| Area | What it checks | Typical question forms |
|------|----------------|------------------------|
| **Theory** | the concepts the lab applies, as taught in the linked lectures | why a method works; what its assumptions are; what breaks when an assumption fails; how two taught concepts relate |
| **Task** | the problem the lab poses and its constraints | why the task is set up this way; what the data is and what its peculiarities imply; what the metric measures and what it hides; what makes the task hard |
| **Solution** | the student's own implementation and results | locate and explain; justify a choice; predict the effect of a change, then verify it; trace by hand on a tiny input; explain an output or plot |
| **Domain** | the problem area beyond this lab | where the method is used and where it is not; failure modes in practice; alternatives and when to choose them; what a practitioner would check next |

### What makes a question resistant to AI-assisted work

A student who delegated the lab to an assistant can often still recite
definitions and summarize the notebook. Prefer questions that require knowing
*this* solution and reasoning *live*:

- **Anchor to the student's artifact.** "In your task 3, show where … and
  explain why it is there", not "what is …?". The student must navigate their
  own code.
- **Predict, then verify.** Ask what will happen to a specific output if one
  thing changes; with hands-on allowed, have them change it and compare.
- **Counterfactuals.** "What if the data had …", "what if you removed …" — the
  answer is not written anywhere in the notebook.
- **Hand trace.** A tiny input (a few numbers) the student works through on
  paper or aloud, checking they know what the code computes.
- **Explain the evidence.** Point at a plot or number the student produced and
  ask why it looks the way it does, connecting it to the theory.
- **Justify, don't describe.** "Why this parameter value / this step order /
  this library call and not the obvious alternative?"

Avoid as main questions: bare definitions, "describe what your code does",
anything the notebook's own markdown already answers, and questions whose answer
is a single memorizable fact. A definition is acceptable only as a warm-up with
a follow-up that forces application.

### Follow-ups are mandatory

A prepared first answer can be memorized from an assistant's explanation; the
second level cannot. Every main question gets **1–2 follow-ups** that go one
step deeper along the student's answer (a "why", an edge case, a consequence).

### Levels

Tag each main question: `basic` (a student who did the work answers it
immediately), `core` (requires understanding, the default), `deep` (separates a
strong answer; use for a higher grade or to probe a doubtful answer).

### Answer criteria

Each question's `**Answer/criteria:**` gives:
- the key points of an acceptable answer — specific to this lab, using the
  course's notation, with the expected numbers where the validation solution
  gives them;
- **red flags** — answers that sound right but show the student does not
  understand: a generic textbook definition not connected to their code,
  describing what the code does line by line but not why, inability to find the
  relevant code, a prediction contradicted by their own output.

The criteria are for the instructor's judgement, not a script. Never phrase a
criterion or a red flag as an accusation of AI use: the defense measures
understanding, whatever produced the code.

### Scope

- Stay inside the lab and the sessions it relies on. A domain question may
  reach beyond the lectures, but must be answerable by a student who did the
  lab thoughtfully, without extra reading.
- Each main question is answerable orally in about 2–3 minutes. No lengthy
  derivations or computations.
- Numerical claims about datasets follow `references/lab_context.md` →
  Factual Claims: verified or not made.

---

## Output: `<LAB_DIR>defense_questions.md`

Write in the course language (headings and labels below are shown in English;
translate the content labels, keep the machine markers exactly):

```markdown
<!-- instructor-only: lab defense questions -->
# Lab N — Defense questions
## <Lab title>

**Format:** oral · <min> per student · <k> main questions · hands-on: yes/no
**Grading:** <pass/fail | points | multiplier>
**Bank:** <n> questions for <students> students, each given to at most <r>
**Set per student:** 1 theory · 1 task · 2 solution · 1 domain; pick
questions not yet asked in this session, take one variant per family, and add a
`deep` question when an answer is doubtful.

---

## Theory

### T1 — <short concept name> · core
*Relies on: <lecture/session>*

<question>

**Follow-ups:**
- <deeper question>
- <deeper question>

**Answer/criteria:** <key points>. Red flags: <…>.

---

## Task
### K1 — …

## Solution
### S1 — <task number / artifact> · core
*Anchor: task <n>, <function/cell/plot the student must find>*
*Hands-on:* <the change to make and what to compare>   ← only if allowed
...

## Domain
### D1 — …
```

### Bank size

The bank must be large enough that students defending one after another do not
all get the same questions — otherwise the questions are passed along the queue
and the defense checks memory of that, not understanding. Size each area from
the dialog answers:

```
questions in area ≥ ceil(students × drawn per student from area / max reuse)
```

Example: 30 students, 2 solution questions each, each question given to at most
3 students → at least 20 solution questions; 1 theory question each → at least
10 theory questions. Never fewer than 6 per area. State the computed sizes in
the summary before generating, and ask before going beyond about 80 questions in
total.

Reaching the size without padding:
- **Question families.** One idea, several variants that need different answers:
  the same "predict the effect" question for a different parameter, task, or
  plot; the same hand trace with different numbers. Number them `S3a`, `S3b`, …
  under one heading, like the parametrized variants of a quiz question
  (`references/quiz_generate.md`). A family counts as several questions only if
  each variant's answer differs; a reworded question is the same question.
- **Every task of the lab.** Spread solution questions over all tasks, not just
  the central one — each task gives several anchors (a function, a parameter, an
  output, a plot).
- Never pad with definitions or near-duplicates to reach the number. If the lab
  cannot support the computed size, say so and propose a smaller bank or a
  higher reuse limit.

### Chunked generation (mandatory)

A full bank is long (each question carries follow-ups and criteria), so it is
generated in chunks, like quiz blocks:
- Chunk 0 = the instructor-only marker, title, and header.
- Then the areas in order — Theory, Task, Solution, Domain — at most **8 main
  questions per chunk**; a larger area takes several chunks.

Append each chunk to the file immediately; do not pause between chunks. To
resume after an interruption (`/course-maker lab defense N next`), read the
file, find the last completed question, and continue from the next one.

---

## Placement and leak safety (CRITICAL)

- Write only to `<LAB_DIR>defense_questions.md`. NEVER write into
  `<LAB_DIR>starter/` — it is published to students via the LMS adapter, and a
  question file there hands out the answer criteria.
- The first line of the file is
  `<!-- instructor-only: lab defense questions -->`. `/course-maker site`
  never stages the file, and `scripts/site_guard.py check` blocks it by name
  and by this marker.
- After writing, verify the placement:
  ```bash
  git status --porcelain -- <LAB_DIR>starter/   # must list nothing new from this command
  ```

---

## Protocol and state

- After the last chunk, count main questions per area (family variants
  separately) and compare with the computed sizes; report totals, levels, and
  any shortfall. Show a brief human-readable summary and ask for approval;
  iterate on feedback (regenerate only the affected questions or area).
- On approval: append an entry to `<LAB_DIR>history.md` (step name
  `Defense questions`; record rejected questions and why, so they are not
  proposed again), and set `defense → ✅` in the Labs row of `COURSE_STATE.md`.
  If the Labs table has no `defense` column (a course created before this
  command existed), insert it after `published` with ❌ for the other labs.
- Do not auto-advance to anything else.
