# Course Conventions — Russian

This file is copied to `course_conventions.md` in the course root by `/course-maker course init`
when the course language is Russian. Edit the terminology dictionary before starting labs.

---

## Language

All materials are written in Russian. English terms are only acceptable in two cases:
- names of libraries, functions, classes, methods, parameters (`np.ndarray`, `hmmlearn`, `fit()`)
- abbreviations used in parallel in both Russian and English (`HMM` / `СММ`, `FFT` / `БПФ`, `ARIMA` / `АРИСС`)

At the first mention of a special term, introduce both variants: Russian and English.
Example: "скрытые марковские модели (СММ, HMM)" or "быстрое преобразование Фурье (БПФ, FFT)".
Afterwards, either variant is acceptable.

---

## Terminology Dictionary

Edit this table to match the terms used in your course.

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

---

## Never Use

- "форма" to mean "размерность массива"
- "learning rate", "shape", "plot" as nouns outside code context
- "fit" without context — use "обучение" / "обучить модель"

---

## Lab Goal Writing Rule

The lab goal is one concise sentence. It states the final result, not a list of steps.

Bad: "реализовать X, обучить Y, сравнить Z, проанализировать W"
Good: "реализовать HMM с нуля и применить её для анализа режимов в финансовых и биомедицинских рядах"
