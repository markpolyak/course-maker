# Lab Step 1b-1 — Notebook Generation

Read `references/lab_context.md` before starting.

---

## Context to Read Before Generating

1. Read `labs/labN/history.md` — find the approved plan (last Step 1a entry).
   The plan must be approved before this step.
2. Read `course_plan.md` section for lab N — course name, lab title.

---

## Prompt to Execute

Generate `labs/labN/starter/exercises.ipynb`.

**Requirements:**

1. Strictly follow the approved plan — no new tasks, no changed points, interfaces, or
   variable names without explicit user approval.

2. Notebook structure — verbatim per the template in `references/lab_context.md`:
   - First two markdown cells: header with instructions + Block 0 divider
   - Block 0: tasks 0.1, 0.2, 0.3 per template; variant formula
     `dataset_id = (Student_ID - 1) % len(datasets)` — verbatim, never change
   - Main blocks with tasks
   - Last two cells: markdown checklist + self-check code with `required_vars` and `bonus_vars`

3. Task formatting — per `references/lab_context.md`:
   - Functions: Russian docstring, type annotations, `# TODO: ваш код`, `raise NotImplementedError`
   - Variables: description comment, `# TODO:`, type annotation, stub `= None`
   - Classes: docstring, empty methods with `# TODO: ваш код`, `raise NotImplementedError`

4. Each task is preceded by a markdown cell with:
   - Title (`### Задание N.M — Название`)
   - Task description for the student — clear and concise; length determined by complexity,
     not a fixed sentence count; use LaTeX formulas where needed
   - Hints if needed (formatted as `> 💡 **Подсказка:** ...`)

5. Template code in task cells — structure only, not solution:
   - Allowed: function signature with docstring, variable stubs with type annotations,
     empty class methods
   - Not allowed: commented-out code that solves the task; step-by-step instructions
     inside code; any code the student just needs to "uncomment"
   - If the task is complex and scaffolding helps — show structure (step names in comments),
     not implementation

6. Terminology and language — per `references/lab_context.md`: Russian terms, English only
   for library names and abbreviations.

7. All numerical dataset characteristics (size, frequency, value range) — verified only.
   If unsure — use web search and cite the source in a cell comment.

---

## Notebook Template

The complete template (Block 0 cells and final cells) is defined in `references/lab_context.md`
under "Notebook Structure". Follow it precisely.

Key invariants:
- Variant formula MUST be verbatim: `dataset_id = (Student_ID - 1) % len(datasets)`
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
