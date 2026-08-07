# Lecture 2 — Speaker notes

**Total time:** 90 min

---

## Slide 1 — Title slide

Welcome back. Last time we built the foundations — bias-variance, ridge, lasso, and three different lenses for understanding regularization. Today we close that loop and then head into deep-learning-specific techniques.

[*Pause while students settle in.*]

By the end of today, you'll have the full regularization toolkit in hand.

---

## Slide 2 — Outline

Here's today's shape. [*Point to each item as you name it.*] We start by finishing elastic net — the technique we teased at the end of last lecture — then move into the deep-learning side: early stopping, dropout, data augmentation, and batch normalization. We'll close by putting everything side by side.

---

## Slide 3 — Recap: three lenses on regularization

⏱ *Checkpoint: ~2 min from the start*

Quick refresher before we build on it. [*Point to each bullet.*] Bias-variance: a little more bias buys a lot less variance. Geometric: coefficients are squeezed into a norm ball — a circle for L2, a diamond for L1. Bayesian: the penalty is really a prior belief about coefficient size.

[*Pause.*] Keep all three in your back pocket — we're about to extend this same thinking in a new direction.

---

## Slide 4 — Elastic net: the objective

Let's close the loop. [*Point to the objective.*] Elastic net just adds both penalties together — L1 and L2, each with its own strength.

Set λ₂ to zero and you're back to lasso. Set λ₁ to zero and you're back to ridge. Everything in between is a genuine blend of both.

---

## Slide 5 — Elastic net: the grouping effect

Here's why you'd actually want that blend. [*Point to the bar chart.*] Two features, strongly correlated with each other.

Ridge shrinks them together, roughly equally. Lasso zeros one out entirely, arbitrarily picking a winner. Elastic net keeps both alive, shrunk together — splitting the difference.

[*Pause.*] This is called the grouping effect, and it's the single biggest practical reason to reach for elastic net over lasso when your features are correlated.

---

## Slide 6 — Elastic net: practical guidance

So, when do you actually use it? [*Pause.*] Elastic net is close to a safe default whenever you have correlated features and you also suspect some of them are irrelevant. It's rarely strictly worse than ridge or lasso — you just pay for it with one more hyperparameter to tune: how much weight goes to each penalty.

---

## Slide 7 — Regularizing deep networks: why it's different

⏱ *Checkpoint: ~19 min from the start*

That closes the classical story. Now — deep networks. [*Pause.*] These models are often absurdly overparameterized: millions of weights, sometimes more parameters than training examples.

Classical weight-norm penalties still apply here, just under a new name: **weight decay**. [*Point to the update rule.*] Every gradient step, you subtract the gradient of the loss *and* a small multiple of the weight itself — which you can regroup as multiplying w by (1 minus eta times lambda) before the usual gradient step. That's not an analogy to ridge regression — it's the exact same L2 penalty from Lecture 1, just applied one optimizer step at a time instead of solved in closed form.

[*Pause.*] One caveat, worth a sentence: this equivalence is exact for plain gradient descent. Adaptive optimizers like Adam actually decouple the two — that's specifically what "AdamW" fixes — but that's a level of detail beyond what we need today.

On its own, weight decay is often not enough. That's what motivates a whole family of techniques built around *how* you train the network, not just what loss function you use.

---

## Slide 8 — Early stopping: the idea

First technique: early stopping. [*Point to the curves.*] Training loss just keeps falling — of course it does, given enough epochs a big network can fit the training set almost perfectly.

Validation loss doesn't cooperate. It falls for a while, then turns around.

[*Point to the marked point.*] Early stopping is beautifully simple: just stop training right there, at the validation minimum, even though training loss would keep improving if you let it run.

---

## Slide 9 — Early stopping: why it's a regularizer

Why does this even count as regularization? [*Pause.*] Weights start near their initialization — often close to zero — and drift further away the longer you train. Stopping early puts a hard cap on how far that drift can go.

Loosely speaking, that's bounding the effective size of the weights — the same spirit as an explicit penalty, except you get it for free, just by training less.

---

## Slide 10 — Dropout: the mechanism

⏱ *Checkpoint: ~34 min from the start*

Second technique, and it's a strange one the first time you see it: dropout. [*Point to the diagram.*] At every single training step, we randomly switch off some fraction of the hidden units — here, the two greyed-out ones marked with an ×.

[*Point to the remaining connections.*] Only the surviving units and their connections get updated on this step. And crucially — a different random subset gets dropped on the very next step.

---

## Slide 11 — Dropout: why it works

Why does randomly deleting part of your network on every step make it better? [*Pause, let them think.*] Two ways to see it. First: no unit can lean on any specific other unit always being there, so the network can't build fragile, over-specific dependencies — that's preventing co-adaptation.

Second, more abstract view: this is roughly like training a huge ensemble of thinned-down subnetworks that all share the same weights, and averaging them. Both stories push toward the same place — more robust, more redundant representations.

---

## Slide 12 — Dropout: train vs. test time

One implementation detail that trips people up. [*Point to the formula.*] During training, each unit survives with probability p, and we rescale its output by 1 over p — that keeps the expected activation size unchanged whether or not a given unit happened to survive this step.

At test time, we just turn dropout off completely — no randomness, no rescaling needed. This combination is called inverted dropout, and it's the standard in every modern framework.

---

## Slide 13 — Data augmentation: the idea

⏱ *Checkpoint: ~49 min from the start*

Third technique — and this one doesn't touch the loss or the architecture at all, it touches the data. [*Point to the five images.*] Same image, five versions: rotated, flipped, shifted, brightness-adjusted.

[*Point to the caption.*] Every single one of these is still unambiguously a photo of the same cat. That's the whole requirement: the transformation has to be label-preserving.

---

## Slide 14 — Data augmentation: as regularization

Why does this count as regularization, if we're not touching the model at all? [*Pause.*] It doesn't add new information about the world — we already had that image. What it does is teach the model which kinds of variation it should ignore.

That effectively shrinks the space of functions the model is willing to consider, toward ones that don't care about rotation or brightness — conceptually the same move as constraining the model, just executed through the data instead of the loss function.

---

## Slide 15 — Batch normalization: the mechanism

⏱ *Checkpoint: ~59 min from the start*

Fourth and last technique: batch normalization. [*Point to the formula.*] For every mini-batch, we normalize each activation using that batch's own mean and variance — zero mean, unit variance — and then apply a learned scale and shift.

[*Point to gamma and beta.*] Those learned parameters matter: they mean the network can undo the normalization entirely if that turns out to be the optimal thing to do. We haven't taken away any expressive power, we've just reshaped the optimization landscape.

---

## Slide 16 — Batch normalization: as implicit regularizer

Here's the regularization angle, and it's a side effect rather than the main point. [*Pause.*] The mean and variance used for normalization come from whichever random mini-batch a given example happens to land in — so the exact same example gets normalized slightly differently depending on which batch it's grouped with.

That's a little bit of injected noise, every single step — in spirit, not unlike dropout. But to be clear: batch norm's primary job is making optimization more stable. The regularizing effect is a nice bonus, not the design goal.

---

## Slide 17 — The full toolkit: a comparison table

⏱ *Checkpoint: ~69 min from the start*

Let's put everything from both lectures side by side. [*Point to each row as you summarize it.*] Ridge and lasso constrain the coefficient norm directly. Elastic net blends both. Early stopping constrains training duration. Dropout perturbs which units are even present. Data augmentation perturbs the inputs. Batch norm perturbs the activation statistics.

[*Point to the footnote on the batch norm row.*] Quick clarification since it trips people up: batch norm's row says "usually none" for extra hyperparameters — that's not forgetting about gamma and beta. Those are learned via backprop exactly like any other weight in the network, so they don't count as a hyperparameter you'd tune the way you tune lambda or the dropout rate.

[*Pause.*] Notice the pattern in the last column: everything below elastic net actually changes your training loop, not just your loss function. That's the real dividing line between classical and deep-learning regularization.

---

## Slide 18 — Choosing in practice

So how do you actually decide what to use? [*Pause.*] Good news: you don't have to pick just one. A typical modern training setup stacks several of these at once.

Start with weight decay and early stopping — they're cheap and there's rarely a reason not to use them. Add dropout if you've got large fully-connected layers. Add augmentation whenever your data type has natural label-preserving transformations — images almost always do. And whatever strength or rate you pick for any of these, validate it — don't guess.

---

## Slide 19 — Summary & closing

⏱ *Checkpoint: ~78 min from the start*

Let's bring both lectures together. [*Point to each bullet.*] Elastic net closed out the classical story — a tunable blend of L1 and L2. Then four deep-learning techniques, each regularizing through a completely different mechanism: capping training time, randomly perturbing units, randomly perturbing inputs, or perturbing activation statistics.

[*Pause.*] Every single one of these, underneath, is doing the same basic trade we started with two lectures ago: a bit more bias, for a lot less variance.

[*Pause. Give students a moment to finish writing.*]

Now let's put this whole toolkit to work in the lab.

Thanks, everyone.

---

## Timing table

| Block | Slides | Time |
|-------|--------|------|
| Closing the elastic net loop | 1–6 | 19 min |
| Early stopping & dropout | 7–12 | 30 min |
| Data augmentation & batch norm | 13–16 | 20 min |
| Synthesis & wrap-up | 17–19 | 13 min |
| Buffer / questions | — | 8 min |
| **Total** | | **~90 min** |

## What can be cut

If time is short:
- Slide 6 (elastic net practical guidance) — fold into slide 18's rules-of-thumb discussion instead of standing alone.
- Slide 9 (early stopping, why it's a regularizer) — compress to two sentences delivered right after slide 8; the mechanism matters more than the justification for an applied audience.
