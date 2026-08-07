# Lecture 1 — Speaker notes

**Total time:** 90 min

---

## Slide 1 — Title slide

Good morning, everyone. Today we're starting a short but dense unit on regularization — how we keep models from memorizing their training data instead of learning from it.

[*Pause while students settle in.*]

By the end of today, you'll be able to look at a model that's overfitting and know exactly which knob to turn.

---

## Slide 2 — Outline

Here's the shape of today's session: four movements. [*Point to each item as you name it.*] Why models overfit, the two foundational penalties — ridge and lasso — how to actually choose the regularization strength, and the Bayesian view that ties everything together.

No need to memorize this now — just keep it as a mental map for where we are as we go.

---

## Slide 3 — Why do models overfit?

⏱ *Checkpoint: ~2 min from the start*

Let's start with a picture instead of a formula. [*Point to the three panels.*] Same data, three different polynomials fit to it.

On the left, a straight line — it just can't bend to follow the curve. That's underfitting: the model is too simple.

On the right, a degree-15 polynomial. Look how it swings wildly near the edges just to pass through every single point exactly. It's not learning the pattern — it's memorizing the noise.

The middle one is what we want: close to the true curve, without chasing every wiggle in the data.

[*Pause. Let students look at the three panels.*]

So the question for today is: how do we get models to behave like the middle one, automatically — without manually picking the right polynomial degree by trial and error?

---

## Slide 4 — The bias-variance tradeoff

To answer that, we need one piece of theory. [*Point to the equation.*]

Expected test error splits cleanly into three pieces.

**Bias** is what you pay when your model is too simple — think of the straight line from the last slide, it's biased toward being flat.

**Variance** is what you pay when your model is too sensitive — retrain the degree-15 polynomial on a slightly different sample of data, and you'd get a wildly different curve.

And there's a floor, the irreducible noise — no model beats that.

[*Pause after introducing each term.*]

Here's the punchline for the rest of the lecture: regularization is a deliberate trade. We accept a little more bias in exchange for a lot less variance — and if we do it right, total error goes down.

---

## Slide 5 — Overfitting in numbers

Same idea, now quantified. [*Point to the two curves.*] Training error just keeps falling as the model gets more complex — of course it does, a more flexible model can always fit the training points better.

But look at validation error — it's U-shaped. It improves for a while, then turns around and gets worse.

[*Point to the shaded region.*] Everything past this point is the overfitting zone: the model is getting better at the training set and worse at everything else.

This gap between the two curves is really the entire diagnostic for overfitting — if you only remember one plot from today, remember this one.

---

## Slide 6 — What is regularization?

So what do we actually do about it? [*Pause, let the question hang for a second.*]

One option: just pick a simpler model by hand — fewer features, lower degree. That works, but it's crude, and it means you're guessing.

Regularization is the more elegant fix. [*Point to the definition box.*] We keep the full model family, but we add a penalty that discourages complexity — and we let a tunable strength decide how much complexity the data actually supports, rather than deciding that ourselves in advance.

This is the idea the rest of today builds on.

---

## Slide 7 — Ridge regression: the L2 penalty

⏱ *Checkpoint: ~19 min from the start*

Let's make this concrete. This is ridge regression. [*Point to the objective.*]

We still want to fit the data well — that's this first term, same as ordinary least squares. But now we add a second term: λ times the squared L2 norm of the coefficients.

**λ** is the whole story here. Set it to zero and you're back to plain least squares. Push it toward infinity and every coefficient gets crushed toward zero.

One small note: we don't penalize the intercept — that would just be penalizing the overall level of y, which isn't what we want.

---

## Slide 8 — Ridge: effect on coefficients

Let's see what that actually looks like. [*Point to the coefficient paths.*] Each line is one coefficient, plotted against λ.

Notice they all shrink smoothly as λ grows — and notice they never quite hit zero. That's the signature of ridge: every feature stays in the model, just with less and less influence.

[*Pause.*] Keep that "never exactly zero" property in mind — it's going to be the key contrast with lasso in a few minutes.

---

## Slide 9 — Geometric picture: L2

Here's a completely different way to see the same thing — geometrically. [*Point to the contour plot.*]

Ridge is mathematically the same as minimizing the loss, but restricted to a circle of some radius t. [*Trace the circle.*] The solution is wherever the smallest loss contour just touches that circle.

[*Point to the tangency point.*] And because a circle has no corners, that touching point almost always has both coordinates nonzero. That's the geometric reason ridge doesn't produce sparsity — there's simply nowhere on a smooth circle for a coordinate to land exactly on zero.

---

## Slide 10 — Lasso regression: the L1 penalty

Now let's change one thing. [*Point to the objective.*] Same idea — fit the data, penalize the coefficients — but now the penalty is the L1 norm: the sum of absolute values instead of the sum of squares.

It looks like a small change.

[*Pause.*] It is not a small change. This single swap is going to give us a fundamentally different kind of solution — let's see why.

---

## Slide 11 — Geometric picture: L1 and sparsity

Same geometric argument as before, different shape. [*Point to the diamond.*] The L1 constraint region is a diamond, not a circle.

[*Trace along an edge to a corner.*] Diamonds have corners — and it turns out the loss contour typically touches the diamond exactly at one of those corners.

[*Point to the marked solution point.*] At a corner, one coordinate is exactly zero. That's it — that's the entire mechanism behind lasso performing automatic feature selection. Not an approximation, not a rounding trick — it falls straight out of the geometry.

---

## Slide 12 — Ridge vs. Lasso

Let's put these side by side. [*Point to each row of the table.*]

Sparsity — lasso gives you it, ridge doesn't.

Correlated features — ridge shrinks them together, roughly equally; lasso will often pick one arbitrarily and zero out the other.

Uniqueness — ridge always has a unique solution; lasso can have ties when features are highly correlated.

And computationally, ridge has a closed form — one matrix solve. Lasso needs an iterative method.

[*Pause.*] As a rule of thumb: if you suspect a lot of your features are irrelevant, reach for lasso. If you think most features carry at least some signal, ridge is usually the safer default.

---

## Slide 13 — Choosing the regularization strength λ

⏱ *Checkpoint: ~47 min from the start*

One thing we've glossed over: where does λ actually come from? [*Pause.*] It's not learned by the training objective — if it were, the optimizer would just set λ to zero and overfit again.

Instead, λ is chosen by cross-validation. [*Point to the left panel.*] This is a regularization path — coefficients as λ sweeps from small to large. [*Point to the right panel.*] And this is the validation error for each λ. We just pick the λ at the bottom of this curve.

[*Point to the dashed line.*] That's not a guess — it's the λ where held-out performance is actually best.

---

## Slide 14 — Regularization as prior belief

Now, a shift in perspective — a Bayesian one. [*Point to the block.*]

Here's the claim: adding a penalty to the loss is mathematically identical to putting a prior distribution on the coefficients and finding the MAP estimate.

[*Pause, let that land.*] In plain language: "penalty strength" is really just "how strongly, before you've seen any data, you believe the coefficients should be small." Ridge and lasso are two different beliefs about how coefficients should behave — let's see exactly which beliefs.

---

## Slide 15 — MAP interpretation: Ridge ⟷ Gaussian prior

Suppose each coefficient has an independent Gaussian prior centered at zero. [*Point to the derivation.*] Work through Bayes' rule, take the negative log, and — up to a constant — you get exactly the ridge objective. The ratio σ²/τ² is standing in for λ.

[*Point to the bullet points.*] Why does this matter beyond being a cute derivation? Because the Gaussian is a soft, symmetric bell curve around zero — no sharp point at the origin. That's precisely why ridge shrinks smoothly and essentially never produces an exact zero. The math and the geometry are telling the same story.

---

## Slide 16 — MAP interpretation: Lasso ⟷ Laplace prior

Now do the same thing with a Laplace prior instead — same derivation, different distribution. [*Point to the formula.*] Same steps, and this time you land exactly on the lasso objective.

[*Point to the bullets.*] The Laplace distribution has a sharp peak right at zero — unlike the smooth Gaussian. That sharp peak is the probabilistic reason lasso favors exact zeros. Notice this is the very same conclusion as the diamond corner from the geometric picture — we've now arrived at it twice, from two completely different directions.

---

## Slide 17 — Putting it together

Let's zoom out. [*Point to each bullet as you say it.*] We've now seen regularization from three angles: it controls the bias-variance tradeoff, it constrains coefficients geometrically to a norm ball, and it encodes a Bayesian prior belief about coefficient size.

[*Pause.*] These aren't three different theories competing with each other — they're three views of the exact same mechanism. Use whichever one makes the most sense to you when you're reasoning about a new problem.

---

## Slide 18 — Beyond L1/L2: elastic net

⏱ *Checkpoint: ~75 min from the start*

One more idea before we close. [*Point to the objective.*] What if you combine both penalties? That's elastic net — you get some of lasso's sparsity and some of ridge's stability with correlated features, controlled by a blend parameter between the two.

[*Pause.*] I won't derive this one today — just wanted you to see the objective and recognize its shape.

---

## Slide 19 — Summary & closing

Let's bring it all together. [*Point to each bullet.*] Overfitting is fundamentally a complexity problem — models with too much capacity memorize noise. Ridge and lasso are our two foundational tools, and they differ in one crucial way: does the penalty produce exact zeros or not. Both have this beautiful equivalence to constrained optimization and to Bayesian priors. And λ itself isn't guessed — it's chosen by cross-validation.

[*Pause. Give students a moment to finish writing.*]

Next lecture, we'll extend this toolkit to elastic net and to regularization techniques built specifically for deep learning, and then we'll put everything into practice together in the lab.

Thanks, everyone — see you next time.

---

## Timing table

| Block | Slides | Time |
|-------|--------|------|
| Why regularize | 1–6 | 19 min |
| Ridge & Lasso mechanics | 7–12 | 28 min |
| Tuning & Bayesian view | 13–17 | 28 min |
| Teaser & wrap-up | 18–19 | 6 min |
| Buffer / questions | — | 8 min |
| **Total** | | **~90 min** |

## What can be cut

If time is short:
- Slide 9 or 11 (geometric pictures) — keep only the L1 diamond (slide 11), since that's the one that explains sparsity, and describe the L2 circle verbally instead of dwelling on slide 9.
- Slide 17 (Putting it together) — can be compressed into a single sentence at the start of the closing slide instead of standing alone.
