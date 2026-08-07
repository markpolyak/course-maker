# AGENTS.md — Regularization in Machine Learning

<!-- Course context, read by your coding agent at session start: Codex CLI and  -->
<!-- Cursor read AGENTS.md natively; Claude Code reads it via the @AGENTS.md     -->
<!-- import in CLAUDE.md. This file is the cross-tool source of truth for the    -->
<!-- course. The course-maker skill itself is installed separately (see the repo -->
<!-- README) and is discovered automatically — do not embed it here.            -->

---

## Course context

<!-- Fill this in during /course init. The agent uses it in every step. -->

**Course name:** Regularization in Machine Learning
**Slug:** regularization-course
**Semester / programme:** [e.g. Master's, semester 2, Mathematical Methods for Systems Analysis]
**Institution:** Claude Cowork
**Slides format:** beamer
<!-- beamer (LaTeX/PDF) | slidev (Markdown deck, presented/exported via `npx slidev`).
     Picks which reference /course-maker slides N uses and which preamble file
     course init generates (slides_preamble.tex vs slides_headmatter.md).
     Override per call: /course-maker slides N slidev. pptx is planned. -->
**LaTeX engine:** pdflatex
**Profile:** local-zip
<!-- LMS adapter from skill/profiles/. Default: local-zip (build a zip and
     upload manually). Other example: github-classroom (gh api sync to GHC).
     This controls only LMS-related behaviour (questions asked by
     /course-maker lab course-init, and the lms_adapter.md installed for
     /course-maker lab publish). It does NOT control instructor preferences
     (language, latex engine, audience, style) — those come from
     ~/.course-maker/defaults.yaml (or $COURSE_MAKER_HOME/defaults.yaml).
     See skill/profiles/README.md for full docs.  -->


### Audience

ML fundamentals: students already know supervised learning, linear/logistic
regression, gradient descent, and basic linear algebra & probability.

### Style preferences

**Rigor vs intuition:** Intuition-first. Build intuition before formalism;
proofs only when they aid understanding, not for completeness.

**Formulas:** Always present with interpretation. Never just the formula alone.

**Language:** English for slides, speaker notes, and figure labels.

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

### Lab grading

grade_reporter: none      # none | scoring_ci | <reporter in skill/extensions/reporters/>
                          # Optional end-of-tests output. 'none' = plain pytest pass/fail.
                          # 'scoring_ci' = points summary + autograder-readable grade line.
lab_variants: false       # true if each student gets a different dataset (per-student
                          # variants; see skill/extensions/variants/). false = same task
                          # for everyone.

**Delivery channel:** Email
  # local-zip profile: no remote starter repo or LMS API. /lab publish builds
  # a self-contained student-bundle-labN.zip; this field just records how you
  # plan to distribute it, for the publish summary.

---

## Notes from past lectures

<!-- The agent appends observations here as lectures are completed. -->
<!-- Useful for maintaining consistency across the course.        -->

<!-- Example entries added automatically:                         -->
<!-- - "Lecture 3: students had trouble with unit root intuition; -->
<!--   spend extra time on the random walk example in lecture 4"  -->
