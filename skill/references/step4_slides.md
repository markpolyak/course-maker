# Step 4 — LaTeX/Beamer Presentation

## Context to gather before writing

1. `lectures/NN/plan.md` — slide titles, content, timing
2. `lectures/NN/visuals.md` — which figures are TikZ vs PNG
3. `ls lectures/NN/figures/*.png` — list of actually existing PNG files
   **Only reference PNG files that exist. Never reference a file not in this list.**
4. `lectures/NN/history.md` — previous layout issues and fixes
5. `course_conventions.md` (course root) — terminology dictionary and language rules
6. `slides_preamble.tex` (course root) — LaTeX preamble to use verbatim

## Preamble

Read `slides_preamble.tex` from the course root and use it verbatim as the preamble.
Before writing Chunk 0, replace these placeholders with values from `CLAUDE.md`:
- `[Course name]` → course name
- `[Author]` → instructor name
- `[Institution]` → institution
- `[Lecture] N. [Title]` in `\subtitle` → course-language word for "Lecture", lecture number, and title from `plan.md`

If `slides_preamble.tex` is missing, stop immediately and show:
```
slides_preamble.tex not found in the course root.
Run /course-maker course init to generate it, or copy
skill/templates/slides_preamble_pdflatex.tex manually and edit it.
```

## Slide template

```latex
% Slide NN — [Title from plan.md]
\begin{frame}{[Title]}
  % content
\end{frame}

```
Always add a blank line after `\end{frame}`.

## Layout rules (read carefully — these prevent most iteration rounds)

### Images + text

```latex
% When image accompanies bullet points:
\begin{columns}[c]
  \begin{column}{0.52\textwidth}
    \begin{itemize}
      \item point 1
      \item point 2
    \end{itemize}
  \end{column}
  \begin{column}{0.44\textwidth}
    \includegraphics[width=\textwidth, height=0.55\textheight,
                     keepaspectratio]{figures/figNN_name.png}
  \end{column}
\end{columns}
```

`height=0.55\textheight` is the hard cap. Never exceed it.

### Slide with many blocks

- Maximum 3 blocks per slide.
- If the plan has 4+ items that each need a block, split into two slides
  or flatten into a table/itemize.
- When 3 blocks are unavoidable: add `[shrink=8]` to the frame.

```latex
\begin{frame}[shrink=8]{Title}
```

### Columns always use `[c]`

```latex
\begin{columns}[c]   % not [t]
```

Exception: only use `[t]` when both columns are text-only with no images.

### TikZ diagrams

Use explicit coordinates. Avoid relative positioning chains longer than 3 nodes.

```latex
% Good
\node (A) at (0, 0) {Input};
\node (B) at (3, 0) {Process};
\node (C) at (6, 0) {Output};

% Risky — long chains cause unpredictable placement
\node (D) [right=of C, below=of B] {Side};
```

### Fragile frames

Frames with `\verb`, `lstlisting`, or `verbatim` need `[fragile]`:

```latex
\begin{frame}[fragile]{Code example}
```

### Math-heavy slides

If a slide has more than 2 display equations, use `\small` or `\footnotesize`
before the equation block, or move one equation to a separate slide.

## Anti-overfull checklist

Before finalizing, mentally check each slide:

- [ ] No more than 6–7 bullet items per column
- [ ] Images: `height` capped at `0.55\textheight`
- [ ] Tables: use `\small` inside `tabular` if more than 5 columns
- [ ] Long text blocks: use `\small` or wrap in a `block` environment
- [ ] Slides with 3 blocks: `[shrink=8]` added
- [ ] No PNG files referenced that don't exist in `figures/`
- [ ] Every `\begin{frame}` has a matching `\end{frame}`
- [ ] Blank line after every `\end{frame}`

## Title and closing slides

Always include:
- Title slide: `\begin{frame}\titlepage\end{frame}`
- Outline slide after title: `\begin{frame}{<outline title in course language>}\tableofcontents\end{frame}`
  (e.g. "Outline" in English, "План лекции" in Russian — translate to course language)
- Closing slide: summary of key takeaways. A single mention of the next lecture topic is allowed here if it flows naturally — but not required.

## Forward reference rules (strictly enforced)

- **No forward references within the presentation.** Do not write "we will cover this later", "see slide X for details", "more on this ahead" on any slide except the closing one.
- **Next-lecture references: maximum 1 per entire presentation.** Allowed only on the closing slide. Omit entirely if there is no compelling reason to mention it. Three or more mentions anywhere in the deck is a hard error.

## Iteration logging

When the user reports a compilation error or layout issue, before fixing,
append to `history.md`:

```
## [date] Step 4: Slides — iteration N
**Issue:** overfull on slide 7 (image height exceeded textheight)
**Fix:** added height=0.55\textheight cap to \includegraphics
```

This prevents the same error in subsequent lectures.
