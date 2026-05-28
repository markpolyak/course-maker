# Lab Pipeline — План реализации

Статус: **готов к выполнению** (не начат)  
Составлен: 2026-05-28  
Контекст: разговор в Claude Code о интеграции labforge → course-maker

---

## Что делаем и зачем

Интегрируем существующий пайплайн создания лабораторных работ (labforge) в скил course-maker.

**Labforge** — набор промптов и шаблонов для трёхэтапного создания ЛР:
- Этап 1: планирование (итерации) + генерация ноутбука и спецификации
- Этап 2: автотесты + conftest.py + README
- Этап 3: валидация от лица студента

Исходные файлы labforge: `/Users/markpolyak/Yandex.Disk.localized/Работа/Студенты/tools/labforge/`

**Course-maker** — Claude Code skill в `~/.claude/skills/course-maker/` (исходник: `/Users/markpolyak/Yandex.Disk.localized/Работа/Студенты/tools/course-maker/skill/`). Сейчас поддерживает только лекции (`/lecture *`). Roadmap уже предусматривает `[ ] Lab assignment pipeline`.

**Цель:** добавить семейство команд `/lab *` в скил, полностью покрывающих создание ЛР в Claude Code (без переключения в claude.ai чат).

---

## Архитектурные решения (принятые)

### 1. Все три этапа — в Claude Code

Оригинальный labforge разделял Этап 1 (claude.ai чат) и Этапы 2–3 (Claude Code) с мотивацией «чат дольше остаётся в рассуждающем режиме». Решено: с современными моделями (Claude Sonnet 4.6+) это различие несущественно. Все этапы интегрируются в скил.

### 2. Структура репозиториев: курсовой репо + starter-репо как git subtree

Преподаватель работает в **приватном курсовом репо** (`my-course/`), где хранятся все файлы: и instructor-only (`lab_spec.md`, `history.md`), и студенческие (`exercises.ipynb`, `tests.py` и т.д.).

Студенческие файлы живут в поддиректории `labs/labN/starter/`, которая является **git subtree**, указывающим на отдельный публичный **starter-репо** на GitHub. Этот starter-репо используется как template в GitHub Classroom.

**Почему subtree, а не submodule:**
- Submodule требует двухшагового коммита (commit в submodule → commit в parent) и страдает от detached HEAD
- Subtree: один `git commit` в курсовом репо, один `git subtree push` для публикации
- Для Claude Code `labs/labN/starter/` выглядит как обычная директория

> **ВНИМАНИЕ:** В финальном предложении пользователя в структуре написано "git submodule". Перед началом реализации уточнить у пользователя: subtree или submodule? Аргументы за subtree изложены выше. Если пользователь настаивает на submodule — добавить в команду `/lab publish N` двухшаговый commit и инструкцию по `git checkout main` внутри submodule.

### 3. GHC-репозиторий синхронизируется через `gh` API

GitHub Classroom создаёт собственную копию starter-репо (GHC-репо) со squashed историей — прямой git push туда не работает. Решение: синхронизировать отдельные файлы через `gh api` (GitHub REST API). Это часть команды `/lab publish N`.

### 4. Системный промпт этапа 1 → отдельный reference-файл

В оригинале labforge системный промпт (`system_prompt_stage1.md`) вставлялся в каждый чат. В Claude Code аналога нет. Решение: создать `skill/references/lab_context.md` с тем же содержимым — каждый reference-файл этапа 1 начинается с инструкции «прочитай `lab_context.md` перед началом».

### 5. `lab_spec.md` и `history.md` — в курсовом репо, не в starter-репо

Студент не должен видеть эти файлы. Они хранятся в `labs/labN/` (курсовой репо), не в `labs/labN/starter/` (starter-репо). В starter-репо их нет.

---

## Итоговая структура курсового репо

```
my-course/                          ← приватный репо преподавателя
  CLAUDE.md                         ← скил + контекст курса (обновить шаблон)
  course_plan.md
  COURSE_STATE.md                   ← расширить: добавить таблицу Labs
  lectures/
    01/ ...
  labs/
    shared/
      tests_template.py             ← шаблон тестов (переиспользуется)
      conftest_base.py              ← базовый conftest.py (переиспользуется)
      tests.yaml                    ← GitHub Actions CI (не менять никогда)
    lab1/
      lab_spec.md                   ← ВЕРСИОНИРУЕТСЯ здесь, студенту не видно
      history.md                    ← ВЕРСИОНИРУЕТСЯ здесь, студенту не видно
      starter/                      ← git subtree → github.com/org/lab1-eda
        exercises.ipynb
        conftest.py
        tests.py
        requirements.txt
        README.md
        datasets_info.md            ← если нужен для данной ЛР
        .github/
          workflows/
            tests.yaml              ← скопирован из labs/shared/
    lab2/
      lab_spec.md
      history.md
      starter/                      ← git subtree → github.com/org/lab2-linreg
        ...
```

**Starter-репо** (публичный, GitHub Classroom template):
```
lab1-eda/                           ← github.com/org/lab1-eda
  exercises.ipynb
  conftest.py
  tests.py
  requirements.txt
  README.md
  datasets_info.md                  ← если нужен
  .github/
    workflows/
      tests.yaml
  # lab_spec.md — ОТСУТСТВУЕТ
  # history.md  — ОТСУТСТВУЕТ
```

---

## Новые команды скила

| Команда | Этап | Что делает |
|---|---|---|
| `/lab course-init` | setup | Создать `labs/shared/`, скопировать шаблоны из `skill/templates/` |
| `/lab init N <url>` | setup | Создать `labs/labN/`, добавить starter как subtree по URL |
| `/lab plan N` | 1a | Итеративное планирование → `labs/labN/history.md` |
| `/lab notebook N` | 1b-1 | Генерация `labs/labN/starter/exercises.ipynb` |
| `/lab spec N` | 1b-2 | Генерация `labs/labN/lab_spec.md` |
| `/lab datasets N` | 1b-3 | Генерация `labs/labN/starter/datasets_info.md` (если нужен) |
| `/lab tests N` | 2 | `tests.py`, `conftest.py`, `requirements.txt`, `README.md` |
| `/lab validate N <student_id>` | 3 | Валидация от лица студента (рекомендовать новую сессию) |
| `/lab publish N` | pub | Push в starter-репо + синхронизация GHC через `gh` |
| `/lab status N` | info | Статус + последние 3 записи `history.md` |

---

## Задача 0: Инициализация структуры скила

**Что менять:** `skill/SKILL.md`

### 0a. Добавить описание `labs/` в раздел "Repository layout"

Вставить после блока `lectures/`:

```
  labs/
    shared/
      tests_template.py   ← reusable style reference for Stage 2
      conftest_base.py    ← base conftest, updated per-lab (scoring block only)
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
```

### 0b. Расширить `COURSE_STATE.md` — добавить таблицу Labs

Вставить после таблицы Lectures:

```markdown
## Labs

| # | Title | plan | notebook | spec | tests | validated | published | Updated |
|---|-------|------|----------|------|-------|-----------|-----------|---------|
| 01 | ... | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — |

Legend: ✅ done · 🔄 in progress · ❌ not started · ⚠️ needs review
```

### 0c. Добавить блок `/lab` команд в раздел "Workflows"

Добавить раздел `/lab` workflows по аналогии с `/lecture`. Подробное содержимое — в Задачах 4 и 5 этого документа.

---

## Задача 1: Обновить COURSE_CLAUDE_TEMPLATE.md

**Что менять:** `skill/COURSE_CLAUDE_TEMPLATE.md`

Добавить секцию `## Lab context` после существующей `## Course context`:

```markdown
## Lab context

**GitHub org:** <org-name>
**GHC classroom org:** <classroom-org>
**GHC repo naming:** <classroom-org>/<prefix>-<lab-slug>
  # Например: cs-classroom/sp2026-lab1-eda
  # Используется командой /lab publish для синхронизации через gh API

**Starter repos:**
| Lab | Slug | Starter repo URL |
|-----|------|-----------------|
| 1 | lab1-eda | https://github.com/<org>/lab1-eda |
| 2 | lab2-linreg | https://github.com/<org>/lab2-linreg |
```

---

## Задача 2: Создать shared templates

**Директория:** `skill/templates/` (создать новую)

Скопировать из labforge-репо следующие файлы. Если у пользователя есть более актуальные версии из реальных ЛР — использовать их вместо labforge-версий.

### `skill/templates/tests_template.py`
**Источник:** из реального `tests.py` ЛР1 (если есть) или шаблон из labforge.  
**Назначение:** образец стиля и паттернов для Claude Code на Этапе 2. Не редактируется при создании каждой ЛР — только читается как reference.

**Структура, которую должен иметь файл:**
```python
# tests_template.py — ОБРАЗЕЦ СТИЛЯ. Не редактировать.
# Используется как reference на Этапе 2 (Stage 2).

import pytest
import numpy as np
import pandas as pd
# ... стандартные импорты

# Паттерн: один класс на одно задание
class TestTask1_1_DataLoading:
    """Задание 1.1: Загрузка данных"""

    def test_variable_exists(self, student_module):
        assert hasattr(student_module, 'raw_data'), \
            "Переменная raw_data не определена"

    def test_variable_type(self, student_module):
        assert isinstance(student_module.raw_data, pd.DataFrame), \
            f"raw_data должна быть pd.DataFrame, получено: {type(student_module.raw_data)}"

    def test_not_empty(self, student_module):
        assert len(student_module.raw_data) > 100, \
            "raw_data пустая или слишком короткая"

# Паттерн для функций:
class TestTask5_1_PlotHiddenStates:
    def test_returns_figure(self, student_module, sample_data):
        fig = student_module.plot_hidden_states(
            sample_data['observations'],
            sample_data['hidden_states'],
            n_states=3
        )
        assert isinstance(fig, plt.Figure), \
            "plot_hidden_states должна возвращать matplotlib.figure.Figure"

    def test_has_title(self, student_module, sample_data):
        fig = student_module.plot_hidden_states(...)
        assert fig.axes[0].get_title() != '', "График должен иметь заголовок"

# Паттерн для бонусных заданий:
class TestBonus:
    def test_bonus_task(self, student_module):
        if not hasattr(student_module, 'bonus_var') or student_module.bonus_var is None:
            pytest.skip("Бонусное задание не выполнено")
        # ... проверки
```

### `skill/templates/conftest_base.py`
**Источник:** из реального `conftest.py` ЛР1 (у пользователя есть актуальная версия).  
**Назначение:** базовый conftest.py, который копируется при `/lab init N` и обновляется на Этапе 2 (только блок scoring).

**Критические инварианты** (не менять ни при каких обстоятельствах):
```python
# Эти строки обязаны присутствовать дословно:
dataset_id = (Student_ID - 1) % len(DATASETS)   # формула варианта
print(f"  TASKID is {dataset_id + 1}")           # читает внешняя CI-система
print(f"  ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА В ЖУРНАЛ: ...")  # формат ожидает CI-система
```

**Структура файла (схематично):**
```python
# conftest.py

import sys, types, io
# ... моки IPython

class DummyIPython: ...     # НЕ ТРОГАТЬ
def get_ipython(): ...      # НЕ ТРОГАТЬ
def fake_input(): ...       # НЕ ТРОГАТЬ
def fake_display(): ...     # НЕ ТРОГАТЬ
# патчинг builtins         # НЕ ТРОГАТЬ

# ======== СИСТЕМА ПОДСЧЁТА БАЛЛОВ ДЛЯ ЛАБОРАТОРНОЙ РАБОТЫ ========
# Этот блок и ниже — обновлять при каждой ЛР

TEST_POINTS = {
    'test_name': points,    # обновлять по lab_spec.md
}

TEST_BLOCKS = {
    'TestClassName': 'test_name',   # обновлять по lab_spec.md
}

DATASETS = [...]   # обновлять по блоку 0 exercises.ipynb

# фикстура student_module    # НЕ ТРОГАТЬ логику, только DATASETS
# pytest_runtest_makereport  # НЕ ТРОГАТЬ
# pytest_sessionfinish       # обновлять только: название ЛР, наличие бонусов
```

### `skill/templates/tests.yaml`
**Источник:** из реального `.github/workflows/tests.yaml` ЛР1 (у пользователя есть).  
**Назначение:** CI-джоба GitHub Actions. **Не менять никогда.**  
Копируется в `labs/labN/starter/.github/workflows/tests.yaml` при `/lab init N`.

---

## Задача 3: Создать reference-файлы Этапа 1

**Директория:** `skill/references/` (существует, добавляем новые файлы)

### `skill/references/lab_context.md`

**Источник:** `labforge/system_prompt_stage1.md`  
**Назначение:** нормы языка, терминологии и оформления для всех этапов. Замена системного промпта чата.

**Содержимое:** адаптировать `system_prompt_stage1.md` дословно, добавив в начало:

```markdown
# Lab Context — Language, Terminology, and Formatting Norms

Read this file at the start of every `/lab` command before taking any action.
This replaces the "system prompt" that was used in the original chat-based workflow.

[Далее — дословное содержимое system_prompt_stage1.md, начиная с раздела "Язык и терминология"]
```

Ключевые разделы из источника:
- Язык и терминология (словарь EN→RU, правила аббревиатур)
- Фактические утверждения (проверять через веб-поиск, не придумывать числа датасетов)
- Оформление заданий в ноутбуке (шаблоны функций, переменных, классов)
- Структура ноутбука
- Баллы и структура задания
- Чего не делать (список запретов)

### `skill/references/lab_step1a_plan.md`

**Источник:** `labforge/prompt_phase1a.md`  
**Назначение:** инструкции для команды `/lab plan N`.

**Структура файла:**

```markdown
# Lab Step 1a — Planning

Read `references/lab_context.md` before starting.

## Context to read before planning

1. Read `course_plan.md` — find the section for lab N (topic, learning objectives).
2. Read `labs/labN/history.md` if it exists — note any rejected ideas or prior decisions.
3. Read `## Lab context` from `CLAUDE.md` — course name, audience.

## What to produce

[Адаптированное содержимое prompt_phase1a.md]

Key requirements:
- Present a numbered plan with format: title, what student does, rationale, interface, checks, points, bonus
- Block 0 (variant selection, dataset loading) is present but has ZERO points
- Sum of mandatory points = <основные баллы> (ask user if not specified)
- For every proposed library: web-search its last release date. If not updated in >1 year, flag it explicitly and propose alternatives or justify the choice
- Do NOT generate notebook code until user writes "план утверждён"

## After approval

- Append to `labs/labN/history.md`:
  ```
  ## [YYYY-MM-DD] Step 1a: Plan approved
  **Topics covered:** <list>
  **Points:** <mandatory> + <bonus> bonus
  **Key decisions:** <any non-obvious choices>
  ```
- Update `COURSE_STATE.md`: plan → ✅
```

### `skill/references/lab_step1b_notebook.md`

**Источники:** `labforge/prompt_phase1b_notebook.md` + `labforge/notebook_template.md`  
**Назначение:** инструкции для команды `/lab notebook N`.

**Структура файла:**

```markdown
# Lab Step 1b-1 — Notebook Generation

Read `references/lab_context.md` before starting.

## Context to read before generating

1. Read `labs/labN/history.md` — find the approved plan (last 1a entry).
2. Read `course_plan.md` section for lab N — course name, lab title.

## What to produce

Generate `labs/labN/starter/exercises.ipynb`.

[Адаптированное содержимое prompt_phase1b_notebook.md]

Key requirements:
- Follow the approved plan strictly — no new tasks, no changed interfaces
- Structure: first two markdown cells (header + block 0 divider) → Block 0 → main blocks → final two cells (checklist + self-check code)
- The variant formula MUST be verbatim:
  dataset_id = (Student_ID - 1) % len(datasets)
  NEVER change this formula — CI and grading systems depend on it
- Functions: docstring in Russian, type annotations, `# TODO: ваш код`, `raise NotImplementedError`
- Variables: Russian comment, `# TODO:`, type annotation, stub `= None`
- Every task preceded by markdown cell with title, description, hints if needed

## Notebook template

[Дословное содержимое notebook_template.md — весь шаблон блока 0 и финальных ячеек]

## After saving

- Append to `labs/labN/history.md`
- Update `COURSE_STATE.md`: notebook → ✅
```

### `skill/references/lab_step1b_spec.md`

**Источники:** `labforge/prompt_phase1b_spec.md` + шаблон `labforge/lab_spec.md`  
**Назначение:** инструкции для команды `/lab spec N`.

**Структура файла:**

```markdown
# Lab Step 1b-2 — Lab Spec Generation

Read `references/lab_context.md` before starting.

## Context to read

1. Read `labs/labN/starter/exercises.ipynb` — must be generated before this step.
2. Read `labs/labN/history.md` — approved plan.

## What to produce

Generate `labs/labN/lab_spec.md` — the contract between Stage 1 and Stage 2.
This file is NOT published to students. It lives only in the course repo.

[Адаптированное содержимое prompt_phase1b_spec.md]

## Lab spec template

[Дословное содержимое шаблона lab_spec.md — со всеми секциями:
metadata, infrastructure, datasets, variant_vars, tasks (переменные/функции/классы/бонусы),
text_vars, scoring table, artifacts, notes для этапа 2]

## Key rules for writing checks (from accumulated experience)

- Tolerances:
  - Values ~order of 1: rtol=0.05
  - Values approaching zero (probabilities, fractions): atol=0.05 (NOT rtol — rtol*~0 fails all correct implementations)
  - Log-likelihood of continuous distributions: do not check sign (density at mode can exceed 1)
- Robustness:
  - Before any numeric check: ask "Does this pass for ALL dataset variants?" If no — condition on DATASET_TYPE or move to oral defense
  - Do NOT check internal matplotlib objects (ax.collections, ax.patches, QuadMesh, etc.) — they change between versions. Check only observable behavior: return type, title, axis labels
  - If multiple standard methods solve correctly (imshow, pcolormesh, heatmap) — test must not prefer one over others
- Reproducibility: all parameters affecting reproducibility (random_state, covariance_type, n_iter, n_init) must be explicitly specified for EVERY function/method where they apply
- Library versions: check PyPI for latest version; flag libraries not updated in >1 year

## After saving

- Append to `labs/labN/history.md`
- Update `COURSE_STATE.md`: spec → ✅
```

### `skill/references/lab_step1b_datasets.md`

**Источник:** `labforge/prompt_phase1b_datasets.md`  
**Назначение:** инструкции для команды `/lab datasets N` (опциональный шаг).

```markdown
# Lab Step 1b-3 — Datasets Info Generation (Optional)

Read `references/lab_context.md` before starting.

This step is optional. Run it when lab_spec.md lists datasets with complex
download procedures or when students need reference information about the data.

## Context to read

1. Read `labs/labN/lab_spec.md` — datasets section.
2. Read `labs/labN/starter/exercises.ipynb` — Block 0 (dataset list, sources).

## What to produce

Generate `labs/labN/starter/datasets_info.md` — reference for students.

[Дословное содержимое prompt_phase1b_datasets.md]

Note: if chat context was exhausted in Stage 1 (original workflow), this file
can be generated at the beginning of Stage 2. Same applies here: if `/lab spec N`
was long, run `/lab datasets N` as a separate command.

## After saving

- Append to `labs/labN/history.md`
- Update `COURSE_STATE.md`: datasets_info noted in lab row
```

---

## Задача 4: Создать reference-файлы Этапов 2–3

### `skill/references/lab_step2_tests.md`

**Источник:** `labforge/prompt_stage2.md` + раздел "Исправленные проблемы" из `labforge/TODO.md`  
**Назначение:** инструкции для команды `/lab tests N`.

```markdown
# Lab Step 2 — Test Generation

## Context to read FIRST (mandatory)

1. Read `labs/labN/lab_spec.md` — full specification.
2. Read `labs/labN/starter/exercises.ipynb` — notebook structure, variable names.
3. Read `labs/shared/conftest_base.py` — existing infrastructure.
4. Read `labs/shared/tests_template.py` — style reference (do not copy logic, only patterns).

## What to produce

Update/create in `labs/labN/starter/`:
- `conftest.py` — updated scoring block
- `tests.py` — full test suite
- `requirements.txt` — updated if needed
- `README.md` — updated for this lab

[Дословное содержимое prompt_stage2.md — все 7 шагов с правилами]

## Accumulated known issues (from production use)

**Library versions:**
- Do NOT take version from local machine — it may be outdated
- For every added/updated package: web-search current version on PyPI and use exact found version (package==X.Y.Z)
- Flag libraries not updated in >1 year (e.g., hmmlearn) — notify professor, propose alternatives

**Matplotlib tests:**
- NEVER check internal matplotlib objects: ax.collections, ax.patches, QuadMesh, AxesImage, etc.
- These change between library versions
- plt.colorbar() / seaborn heatmap with colorbar add extra axes — len(fig.axes)==2 test wrongly forbids colorbar
- Correct check for "main axes only": filter axes by SubplotSpec (colorbars have none):
  main_axes = [ax for ax in fig.axes if ax.get_subplotspec() is not None]

**Axis count checks:**
- If spec says "figure has exactly 2 subplots" — check main_axes (no colorbars), not all axes

## After saving

- Append to `labs/labN/history.md`
- Update `COURSE_STATE.md`: tests → ✅
- Run compatibility check:
  - All keys in TEST_POINTS match test function names in tests.py
  - All tests in TEST_BLOCKS exist in tests.py
  - Sum of TEST_POINTS matches scoring table in lab_spec.md
```

### `skill/references/lab_step3_validate.md`

**Источник:** `labforge/prompt_stage3.md`  
**Назначение:** инструкции для команды `/lab validate N`.

```markdown
# Lab Step 3 — Validation

## IMPORTANT: Run in a new isolated Claude Code session

This step simulates a student solving the lab. Claude must not have access to
lab_spec.md or tests before completing all tasks.

When the user runs `/lab validate N <student_id>`, show this message:
"Этап валидации рекомендуется запускать в новой сессии Claude Code.
Откройте новую сессию, перейдите в `labs/labN/starter/`, и запустите команду снова."

If the user confirms they want to run in the current session, proceed with the
instructions below — but strictly enforce the file access rules.

## Files available during validation

ALLOWED to read:
- `labs/labN/starter/exercises.ipynb`
- `labs/labN/starter/datasets_info.md` (if exists)
- Public library documentation (web search allowed)

NOT ALLOWED to read until all tasks are complete:
- `labs/labN/starter/tests.py`
- `labs/labN/starter/conftest.py`
- `labs/shared/tests_template.py`

NEVER allowed to read:
- `labs/labN/lab_spec.md`

[Дословное содержимое prompt_stage3.md — все правила и финальная последовательность действий]

## After validation

Append to `labs/labN/history.md`:
```
## [YYYY-MM-DD] Step 3: Validation — Student_ID=<N>
**All tasks completed:** yes/no
**Issues found:** <list or "none">
**Test results:** X passed, Y failed
**Action required:** <return to step 1/2 or ready to publish>
```
Update `COURSE_STATE.md`: validated → ✅ or ⚠️
```

---

## Задача 5: Команды `/lab *` в SKILL.md

Добавить в `SKILL.md` раздел **Lab Workflows** после раздела Lecture Workflows.

### `/lab course-init`

```
1. Create `labs/shared/` directory.
2. Copy from `skill/templates/`:
   - `tests_template.py` → `labs/shared/tests_template.py`
   - `conftest_base.py`  → `labs/shared/conftest_base.py`
   - `tests.yaml`        → `labs/shared/tests.yaml`
3. Tell user: "shared assets created. Now run /lab init N <url> for each lab."
```

### `/lab init N <url>`

```
1. Create `labs/labN/` directory.
2. Create empty `labs/labN/history.md`:
   # Lab N — History
   (no entries yet)
3. Create empty `labs/labN/lab_spec.md` (placeholder, will be filled by /lab spec N).
4. Add starter repo as git subtree:
   git subtree add --prefix=labs/labN/starter <url> main --squash
5. Copy CI file:
   cp labs/shared/tests.yaml labs/labN/starter/.github/workflows/tests.yaml
6. Copy base conftest:
   cp labs/shared/conftest_base.py labs/labN/starter/conftest.py
7. Add lab N row to COURSE_STATE.md Labs table (all columns ❌).
8. Commit: git add -A && git commit -m "lab N: init starter subtree"
```

### `/lab plan N`

```
Read: references/lab_step1a_plan.md
Input files: course_plan.md (lab N section), labs/labN/history.md, CLAUDE.md (Lab context)
Output: iterative planning conversation → approved plan
State: update history.md, COURSE_STATE.md plan → ✅
```

### `/lab notebook N`

```
Read: references/lab_step1b_notebook.md
Input files: labs/labN/history.md (approved plan), course_plan.md
Output: labs/labN/starter/exercises.ipynb
State: update history.md, COURSE_STATE.md notebook → ✅
```

### `/lab spec N`

```
Read: references/lab_step1b_spec.md
Input files: labs/labN/starter/exercises.ipynb, labs/labN/history.md
Output: labs/labN/lab_spec.md
State: update history.md, COURSE_STATE.md spec → ✅
```

### `/lab datasets N`

```
Read: references/lab_step1b_datasets.md
Input files: labs/labN/lab_spec.md, labs/labN/starter/exercises.ipynb
Output: labs/labN/starter/datasets_info.md
State: update history.md
```

### `/lab tests N`

```
Read: references/lab_step2_tests.md
Input files: labs/labN/lab_spec.md, labs/labN/starter/exercises.ipynb,
             labs/shared/conftest_base.py, labs/shared/tests_template.py
Output: labs/labN/starter/{tests.py, conftest.py, requirements.txt, README.md}
State: update history.md, COURSE_STATE.md tests → ✅
Commit: git add -A && git commit -m "lab N: add tests and conftest"
```

### `/lab validate N <student_id>`

```
Read: references/lab_step3_validate.md
Warn user to use a new isolated session.
If proceeding: simulate student solving exercises.ipynb for given Student_ID.
State: update history.md, COURSE_STATE.md validated → ✅ or ⚠️
```

### `/lab publish N`

```
Read: CLAUDE.md → Lab context (GHC org, repo naming)

Step 1 — push to starter repo (git subtree):
  git subtree push --prefix=labs/labN/starter <url> main

Step 2 — sync GHC repo via gh API:
  Read CLAUDE.md to find GHC repo name for lab N.
  For each student-facing file in labs/labN/starter/:
    [exercises.ipynb, conftest.py, tests.py, requirements.txt,
     README.md, datasets_info.md (if exists),
     .github/workflows/tests.yaml]
  
  Run for each file:
    SHA=$(gh api repos/$GHC_REPO/contents/$FILE --jq '.sha // empty' 2>/dev/null)
    CONTENT=$(base64 < labs/labN/starter/$FILE)
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

Step 3 — update course repo:
  git add labs/labN/
  git commit -m "lab N: publish"
  git push

Step 4 — update COURSE_STATE.md: published → ✅
Step 5 — append to labs/labN/history.md: publish event with date and list of synced files.

Note: lab_spec.md and history.md are explicitly NOT in the sync list.
```

### `/lab status N`

```
Print:
1. Row from COURSE_STATE.md Labs table for lab N.
2. Last 3 entries from labs/labN/history.md.
3. Any ⚠️ warnings with explanation.
```

### `/lab update N`

```
Use this when a lab needs to be updated AFTER publishing (fix tests, fix notebook).

1. Make the needed changes in labs/labN/starter/.
2. Run /lab validate N <student_id> to verify fix doesn't break correct solutions.
3. Run /lab publish N to sync changes to starter repo and GHC repo.
4. Append to labs/labN/history.md:
   ## [YYYY-MM-DD] Post-publish update
   **Changed:** <files>
   **Reason:** <why update was needed>
   **Validated:** Student_ID=<N>
5. Update COURSE_STATE.md: set validated → 🔄 if re-validation needed.
```

---

## Задача 6: Обновить Quick reference в SKILL.md

Добавить в таблицу Quick reference раздел Labs:

```markdown
**Lab commands:**

| Command | Description |
|---|---|
| `/lab course-init` | Create labs/shared/, copy base templates |
| `/lab init N <url>` | Scaffold lab N with starter subtree |
| `/lab plan N` | Step 1a — interactive planning until approved |
| `/lab notebook N` | Step 1b — generate exercises.ipynb |
| `/lab spec N` | Step 1b — generate lab_spec.md |
| `/lab datasets N` | Step 1b — generate datasets_info.md (optional) |
| `/lab tests N` | Step 2 — tests.py, conftest.py, requirements.txt, README |
| `/lab validate N <id>` | Step 3 — validate as student (new session recommended) |
| `/lab publish N` | Push to starter repo + sync GHC via gh API |
| `/lab update N` | Re-publish after post-release fix |
| `/lab status N` | Status + last 3 history entries |
```

---

## Задача 7: Документация

### 7a. Обновить README.md

В разделе Roadmap заменить:
```
- [ ] Lab assignment pipeline (`/lab-pipeline`)
```
на:
```
- [x] Lab assignment pipeline (`/lab *` commands)
```

### 7b. Добавить раздел в docs/getting-started.md

Добавить раздел "Creating lab assignments" с примером полного workflow:
```
/lab course-init
/lab init 1 https://github.com/org/lab1-eda
/lab plan 1        # iterate until approved
/lab notebook 1    # generate exercises.ipynb
/lab spec 1        # generate lab_spec.md
/lab tests 1       # generate tests.py, conftest.py
/lab validate 1 7  # validate as student 7
/lab publish 1     # push to GitHub + sync GHC
```

### 7c. Тест на реальной ЛР

После реализации: прогнать полный пайплайн на ЛР2. Зафиксировать в `labs/lab2/history.md` все места, где потребовалось >1 итерации. Внести исправления в соответствующие reference-файлы.

---

## Инвентарь исходных файлов

Все исходники в: `/Users/markpolyak/Yandex.Disk.localized/Работа/Студенты/tools/labforge/`

| Файл labforge | Используется в |
|---|---|
| `system_prompt_stage1.md` | → `skill/references/lab_context.md` |
| `system_prompt_stage1_full.md` | То же содержимое, более полная версия — использовать её |
| `prompt_phase1a.md` | → `skill/references/lab_step1a_plan.md` |
| `prompt_phase1b_notebook.md` | → `skill/references/lab_step1b_notebook.md` |
| `notebook_template.md` | → встроить в `lab_step1b_notebook.md` |
| `prompt_phase1b_spec.md` | → `skill/references/lab_step1b_spec.md` |
| `lab_spec.md` (шаблон) | → встроить в `lab_step1b_spec.md` |
| `prompt_phase1b_datasets.md` | → `skill/references/lab_step1b_datasets.md` |
| `prompt_stage2.md` | → `skill/references/lab_step2_tests.md` |
| `prompt_stage3.md` | → `skill/references/lab_step3_validate.md` |
| `TODO.md` (раздел "Исправленные") | → встроить в `lab_step2_tests.md` (known issues) |
| `tests_template.py` | → `skill/templates/tests_template.py` |
| `PIPELINE.md` | Справочник — не копировать, использовать как контекст |

**Файлы, которых нет в labforge, нужно получить от пользователя:**
- Актуальный `conftest.py` из реальной ЛР1 → `skill/templates/conftest_base.py`
- Актуальный `tests.yaml` из реальной ЛР1 → `skill/templates/tests.yaml`
- Опционально: актуальный `tests_template.py` из реальной ЛР1 (может быть лучше labforge-версии)

---

## Критические инварианты (нельзя нарушать ни при каких условиях)

Эти строки должны присутствовать дословно везде, где встречаются:

```python
# Формула варианта — ДОСЛОВНО, не менять:
dataset_id = (Student_ID - 1) % len(datasets)

# Строка для внешней CI-системы — ДОСЛОВНО, не менять:
print(f"  TASKID is {dataset_id + 1}")

# Строка оценки — формат ДОСЛОВНО, только числитель можно адаптировать:
print(f"  ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА В ЖУРНАЛ: ...")
```

Эти строки читают внешние системы автоматической проверки. Любое изменение сломает проверку для всех студентов всех прошедших и будущих ЛР.

---

## Открытые вопросы (уточнить перед началом реализации)

1. **Subtree или submodule?** Рекомендовано subtree (проще workflow), но пользователь в финальной структуре написал "git submodule". Уточнить выбор. Если submodule — добавить в `/lab init N` и `/lab publish N` двухшаговый commit и инструкцию по `git checkout main`.

2. **Актуальные shared-файлы.** Перед созданием `skill/templates/` запросить у пользователя актуальные `conftest.py`, `tests.yaml`, (опционально) `tests_template.py` из реальной ЛР1.

3. **prompt_reverse_spec.md.** В labforge есть файл `prompt_reverse_spec.md` — не задокументирован в PIPELINE.md. Уточнить назначение и нужно ли его включать.

---

## Порядок выполнения задач

```
Задача 0  →  Задача 1  →  Задача 2  →  Задача 3  →  Задача 4  →  Задача 5  →  Задача 6  →  Задача 7
(структура)  (шаблон)    (ref Stage1) (ref Stage2-3) (команды)  (quick ref)  (docs)    (тест)
```

Задачи 2, 3, 4 можно выполнять параллельно. Задача 5 зависит от 2–4. Задача 7 — последняя.

Задача 7c (тест на реальной ЛР) — после полной реализации, в отдельной сессии.
