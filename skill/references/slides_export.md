# /course-maker slides N export [format]

Mechanical export of an already-generated deck to a file. This does **not**
generate or present slides — it converts the existing deck in `lectures/NN/`
(seminar mirror: `seminars/NN/`) to a document. No approval needed, no
`COURSE_STATE.md` change, no `history.md` entry.

Presenting a deck live — `npx slidev` for Slidev, `quarto preview` for Quarto,
both dev servers in the browser — is the user's job. This command never launches
either.

## Resolve the deck format

Detect from the existing file (do not read `AGENTS.md`):
- `lectures/NN/slides.tex` → **beamer**
- `lectures/NN/slides.md` → **slidev**
- `lectures/NN/slides.qmd` → **quarto**

If none exists, stop: "No deck found in lectures/NN/. Run
`/course-maker slides N` first."

Default output format when the command is given no argument:

| Deck | Default | Also available |
|---|---|---|
| beamer (`slides.tex`) | `pdf` | — |
| slidev (`slides.md`) | `pdf` | `png` |
| quarto (`slides.qmd`) | **`html`** | `pdf`, `pptx` |

A Quarto deck defaults to `html` because reveal.js is the only target that
carries everything the deck can contain. PDF and PowerPoint are lossy: an
interactive figure becomes a dead image or nothing at all, and the loss is
silent. Defaulting a Quarto deck to PDF would hide the capability the format
was chosen for.

## Beamer export (slides.tex → PDF)

Pick the engine from the course preamble: if `slides_preamble.tex` loads
`fontspec` → `xelatex`; otherwise `pdflatex`.

```bash
cd lectures/NN
latexmk -xelatex -interaction=nonstopmode slides.tex   # or: latexmk -pdf ... for pdflatex
```

- If `latexmk` is not installed, run the engine directly twice (for references/toc):
  `xelatex slides.tex && xelatex slides.tex` (or `pdflatex`).
- If no LaTeX engine is available, stop and tell the user which engine the deck
  needs and how to install a TeX distribution. Do not fail silently.
- `png` for beamer is not supported directly — suggest exporting `pdf` and
  converting with `pdftoppm`/`pdftocairo` if the user needs images.
- Result: `lectures/NN/slides.pdf`.

## Slidev export (slides.md → PDF/PNG)

```bash
cd lectures/NN
npx slidev export slides.md --output slides.pdf              # pdf (default)
npx slidev export slides.md --format png --output slides     # png frames
```

- Slidev export needs a headless browser. If it errors about a missing browser,
  tell the user to install it once: `npx playwright install chromium` (or follow
  the exact hint Slidev prints). Do not fail silently.
- If `node`/`npx` is not available, stop and tell the user Slidev needs Node.js.
- Result: `lectures/NN/slides.pdf` (pdf) or per-slide PNGs (png).

## Quarto export (slides.qmd → PDF/HTML/PPTX)

One source, three targets. Always name the target explicitly — a bare
`quarto render` builds every format declared in the headmatter.

```bash
cd lectures/NN
quarto render slides.qmd --to revealjs   # html (default) → slides.html
quarto render slides.qmd --to beamer     # pdf            → slides.pdf
quarto render slides.qmd --to pptx       # pptx           → slides.pptx
```

Map the command argument to the target: `html` → `revealjs`, `pdf` → `beamer`,
`pptx` → `pptx`.

**Warn before a lossy export.** When the target is `pdf` or `pptx`, check the
deck for interactive output — a chunk importing `plotly`, `altair`, `bokeh`, or
`ipywidgets`, or a `::: {.content-visible when-format="html"}` block. If any is
present, say which slides will lose it and offer `html` instead. Export anyway
if the user confirms; the point is that the loss is never silent.

- `png` is not supported. Say so, and suggest exporting `pdf` and converting
  with `pdftoppm`/`pdftocairo`.
- If `quarto` is not on PATH, stop and tell the user to install it
  (`brew install quarto`, or https://quarto.org/docs/get-started/).
- If the `beamer` target fails for a missing LaTeX distribution, tell the user
  to run `quarto install tinytex` — Quarto ships its own installer. Do not fall
  back to another target.
- If the render fails on a Python traceback, an executable figure chunk is
  broken. Show the traceback and fix the chunk. Never make the error go away
  with `error: true` or by deleting the chunk.
- **`pdf` only — verify non-Latin text survived.** A beamer export with no
  `mainfont` in `slides_headmatter.qmd` succeeds and produces a PDF whose
  Cyrillic/Greek/CJK text is simply absent: xelatex falls back to Latin Modern,
  which has no such glyphs, and nothing warns. If the deck contains non-Latin
  characters, check the output before reporting success:

  ```bash
  pdftotext slides.pdf - | grep -c '<a word from the deck>'   # must be > 0
  ```

  If it is zero (or `pdftotext` is unavailable, so you cannot tell — say so),
  the fix is `mainfont` in the `beamer:` block of `slides_headmatter.qmd`, set
  to a font covering the script (`fc-list :lang=<code> family`; `DejaVu Serif`
  ships with TeX Live and covers Latin, Cyrillic, and Greek). Do not report a
  successful export until the text is confirmed present.
- The `revealjs` target writes a `slides_files/` directory next to the HTML. It
  is part of the output — mention it, and note that `embed-resources: true` in
  the headmatter produces a single portable file instead.

## After export

List the produced file(s) for the user. Nothing else changes — export is a pure
read-of-source, write-of-artifact step.
