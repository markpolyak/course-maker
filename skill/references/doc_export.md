# Document export — markdown to pdf / latex / docx

The single place that describes how a generated Markdown document becomes a
distributable file. Used by `/course-maker syllabus`, `/course-maker homework
publish`, and `/course-maker quiz publish`. Those commands decide *what* to
write and *who may see it*; this file only converts an already-written file.

Export is mechanical: no approval, no `COURSE_STATE.md` change, no `history.md`
entry. The Markdown file is the source of truth and always stays on disk.

**Order matters when the caller has a leak check.** Convert only the file that
has already passed it. Never export an intermediate that still holds
instructor-only content — the check protects the Markdown, not the PDF made
from it.

## Choose the backend

Read `AGENTS.md` → `## Course context` → `Doc export:`.

| Value | Tool | PDF route |
|---|---|---|
| `pandoc` (default, and when the field is absent) | `pandoc` | LaTeX — needs a TeX distribution |
| `quarto` | `quarto` | Typst — **no LaTeX needed**, Typst ships inside Quarto |

If the chosen tool is not installed, **stop**: name the tool, say how to install
it, and leave the Markdown in place. Do not quietly fall back to the other
backend — a document silently produced by a different toolchain than the course
configured is worse than no document.

## pandoc

```bash
pandoc <file>.md -o <file>.pdf      # needs a LaTeX engine installed
pandoc -s <file>.md -o <file>.tex   # standalone LaTeX source
pandoc <file>.md -o <file>.docx
```

- If `pandoc` is missing: stop and tell the user how to install it.
- For `pdf`, if pandoc reports no LaTeX engine, say so and offer `latex` or
  `docx` instead (or installing a TeX distribution).

## quarto

```bash
quarto render <file>.md --to typst   # → <file>.pdf, no LaTeX involved
quarto render <file>.md --to docx    # → <file>.docx
quarto render <file>.md --to latex   # → <file>.tex
```

- `--to typst` is the reason to pick this backend: it produces a PDF on a
  machine with no TeX distribution, and covers non-Latin scripts with its
  default fonts.
- By default the output lands next to the input, named after it. Use
  `-o <name>` for a different filename, `--output-dir <dir>` for a different
  directory.
- If `quarto` is missing: stop and tell the user
  (`brew install quarto`, or https://quarto.org/docs/get-started/).
- Typst sizes images differently from LaTeX. If the document embeds images and
  they come out wrong, give them an explicit width rather than switching
  backends.
- `--to latex` goes through Quarto's LaTeX writer, so unlike `--to typst` it is
  only useful when a TeX toolchain exists downstream.

## After export

List the produced file for the user. Nothing else changes.
