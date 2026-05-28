# Step 2 — Visualizations List

## Context to gather before writing

From `lectures/NN/plan.md`:
- All slides tagged `[figure]`
- Slide content descriptions — to understand what the figure must convey

From `history.md`:
- Any figures the user rejected or redesigned in a previous round

## Decision rule: include a visualization only if

It conveys something that text or a formula alone cannot:
spatial relationships, data shape, algorithm steps, system structure,
process flow, comparative plots.

If a slide has `[formula]` but no `[figure]` tag, don't invent a figure.

## Output format: `lectures/NN/visuals.md`

```markdown
# Lecture N — Visualizations

| # | Slide | Description | TikZ |
|---|-------|-------------|------|
| V01 | 4 | ACF plot for AR(2) process — decaying oscillating bars | No — needs real data |
| V02 | 7 | Block diagram: AR → MA → ARMA nesting | Yes |
| V03 | 9 | Comparison: stationary vs non-stationary trajectory | No — needs simulated data |
| V04 | 12 | Unit circle with roots plotted | Yes |
```

TikZ column values:
- **Yes** — straightforward geometric or schematic diagram, no data needed
- **Hard** — possible in TikZ but error-prone (e.g. complex positioning,
  many nodes); prefer Python unless the user specifically wants TikZ
- **No — needs real data** — plot requires numpy/scipy computation
- **No — needs simulation** — requires a random process to be generated

## After writing the table

Count rows where TikZ = "No" or "Hard" — these drive Step 3.
Mention this count to the user: "X figures need Python generation."

If TikZ = "Yes" for a figure, include a brief description of the
TikZ approach (e.g. "tikzpicture with nodes and arrows,
\draw commands for the block diagram").
