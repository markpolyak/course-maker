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

Default output format is `pdf` for every deck. `png` is slidev-only; `html` and
`pptx` are quarto-only.

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
quarto render slides.qmd --to beamer     # pdf (default)  → slides.pdf
quarto render slides.qmd --to revealjs   # html           → slides.html
quarto render slides.qmd --to pptx       # pptx           → slides.pptx
```

Map the command argument to the target: `pdf` → `beamer`, `html` → `revealjs`,
`pptx` → `pptx`.

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
- The `revealjs` target writes a `slides_files/` directory next to the HTML. It
  is part of the output — mention it, and note that `embed-resources: true` in
  the headmatter produces a single portable file instead.

## After export

List the produced file(s) for the user. Nothing else changes — export is a pure
read-of-source, write-of-artifact step.
