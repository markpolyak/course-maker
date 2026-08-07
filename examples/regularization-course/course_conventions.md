# Course Conventions — English

This file is copied to `course_conventions.md` in the course root by `/course-maker course init`
when the course language is English. Edit the terminology dictionary before starting labs.

---

## Language

All materials are written in English. Language rules:
- Library names, function names, class names, parameters: use as-is (`np.ndarray`, `fit()`)
- Abbreviations: introduce at first mention — "hidden Markov model (HMM)"
- Afterwards, either the full term or abbreviation is acceptable

---

## Terminology Dictionary

Edit this table to match the terms used in your course. Add rows as needed.

| Preferred term | Avoid |
|---|---|
| dimensionality / shape | "form" for array shape |
| training / fitting | "fit" used as a noun without context |
| loss function | — |
| forecast | — |
| threshold | — |
| feature | — |

---

## Never Use

- "form" to mean array shape — use "shape" or "dimensionality"
- "fit" as a noun without context — use "training" or "model fitting"
- Jargon abbreviations without introducing them at first mention

---

## Lab Goal Writing Rule

The lab goal is one concise sentence. It states the final result, not a list of steps.

Bad: "implement X, train Y, compare Z, analyze W"
Good: "implement an HMM from scratch and apply it to regime detection in financial and biomedical time series"
