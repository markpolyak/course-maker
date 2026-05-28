# Lab Step 1a — Planning

Read `references/lab_context.md` before starting.

---

## Context to Read Before Planning

1. Read `course_plan.md` — find the section for lab N (topic, learning objectives).
2. Read `labs/labN/history.md` if it exists — note any rejected ideas or prior decisions.
3. Read `## Lab context` from `CLAUDE.md` — course name, audience, GitHub org.

---

## Prompt to Execute

Ask the user for any missing parameters (mandatory points, bonus points, additional requirements)
if they were not provided with the command.

Then start an iterative planning conversation. Produce a numbered task list in the following
format. For each task:

```
### Задание N.M — <Название>
- Что делает студент: <одна фраза — реализует функцию / определяет переменную / реализует класс>
- Обоснование: <почему это задание включено — что именно студент поймёт или научится делать;
  не "развивает навыки", а конкретно: "студент вручную реализует X и увидит Y">
- Интерфейс: <сигнатура функции или имя и тип переменной или название класса с методами>
- Что проверяется: <2–4 конкретных проверки — тип, размерность, диапазон значений, связь с другими переменными>
- Баллы: <число>
- Бонус: <да / нет>
```

**Requirements for the plan:**
- Block 0 (variant selection, dataset loading) is present but has ZERO points
- Sum of mandatory task points = <mandatory points from user>
- Sum of bonus task points = <bonus points from user>
- Tasks follow a logical order: from data loading to modeling and interpretation
- If a task involves visualization — the function returns `matplotlib.figure.Figure`
- Text student comments (result interpretation) are separate tasks with explicit variable names
- For every proposed library: web-search its last release date on PyPI and activity.
  If not updated in more than one year — explicitly flag this in the plan and propose alternatives
  or justify the choice. Do NOT propose abandoned libraries without discussion.

After the task list, add:
- Summary scoring table (block — task — points — bonus)
- Variable list for the self-check cell: `required_vars` and `bonus_vars`

**Do NOT generate notebook code until the user writes "план утверждён".**
Present the plan, wait for feedback, iterate.

---

## After User Approves the Plan

Write to `labs/labN/history.md` (append if file exists, create if not):

```markdown
## [YYYY-MM-DD] Step 1a: Plan approved

**Topics covered:** <list>
**Points:** <mandatory> mandatory + <bonus> bonus
**Key decisions:** <any non-obvious choices, rejected alternatives>
**Required vars:** <list from required_vars>
**Bonus vars:** <list from bonus_vars>
```

Update `COURSE_STATE.md` Labs table: set `plan` column for lab N to ✅.
