# /course-maker site [init|render|preview|publish]

Build a student-facing course website with Quarto and put it on the web.

This command publishes. Everything it touches is about to be readable by anyone
with the URL, so it is built default-deny: material reaches the site only by
being on the allow-list below, never by being found in the course directory.

Needs `quarto` on PATH. If it is missing, stop and say how to install it
(`brew install quarto`, or https://quarto.org/docs/get-started/).

## Architecture: a staged build in `site/`

- The site project lives in **`site/`** and owns the only `_quarto.yml`.
- `site render` **stages** the allowed artifacts into `site/`, then renders the
  site into `site/_site/`.
- Decks are staged **already rendered**, as static files. The site build does
  not re-execute their chunks, so publishing cannot produce a deck different
  from the one the lecturer reviewed.

**Never put `_quarto.yml` in the course root.** It makes the whole course one
Quarto project, and rendering a single deck then writes into that project's
`output-dir` instead of next to the source, breaking
`/course-maker slides N export`.

## What may be published (allow-list)

Stage only these. Anything not named here does not go on the site.

| Source | Staged as |
|---|---|
| `syllabus.md` | `site/syllabus.qmd` |
| `lectures/NN/slides.*` rendered to HTML | `site/decks/lectures/NN/` |
| `seminars/NN/slides.*` rendered to HTML | `site/decks/seminars/NN/` |
| `<LAB_DIR>README.md` | a page under `site/labs/` |
| `HW_DIR/homework_student.md` | a page under `site/homework/` |

Two things are allowed only if the instructor asks for them explicitly, each
time — never by default:

- **Quiz student sheets.** Publishing them before the exam defeats the exam.
  Ask, and say what the risk is.
- **`course_plan.md`.** It is the instructor's plan and routinely holds internal
  notes and timing. `syllabus.md` is the student-facing version and exists
  precisely so the plan does not have to be published.

## What must never be published (deny-list)

Instructor-only by construction. These are never staged, and the guard below
re-checks the built site for them:

`rubric.md` · `quizzes/NN/quiz_questions.md` · `lab_spec.md` ·
`defense_questions.md` · `tests.py` ·
`conftest.py` · `grade_report.py` · `speaker_notes.md` · `history.md` ·
`COURSE_STATE.md` · `lms_adapter.md` · `AGENTS.md` · `CLAUDE.md` ·
`datasets_info.md` · everything under `labs/*/starter/` except `README.md`

## Speaker notes must be stripped from published decks

A rendered reveal.js deck carries injected notes in its HTML as
`<aside class="notes">`, readable by anyone who opens the page source or presses
`S`. They are lecturer material and do not go on the site.

Because `/course-maker notes N` writes them as marked blocks, stripping is
deterministic — and it is done by a script, not by hand:

```bash
python <skill>/scripts/site_guard.py strip-notes \
    lectures/NN/slides.qmd /tmp/slides_public.qmd
```

Render **that copy** for the site and stage the result. Never strip in place —
`slides.qmd` keeps its notes.

The script exits 1 and writes nothing if the deck holds an unmarked
`::: {.notes}` block (hand-written rather than injected): it cannot be removed
without guessing. Relay the message and stop — do not hand-edit the deck to get
past it.

## `site init`

1. Create `site/` and write `_quarto.yml` from
   `templates/quarto_site_yml.md`, filling the placeholders from `AGENTS.md`
   and `course_plan.md`. Drop navbar entries for sections the course does not
   have.
2. Write a minimal `site/index.qmd` — course name, one-paragraph description,
   links to the sections that exist.
3. Append the generated paths to `.gitignore` (list in the template).
4. Ask which publishing method to use and record the answer in `site/_quarto.yml`
   as a comment, so `site publish` need not re-ask:

   - **`gh-pages` branch** (default): `quarto publish gh-pages` from `site/`.
     Quarto pushes the built site to a `gh-pages` branch.
   - **`docs/` directory**: set `output-dir` to a `docs/` folder the repository
     serves, add `.nojekyll`, commit the built site.
   - **GitHub Action**: `quarto-dev/quarto-actions/publish@v2` with
     `target: gh-pages` and `path: site` (the project is in a subdirectory).
     Requires one local `quarto publish gh-pages` first to create `_publish.yml`.

Idempotent: never overwrite an existing `site/_quarto.yml` or `index.qmd`.

## `site render`

1. Verify the allow-list sources exist; report what is missing rather than
   silently publishing a partial site.
2. Stage each allowed artifact. For decks: strip notes into a temporary copy,
   render it to HTML, stage the output.
3. `cd site && quarto render`.
4. Run the guard below.
5. Report what was staged and what was skipped, per section.

## CRITICAL — leak guard before publishing (do not skip)

After rendering and before any publish, scan the built site:

```bash
python <skill>/scripts/site_guard.py check site/_site
```

It reports deny-listed filenames and machine-written markers (speaker-notes
markers, rendered `<aside class="notes">`, instructor asides, rubric metadata),
and exits 1 on any finding.

Any finding blocks publication. Show the output, fix the **staging** so the
content never reaches the site, re-render, and re-check until clean. Do not
publish "just this once" with a known finding, and never edit the script's
patterns to make a run pass — a loosened guard is how the leak ships next time.

Two limits to state plainly rather than paper over:

- The check matches markers and filenames, not meaning. It cannot tell whether a
  page's prose should be student-facing. That judgement stays with the user.
- It is the second line of defence. The first is that nothing outside the
  allow-list is ever staged.

## `site preview`

Presenting a live preview is the user's job. Print the command and stop:

```bash
cd site && quarto preview
```

Never launch it — it starts a server that blocks.

## `site publish`

Run `site render` and the guard first. Then execute the method recorded at
`site init`:

```bash
cd site && quarto publish gh-pages          # gh-pages branch
```

- `--no-browser` when a browser should not open; `--no-prompt` only for an
  unattended run the user asked for.
- For the `docs/` method, commit the built directory — the publish is the commit.
- For the Action method, the push is the publish; say so instead of running
  anything.

Publishing is outward-facing and hard to take back: a page indexed once may stay
cached. Confirm with the user before the first publish of a course, and any time
the guard's report changed since the last run.

## State

No `COURSE_STATE.md` row — the site is a derived artifact, like `syllabus.md`.
Record publishing decisions (method chosen, opt-ins for quizzes or the plan) in
the course-root `history.md` if one exists, otherwise report them in chat.
