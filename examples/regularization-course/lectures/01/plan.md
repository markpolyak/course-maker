# Lecture 1 — Regularization Foundations

**Total time:** 90 min
**Slides:** 19

---

## Slide plan

| # | Title | Content summary | Time |
|---|-------|------------------|------|
| 1 | Title slide | — | 1 min |
| 2 | Outline | — | 1 min |
| 3 | Why do models overfit? | Motivating example: polynomial fits of increasing degree [figure] | 4 min |
| 4 | The bias-variance tradeoff | Formal decomposition of expected test error [formula] | 5 min |
| 5 | Overfitting in numbers | Train vs. test error as a function of model complexity [figure] | 5 min |
| 6 | What is regularization? | Intuition: constrain/penalize the hypothesis space instead of shrinking the model by hand | 4 min |
| 7 | Ridge regression: the L2 penalty | Objective function with squared-norm penalty [formula] | 4 min |
| 8 | Ridge: effect on coefficients | Shrinkage of coefficient magnitudes as λ grows [figure] | 5 min |
| 9 | Geometric picture: L2 | Constrained optimization view — elliptical loss contours vs. circular constraint [figure] | 5 min |
| 10 | Lasso regression: the L1 penalty | Objective function with L1-norm penalty [formula] | 4 min |
| 11 | Geometric picture: L1 and sparsity | Diamond-shaped constraint region — why corners induce exact zeros [figure] | 6 min |
| 12 | Ridge vs. Lasso | Side-by-side comparison: sparsity, correlated features, uniqueness of solution | 4 min |
| 13 | Choosing the regularization strength λ | Regularization path + role of cross-validation [figure] | 8 min |
| 14 | Regularization as prior belief | Bridge to the Bayesian view: penalty ⟷ prior on parameters | 4 min |
| 15 | MAP interpretation: Ridge ⟷ Gaussian prior | Deriving L2 penalty from a Gaussian prior via MAP estimation [formula] | 6 min |
| 16 | MAP interpretation: Lasso ⟷ Laplace prior | Deriving L1 penalty from a Laplace prior via MAP estimation [formula] | 6 min |
| 17 | Putting it together | Recap: regularization = complexity control = prior belief | 4 min |
| 18 | Beyond L1/L2 (announce only) | One-slide teaser: elastic net combines both — full treatment next lecture | 2 min |
| 19 | Summary & closing | Key takeaways; one pointer forward to the lab applying these methods | 4 min |

**Buffer:** ~8 min

---

## Detailed descriptions

### Slide 3 — Why do models overfit?
Show three polynomial fits (degree 1, degree ~4, degree ~15) to a small, noisy
dataset generated from a smooth underlying function, side by side or as three
panels. The degree-1 fit underfits (high bias, misses the curve); the
degree-4 fit tracks the underlying trend well; the degree-15 fit wiggles
through every training point. Emphasize: more parameters means more capacity
to memorize noise, not necessarily to generalize better. [figure]

### Slide 4 — The bias-variance tradeoff
Present the decomposition of expected test error into Bias² + Variance +
Irreducible noise. [formula] Walk through what each term means intuitively:
bias is systematic error from a model that's too simple to capture the true
pattern; variance is sensitivity to the particular training sample drawn.
State plainly that regularization is a tool for trading a small increase in
bias for a larger reduction in variance, which can lower total test error.

### Slide 5 — Overfitting in numbers
Plot training error (monotonically decreasing) and validation/test error
(U-shaped) against model complexity (e.g., polynomial degree or number of
features) on the same axes. Mark the point of minimum validation error and
shade the region to its right as the "overfitting zone," where training error
keeps falling but test error rises. [figure]

### Slide 6 — What is regularization?
Define regularization as any technique that discourages a model from fitting
the training data too closely, without changing the model family, typically
by adding a penalty or constraint tied to model complexity. Contrast with the
naive alternative of manually choosing a simpler model (e.g., fewer features
by hand): regularization lets the data — via a tunable strength — decide how
much complexity is actually warranted.

### Slide 7 — Ridge regression: the L2 penalty
Present the ridge objective: minimize the residual sum of squares plus λ
times the squared L2 norm of the coefficient vector. [formula] Explain λ as a
knob: λ = 0 recovers ordinary least squares exactly; as λ → ∞, all
coefficients are pushed toward zero. Note that the intercept is conventionally
left out of the penalty.

### Slide 8 — Ridge: effect on coefficients
Show a coefficient-shrinkage plot: several coefficient trajectories (one line
per feature) as λ sweeps from 0 to a large value, all shrinking smoothly and
continuously toward — but essentially never exactly reaching — zero.
Emphasize "smoothly" and "rarely exactly zero"; this sets up the contrast
with Lasso two slides later. [figure]

### Slide 9 — Geometric picture: L2
Show elliptical contours of the unregularized least-squares loss overlaid
with a circular constraint region (the L2 ball) in 2D coefficient space. The
ridge solution sits where the smallest loss contour just touches the circle.
Emphasize that because a circle has no corners, that tangency point generically
has both coordinates nonzero — the geometric reason ridge doesn't produce
sparse solutions. [figure]

### Slide 10 — Lasso regression: the L1 penalty
Present the lasso objective: residual sum of squares plus λ times the L1 norm
(sum of absolute values) of the coefficient vector. [formula] Contrast
directly with slide 7: same overall idea (penalize the loss), different norm.

### Slide 11 — Geometric picture: L1 and sparsity
Same loss contours as slide 9, now overlaid with a diamond-shaped L1
constraint region. Show that the loss contour typically first touches the
diamond at one of its corners, where one coordinate is exactly zero. This is
the geometric reason lasso performs automatic feature selection — a direct
payoff contrast with slide 9's circle. [figure]

### Slide 12 — Ridge vs. Lasso
Comparison table/summary covering: sparsity (lasso yes, ridge no); behavior
with correlated features (ridge shrinks correlated coefficients together,
lasso tends to arbitrarily pick one and zero the other); uniqueness of the
solution (ridge is always unique, lasso may not be under strong correlation);
computational form (ridge has a closed-form solution, lasso requires
iterative methods like coordinate descent). Frame as practical guidance for
"which to reach for."

### Slide 13 — Choosing the regularization strength λ
Show a regularization path plot: coefficient values (or validation error) as
a function of λ on a log scale, sweeping from near-zero to strong
regularization. Explain that λ is a hyperparameter, not learned from the
training objective directly — it is selected via cross-validation, by
evaluating held-out performance across a grid of λ values and choosing the
one that minimizes validation error. [figure]

### Slide 14 — Regularization as prior belief
Bridge slide: introduce the idea that adding a penalty term to the loss is
mathematically equivalent to placing a prior distribution over the
parameters and computing the maximum a posteriori (MAP) estimate. This
reframes "penalty strength" as "how strongly we believe, before seeing any
data, that coefficients should be small."

### Slide 15 — MAP interpretation: Ridge ⟷ Gaussian prior
Derive that if each coefficient is given an independent zero-mean Gaussian
prior, the negative log-posterior — up to an additive constant — equals the
least-squares loss plus a term proportional to the squared L2 norm: exactly
the ridge objective. [formula] Emphasize that the Gaussian prior is
symmetric and "soft" around zero, which is the probabilistic reason ridge
shrinks smoothly rather than zeroing out coefficients.

### Slide 16 — MAP interpretation: Lasso ⟷ Laplace prior
Derive that if each coefficient is given an independent zero-mean Laplace
(double-exponential) prior, the negative log-posterior equals the
least-squares loss plus a term proportional to the L1 norm: exactly the
lasso objective. [formula] Emphasize that the Laplace prior has a sharp peak
at zero, which is the probabilistic reason lasso favors exact zeros — the
same conclusion as the geometric picture on slide 11, now from a different
angle.

### Slide 17 — Putting it together
Recap slide, no new content: regularization is simultaneously a complexity
control (bias-variance lens), a geometric constraint (L2 ball vs. L1
diamond), and a Bayesian prior (Gaussian vs. Laplace) — three equivalent ways
of understanding the same mechanism. Encourage students to keep whichever
lens they find most intuitive; all three give the same answer.

### Slide 18 — Beyond L1/L2 (announce only)
One slide, no derivation. Mention that combining both penalties — elastic
net — gets some of the sparsity of lasso together with the stability of
ridge under correlated features, and that this technique, along with
regularization approaches specific to deep learning, is the subject of the
next lecture.

### Slide 19 — Summary & closing
Bullet recap of the three lenses (bias-variance, geometric, Bayesian) and the
two core methods (ridge, lasso). Include exactly one forward pointer, phrased
naturally: "Next lecture, we'll extend these ideas to elastic net and to
regularization techniques used in deep learning, before applying all of this
hands-on in the lab."

---

## Timing table

| Block | Slides | Time |
|-------|--------|------|
| Block 1: Why regularize | 1–6 | 19 min |
| Block 2: Ridge & Lasso mechanics | 7–12 | 28 min |
| Block 3: Tuning & Bayesian view | 13–17 | 28 min |
| Block 4: Teaser & wrap-up | 18–19 | 6 min |
| Buffer / questions | — | 8 min |
| **Total** | | **~90 min** |

## Cut candidates
- Slide 9 or 11 (geometric pictures): if time-constrained, keep only the L1
  diamond (it's the one that explains sparsity) and cover the L2 picture
  verbally instead.
- Slide 17 (Putting it together): can be compressed into the closing slide
  if running long.
