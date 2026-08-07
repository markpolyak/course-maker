# Lecture 2 — History

## [2026-07-21] Step 1: Plan — iteration 1
**Result:** plan.md created (19 slides, 90 min)
**User feedback:** Approved without changes on first draft.
**Decision:** Structure = 4 blocks (closing the elastic net loop → early
stopping/dropout → data augmentation/batch norm → synthesis + wrap-up).
Elastic net gets full treatment here (was announce-only in Lecture 1, per
course_plan.md). Single forward reference (to the lab) placed on closing
slide 19 only.

## [2026-07-21] Step 2: Visuals — iteration 1
**Result:** visuals.md created (4 figures, V01–V04; 3 need Python, 1 is TikZ)
**User feedback:** Approved without changes.
**Decision:** V03 (dropout mechanism) classified as TikZ "Yes" — it's a pure
schematic network diagram with no data dependency, unlike the geometric
contour figures in Lecture 1 which needed exact computed data.

## [2026-07-21] Step 3: Figures — iteration 1
**Result:** figures.py created and run clean; fig01, fig02, fig04 generated
and verified visually (fig03/V03 is TikZ, deferred to slides.tex in Step 4).
**Decisions:**
- Generalized Lecture 1's lasso coordinate-descent into an elastic-net
  coordinate descent (lasso is now the lam2=0 special case) — reused on the
  same correlated-feature data as Lecture 1's fig04/fig05 for continuity.
  λ₁=λ₂=40 chosen so elastic net visibly keeps both coefficients nonzero
  (unlike lasso's exact zero) while shrinking more than ridge — confirmed
  numerically before finalizing: ridge=[2.57, 1.76], lasso=[1.46, 0.0],
  elastic net=[1.17, 0.91].
- fig02: synthetic train/val loss curves (exponential decay + a validation-
  only overfitting term kicking in after epoch ~18); early-stopping point
  found via argmin, not hardcoded.
- fig04: built a synthetic "circle" image from scratch in numpy (no external
  dataset) with an asymmetric marker patch so rotation/flip/shift are
  visually distinguishable in a static figure.

## [2026-07-21] Step 4: Slides — chunk 0
**Result:** slides.tex created with preamble (title/subtitle/author/institute
filled from AGENTS.md, date = \today) + title slide (01) + outline slide (02).
Used T1 fontenc directly (not T2A) from the start, matching the fix already
applied to Lecture 1 and the course-root slides_preamble.tex.
**Status:** in progress — content slides 3–19 pending via
`/course-maker slides 2 next`.

## [2026-07-21] Step 4: Slides — chunk 1 (slides 3–7)
**Result:** appended slides 3–7 (three-lenses recap, elastic net objective,
grouping effect, practical guidance, deep-net motivation). fig01 referenced
(exists in figures/).
**Status:** in progress — slides 8–19 pending via `/course-maker slides 2 next`.

## [2026-07-21] Step 4: Slides — chunk 2 (slides 8–12)
**Result:** appended slides 8–12 (early stopping idea + regularizer
justification, dropout mechanism via TikZ diagram, why dropout works,
inverted-dropout train/test scaling). fig02 referenced (exists in figures/).
**Verification:** mid-chunk, compiled a throwaway copy (`slides_check.tex`,
appended `\end{document}`) to sanity-check the TikZ dropout diagram
specifically, since hand-written TikZ is the most error-prone element in this
deck. Compiled clean (exit 0, 12 pages, zero overfull/underfull), and the
rendered diagram looks correct — two greyed-out crossed-out units with no
connections, active units fully wired. (Could not delete the throwaway
`slides_check.*` files afterward — sandbox filesystem permissions block
`rm` on them — so they're left alongside `slides.tex`; harmless scratch
output, not part of the deck.)
**Status:** in progress — slides 13–19 pending via `/course-maker slides 2 next`.

## [2026-07-21] Step 4: Slides — chunk 3 (slides 13–17)
**Result:** appended slides 13–17 (data augmentation idea + regularization
framing, batch norm mechanism + implicit-regularizer framing, and a 7-row
comparison table spanning both lectures' techniques). fig04 referenced
(exists in figures/). Table uses `\small` for the 7×4 grid — fits comfortably
without needing `[shrink]`.
**Status:** in progress — slides 18–19 (choosing in practice + closing)
pending via `/course-maker slides 2 next`.

## [2026-07-21] Step 4: Slides — chunk 4 (slides 18–19, final)
**Result:** appended slide 18 (choosing in practice) and slide 19 (summary &
closing, with the single forward reference "Now let's put this whole toolkit
to work in the lab") + `\end{document}`. Deck complete, 19/19 slides.
Verified via grep: no other forward-reference language anywhere in the deck.
**Compilation check:** ran `pdflatex slides.tex` (x2, to settle cross-refs).
Clean on first attempt this time (T1 fontenc fix was already applied from
chunk 0) — exit 0, 19 pages, zero overfull/underfull warnings. Rendered
pages 17–19 (the dense comparison table and the closing slide) to PNG and
confirmed both are laid out cleanly with no clipping. Could not delete
LaTeX build artifacts (`slides.aux`, `.log`, etc.) or the earlier
`slides_check.*` scratch files due to sandbox filesystem permissions — left
in place, harmless.

## [2026-07-21] Step 5: Speaker notes
**Result:** speaker_notes.md written for all 19 slides + timing table +
what-can-be-cut, in one pass (auto-chained per step 5's no-per-chunk-approval
rule). English, matching AGENTS.md course language. Checkpoint minutes
computed precisely from plan.md's per-slide time column (cumulative time
elapsed before each checkpointed slide begins), not estimated.
**Verification:** grepped for forward-reference language before finalizing —
clean on the first pass this time (learned from Lecture 1's slide-1 mistake):
only one forward-looking line exists, on the closing slide, pointing to the
lab (not "next lecture," since this is the last lecture before it).

## [2026-08-06] Revision: Slide 7 — explicit weight decay explanation

**User feedback:** "weight decay" was mentioned on slide 7 (bridge slide) and
slide 18 (practical checklist) and equated to L2 regularization, but only via
a bare one-line parenthetical — never actually explained, unlike ridge's full
geometric + Bayesian treatment in Lecture 1. Asked whether to add an
explanation or remove the term.
**Decision:** Add explanation rather than remove — reasoning: (1) slide 7 is
already the deliberate bridge from Lecture 1's L2 treatment into the DL
section, so this is exactly where the "same concept, new name" connection
belongs; (2) slide 18 depends on the term already being explained; (3) it's
the literal PyTorch/TensorFlow optimizer argument name — high practical
payoff; (4) the prior one-liner violated AGENTS.md's own style rule
("formulas always with interpretation, never just the formula alone").
**Change:** Slide 7 (`slides.tex`) expanded from 3 sparse bullets into 2
itemize blocks + a displayed gradient-descent update rule
$w \leftarrow w - \eta(\nabla L(w) + \lambda w) = (1-\eta\lambda)w - \eta\nabla L(w)$,
with interpretation ("shrinks w by $(1-\eta\lambda)$ each step — the same
ridge penalty from Lecture 1, applied via the optimizer instead of solved in
closed form") and an explicit accuracy caveat: the equivalence is exact for
plain gradient descent only; adaptive optimizers like Adam decouple it
(AdamW), which is out of scope for this course. `plan.md`'s slide 7 entry and
`speaker_notes.md`'s slide 7 notes updated to match (including the same
caveat, delivered as a one-line aside). Slide 18's mention of weight decay
left as-is — now backed by a real explanation instead of dangling.
**Verification:** Recompiled `slides.tex` (pdflatex ×2) — clean, exit 0, 19
pages, zero overfull/underfull warnings (grep confirmed). Rendered slide 7 to
PNG and visually confirmed the expanded content fits cleanly with no
clipping or overflow. Scope unchanged: still 19 slides, no slide count or
timing-table changes needed. Could not delete the throwaway
`slide7_check-07.png` or refreshed LaTeX build artifacts afterward — same
sandbox filesystem permission restriction noted in the original Step 4 log;
harmless scratch output left in place.

## [2026-08-06] Revision: Outline slide (Slide 2) was rendering empty

**User feedback:** outline slide is empty in both lectures.
**Root cause:** slide 2 used `\tableofcontents`, but the deck never contains
any `\section{}` commands, so there was nothing for Beamer to list.
**Fix:** replaced `\tableofcontents` with a plain 4-item bullet list matching
this lecture's own timing-table blocks from `speaker_notes.md` ("Closing the
elastic net loop", "Early stopping & dropout", "Data augmentation & batch
norm", "Synthesis & wrap-up") — reused verbatim rather than invented, for
full traceability. Chose this over adding real `\section{}` markers because
the Madrid theme would then render a section-navigation header bar on every
slide, a much bigger visual change than fixing the outline alone.
**Verification:** recompiled (pdflatex ×2) — clean, exit 0, 19 pages, zero
overfull/underfull. Rendered slide 2 to PNG and visually confirmed the
bullets render correctly with no clipping.

## [2026-08-06] Revision: Slide 17 — footnote clarifying batch norm's γ, β

**User feedback:** the comparison table's "Extra hyperparameter" column says
"(usually none)" for batch norm — are γ and β not hyperparameters?
**Decision:** add a footnote rather than change the table's verdict. γ and β
are learned via backprop like ordinary weights (already stated on slide 15),
so they are correctly excluded from a "hyperparameter" column — but a reader
looking only at slide 17 in isolation could reasonably wonder why they're
missing. A one-line footnote resolves the ambiguity without changing the
table's content or complicating it with an asterisked exception clause.
**Change:** `slides.tex` slide 17 — table cell now reads
"(usually none)$^*$" with a `\scriptsize` footnote below the table:
"$\gamma, \beta$ are learned via backprop like ordinary network weights ---
not tuned hyperparameters." `plan.md` and `speaker_notes.md` slide 17 entries
updated to match (notes add a short spoken aside pointing at the footnote).
**Verification:** recompiled (pdflatex ×2) — clean, exit 0, 19 pages, zero
overfull/underfull. Rendered slide 17 to PNG and visually confirmed the
footnote fits cleanly below the table with no crowding or clipping.

## [2026-08-06] Revision: Slide 13 (fig04) — real photo instead of synthetic circle

**User feedback:** fig04 (data augmentation) looked bad — requested a real
image, e.g. `skimage.data.cat()`.
**Change:** `figures/figures.py`'s `fig04_data_augmentation()` rewritten to
use `skimage.data.cat()` (a real sample photo bundled directly in the
scikit-image package — no network access needed at runtime) instead of the
hand-drawn synthetic filled-circle image. Removed the now-unused
`_make_base_image()` helper. Augmentations kept conceptually the same
(rotate/flip/shift/brightness) but implemented via `skimage.transform.rotate`
and `img_as_float` for a real RGB image instead of a binary mask. New
dependency noted in the file's module docstring: `pip install scikit-image`.
Updated `visuals.md` (V04 description + TikZ column), `plan.md` (slide 13
description), and `speaker_notes.md` (slide 13's "same circle" →  "same cat")
to match — figure caption also changed from "circle" to "cat".
**Verification:** ran `figures/figures.py` — clean run, `fig04_data_augmentation.png`
regenerated and visually inspected (real cat photo, all 5 panels clearly the
same subject, no artifacts). Recompiled `slides.tex` (pdflatex ×2) — clean,
exit 0, 19 pages, zero overfull/underfull. Rendered slide 13 to PNG and
confirmed the new figure fits the existing `height=0.5\textheight` constraint
cleanly with no clipping.
