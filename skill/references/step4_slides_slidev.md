# Step 4 (Slidev) — Markdown presentation

The Slidev variant of Step 4. Produces `lectures/NN/slides.md` — a single
[Slidev](https://sli.dev) Markdown deck — instead of a Beamer `slides.tex`.
Used when the course's slide format is `slidev` (see the slides dispatcher in
`SKILL.md`). The Beamer path is `references/step4_slides.md`; the discipline
below (chunking, PNG existence, staleness, forward references) is the same — only
the output syntax differs.

> **Session directory.** Paths below use `lectures/NN/`. For the seminar mirror
> `/course-maker seminar slides N`, substitute `seminars/NN/` throughout.

## Context to gather before writing

1. `lectures/NN/plan.md` — slide titles, content, timing.
2. `lectures/NN/visuals.md` — which figures exist as PNG.
3. `ls -l lectures/NN/figures/*.png lectures/NN/figures/figures.py` — the PNG
   files that actually exist, with timestamps.
   **Only reference PNG files that exist. Never reference a file not in this list.**
   **Staleness check:** if any PNG is older than `figures.py`, warn that the
   figures may be out of date and offer to re-run `/course-maker figures N`
   first. Warning, not a hard block.
4. `lectures/NN/history.md` — previous layout issues and fixes.
5. `course_conventions.md` (course root) — terminology dictionary and language rules.
6. `slides_headmatter.md` (course root) — the deck headmatter, used verbatim.

## Headmatter

Read `slides_headmatter.md` from the course root and use it verbatim as the
opening of Chunk 0. Before writing Chunk 0, replace these placeholders with
values from `AGENTS.md` and `plan.md`:
- `[Course name]` → course name
- `[Author]` → instructor name
- `[Institution]` → institution
- `[Lecture] N. [Title]` → course-language word for "Lecture", lecture number,
  and the title from `plan.md`

If `slides_headmatter.md` is missing, stop immediately and show:
```
slides_headmatter.md not found in the course root.
Run /course-maker course init to generate it, or copy
skill/templates/slides_headmatter_slidev.md manually and edit it.
```

## Slide syntax

Slides are separated by a line containing only `---`. Per-slide options go in a
small YAML block immediately after the separator:

```markdown
---
layout: default
---

# Slide title

- point 1
- point 2
```

- Slide numbers in your section comments must match `plan.md` exactly: slide 1 =
  title slide, slide 2 = outline, first content slide = 3. Never renumber.
- Math: `$inline$` and `$$display$$` (KaTeX). No LaTeX preamble needed.
- Code: fenced blocks ```` ```python ````; Slidev highlights them — no `fragile`
  equivalent is needed.

## Layout rules (these prevent most iteration rounds)

### Image + text (two columns)

Use the `two-cols` layout; `::right::` splits the slide:

```markdown
---
layout: two-cols
---

# Title

- point 1
- point 2

::right::

<img src="/figures/figNN_name.png" class="h-60 mx-auto" />
```

- Reference figures by path under the deck: `figures/figNN_name.png` (Slidev
  serves the deck directory; a leading `/` maps to it).
- Cap image height with a utility class (`h-60`, `h-72`, …) or inline
  `style="max-height: 60%"`. Do not let an image push content off the slide.

### One image, centered

```markdown
![alt text](/figures/figNN_name.png)
```

Add `{width=600px}` or wrap in `<img class="h-80 mx-auto" />` to constrain size.

### Density

- Max ~6–7 bullets per column; split a dense slide into two rather than shrink.
- Max 3 "blocks" (callouts) per slide; if the plan has 4+, split or flatten into
  a table.
- More than 2 display equations on one slide → move one to a separate slide.

## Chunking protocol (identical to the Beamer path)

Output is ALWAYS chunked — do not generate the whole deck in one shot.

- **Chunk 0** = headmatter (filled) + title slide + outline slide.
- **Chunk K (K≥1)** = slides `[5K-4 … 5K]`, each preceded by its `---` separator.
- **Chunk last** = closing slide.

Append each chunk to `slides.md` immediately; do not pause between chunks
(auto-chain to the end). **Resuming:** `/course-maker slides N next` reads
`slides.md`, finds the last completed slide, and continues from there.

## Title, outline, closing

- **Title slide** = the headmatter's first slide (course name, lecture, author).
- **Outline slide** right after the title. Slidev has no `\tableofcontents`;
  write a short bullet list of the lecture's sections (heading in the course
  language, e.g. "Outline").
- **Closing slide** = key takeaways. A single mention of the next lecture is
  allowed here if it flows naturally — not required.

## Forward reference rules (strictly enforced)

- No forward references within the deck ("we will cover this later", "see slide
  X") except on the closing slide.
- Next-lecture references: at most 1, only on the closing slide. Three or more
  anywhere is a hard error.

## Speaker notes

Speaker notes stay in `lectures/NN/speaker_notes.md` via
`/course-maker notes N` — do not inline them into `slides.md` at this step.

## Iteration logging

When the user reports a rendering or layout issue, before fixing, append to
`history.md`:

```
## [date] Step 4: Slides (slidev) — iteration N
**Issue:** image overflowed on slide 7
**Fix:** capped height with class h-60
```
