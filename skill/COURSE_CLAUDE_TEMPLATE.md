# CLAUDE.md — [Course Name]

<!-- This file is read by Claude Code at the start of every session. -->
<!-- Two parts: (1) skill instructions, (2) course-specific context.  -->

---

## course-maker Skill

<!-- The skill is embedded below. Do not edit this section manually. -->
<!-- To update the skill, run: /skill update                          -->

<!-- SKILL:START -->
<!-- paste contents of course-maker/SKILL.md here on /course init -->
<!-- SKILL:END -->

---

## Course context

<!-- Fill this in during /course init. Claude uses it in every step. -->

**Course name:** [Full course name]
**Slug:** [course-slug]
**Semester / programme:** [e.g. Master's, semester 2, Mathematical Methods for Systems Analysis]

### Audience

[Describe what students already know. Be specific.
Example: "Masters students. Strong background in probability theory,
linear algebra, and basic ML. Some exposure to signal processing.
No prior experience with time series models."]

### Style preferences

**Rigor vs intuition:** [e.g. "Balance: intuition first, then formal statement.
Proofs only when they build understanding, not for completeness."]

**Formulas:** [e.g. "Always present with interpretation. Never just the formula alone."]

**Language:** [Any language is supported. Specify the language for slides,
speaker notes, and figure labels separately if needed.
e.g. "Slides in German. Speaker notes in German. Code comments and axis labels in English."
or "Slides and speaker notes in Japanese. No language restrictions on figures."]

> Note: `course_conventions.md` and `lab_templates.md` are generated automatically
> by the init wizard. Edit them after generation if your conventions differ from
> the language defaults.

### Recurring rules

<!-- Add any rules that apply across all lectures. Examples: -->
- [e.g. "Always connect new material to applications in system analysis"]
- [e.g. "When introducing a new distribution, always show: PDF shape, typical use case, key parameter meaning"]
- [e.g. "Sections marked 'announce-only' in the course plan: 1–2 slides, no derivations"]

### Sections to handle specially

<!-- If some topics appear in multiple lectures or need consistent treatment: -->
- [e.g. "ACF/PACF plots: always show both, always explain cutoff interpretation"]
- [e.g. "Python code examples: use numpy/scipy idioms, not pandas"]

---

## Lab context

<!-- Fill this in when running /lab course-init. Used by all /lab commands. -->

**GitHub org:** [org-name]
**GHC classroom org:** [classroom-org]
**GHC repo naming:** [classroom-org]/[prefix]-[lab-slug]
  # Example: cs-classroom/sp2026-lab1-eda
  # Used by /lab publish to sync via gh API

**Starter repos:**
| Lab | Slug | Starter repo URL |
|-----|------|-----------------|
| 1 | lab1-[slug] | https://github.com/[org]/lab1-[slug] |
| 2 | lab2-[slug] | https://github.com/[org]/lab2-[slug] |

---

## Notes from past lectures

<!-- Claude appends observations here as lectures are completed. -->
<!-- Useful for maintaining consistency across the course.        -->

<!-- Example entries added automatically:                         -->
<!-- - "Lecture 3: students had trouble with unit root intuition; -->
<!--   spend extra time on the random walk example in lecture 4"  -->
