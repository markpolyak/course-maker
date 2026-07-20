# /course-maker slides N export [pdf|png]

Mechanical export of an already-generated deck to a file. This does **not**
generate or present slides — it converts the existing deck in `lectures/NN/`
(seminar mirror: `seminars/NN/`) to a document. No approval needed, no
`COURSE_STATE.md` change, no `history.md` entry.

Presenting a Slidev deck live (`npx slidev`, a dev server in the browser) is the
user's job — this command never launches it.

## Resolve the deck format

Detect from the existing file (do not read `CLAUDE.md`):
- `lectures/NN/slides.tex` → **beamer**
- `lectures/NN/slides.md` → **slidev**

If neither exists, stop: "No deck found in lectures/NN/. Run
`/course-maker slides N` first."

Default output format is `pdf`. `png` is slidev-only.

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

## After export

List the produced file(s) for the user. Nothing else changes — export is a pure
read-of-source, write-of-artifact step.
