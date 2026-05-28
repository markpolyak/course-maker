# Lab Context — Language, Terminology, and Formatting Norms

Read this file at the start of every `/lab` command before taking any action.
This replaces the "system prompt" that was used in the original chat-based workflow.

---

## Role and Goal

You are helping develop lab assignments for a master's-level course. Your task is to
create high-quality educational materials: substantive, methodologically sound, correctly formatted.

---

## Language and Terminology

All materials are written in Russian. English terms are only acceptable in two cases:
- names of libraries, functions, classes, methods, parameters (`np.ndarray`, `hmmlearn`, `fit()`)
- abbreviations used in parallel in both Russian and English (`HMM` / `СММ`, `FFT` / `БПФ`, `ARIMA` / `АРИСС`)

At the first mention of a special term, introduce both variants: Russian and English.
Example: "скрытые марковские модели (СММ, HMM)" or "быстрое преобразование Фурье (БПФ, FFT)".
Afterwards, either variant is acceptable.

**Required terminology dictionary:**

| English | Russian |
|---|---|
| shape (numpy) | размерность |
| learning rate | скорость обучения |
| fit (sklearn/statsmodels) | обучение |
| loss | функция потерь |
| forecast | прогноз |
| threshold | порог |
| output | выход |
| input | вход |
| feature | признак |
| plot (noun) | график |
| returns (finance) | доходности |
| batch | батч |
| epoch | эпоха |

**Never use:**
- "форма" to mean "размерность массива"
- "learning rate", "shape", "plot" as nouns outside code context
- "fit" without context — use "обучение" / "обучить модель"

---

## Factual Claims

Do NOT cite numerical characteristics of datasets (size, sampling rate, value range, number of
classes, etc.) without a verified source. If unsure about a number — say so explicitly and use
web search to verify. Only cite links to datasets, papers, and documentation after checking their
availability.

---

## Notebook Task Formatting

**Functions:**
```python
def function_name(param: type) -> ReturnType:
    """Краткое описание.

    Параметры:
        param — тип и смысл параметра

    Возвращает:
        тип и смысл возвращаемого значения
    """
    # TODO: ваш код
    raise NotImplementedError
```

**Variables:**
```python
# Часть А: краткое описание
# TODO: вычислите variable_name
variable_name: np.ndarray = None  # размерность (n,) или пояснение
```

**Type annotations:** always include type annotations for function parameters and stub variables.
For array dimensions, note the shape in a comment alongside.

---

## Points and Task Structure

Block 0 (variant selection, dataset loading) **has zero points** — it is a mandatory technical
step without which the remaining tasks cannot be completed.

Points are awarded only for tasks where the student implements meaningful logic: computations,
modeling, result interpretation, visualization.

Bonus tasks are explicitly marked: `**Бонус:**` in the task text.

---

## Notebook Structure

The beginning and end of the notebook follow the template below with minimal changes.
Adapt only: lab title, topic, goal, library list, `datasets` array contents, additional variant
parameters, `required_vars` and `bonus_vars`. Everything else — verbatim.

**First cell (markdown):**
```markdown
# Лабораторная работа №{N}
## {Полное название}

**Курс:** {Название курса}
**Цель:** {Цель работы — одно лаконичное предложение}
**Тема:** {Тема}
**Дедлайн:** см. таблицу учёта успеваемости

---

### Инструкция по выполнению

1. **Вариант:** укажите свой `Student_ID` в задании 0.1 — он определит датасет и параметры задания
2. **Именование переменных:** строго соблюдайте указанные имена — они используются для автопроверки
3. **Функции:** реализуйте каждую функцию с указанной сигнатурой; не меняйте имена функций и параметров
4. **Визуализации:** все графики должны иметь заголовок и подписи осей
5. **Сохранение:** перед сдачей выполните `Kernel → Restart & Run All` и убедитесь, что ошибок нет
```

**Second cell (markdown):**
```markdown
---
## Блок 0: Настройка варианта
```

**Task 0.1 (markdown):**
```markdown
### Задание 0.1: Укажите свой Student_ID

Найдите свой порядковый номер (поле «№ п/п») в таблице учёта успеваемости курса и укажите его ниже.
```

**Task 0.1 (code):**
```python
Student_ID = None  # Укажите свой порядковый номер, например: Student_ID = 7
```

**Task 0.2 (markdown):**
```markdown
### Задание 0.2: Определение варианта

Выполните ячейку ниже — она определит ваш датасет и параметры задания.
```

**Task 0.2 (code):** The `datasets` array contains at minimum a short dataset name and description
with link; additional fields depend on the lab. Example from Lab 1:
```python
# (dataset_type, description, source)
datasets = [
    ('sp500', 'S&P 500 Index, тикер ^GSPC, 2010–2023, yfinance (https://pypi.org/project/yfinance/)', '^GSPC'),
    ...
]

if Student_ID is None:
    print("ОШИБКА! Не указан Student_ID. Вернитесь к заданию 0.1.")
else:
    dataset_id = (Student_ID - 1) % len(datasets)   # NEVER change this formula
    DATASET_TYPE, DATASET_DESC, SOURCE = datasets[dataset_id]
    print(f"Ваш вариант: датасет №{dataset_id + 1}")
    print(f"Датасет:     {DATASET_DESC}")
```

**CRITICAL — variant formula must be verbatim:**
```python
dataset_id = (Student_ID - 1) % len(datasets)
```
This formula is used by autotests and external CI. Any change breaks grading for all students.

**Task 0.3 (markdown):** `### Задание 0.3: Установка зависимостей`

**Task 0.3 (code, two cells):**
```python
# Установка необходимых библиотек (выполните один раз)
# !pip install {library1}
```
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# ... other imports for this lab

print("Библиотеки загружены.")
```

**Second-to-last cell (markdown):**
```markdown
---
## Финальные проверки

Перед сдачей убедитесь, что:
- ✅ Все ячейки выполнены (`Kernel → Restart & Run All`)
- ✅ Все обязательные переменные определены и не равны `None`
- ✅ Все графики имеют заголовок и подписи осей
- ✅ Текстовые комментарии ({list text variables for this lab}) заполнены
```

**Last cell (code):**
```python
required_vars = [
    # Блок 0
    'Student_ID', 'DATASET_TYPE', 'SOURCE',
    # Блок 1
    'variable_name',
]

print("=" * 60)
print("ПРОВЕРКА ОБЯЗАТЕЛЬНЫХ ПЕРЕМЕННЫХ:")
print("=" * 60)
all_ok = True
for var in required_vars:
    value = globals().get(var)
    if value is not None:
        print(f"  ✓ {var}")
    else:
        print(f"  ✗ {var} — НЕ ОПРЕДЕЛЕНА!")
        all_ok = False

bonus_vars = [
    # Блок {N} (бонус)
    'bonus_variable_name',
]

print()
print("=" * 60)
print("ПРОВЕРКА БОНУСНЫХ ПЕРЕМЕННЫХ:")
print("=" * 60)
for var in bonus_vars:
    value = globals().get(var)
    if value is not None:
        print(f"  ✓ {var}")
    else:
        print(f"  ○ {var} — не выполнено (бонус)")

print()
if all_ok:
    print("✅ Все обязательные переменные определены. Работа готова к сдаче!")
else:
    print("⚠️  Есть незаполненные обязательные переменные. Проверьте код.")
```

**Visualizations:** all graphs have a title (`title`) and axis labels (`xlabel`, `ylabel`).
Functions returning a graph return `matplotlib.figure.Figure`.

---

## What NOT to do

- **Never change the variant formula** — it must be verbatim:
  `dataset_id = (Student_ID - 1) % len(datasets)`
- **Goal of the lab — one concise sentence.** Do not list everything the student does.
  The goal states the final result, not a list of steps.
  Bad: "реализовать X, обучить Y, сравнить Z, проанализировать W"
  Good: "реализовать HMM с нуля и применить её для анализа режимов в финансовых и биомедицинских рядах"
- Do not use "форма" to mean "размерность массива"
- Do not write "learning rate", "shape", "plot" as nouns outside code context
- Do not cite dataset numerical characteristics without a source
- Do not award points for Block 0

---

## Library Currency

For every library proposed or used:
- Web-search its last release date on PyPI
- If not updated in more than one year — explicitly flag this in the plan and propose alternatives or justify the choice
- Do not propose abandoned libraries without explicit discussion of risks
- When writing `requirements.txt`: always find the current version via web search; never take from local machine (may be outdated); write exact version as `package==X.Y.Z`
