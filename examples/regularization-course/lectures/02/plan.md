# Lecture 2 — Regularization in Practice & Deep Learning

**Total time:** 90 min
**Slides:** 19

---

## Slide plan

| # | Title | Content summary | Time |
|---|-------|------------------|------|
| 1 | Title slide | — | 1 min |
| 2 | Outline | — | 1 min |
| 3 | Recap: three lenses on regularization | Quick refresher of bias-variance / geometric / Bayesian views from Lecture 1 | 3 min |
| 4 | Elastic net: the objective | Combining L1 + L2 penalties [formula] | 5 min |
| 5 | Elastic net: the grouping effect | Behavior under correlated features vs. pure ridge/lasso [figure] | 6 min |
| 6 | Elastic net: practical guidance | Blend parameter, when to reach for it | 3 min |
| 7 | Regularizing deep networks: why it's different | Overparameterization, classical penalties alone often aren't enough | 4 min |
| 8 | Early stopping: the idea | Halt training when validation loss stops improving [figure] | 6 min |
| 9 | Early stopping: why it's a regularizer | Bounds how far weights wander from initialization | 5 min |
| 10 | Dropout: the mechanism | Randomly zeroing units during training [figure] | 6 min |
| 11 | Dropout: why it works | Prevents co-adaptation; ensemble-of-subnetworks interpretation | 5 min |
| 12 | Dropout: train vs. test time | Inverted dropout, activation scaling [formula] | 4 min |
| 13 | Data augmentation: the idea | Label-preserving transformations expand the effective dataset [figure] | 6 min |
| 14 | Data augmentation: as regularization | Why synthetic variation reduces overfitting | 4 min |
| 15 | Batch normalization: the mechanism | Normalizing layer activations per mini-batch [formula] | 6 min |
| 16 | Batch normalization: as implicit regularizer | Mini-batch noise has a regularizing side effect | 4 min |
| 17 | The full toolkit: a comparison table | Classical vs. deep-learning regularizers, side by side | 5 min |
| 18 | Choosing in practice | Techniques are usually combined, not exclusive; rules of thumb | 4 min |
| 19 | Summary & closing | Key takeaways; one pointer forward to the lab | 4 min |

**Buffer:** ~8 min

---

## Detailed descriptions

### Slide 3 — Recap: three lenses on regularization
Brief refresher, no new content: regularization from Lecture 1 can be
understood as (1) a bias-variance trade that reduces test error, (2) a
geometric constraint on the coefficient vector, (3) a Bayesian prior belief
about coefficient size. State this in one or two sentences per lens, purely
as a bridge — the goal is to reactivate the mental model before extending it,
not to re-derive anything.

### Slide 4 — Elastic net: the objective
Present the elastic net objective: least-squares loss plus a weighted
combination of the L1 and L2 penalties, λ₁‖β‖₁ + λ₂‖β‖₂². [formula] Frame it
explicitly as interpolating between lasso (λ₂ = 0) and ridge (λ₁ = 0) — this
was teased at the end of Lecture 1; this slide delivers the full objective.

### Slide 5 — Elastic net: the grouping effect
Show a grouped bar chart: for a pair of strongly correlated features, plot
the fitted coefficient of each feature under ridge, lasso, and elastic net
side by side. Ridge assigns them nearly equal (shared) weight; lasso
arbitrarily picks one and zeroes the other; elastic net keeps both nonzero
but shrinks them together — a compromise. This is called the "grouping
effect": correlated features tend to get similar coefficients under elastic
net, unlike lasso. [figure]

### Slide 6 — Elastic net: practical guidance
No figure. Practical rule of thumb: elastic net is the default choice when
you have many correlated features and also suspect some are irrelevant —
it's rarely strictly worse than ridge or lasso alone, at the cost of one
extra hyperparameter (the blend between λ₁ and λ₂) to tune via
cross-validation.

### Slide 7 — Regularizing deep networks: why it's different
Bridge slide, no figure. Deep networks are typically massively
overparameterized (far more weights than training examples), so classical
weight-norm penalties still apply. Explicitly explain **weight decay** as the
deep-learning name for L2 regularization: show the gradient-descent update
rule w ← w − η(∇L(w) + λw) = (1 − ηλ)w − η∇L(w), and interpret it as directly
shrinking w by (1 − ηλ) each step — the same ridge penalty from Lecture 1,
now applied via the optimizer instead of solved in closed form. Caveat: this
exact equivalence holds for plain gradient descent; adaptive optimizers like
Adam decouple weight decay from the gradient scaling (AdamW), which is out
of scope for this course. Still often not sufficient alone — motivates a
family of regularization techniques specific to how neural networks are
trained: early stopping, dropout, data augmentation, and batch
normalization.

### Slide 8 — Early stopping: the idea
Show training loss decreasing monotonically over epochs, and validation loss
decreasing then turning upward, with the stopping point (minimum validation
loss) marked. Early stopping means simply halting training at that point,
even though more epochs would keep reducing training loss further. [figure]

### Slide 9 — Early stopping: why it's a regularizer
No figure. Explain the mechanism: weights start near initialization (often
near zero) and move further from it as training progresses, effectively
exploring a larger hypothesis space over time. Stopping early caps how far
the weights travel, which behaves similarly — in a rough, informal sense —
to bounding the norm of the weights the way an explicit penalty would.

### Slide 10 — Dropout: the mechanism
Schematic diagram of a small feedforward network (2–3 layers) where, during
one training step, some fraction of hidden units are randomly dropped
(shown crossed out or greyed out), leaving only the remaining active units
connected. A different random subset is dropped at every training step.
[figure]

### Slide 11 — Dropout: why it works
No figure. Two complementary explanations: (1) it prevents units from
co-adapting — relying too heavily on the exact presence of specific other
units — because any unit might vanish at any step; (2) training with dropout
is approximately equivalent to training and averaging an ensemble of many
different thinned subnetworks that share weights.

### Slide 12 — Dropout: train vs. test time
Present inverted dropout: during training, each unit is kept with
probability p and its output divided by p (so its expected output magnitude
matches test time). [formula] At test time, dropout is turned off entirely
and no scaling is applied — this is the standard modern convention, as
opposed to the older approach of scaling weights only at test time.

### Slide 13 — Data augmentation: the idea
Show one original training photo (a real image, `skimage.data.cat()`)
alongside several augmented versions of it — rotated, flipped, shifted,
brightness-jittered — all sharing the same label. Emphasize
"label-preserving": the transformation must not change what the correct
answer is. [figure]

### Slide 14 — Data augmentation: as regularization
No figure. Framing: augmentation doesn't add new information about the
world, but it does teach the model which variations shouldn't matter for the
task, which shrinks the effective hypothesis space toward functions that are
invariant to those transformations — conceptually similar to constraining
the model, just enforced through the data rather than through the loss.

### Slide 15 — Batch normalization: the mechanism
Present the batch normalization transform: for each mini-batch, normalize
each activation to zero mean and unit variance using the batch's own
statistics, then apply a learned scale and shift. [formula] Emphasize that
the scale and shift parameters let the network undo the normalization if
that's what's optimal — batch norm doesn't remove the network's expressive
power, it just changes the optimization landscape.

### Slide 16 — Batch normalization: as implicit regularizer
No figure. Because the normalization statistics (mean, variance) are
computed from a randomly sampled mini-batch rather than the full dataset,
each example is normalized slightly differently depending on which batch it
lands in — this injects a small amount of noise into training, similar in
spirit to dropout, which has an incidental regularizing effect even though
batch norm's primary purpose is optimization stability, not regularization.

### Slide 17 — The full toolkit: a comparison table
Table comparing the techniques covered across both lectures: ridge, lasso,
elastic net, early stopping, dropout, data augmentation, batch norm.
Columns: what it constrains/perturbs, one extra hyperparameter it
introduces, and whether it requires changing the training loop vs. just the
loss function. No figure — this is a dense reference table, best as text.
Batch norm's hyperparameter cell reads "(usually none)" with a footnote
clarifying that γ and β are learned via backprop like ordinary weights, not
tuned hyperparameters — avoids the reader mistaking them for an omitted
hyperparameter, consistent with how they were already introduced on slide 15.

### Slide 18 — Choosing in practice
No figure. Key message: these techniques are not mutually exclusive — a
typical modern training setup combines several at once (e.g. weight decay +
dropout + data augmentation + early stopping, simultaneously). Give a short
practical checklist: start with weight decay and early stopping as
low-cost defaults, add dropout for large fully-connected layers, add
augmentation whenever label-preserving transformations exist for the data
type, and always validate strength/rate choices via cross-validation or a
held-out set.

### Slide 19 — Summary & closing
Bullet recap of the two families covered today (elastic net closing the
classical-methods story; early stopping, dropout, augmentation, and batch
norm for deep networks) and the unifying idea that all of them trade a
little bias for less variance, just through different mechanisms. Include
exactly one forward pointer: "Now let's put this whole toolkit to work in
the lab."

---

## Timing table

| Block | Slides | Time |
|-------|--------|------|
| Block 1: Closing the elastic net loop | 1–6 | 19 min |
| Block 2: Early stopping & dropout | 7–12 | 30 min |
| Block 3: Data augmentation & batch norm | 13–16 | 20 min |
| Block 4: Synthesis & wrap-up | 17–19 | 13 min |
| Buffer / questions | — | 8 min |
| **Total** | | **~90 min** |

## Cut candidates
- Slide 6 (elastic net practical guidance): can be folded into slide 18's
  comparison/rules-of-thumb discussion if running long.
- Slide 9 (early stopping, why it's a regularizer): can be compressed to 2
  sentences on slide 8 if time-constrained — the mechanism (slide 8) matters
  more than the theoretical justification for an applied audience.
