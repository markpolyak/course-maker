# Lecture 1 — History

## [2026-07-21] Step 1: Plan — iteration 1
**Result:** plan.md created (19 slides, 90 min)
**User feedback:** Approved without changes on first draft.
**Decision:** Structure = 4 blocks (why regularize → ridge/lasso mechanics →
tuning & Bayesian view → elastic net teaser + wrap-up). Elastic net kept
announce-only (1 slide, slide 18) per course_plan.md; full treatment deferred
to Lecture 2. Single forward reference to Lecture 2 / lab placed on closing
slide 19 only.

## [2026-07-21] Step 2: Visuals — iteration 1
**Result:** visuals.md created (6 figures, V01–V06, all requiring Python)
**User feedback:** Approved without changes.
**Decision:** Geometric contour figures (V04 L2, V05 L1) classified as
"No — needs real data" rather than TikZ "Hard", since exact tangency geometry
requires computed quadratic contours rather than a schematic drawing.

## [2026-07-21] Step 3: Figures — iteration 1
**Result:** figures.py created and run clean; all 6 PNGs verified visually.
**Decisions/fixes during generation:**
- Ridge/Lasso implemented from scratch in numpy (closed-form ridge,
  coordinate-descent lasso) — no sklearn dependency, per style rules.
- fig05 (L1 geometry): swept lasso λ to find a value (100.0) that produces an
  exact zero coefficient, so the corner-tangency point is real, not
  approximate — the geometric picture is mathematically exact, not schematic.
- fig04/fig05: axis limits initially clipped the L1 diamond (t≈1.46 > xlim
  start of -1); widened both to (-2, 5) and re-ran.
- fig02: validation error clipped at 5 for high-degree fits to keep the log
  y-axis readable.

## [2026-07-21] Step 4: Slides — chunk 0
**Result:** slides.tex created with preamble (title/subtitle/author/institute
filled from AGENTS.md, date = \today) + title slide (01) + outline slide (02).
**Status:** in progress — content slides 3–19 pending via
`/course-maker slides 1 next`.

## [2026-07-21] Step 4: Slides — chunk 1 (slides 3–7)
**Result:** appended slides 3–7 (overfitting motivation, bias-variance
formula, train/val error curves, regularization definition, ridge L2
objective). fig01 and fig02 referenced (both exist in figures/).
**Status:** in progress — slides 8–19 pending via `/course-maker slides 1 next`.

## [2026-07-21] Step 4: Slides — chunk 2 (slides 8–12)
**Result:** appended slides 8–12 (ridge shrinkage, L2 geometry, lasso L1
objective, L1 geometry/sparsity, ridge-vs-lasso comparison table). fig03,
fig04, fig05 referenced (all exist in figures/). Dropped an initial draft
phrase on slide 10 ("...consequence, next") for violating the no-forward-
reference rule; rewrote without it.
**Status:** in progress — slides 13–19 pending via `/course-maker slides 1 next`.

## [2026-07-21] Step 4: Slides — chunk 3 (slides 13–17)
**Result:** appended slides 13–17 (choosing λ via cross-validation, prior-belief
bridge, MAP Ridge/Gaussian derivation, MAP Lasso/Laplace derivation, unifying
recap of the three lenses). fig06 referenced (exists in figures/).
**Status:** in progress — slides 18–19 (elastic net teaser + closing) pending
via `/course-maker slides 1 next`.

## [2026-07-21] Step 4: Slides — chunk 4 (slides 18–19, final)
**Result:** appended slide 18 (elastic net teaser, announce-only) and slide 19
(summary & closing) + `\end{document}`. Deck complete, 19/19 slides.
**Decision:** plan.md's slide 18 description said "...next lecture" but the
forward-reference rule caps next-lecture mentions at 1, only on the closing
slide. Dropped the "next lecture" phrase from slide 18 (teased the elastic
net concept without saying when it's covered) and kept the single allowed
mention on slide 19's closing line instead. Verified via grep: no other
forward-reference language anywhere else in the deck.
**Compilation check:** ran `pdflatex slides.tex` (x2, to settle cross-refs).
First run failed — `t2aenc.def` (Cyrillic T2A encoding) not available in this
sandbox and no network access to install `texlive-lang-cyrillic`. Since the
course is English-only, switched `\usepackage[T2A]{fontenc}` to
`[T1]{fontenc}` in both this deck and the course-root `slides_preamble.tex`
(so Lecture 2 doesn't hit the same failure). Second run: exit 0, 19 pages,
zero overfull/underfull warnings. Rendered pages to PNG and spot-checked
title, bias-variance, both geometry slides, CV slide, and closing slide —
all laid out cleanly, no clipped images or text.

## [2026-07-21] Step 5: Speaker notes
**Result:** speaker_notes.md written for all 19 slides + timing table + what-
can-be-cut, in one pass (auto-chained per step 5's no-per-chunk-approval
rule). English, matching AGENTS.md course language.
**Fix:** initial draft had a "next lecture" mention on slide 1 in addition to
slide 19's closing mention — violated the max-1/closing-slide-only rule.
Removed it from slide 1; verified via grep that only the closing-slide
mention remains.

## [2026-08-06] Revision: Outline slide (Slide 2) was rendering empty

**User feedback:** outline slide is empty in both lectures.
**Root cause:** slide 2 used `\tableofcontents`, but the deck never contains
any `\section{}` commands, so there was nothing for Beamer to list.
**Fix:** replaced `\tableofcontents` with a plain 4-item bullet list matching
this lecture's own timing-table blocks from `speaker_notes.md` ("Why
regularize", "Ridge & Lasso mechanics", "Tuning & Bayesian view", "Teaser &
wrap-up") — reused verbatim rather than invented, for full traceability.
Chose this over adding real `\section{}` markers because the Madrid theme
would then render a section-navigation header bar on every slide, a much
bigger visual change than fixing the outline alone.
**Verification:** recompiled (pdflatex ×2) — clean, exit 0, 19 pages, zero
overfull/underfull. Rendered slide 2 to PNG and visually confirmed the
bullets render correctly with no clipping.
