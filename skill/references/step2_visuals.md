# Step 2 — Visualizations List

> **Session directory.** Paths below use `lectures/NN/`. For the seminar mirror
> `/course-maker seminar visuals N`, substitute `seminars/NN/` for `lectures/NN/`
> throughout — the structure is identical.

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

The last column depends on the course's slide format (`Slides format:` in
`AGENTS.md`). Read it before writing the table.

### Beamer and Slidev courses — `TikZ` column

```markdown
# Lecture N — Visualizations

| # | Slide | Description | TikZ |
|---|-------|-------------|------|
| V01 | 4 | ACF plot for AR(2) process — decaying oscillating bars | No — needs computed data |
| V02 | 7 | Block diagram: AR → MA → ARMA nesting | Yes |
| V03 | 9 | Comparison: stationary vs non-stationary trajectory | No — needs simulated data |
| V04 | 12 | Unit circle with roots plotted | Yes |
```

TikZ column values:
- **Yes** — straightforward geometric or schematic diagram, no data needed
- **Hard** — possible in TikZ but error-prone (e.g. complex positioning,
  many nodes); prefer Python unless the user specifically wants TikZ
- **No — needs computed data** — plot requires numpy/scipy computation
- **No — needs simulation** — requires a random process to be generated

### Quarto courses — `Render` column

A Quarto deck can carry the plotting code itself, so the question is not "TikZ
or Python" but "where does this figure live". TikZ is not offered: raw LaTeX
renders only in the PDF target and breaks the HTML and PowerPoint ones.

```markdown
# Lecture N — Visualizations

| # | Slide | Description | Render |
|---|-------|-------------|--------|
| V01 | 4 | ACF plot for AR(2) process — decaying oscillating bars | inline |
| V02 | 7 | Block diagram: AR → MA → ARMA nesting | inline |
| V03 | 9 | Trajectory comparison, also used in lab 2 | png |
```

Render column values:
- **inline** — an executable chunk written straight into `slides.qmd` at Step 4.
  The default. Nothing to generate beforehand.
- **png** — a file produced by `figures.py` at Step 3. Choose this only when the
  same image is needed outside the deck (a lab notebook, a handout, a printed
  sheet), or when the plot is expensive enough that you want it computed once.

## After writing the table

**Beamer / Slidev:** count rows where TikZ = "No" or "Hard" — these drive Step 3.
Mention this count to the user: "X figures need Python generation."
If TikZ = "Yes" for a figure, include a brief description of the TikZ approach
(e.g. "tikzpicture with nodes and arrows, \draw commands for the block diagram").

**Quarto:** count rows where Render = `png`. Tell the user the count and what it
means for the next step: with at least one `png` row, Step 3 generates just
those figures; with none, Step 3 is skipped entirely and Step 4 comes next.
