# Step 4 (Quarto) — one deck, three targets

The Quarto variant of Step 4. Produces `lectures/NN/slides.qmd` — a single
[Quarto](https://quarto.org/docs/presentations/) source that renders to
reveal.js (HTML), Beamer (PDF), and PowerPoint. Used when the course's slide
format is `quarto` (see the slides dispatcher in `SKILL.md`). The other two
paths are `references/step4_slides.md` (Beamer) and
`references/step4_slides_slidev.md` (Slidev); the discipline below (chunking,
figure verification, forward references) is the same — the syntax and the
figure model differ.

> **Session directory.** Paths below use `lectures/NN/`. For the seminar mirror
> `/course-maker seminar slides N`, substitute `seminars/NN/` throughout.

## Context to gather before writing

1. `lectures/NN/plan.md` — slide titles, content, timing.
2. `lectures/NN/visuals.md` — the visualization list, including each one's
   `render:` mode (`inline` or `png`).
3. For every visualization with `render: png`:
   `ls -l lectures/NN/figures/*.png lectures/NN/figures/figures.py`.
   **Only reference PNG files that exist. Never reference a file not in this list.**
   **Staleness check:** if any PNG is older than `figures.py`, warn that the
   figures may be out of date and offer to re-run `/course-maker figures N`
   first. Warning, not a hard block. A lecture whose visualizations are all
   `inline` has no `figures/` directory — that is normal, not a missing step.
4. `lectures/NN/history.md` — previous layout issues and fixes.
5. `course_conventions.md` (course root) — terminology dictionary and language rules.
6. `slides_headmatter.qmd` (course root) — the deck headmatter, used verbatim.

## Headmatter

Read `slides_headmatter.qmd` from the course root and use it verbatim as the
opening of Chunk 0. Before writing Chunk 0, replace these placeholders with
values from `AGENTS.md` and `plan.md`:
- `[Course name]` → course name (goes in `subtitle`)
- `[Author]` → instructor name
- `[Institution]` → institution
- `[Lecture] N. [Title]` → course-language word for "Lecture", lecture number,
  and the title from `plan.md` (goes in `title`)

Also set `lang:` to the course language as a BCP 47 tag if it is still `en` and
the course is taught in another language.

If `slides_headmatter.qmd` is missing, stop immediately and show:
```
slides_headmatter.qmd not found in the course root.
Run /course-maker course init to generate it, or copy
templates/slides_headmatter_quarto.qmd manually and edit it.
```

## Slide syntax

A slide is a level-2 heading. A level-1 heading is a section divider slide.

```markdown
<!-- Slide 03 -->
## Slide title

- point 1
- point 2
```

- **Never use `---` as a slide separator.** In Quarto a horizontal rule creates
  an *untitled* slide, so the Slidev habit silently produces a deck full of
  blank-headed slides. `---` appears exactly once in the file: closing the
  headmatter.
- **The title slide is generated from the headmatter** (`title`, `subtitle`,
  `author`, `institute`). Do not write a `##` heading for it.
- Precede every slide with an HTML comment marker `<!-- Slide NN -->`. The
  marker is how `/course-maker slides N next` finds where to resume, and how
  `/course-maker notes N` attaches speaker notes.
- Slide numbers must match `plan.md` exactly: slide 1 = title slide, slide 2 =
  outline, first content slide = 3. Never renumber.
- Math: `$inline$` and `$$display$$` — MathJax in HTML, real LaTeX in Beamer.
- Display-only code (a snippet the students read, not run): a plain fenced
  block ```` ```python ````. It is highlighted, never executed.

## Figures — two modes

`visuals.md` assigns each visualization a mode. Both are legitimate; the deck
may mix them.

### `inline` — an executable chunk (Quarto only, the default for this format)

````markdown
```{python}
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(5, 2.5))
ax.plot(x, y)
plt.show()
```
````

- The course headmatter sets `echo: false`, so the plot is shown and the source
  is not. Add `#| echo: true` to a chunk when the code itself is the teaching
  point.
- Per-chunk options are `#| key: value` comments in the first lines of the block.
- Quarto writes the rendered image into `lectures/NN/slides_files/` and wires up
  the reference itself — there is no PNG to name and nothing to check into
  `figures/`.
- **Verification is the render, not a file listing.** A chunk that raises stops
  `quarto render` with a non-zero exit, prints the traceback, and produces no
  output file. That is the guarantee this mode rests on — never suppress it with
  `error: true`.

### `png` — a pre-generated file from `figures.py`

```markdown
![](figures/fig03_name.png){width="70%"}
```

- Same rule as every other format: only reference PNG files that exist.
- **Always give an explicit width.** Default image sizing differs between HTML,
  Beamer, and PowerPoint, so an unsized image that looks right in one target
  overflows in another.

Use `png` when the same figure must also appear outside the deck (a lab
notebook, a handout, a printed sheet). Use `inline` otherwise.

## Interactive figures and the multi-format cost

Interactive output (plotly, altair, bokeh) is real and worth using — but it
exists only in HTML. In Beamer and PowerPoint an interactive widget does not
render. If the course exports PDF or pptx regularly, either keep the figure
static, or write both branches:

````markdown
::: {.content-visible when-format="html"}
```{python}
# interactive version
```
:::

::: {.content-visible when-format="pdf"}
```{python}
# static fallback
```
:::
````

- Format aliases: `html` covers reveal.js, `pdf` covers Beamer. Write those, not
  `revealjs` / `beamer`.
- **Both branches execute.** `.content-visible` hides output; it does not skip
  the code. A fallback costs render time on every target.
- Do not write the two-branch pattern by default. Reach for it only when a
  specific figure genuinely benefits from interaction.

## Portability checklist

One source feeds three targets. Before finalizing each slide:

- [ ] No raw LaTeX or TikZ in shared content — it renders in Beamer and breaks
      everywhere else. If a diagram must be TikZ, put it inside
      `::: {.content-visible when-format="pdf"}` and give HTML a static
      alternative. Prefer generating the diagram in Python instead.
- [ ] Every image has an explicit width.
- [ ] No HTML/CSS layout tricks — PowerPoint drops them.
- [ ] At most 2 display equations per slide.
- [ ] Max ~6–7 bullets per column; split a dense slide rather than shrink it.
- [ ] Max 3 callout blocks per slide.

## Layout rules

### Two columns

```markdown
:::: {.columns}
::: {.column width="50%"}
- point 1
- point 2
:::
::: {.column width="50%"}
![](figures/fig03_name.png){width="100%"}
:::
::::
```

Note the four-colon outer fence and the three-colon inner ones. PowerPoint maps
this onto its "Two Content" or "Comparison" layout; more than two columns has no
pptx equivalent and should be avoided.

### One centered image

```markdown
![](figures/fig05_name.png){width="70%" fig-align="center"}
```

## Speaker notes

Speaker notes are **not written at this step.** `/course-maker notes N`
generates `lectures/NN/speaker_notes.md` and then injects `::: {.notes}` blocks
into `slides.qmd`. Leave the deck free of notes here; writing them now would
collide with that injection.

## Chunking protocol

Output is ALWAYS chunked — do not generate the whole deck in one shot.

- **Chunk 0** = filled headmatter + the outline slide (slide 2). The title slide
  comes from the headmatter and is not written out.
- **Chunk K (K≥1)** = slides `[5K-4 … 5K]`, each preceded by its
  `<!-- Slide NN -->` marker.
- **Chunk last** = closing slide.

Append each chunk to `slides.qmd` immediately; do not pause between chunks
(auto-chain to the end). **Chunking is not a review cycle:** the user approves
the finished deck, not each chunk.

**After the last chunk, render the deck once:**

```bash
cd lectures/NN && quarto render slides.qmd --to revealjs
```

Show the output. If it fails — a chunk raised, a PNG is missing, the YAML is
malformed — fix and re-render until clean. **A deck that has not rendered
cleanly is not finished**, and Step 4 is not marked ✅.

Two failure modes worth recognizing:
- `is of type a null value` pointing at `format: <name>` — a format key in the
  headmatter has only comments under it. It needs a value (`pptx: default`).
- A Python traceback — an `inline` chunk failed. Fix the chunk; do not switch it
  to `png` to make the error go away.

**Resuming:** `/course-maker slides N next` reads `slides.qmd`, finds the last
`<!-- Slide NN -->` marker, and continues from there.

**Revising:** "fix slide 7" → regenerate just that slide, show the diff, apply
after approval, re-render.

## Title, outline, closing

- **Title slide** = the headmatter fields. Nothing to write.
- **Outline slide** right after it: a short bullet list of the lecture's
  sections, heading in the course language.
- **Closing slide** = key takeaways. A single mention of the next lecture is
  allowed here if it flows naturally — not required.

## Cross-reference rules (strictly enforced)

- A slide never cites another slide by number or position, in either direction.
  Name the content instead; a slide must stand on its own.
- Next-lecture references: at most 1, only on the closing slide. Three or more
  anywhere is a hard error.

## Iteration logging

When the user reports a rendering or layout issue, before fixing, append to
`history.md`:

```
## [date] Step 4: Slides (quarto) — iteration N
**Issue:** interactive plot rendered blank in the pptx export
**Fix:** added a static fallback branch for when-format="pdf"
```

Wording the user rejects twice also goes to `Never Use` in
`course_conventions.md`, not just to `history.md`.
