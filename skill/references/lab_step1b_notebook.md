# Lab Step 1b-1 — Notebook Generation

Read `references/lab_context.md` before starting.

---

## Context to Read Before Generating

1. Read `labs/labN/history.md` — find the approved plan (last Step 1a entry).
   The plan must be approved before this step.
2. Read `course_plan.md` section for lab N — course name, lab title.
3. Read `course_conventions.md` from the course root — language rules and terminology dictionary.
4. Read `lab_templates.md` from the course root — notebook header, Block 0 template,
   self-check cell, task formatting, scoring strings.

---

## Prompt to Execute

Generate `labs/labN/starter/exercises.ipynb`.

**Requirements:**

1. Strictly follow the approved plan — no new tasks, no changed points, interfaces, or
   variable names without explicit user approval.

2. Notebook structure — verbatim per the template in `lab_templates.md`:
   - First two markdown cells: header with instructions + Block 0 divider
   - Block 0: setup / dependency install. When `lab_variants: true` (see
     `AGENTS.md` → `## Lab context` → `### Lab grading`), Block 0 also includes
     the variant-selection cells from `skill/extensions/variants/block0_snippet.md`
     — the variant formula there is verbatim, never change it. When
     `lab_variants: false`, Block 0 has no variant cells.
   - Main blocks with tasks
   - Last two cells: markdown checklist + self-check code with `required_vars` and `bonus_vars`

3. Task formatting — per `lab_templates.md`:
   - Functions: docstring in course language (format from lab_templates.md), type annotations,
     TODO comment per lab_templates.md, `raise NotImplementedError`
   - Variables: description comment, TODO per lab_templates.md, type annotation, stub `= None`
   - Classes: docstring (format from lab_templates.md), empty methods with TODO per lab_templates.md,
     `raise NotImplementedError`

4. Each task is preceded by a markdown cell with:
   - Title — use task title format from lab_templates.md
   - Task description for the student — clear and concise; length determined by complexity,
     not a fixed sentence count; use LaTeX formulas where needed
   - Hints if needed — use hint format from lab_templates.md

5. Template code in task cells — structure only, not solution:
   - Allowed: function signature with docstring, variable stubs with type annotations,
     empty class methods
   - Not allowed: commented-out code that solves the task; step-by-step instructions
     inside code; any code the student just needs to "uncomment"
   - If the task is complex and scaffolding helps — show structure (step names in comments),
     not implementation

6. Terminology and language — per `course_conventions.md`: use course-language terms;
   English only for library names and abbreviations.

7. All numerical dataset characteristics (size, frequency, value range) — verified only.
   If unsure — use web search and cite the source in a cell comment.

---

## Notebook Template

The complete template (Block 0 cells and final cells) is defined in `lab_templates.md`
in the course root. Follow it precisely.

Key invariants:
- When `lab_variants: true`, the variant formula MUST be verbatim — see
  `skill/extensions/variants/README.md`.
- Self-check cell MUST follow the exact print format from the template
- Block 0 has ZERO points

---

## After Saving

Append to `labs/labN/history.md`:
```markdown
## [YYYY-MM-DD] Step 1b-1: Notebook generated

**File:** labs/labN/starter/exercises.ipynb
**Blocks:** <list of blocks and their titles>
**Variables count:** <number of required_vars>
**Notes:** <any deviations from plan, if any>
```

Update `COURSE_STATE.md` Labs table: set `notebook` column for lab N to ✅.
