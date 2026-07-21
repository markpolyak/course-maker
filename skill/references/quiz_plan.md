# /course-maker quiz plan N — Step 1

Plan a quiz/exam before generating questions. Output is
`quizzes/NN/quiz_plan.md`, instructor-only. Like a lecture or lab plan: interactive,
iterate until approved, log decisions to `quizzes/NN/history.md`.

## Context to read first

1. `quizzes/NN/history.md` — past iterations for this quiz (read before anything).
2. `course_plan.md` — the quiz's row in the `## Sessions` table (Type `Quiz`) and
   any topic/weight notes; the `## Overview` for context.
3. `COURSE_STATE.md` — which lectures/seminars are already taught (so the quiz
   only covers delivered material). Suggest topics from completed sessions.
4. `AGENTS.md` → `## Course context` and `course_conventions.md` — language and
   terminology. The plan file is English (skill machinery); the quiz *content*
   (topics, later the questions) is in the course language.

## Dialog (one question at a time, wait for each answer)

Skip any question already answered in `course_plan.md` or `AGENTS.md`.

1. **Header metadata:** time limit, weight in the final grade, numeric-answer
   precision (e.g. 3 decimals), any global instructions.
2. **Blocks / topics:** the list of thematic blocks. Suggest blocks from taught
   lectures/seminars; let the instructor edit, merge, reorder.
3. **Per block — question types and counts.** The instructor defines the types
   (these are course-specific, e.g. "single choice", "multiple choice",
   "calculation", "open"). For each block ask: which types, how many of each,
   and the point weight per question. Record a **type legend** so `quiz generate`
   knows what each type means and how its answer is encoded.
4. **Variants per question (M).** Either:
   - a pool with `M = 1` (one version per question; the instructor picks which
     questions to give), or
   - `M > 1` parametrized variants per question (same structure, different
     numbers/data — the A/B/C… variants, with labels in the course language),
     for anti-cheating.
5. **Points / total.** Confirm the weights sum to 100% (or the chosen total).

## Output: `quizzes/NN/quiz_plan.md`

Write directly (do not dump the whole plan in chat first). Structure:

```markdown
# Quiz N — Plan

## Header
- Time: <min> · Weight: <%> · Numeric precision: <N decimals>
- Instructions: <global instructions>

## Question type legend
- Type 1 (<name>): <what it is; how the answer is encoded in the bank>
- Type 2 (<name>): ...

## Structure
| Block | Topic | Questions (by type) | Weight each | Variants (M) |
|-------|-------|---------------------|-------------|--------------|
| 1 | <topic> | 2× Type 1, 1× Type 3 | 8% | 5 |
| ... |
| | **Total** | **N questions** | **100%** | |
```

Keep block topics and the type-name column in the course language; keep the
table headers and field labels English.

## Protocol

Show a short human-readable summary, ask for confirmation, iterate on feedback.
On approval: save `quiz_plan.md`, append an entry to `quizzes/NN/history.md`, set
`plan → ✅` in the `## Quizzes` section of `COURSE_STATE.md` (create that section
with the standard columns if it does not exist yet). Do not auto-advance to
`quiz generate` — wait for the explicit command.
