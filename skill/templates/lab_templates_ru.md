# Lab Templates — Russian

This file is copied to `lab_templates.md` in the course root by `/course-maker lab course-init`
when the course language is Russian. Edit after generation if your conventions differ.

---

## Notebook Header Cell (markdown)

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

---

## Block 0 Divider Cell (markdown)

```markdown
---
## Блок 0: Настройка варианта
```

---

## Task 0.1 (markdown)

```markdown
### Задание 0.1: Укажите свой Student_ID

Найдите свой порядковый номер (поле «№ п/п») в таблице учёта успеваемости курса и укажите его ниже.
```

## Task 0.1 (code)

```python
Student_ID = None  # Укажите свой порядковый номер, например: Student_ID = 7
```

---

## Task 0.2 (markdown)

```markdown
### Задание 0.2: Определение варианта

Выполните ячейку ниже — она определит ваш датасет и параметры задания.
```

## Task 0.2 (code)

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

---

## Task 0.3 (markdown)

```markdown
### Задание 0.3: Установка зависимостей
```

## Task 0.3 (code, two cells)

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

---

## Final Checklist Cell (markdown, second-to-last)

```markdown
---
## Финальные проверки

Перед сдачей убедитесь, что:
- ✅ Все ячейки выполнены (`Kernel → Restart & Run All`)
- ✅ Все обязательные переменные определены и не равны `None`
- ✅ Все графики имеют заголовок и подписи осей
- ✅ Текстовые комментарии ({list text variables for this lab}) заполнены
```

---

## Self-Check Cell (code, last)

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

---

## Task Formatting

### Function stub

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

### Variable stub

```python
# Часть А: краткое описание
# TODO: вычислите variable_name
variable_name: np.ndarray = None  # размерность (n,) или пояснение
```

### Task title format

```
### Задание N.M — Название
```

### Hint format

```markdown
> 💡 **Подсказка:** ...
```

### Bonus task marker

```markdown
**Бонус:**
```

---

## conftest.py Strings

### Scoring block marker (start of editable section)

```python
# СИСТЕМА ПОДСЧЁТА БАЛЛОВ ДЛЯ ЛАБОРАТОРНОЙ РАБОТЫ
```

### Grade output string (do not modify format — CI reads it)

```python
print(f"  ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА В ЖУРНАЛ: ...")
```

---

## datasets_info.md

### Common issues section title

```
Частые проблемы и их решения
```

---

## Error Messages

Error messages in tests: Russian.
