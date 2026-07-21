# /course-maker quiz generate N — Step 2

Generate the canonical question bank `quizzes/NN/quiz_questions.md` from
`quiz_plan.md`. This file is **instructor-facing**: answers live inline. It is
the single source of truth and doubles as the answer key. `quiz publish` later
exports a student-facing version with answers stripped.

## Context to read first

1. `quizzes/NN/history.md` — past iterations, rejected questions.
2. `quizzes/NN/quiz_plan.md` — header, type legend, structure (blocks, types,
   counts, weights, M variants).
3. `course_conventions.md`, `AGENTS.md` → `## Course context` — the bank
   **content** is written in the course language; this reference file is English.
4. Taught lectures/seminars for the covered topics, to keep questions in scope.

## Output format: `quizzes/NN/quiz_questions.md`

Follow this structure (content in the course language):

```markdown
# <Quiz title>
## <Course name>

**<Program / level / time / weight / numeric precision — from quiz_plan.md>**

---

## Quiz structure
| Block | Topic | Questions | Weight each |
|-------|-------|-----------|-------------|
| 1 | <topic> | 3 | 8% |
| | **Total** | **N** | **100%** |

---

## Block 1 — <topic>

### Question 1.1 — Type T (<type name>), <weight>%
*<short subtitle: the specific concept>*   [optional: ⚠️ trick question]

**Variant A:** <question text>
- <option> ✓        ← correct option(s) marked with ✓
- <option>
- <option>

**Variant B:** <reworded / re-parametrized version>
- ...
```

(Variant labels above are illustrative Latin letters; write the actual labels as
the alphabet sequence of the course language.)

**Encoding answers inline, by type (per the plan's legend):**
- Single choice: list options; mark the one correct option with a trailing ` ✓`.
- Multiple choice: mark every correct option with ` ✓`.
- Calculation: state the problem, then a single answer line showing the working
  and the **bold** result with ` ✓`, e.g. `- σ = √(2/(128+64)) ≈ **0.102** ✓`.
  Include the formula in the question preamble when helpful.
- Open question: after the prompt, add `**Answer/criteria:** <key points and
  point allocation>` (translated) — this is the rubric for manual grading.

**Variants (M from the plan):** generate M alternative versions per question
(A, B, C, … in the course-language alphabet). For parametrized types, keep the
structure identical and vary only
the numbers/data; recompute each answer. For `M = 1`, emit a single variant.

## Chunked generation (mandatory)

A full bank is long (often 600+ lines) — generating it in one shot exceeds a
single generation/context budget and stalls the agent, exactly like slides.
Generate **one block per chunk**:
- Chunk 0 = title + header + the "Quiz structure" table.
- Chunk K = Block K (all its questions and all their variants).
- Append each chunk to `quiz_questions.md` immediately; do not pause between
  chunks. `quiz generate N next` reads the file, finds the last completed block,
  continues from there.

## Verification and state

After the last block: count questions and variants per block and confirm they
match `quiz_plan.md`. Report any mismatch. On approval, append an entry to
`quizzes/NN/history.md` and set `questions → ✅` in the `## Quizzes` section of
`COURSE_STATE.md`. Do not auto-advance to `quiz publish`.
