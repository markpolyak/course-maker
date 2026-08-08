# Changelog

## [2026-08-08] — Russian README; sharpened pitch

### Added

**`README.ru.md`** — a full Russian adaptation (not a literal translation) for
sharing with Russian-speaking instructor communities, cross-linked with the
English README.

### Changed

**README framing** (both languages). The opening hook, "Why", and "What it does"
now sell the problem solved (weeks of manual preparation; a chat that loses
context between sessions) and the full breadth of the pipelines — lectures,
seminars, labs, quizzes, homework — rather than lecture slides alone. The
opening no longer implies a `course_plan.md` must already exist: creating the
plan is itself part of the pipeline. Claude-specific phrasing ("Claude doesn't
remember…", "causes Claude Code to hang") is now tool-neutral, and the
requirements section reads as "any Agent Skill-compatible agent, tested on
Claude Code, Cowork, Codex CLI, and Cursor" instead of a closed list of three.

## [2026-08-07] — `examples/` populated from a pipeline run; slide cross-references banned by content

### Added

**`examples/regularization-course/`** — the real population of `examples/`
(wave 2, step 2.6). `examples/README.md` had said since `e41d224` that a genuine
example must come from an actual pipeline run rather than being hand-assembled;
this is that run: a 2-lecture course produced end to end (plan, visuals, figures
+ PNGs, slides, speaker notes, history for both lectures) plus a lab through
plan/notebook/spec/tests. The course content is synthetic (institution "Claude
Cowork"), so there was no PII to strip — `examples/README.md` says so explicitly,
along with what the example does not cover (no validated/published lab, no
seminars/quizzes/homework). Scratch files the course's own `history.md` flags as
unwanted and LaTeX build byproducts were dropped and gitignored repo-wide.

### Changed

**Slide cross-references are banned by content, not by direction**
(`step4_slides.md`, `step4_slides_slidev.md`, `SKILL.md`). Two earlier attempts
to stop "compare with slide 20" failed for two reasons visible in the rule text
itself: each statement spelled out the exact phrasings to avoid (which supplies a
template rather than a prohibition — the same mechanism seen with "real"), and
all of them constrained *direction*, leaving a numbered pointer backwards
legitimate. The rule is now positive and direction-free: a slide never cites
another by number or position; continuity comes from naming the content; for a
comparison, put both items on one slide. No example phrasings are given.

**`docs/PROJECT_CONTEXT.md`** — roadmap, known-issues, and file tree brought in
line with the actual repository (the tree predated `skill/profiles/`,
`skill/extensions/`, and most of the current `references/`).

## [2026-08-02] — Stop priming "real"; rejected wording gets a course-wide home

### Fixed

**Authenticity adjectives leaking into generated material.** The skill was
feeding them: "real" appeared 15 times in its own agent-facing instructions ("a
real file", "needs real data", "what a real student sees"), and the model read
that as the register of the task. Three layers, none of which hardcode one
model's tics:

1. **Drop the priming** — all 15 sites now say what they mean ("populated file",
   "computed data", "the dataset from the source", "observed pace"). The only
   surviving "real" is the rule that bans it. Meaning is unchanged, including the
   ban on substituting synthetic data.
2. **One positive rule instead of a growing blocklist** — adjectives asserting
   authenticity are empty for a student: name the property or drop the word.
3. **Close the feedback loop** — rejected wording only ever reached `history.md`,
   which is per unit, so the lesson was relearned every lecture. A word rejected
   twice now also goes to `Never Use` in `course_conventions.md` — course-wide,
   and read by every step that writes text.

Taste stays out of the shared skill: `course_conventions.md` is a course
artifact, and the only layer where language-specific bans can live at all, since
`skill/` is English-only.

## [2026-07-29] — Course plan linter; chunk approval; notes modes; slide count

### Added

**`skill/scripts/lint_plan.py`** — a linter for `course_plan.md` (P1 item 25),
with unit coverage. It checks the Sessions table and per-lecture subsections;
ERROR/WARN findings with a summary line. Two follow-ups fixed real defects: the
k-th `### Lecture` row is matched by lecture sequence, not by the session `#`
column (a valid plan reported two false ERRORs, since the canonical example's
second lecture is session #3); en dash, hyphen, and colon are accepted as
heading separators; duplicate `#` values and duplicate lecture subsections are
reported instead of collapsing silently.

**Linter wired into the pipeline.** It existed but nothing called it, so a plan
could drift unnoticed until `stats` reported wrong totals or `syllabus` shipped a
stale description to students. `course plan` now runs it after every write (all
four phases end in a save): ERROR must be fixed before the phase is reported
done, WARN is reported. TODO warnings are expected in a fresh draft and
explicitly not a blocker in Phase 2. `doctor` runs it as the second half of the
facts layer, replacing the `grep "<!-- TODO -->"` semantic check — one plan check
in one place, so the grep and the linter cannot drift apart.

**Speaker-notes modes** (`step5_notes.md`). `step5_notes.md` gave no volume
target at all, so generation drifted to a summary while the template's spoken
opening ("Good morning…") stayed — notes that read as an outline but start like a
script and match no timing in `plan.md`. Three modes (`minimal` / `medium` /
`detailed`) set how much of the delivery is written out; resolution is
arg → `Notes mode:` in `AGENTS.md` → `medium`. Volume is anchored **per slide**
as factor × speech rate × planned minutes (rate asked once in `course init`,
stored in `AGENTS.md`, 110 wpm assumed if absent), so unevenness cannot average
out across the deck. Verbatim text is scoped to wording that matters — openings,
closings, definitions, transitions, the framing of a derivation — in every mode,
which makes a greeting deliberate instead of a leftover and forbids the
greeting + bullet-point-body hybrid outright. After the last chunk the agent
reports words vs band per slide and offers to fix outliers.

### Fixed

**Per-chunk approval in `slides` and `notes`.** The Inviolable rule "wait for
explicit approval before saving" was unqualified, so it outranked the
dispatchers' "do not pause between chunks" whenever a reference did not restate
the latter; `7a64cab` had patched `notes` at the dispatcher level but left the
conflicting global rule in place, and the auto-chain instruction lived only in
the Slidev reference — the Beamer and notes paths, read in full at execution
time, had nothing to counter it. Both now carry the same chunking protocol, and
the global rule states that approval is per step, not per chunk. Also made
explicit that a chunk is never printed for review instead of being written:
LaTeX is unreadable in a terminal, and the deck is reviewed by compiling it.

**Slide count derived from planned duration** (`step4_slides.md`,
`step1_plan.md`). "Maximum 20 content slides" was unconditional, so a 135-minute
session got the same ceiling as a 90-minute one — 9 minutes per slide, which no
pace justifies. The duration was already available and unused. The count now
follows a target of 3–6 minutes per content slide (~4.5 by default), which
reproduces exactly 20 slides at 90 minutes and gives 30 at 135. Pace is not a new
setting: when earlier lectures have `plan.md`, their `**Total time:**` and
`**Slides:**` give the instructor's observed minutes per slide, and that median
replaces the default. Hardcoded 85–90 min in the plan template and the timing
table total also removed.

**Pipeline vocabulary in student-facing material.** Slides were picking up the
skill's own register: process commentary ("before using this material in future
sessions"), data-authenticity asides, and "honest" as a blanket verdict on
results. Nothing in the skill emitted those strings — the agent was echoing its
own instructions into the artifact, and no rule forbade it. Adds an Inviolable
rule against pipeline concerns appearing in student-facing text, plus a
`Never Use` entry in both `course_conventions` templates for "honest"/"fair" as a
verdict (the precise property — "held-out estimate", "no feature leakage" — says
what is meant). The templates apply to newly initialized courses; existing
courses need the line added to their own `course_conventions.md`.

## [2026-07-23] — Release process

### Added

`scripts/package.sh`, a release GitHub Actions workflow, and `docs/releasing.md`
— packaging the skill as a distributable zip. README, getting-started, and the
Makefile updated accordingly.

## [2026-07-21] — Multi-harness support; Slidev; slides export

The skill is a cross-tool Agent Skill: the same `SKILL.md` runs on Claude Code,
Codex CLI, and Cursor — only the install location differs. This session made that
true in wording, in the course-context layer, and in the docs, and added a second
slide format.

### Added

**Slidev as a second slide format** (`references/step4_slides_slidev.md`,
`templates/slides_headmatter_slidev.md`). A Markdown deck presented and exported
locally via Node (`npx slidev`) — no paid services — reusing the `figures.py` PNG
pipeline unchanged. Format selection: `Slides format:` in the course context
(default `beamer`), overridable per call (`/course-maker slides N slidev`); on
resume the format is detected from the existing deck file (`slides.tex` vs
`slides.md`). Same chunking and forward-reference discipline as the Beamer path;
notes stay in step 5. `course init` asks the format, makes the LaTeX-engine
question beamer-only, and generates either `slides_preamble.tex` or
`slides_headmatter.md`; `user_defaults` gains `default_slides_format`.
`validate_state.py`: a done `slides` step is satisfied by `slides.tex` **or**
`slides.md`.

**`/course-maker slides N export [pdf|png]`** (`references/slides_export.md`) —
mechanical export of an existing deck; no approval, no state change. Detects the
format from the file present (`slides.tex` → Beamer PDF via latexmk/engine;
`slides.md` → `npx slidev export`). A missing export tool produces installation
instructions rather than a silent failure. Presenting a Slidev deck live remains
the user's job — the skill never launches it.

**`AGENTS.md` as the course-context layer.** Course context becomes cross-tool:
`AGENTS.md` is the single source of truth (read natively by Codex CLI and
Cursor), and `CLAUDE.md` is a thin `@AGENTS.md` import wrapper (Claude Code) with
a slot for Claude-only overrides. `skill/COURSE_AGENTS_TEMPLATE.md` holds the
course/lab context, recurring rules, and notes; `COURSE_CLAUDE_TEMPLATE.md` is
reduced to the wrapper. `course_init.md` detects both files, generates both, and
migrates pre-cross-tool courses idempotently (copy inline context into
`AGENTS.md`, then trim `CLAUDE.md`). Guarded by
`tests/static/test_agents_wrapper.py`. A first pass used an indirection rule
("wherever a reference says CLAUDE.md → context, read AGENTS.md"); that was a
`#define TRUE FALSE`-style redirect and was replaced by the real rename across
`SKILL.md`, `references/`, `templates/`, `profiles/`, and `extensions/`.
`CLAUDE.md` is now named only where it is literally the wrapper file.

**`docs/MULTI_HARNESS_PLAN.md`** — verified facts, the two-layer architecture
(skill vs course context), decisions, phased plan, risks, and sources.

### Changed

**Declaudized wording** (Phase 0). Claude Code-specific phrasings generalized
without behavior change: the chunking rationale ("causes Claude Code to hang" →
"exceeds a single generation/context budget and stalls the agent"), the
`lab validate` fresh-context step (now names all three tools instead of assuming
`/clear`), and "Claude" → "the agent" in instruction prose.

**Install documentation.** Two global symlinks — `~/.claude/skills` (Claude Code)
and `~/.agents/skills` (Codex CLI + Cursor) — with copying documented as the
self-contained alternative. An earlier note, based on a third-party blog, wrongly
claimed Cursor is project-scoped only; the official docs
(https://cursor.com/docs/skills) show Cursor loads skills from global locations
including the Claude Code and Codex directories, so it piggybacks and needs no
symlink of its own. Cursor de-duplicates the double install, so the documented
duplicate caveat was softened to match observed behavior. Manual smoke by the
instructor confirmed the skill loads in all three tools.

**Bundled-resource paths are skill-root-relative.** Internal references pointed
at `skill/templates/…`, `skill/extensions/…`, `skill/profiles/…`, which matches
the repository layout but not the installed skill (whose root has no `skill/`
subdirectory); the hosts tolerated it only via fuzzy file resolution. All 22
such paths de-prefixed and verified to resolve. Files copied into a user's course
repo keep the `skill/…` form, since a bare `extensions/…` would be meaningless
there.

**Claude chat app (claude.ai / Desktop) marked out of scope.** It supports custom
skills via zip upload, but runs them in a sandboxed cloud VM — no local course
repo, git, or LaTeX/pandoc/pytest toolchain, and an ephemeral filesystem. Claude
Code for Desktop is just Claude Code and remains fully supported.

## [2026-07-20] — Wave 5 (partial): homework; wave 6 closed out

### Added

**`/course-maker homework` pipeline** (`references/homework.md`) — a light
take-home pipeline distinct from labs: a task brief plus an instructor-only
rubric, manually graded, with no `starter/`, autograder, CI, or `validate`. The
model is "task brief + rubric", not "lab minus CI". `homework plan N [dir]`
produces `task.md` + `rubric.md`; `homework publish N [format]` assembles
`homework_student.md` (markdown default, pdf/latex/docx via pandoc, like
`syllabus`) and strips instructor-only content with a leak check — the rubric
reaches the student handout only if opted into at plan time. `HW_DIR` resolves
from a `Dir` column holding a full path from the course root, so homework can
nest under a seminar (`seminars/<name>/homework/`). State: a `## Homework`
section, drift-checked by `validate_state.py` (task/rubric/published, with
nested-`Dir` resolution) and covered by `doctor` and `stats`.

**`docs/EXAMPLE_COURSE_PLAN.md`** — a step-by-step plan (with prompts) for
producing a real `examples/` course from an actual pipeline run.

### Changed

**`history.md` compaction reframed** (wave 6, step 6.3). A full
`/course-maker compact-history` command is **deferred**: at realistic per-unit
sizes the pain is hypothetical, and lossy compaction risks dropping exactly the
rejected-idea detail that `history.md` exists to preserve. The cheap, risk-free
alternative: `validate_state.py` emits an advisory `BULKY` finding when any
`history.md` exceeds `HISTORY_WARN_LINES` (200), never changing the exit code;
`doctor` frames it as optional housekeeping — trim resolved iterations by hand,
keep rejections verbatim. Two unit tests.

**README drift fixed.** The README was behind both the command surface and the
wave 4 profile refactor: added the Seminar, Quiz, and Homework command tables and
`doctor`/`stats`/`syllabus`; made `lab publish`/`lab init` LMS-agnostic
(`lms_adapter.md`, optional URL) instead of hardcoding GitHub Classroom + git
subtree; updated the repository layout and roadmap.

## [2026-07-09] — Nightly e2e trigger disabled

### Fixed

**Unattended e2e runs.** The nightly cron was firing on its own and sending
daily "Run failed: e2e" mail even though e2e is manual-only. Commented out rather
than removed, so the disabled configuration stays visible.

## [2026-07-02] — Neutralized the Russian grade-label default

### Changed

The `ru` template shipped a specific external-CI gradebook phrase as the default
grade-output label, so every Russian course inherited one instructor's autograder
contract. It is replaced with a generic label; an instructor's exact phrase now
lives in their personal `user_defaults`, outside the shared repository:
`profiles/README.md` documents optional `default_grade_output_label` /
`default_taskid_label` / `default_scoring_header`, and `lab course-init` Phase 2a
resolves each reporter label by precedence
user_defaults → `lab_templates.md` → reporter default. The personal string no
longer appears anywhere under `skill/` (only in historical docs). This closes
wave 2, step 2.4.

Also documented (2026-07-01): labs default to plain pytest pass/fail — no scoring
block, no autograder line, no per-student variants — with a getting-started
walkthrough for enabling an autograded course with variants.

## [2026-06-29] — Wave 4 revision (2/2): rewiring, guards, LMS-owned starter setup

### Changed

**Lab references rewired around the two flags.** The per-student variant formula
no longer appears inline in any universal file; every mention is conditional
("when `lab_variants: true`, see `extensions/variants/README.md`"), across
`lab_context`, `lab_step1a_plan`, `lab_step1b_notebook`, `lab_step1b_spec`
(Datasets / Variant Variables marked variants-only), and `lab_step3_validate`
(which also lost a stray master's-student audience hardcode). Grade labels moved
to the reporter: `lab_step2_tests` Step 4 edits `grade_report.py` instead of
`conftest.py`, and the "conftest.py Strings" section of `lab_templates_{en,ru}`
became "Grade reporter labels".

**Inviolable rules made conditional** (`SKILL.md`). The two global `NEVER`
grading invariants presupposed that every lab has per-student variants and an
external-CI grade format. The variant formula is now an invariant only when
`lab_variants: true`, and the grade-output layout is fixed only when a grade
reporter is configured — removing the last inline copy of the formula from the
universal files. The quiz-answers invariant is unchanged.

**`tests.yaml` stops presenting `STUDENT_ID` and grade capture as universal.**
Both are conditional: `STUDENT_ID` matters only with variants (harmless
otherwise), and grade-line capture only with a reporter. A generic course gets
plain pytest pass/fail as the CI outcome.

**Starter setup moved out of `lab_init` into the LMS profile.** `lab_init.md`
unconditionally ran `git subtree add … <url>`, which is the GitHub Classroom
model (a separate public starter repo); a local-zip course has no such repo or
URL. Step 4 now delegates to `lms_adapter.md` § "Lab init — starter setup":
`github-classroom/lms.md` attaches the public starter repo via `git subtree add`,
`local-zip/lms.md` just creates a local `starter/`. The `<url>` argument is
optional, required only for remote-starter profiles.

**Anti-personalization guard hardened.**
`test_no_variant_formula_in_universal_files` drops its `xfail` and becomes a hard
guard now that the formula is gone from universal files; the English-only guard
now also scans `skill/extensions/*.md`, since the opt-in reporter and variant
docs are skill machinery.

## [2026-06-28] — Wave 4 revision (1/2): grading as opt-in extensions

The grading layer was extracted **not** into a profile (as wave 4 step 4.4
assumed) but into a third axis, `skill/extensions/`. Rationale: an autograder
contract and a variant scheme are orthogonal to both the LMS and the instructor —
autograding can run locally, and one instructor may teach one course with
variants and another without.

### Added

**`skill/extensions/reporters/scoring_ci.py`** — the scoring block removed from
`conftest_base.py`, exposed as `report(outcomes)` per the reporter seam. It
preserves the previous output verbatim (boxed scoring block, per-block markers,
grade line, bonus tally) and the external-CI grade-line contract, so a course
that opts in grades exactly as before. The TASKID line is printed only when
`DATASETS` is non-empty, making the reporter independent of the variant
extension. `README.md` documents the contract, selection (`grade_reporter:` in
the course context), installation, and how to write your own.

**`skill/extensions/variants/`** — the per-student variant system, gated by
`lab_variants: true` rather than baked into Block 0 of every lab, since many labs
give every student the same task. `README.md` states when to enable it, what
changes on and off, and the canonical formula
`dataset_id = (student_id - 1) % len(datasets)` as an invariant that holds only
while variants are in use; `block0_snippet.md` carries the Block 0 cells with
language-neutral code (localized prose still comes from `lab_templates.md`).

### Changed

**`conftest_base.py` reduced to a universal harness.** It had mixed a universal
pytest harness (notebook import, fixtures, outcome tracking) with one
instructor's grading contract: a fixed `pytest_sessionfinish` scoring block,
TASKID/GRADE/SCORING labels, and the variant formula. Everything personal is
stripped; the harness collects per-test outcomes and, at session end, hands them
to an optional `grade_report.py` (`report(outcomes)`) sitting next to it. With no
reporter, plain pytest — nothing extra printed. The universal harness now
presupposes neither an autograder nor a variant scheme.

**`grade_reporter` / `lab_variants` flags wired into `lab course-init`.** Both
default to the generic path (`none` / `false`). Phase 2a no longer substitutes
labels into `conftest_base.py` (they are gone from the harness); instead, when a
reporter is selected, it copies `extensions/reporters/<name>.py` to
`labs/shared/grade_report.py` and substitutes course-language labels there.
`lab init` copies `grade_report.py` into each lab's `starter/` when present.
Phase 1 stops hunting for a placeholder conftest — it ships real now.

**Lab audience universalized.** `lab_context.md` hardcoded a master's-level role
for every course; the audience level and background now come from the course
context, matching the lecture pipeline (wave 4, step 4.4).

## [2026-06-26] — Automated test suite; `/course-maker lab triage`

### Added

**`tests/` — a three-level harness**, replacing manual command-by-command
checking:
- **Level 0 (`tests/static`)** — deterministic skill checks: English-only guard,
  command↔reference structure integrity, py/yaml syntax, and an
  anti-personalization tracker (no personal literals hardcoded).
- **Level 1 (`tests/unit`)** — contract tests for `validate_state.py` (exit codes
  and DRIFT/STALE/UNTRACKED/BLIND findings) and `nonlatin.py`.
- **Level 3 (`tests/e2e`)** — opt-in behavioural smoke tests (`COURSE_MAKER_E2E=1`)
  that drive the skill against a fixture course and assert deterministic
  post-conditions for figures, slides, and quiz publish. Each run captures the
  turn-by-turn conversation to `tests/e2e/logs/<command>.jsonl` (gitignored) and
  prints the path; `COURSE_MAKER_E2E_MODEL` pins the model for reproducibility.

Wiring: `Makefile`, `tests/requirements.txt`, `tests/README.md`, `pytest.ini`,
and CI workflows (checks on push/PR; e2e on dispatch).

**`/course-maker lab triage N`** (`references/lab_triage.md`, wave 5 step 5.5) —
after a `⚠️` validation, reads the latest Step 3 history entry, classifies each
issue to its root-cause step (plan / notebook / spec / datasets / tests), and
names the command to run next (earliest pipeline step first). Read-only: edits
nothing, changes no state.

## [2026-06-18] — Wave 5 (partial): seminar pipeline

A seminar = a lecture deck plus a practical part, all in `seminars/NN/` (the
"full mirror" model, chosen over a practice-only or problem-walkthrough model).
This also closes a real gap: the drift checker tracked `## Seminars` but no
command wrote to `seminars/` — now the deck steps do.

### Added

**`/course-maker seminar` pipeline:**
- `seminar plan|visuals|figures|slides|notes N` reuse the lecture step
  references (`step1_plan.md` … `step5_notes.md`), retargeted to `seminars/NN/`.
  Each step reference gained a "Session directory" note making the
  `lectures/NN/` → `seminars/NN/` substitution explicit.
- `seminar practice N` (`references/seminar_practice.md`) generates
  `seminars/NN/practice.ipynb` — an instructor-driven live code-demo notebook,
  not autograded (no conftest/tests). Chunked by section; executed top-to-bottom
  (`nbconvert --execute`) and fixed until clean before `practice → ✅`.
- `seminar status N`.

The form of the practical part is course-specific; the skill stays neutral and
ships only the demo-notebook flavor here.

**State + drift:** `## Seminars` gains a `practice` column; `validate_state.py`
drift-checks the deck artifacts plus `practice.ipynb` for seminars (lectures
unaffected — `check_lecture_like` gained an `extra_steps` param).
`repository_layout.md` documents the `seminars/` layout, the `## Seminars` state
table, and the `practice` vocabulary key.

### Changed

**SKILL.md** (346/350): Seminar commands table + Seminar workflows section; the
chunking inviolable rule now covers `seminar practice`; `help` prints four
tables (Lecture, Seminar, Lab, Quiz); no-arg status lists seminars; `/seminar`
added to the trigger description.

## [2026-06-17] — Wave 5 (partial): syllabus

### Added

**`/course-maker syllabus [pdf|latex|docx]`** (`references/syllabus.md`) —
generates a student-facing `syllabus.md` from `course_plan.md` (title,
instructors, description, prerequisites, human-readable schedule, grading,
materials) in the course language. Drops internal pipeline notes
(`labs/lab1/`, `quizzes/01/`, `no pipeline`) and **omits unfilled
`<!-- TODO -->` sections** — these are reported to the instructor in chat, never
leaked into the student document. With a format arg it exports via pandoc (pdf
needs a LaTeX engine; latex and docx are pandoc targets too); if pandoc is
missing it leaves the markdown in place and explains how to convert. A derived
view of the plan — no state row, no history; regenerate when the plan changes.
`syllabus.md` added to the course-root layout in `repository_layout.md`.

### Fixed

**`notes` auto-chains chunks without per-chunk approval** (`SKILL.md`). It used
to ask for approval before saving every chunk because, unlike `slides`, its
CRITICAL block lacked the "do not pause between chunks" phrase, so the global
"wait for approval before saving" rule took over. Now mirrors `slides`: all
chunks are appended back to back; approval is only for marking the step done.

## [2026-06-16] — Wave 5 (partial): quiz pipeline

Implemented `/course-maker quiz` only (the rest of wave 5 — syllabus, seminar,
homework, lab triage — is untouched). Named `quiz` (not `test`) to avoid the
collision with lab autograding `tests` (`tests.py`/pytest) and the Russian
reading of "test" as "experimental/not yet tested".

### Added

**`/course-maker quiz` pipeline** — three commands and reference files:
- `quiz plan N` (`references/quiz_plan.md`): interactive plan. Question types and
  counts are instructor-defined (not hardcoded); supports a pool (`M = 1`) or
  `M > 1` parametrized variants per question. Output `quizzes/NN/quiz_plan.md`.
- `quiz generate N [next]` (`references/quiz_generate.md`): generates the
  canonical bank `quizzes/NN/quiz_questions.md` with answers inline (the bank is
  also the answer key). Chunked one block per chunk — a full bank is 600+ lines
  and one-shot generation hangs Claude Code, same as slides. Content in the
  course language. Format modeled on a real exam bank.
- `quiz publish N [format]` (`references/quiz_publish.md`): exports a
  student-facing copy with all answers stripped. Only `markdown` is implemented;
  the dispatcher is ready for latex/docx/moodle (not built). A mandatory
  `grep ✓` leak check must return empty before a quiz is marked `published`.

Architecture mirrors labs: a canonical instructor-only source separated from the
student-facing export (bank ↔ publish, like `lab_spec.md` ↔ `starter/`).

**State + drift integration**: new `## Quizzes` section in `COURSE_STATE.md`
(English-canonical columns `plan | questions | published`). `validate_state.py`
checks it (published satisfied by `quiz_student.md` or any `quiz_variant_*.md`);
blind-run guard, summary, and `doctor.md` coverage all include quizzes.

### Changed

**Inviolable rules**: the chunking rule now covers `quiz generate`; a new
grading invariant forbids handing `quiz_questions.md` to students and requires
the answer-leak check before marking a quiz published.

**SKILL.md target raised 300 → 350**: with a 4th pipeline plus the inline
CRITICAL safety blocks, ≤300 was unreachable without removing safety rails.
Updated in `contributing.md`, `PROJECT_CONTEXT.md`, and the IMPROVEMENT_PLAN
success criterion. Also slimmed: `course update`/`lab update` workflows extracted
to `references/`; redundant Input/Output/State lines removed from the
`plan`/`visuals` dispatchers (they duplicated the references). SKILL.md is ~312.

**`/course-maker help` fix**: the instruction said "print the tables above",
which Claude read as already-shown (the tables are in its loaded SKILL.md) and so
it only said so — but the user never sees SKILL.md. Now it prints the three
command tables into the chat.

**Cyrillic scrub**: removed Russian that had entered skill instruction files
(variant-label and section-heading examples added earlier this session, and a
pre-existing Russian outline-title example in `step4_slides.md`). Skill machinery stays
English-only; illustrative labels are Latin with a course-language note.

## [2026-06-14] — Improvement wave 6 (QoL & observability)

Scope decisions for this wave (from design discussion): the lock-file step was
**dropped** (single-user git-backed repo; a stale `.lock` from a crashed session
causes more harm than the rare concurrent-run it prevents), and `history.md`
compaction was **deferred** (no real large `history.md` exists to design against;
folding it on spec risks losing the rejected-ideas memory that is its whole
value). `doctor` is **read-only** this iteration — it reports and names the fix
command, never edits.

### Added

**`scripts/validate_state.py`** — the skill's first executable artifact. Facts
layer for drift detection: parses `COURSE_STATE.md` and cross-checks every `✅`
status against the artifact that should exist on disk. Lenient Markdown parser
(maps columns by header name, agnostic to order/spacing), pure stdlib. Findings
are prefixed `DRIFT` (done but missing) / `STALE` (figures older than
`figures.py`) / `UNTRACKED` (artifact exists, status ❌) / `SKIP` (unparseable
row). Exit code 1 on drift/stale so it is usable standalone in external CI. The
step→file mapping is kept in sync with `references/repository_layout.md`.

**`/course-maker doctor`** (`references/doctor.md`) — read-only diagnostic.
Step 1 runs `validate_state.py` (mechanical facts). Step 2 adds semantic checks
Claude does itself: leftover `<!-- TODO -->` in `course_plan.md`,
profile↔`lms_adapter.md` consistency, presence of generated config files
(`course_conventions.md`, `slides_preamble.tex`, `lab_templates.md`). Step 3
reports each finding with the exact command that fixes it. The split — script
for deterministic facts, instructions for judgement — is the deliberate hybrid
chosen for this wave.

**`/course-maker stats`** (`references/stats.md`) — read-only progress bars.
Planned totals from `course_plan.md` (Overview/Sessions + per-lecture estimated
time); completion from `COURSE_STATE.md` (lecture complete = all 5 steps ✅, lab
complete = tests+validated+published ✅). 10-cell bars per pipeline, optional
hours line, in-progress list; flags plan/state count mismatches toward `doctor`.

### Changed

**Slides stale-figure guard** (`references/step4_slides.md`, `SKILL.md`). The
slides step now lists PNGs *with timestamps* and warns when any PNG is older
than `figures.py` (figures may be out of date), offering to re-run
`/course-maker figures N` first. A warning, not a hard block. Same fact the
`validate_state.py` `STALE` finding surfaces, applied inline at slide time.

**`SKILL.md`**: `doctor` and `stats` added to the command table and as thin
dispatchers (now 299 lines — still under the 300 target, but tight; the next
addition should prompt extracting something).

---

## [2026-06-13] — Improvement waves 1–3

### Added

**`IMPROVEMENT_PLAN.md`** (`docs/IMPROVEMENT_PLAN.md`) — comprehensive skill
review and 7-wave execution roadmap. Each wave has atomic steps and
completion criteria. Recommended execution order: 1 (SKILL.md compaction) →
2 (bootstrap) → 3 (doc drift) → 4 (profiles) → 6 (QoL) → 5 (new pipelines)
→ 7 (alternative formats).

**`## Inviolable rules` block in `SKILL.md`** — 15 rules grouped into
Observability, Grading invariants, Validation isolation, Slides & figures,
and Process. They apply regardless of which reference file was read. The
first rule is the observability rule: every step must list which
`references/*.md` files were read in the first chat message — silent skips
become detectable. Rationale: critical rules buried in 100-line workflows
are skipped as often as instructions in external reference files; sticky
rules require short, high-visibility, negatively framed statements that
survive any path.

**New reference files** extracted from the bloated `SKILL.md`:
`references/course_init.md`, `course_plan.md`, `lab_course_init.md`,
`lab_init.md`, `lab_publish.md`, `repository_layout.md`. The `lab_publish.md`
file additionally documents recovery from `git subtree push` failures caused
by GitHub Classroom squashed-history divergence.

**Working out-of-the-box templates** (`skill/templates/`):
- `conftest_base.py` — real pytest conftest (~210 lines): IPython mocking,
  nbformat-based student notebook importer, `student_module` fixture,
  outcome tracking, session finalizer with parameterized labels
  (`TASKID_LABEL`, `GRADE_OUTPUT_LABEL`, `SCORING_HEADER`). Substitutes
  the previous placeholder that required pasting from a real lab.
- `tests.yaml` — real GitHub Actions workflow: checkout, setup-python,
  install requirements + pytest + nbformat + jupyter, nbconvert, pytest.
  `STUDENT_ID` read from a repo variable so external CI can override per-fork.

**`.gitignore`** for `__pycache__/`, editor caches, OS metadata.

**`examples/`** stub with an honest README (`examples/README.md`).
Hand-assembled artifacts labelled as "produced by the skill" would diverge
from real pipeline output in tone, history.md evolution, and cross-step
coherence — so the directory stays empty until a genuine example is produced
by running the skill.

**`docs/contributing.md`** — minimal contribution guide (priorities, skill
conventions, PR checklist).

**`docs/archive/`** — completed planning documents moved here:
`TEMPLATE_MIGRATION_PLAN.md` (template language abstraction — done) and
`LAB_PIPELINE_PLAN.md` (labforge integration — done). The archive README
explains what was implemented for each.

### Changed

**`SKILL.md` compacted from 978 → 280 lines** (target ≤300). Full
workflows for `course init`, `course plan`, `lab course-init`, `lab init`,
and `lab publish` moved out to dedicated reference files. Each command in
`SKILL.md` is now a thin dispatcher (`Read: references/X.md`) plus, for
steps with a history of silent skips (`figures`, `slides`, `notes`,
`lab validate`), a short `**CRITICAL — even if reference was skipped:**`
block. Repository layout and state file formats extracted to
`references/repository_layout.md`.

**`tests_template.py` translated from Russian to English.** The file is
the universal style reference for generated `tests.py`; per-language strings
(error messages in the course language) are substituted at generation time
from `course_conventions.md`.

**Grade output strings are now parameters, not invariants.** The Russian
phrases `СИСТЕМА ПОДСЧЁТА БАЛЛОВ ДЛЯ ЛАБОРАТОРНОЙ РАБОТЫ` and
`ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА В ЖУРНАЛ` (read by external CI) used to be hardcoded
"critical invariants" in `conftest_base.py` and `lab_step2_tests.md`. They
are now values in `lab_templates_ru.md` (and English equivalents in
`lab_templates_en.md`) under `SCORING_HEADER`, `TASKID_LABEL`,
`GRADE_OUTPUT_LABEL`. `conftest_base.py` parameterizes the print() format
once; per-course labels are substituted during `lab course-init` (new
Phase 2a). The print() format itself is fixed, so external CI still
matches; the labels become a course/language configuration knob.

**`COURSE_CLAUDE_TEMPLATE.md` no longer embeds `SKILL.md`.** Removed the
`SKILL:START`/`SKILL:END` markers and the reference to the non-existent
`/skill update` command. The skill is loaded globally from
`~/.claude/skills/course-maker/` and discovered automatically — embedding
it in course-level `CLAUDE.md` was redundant and went stale on every
skill update.

**`docs/PROJECT_CONTEXT.md` updated**:
- Layout corrected (`course-maker/skill/SKILL.md` not `course-maker/SKILL.md`)
  and expanded to list all current files in `skill/`, `docs/`, `examples/`.
- "Known issues" updated: chunked-generation is no longer "in v2", Inviolable
  rules and out-of-the-box templates marked fixed in waves 1 and 2.
- Roadmap pointed to `IMPROVEMENT_PLAN.md` as the authoritative source;
  original design intent preserved for context.
- Agent-agnostic core and Overleaf integration kept as separate items
  (different goals, different consumers).

**`docs/getting-started.md` updated**: the lab `reverse-spec` example
replaced with the new `lab spec` auto-detect notebook-mode flow.
Pre-init manual file copy step removed (handled by `course init`).

**`README.md` updated**: command tables now match `SKILL.md` (added
missing commands: `/course-maker` (no-arg status), `/course-maker help`,
`/course-maker course plan`, `lab datasets`, `lab update`, `lab status`;
split into two tables: Lecture pipeline and Lab pipeline). Repository
layout now lists `course_conventions.md`, `slides_preamble.tex`,
`lab_templates.md`, and `labs/`. Roadmap aligned with `IMPROVEMENT_PLAN.md`.
"Examples" section honest about the empty stub state.

### Fixed

**Reference dispatchers reorganized** so that lab `spec` reflects the
auto-detection of plan vs notebook mode (no separate `reverse-spec`
command — the previous merge is now consistently documented).

---

## [2026-06-04] — Per-course preamble, hardened validate, slide numbering

### Added

**Per-course LaTeX preamble template** (`skill/templates/slides_preamble_pdflatex.tex`,
`slides_preamble_xelatex.tex`). The engine choice (pdflatex / xelatex /
lualatex) is asked during `course init`; the correct preamble template is
copied to `slides_preamble.tex` in the course root. Removes the hardcoded
engine assumption.

### Changed

**Slide numbering convention** (`skill/references/step1_plan.md`,
`skill/references/step4_slides.md`): title = slide 1, outline = slide 2,
first content slide = 3. Slide numbers are absolute and never restart.
Comments in `slides.tex` (e.g. `% Slide 07`) match `plan.md` exactly.

### Fixed

**`lab validate`: inline critical rules to prevent silent skips**
(`skill/SKILL.md`, `skill/references/lab_step3_validate.md`). Even when
`references/lab_step3_validate.md` is skipped (which happens under heavy
context), the inline `**CRITICAL rules — apply regardless of whether the
reference file was read:**` block enforces: never read `history.md` during
the student simulation; never open `tests.py`, `conftest.py`, or
`tests_template.py` until tasks are complete; download the dataset from
Block 0; run `nbconvert + pytest tests.py -v` and show full output.

---

## [2026-05-31] (2)

### Added

**`/course-maker course plan` — dedicated command for course plan creation and filling**
(`skill/SKILL.md`, `skill/references/step1_plan.md`)

`course_plan.md` is now a first-class artifact with its own command. The command is
idempotent: detects whether the plan is missing, partial (has `<!-- TODO -->` sections),
or complete, and picks up from the right place.

**Three creation modes:**

- **[1] Import existing plan** — accepts a file path or pasted content in any format.
  Claude extracts sessions, lecture topics, labs, prerequisites, grading, and instructor
  info; fills a structured template; marks anything not found as `<!-- TODO -->`.
  Original file saved as `course_plan_source.*`. Iterates until approved.

- **[2] Structure known content** — 10-question dialog (one at a time) covering session
  types and counts, schedule, topics, prerequisites, grading, self-study materials,
  instructor info. Skips questions the user presses Enter on (filled with TODO).

- **[3] Help determine content** — same dialog, but after collecting basics Claude
  generates a full proposed outline using knowledge of typical university curricula
  for the subject and audience. Iterates with open-ended feedback until approved.
  Claude is explicit that the proposal is based on general knowledge.

**`course_plan.md` format** now includes:
- `## Overview` — session type counts and standard duration
- `## Sessions` table — all sessions of all types in chronological order; sessions
  without a skill pipeline marked `no pipeline`
- `## Lectures` — one subsection per lecture with topics, time, within-course
  prerequisites, and announce-only sections
- `## Labs` — one-line pointer per lab to the lab pipeline directory
- `## Prerequisites`, `## Grading`, `## Self-study Materials`, `## Instructors` —
  optional sections with `<!-- TODO -->` until filled

**`/course-maker course plan update`** — dedicated command for intentional plan edits
(session removed, topic shifted, schedule compressed). Applies edits, then cross-checks
`COURSE_STATE.md` and flags affected lectures/labs as ⚠️.

**`/course-maker course update`** — narrowed to detecting *manual* edits (git diff)
and flagging affected materials. No longer handles intentional edits (use `course plan update`).

**`course init`** no longer runs a plan dialog — just reports if `course_plan.md` is
missing and points to `/course-maker course plan`.

`step1_plan.md` updated to read from the new `## Sessions` table and `## Lectures`
subsection format.

---

## [2026-05-31]

### Fixed

**lab validate: no /clear prompt before validation** (`skill/references/lab_step3_validate.md`, `skill/SKILL.md`)

The current session context contains `lab_spec.md`, `tests.py`, and `conftest.py` from
prior steps, which would compromise the student simulation. The skill now shows a blocking
message asking the user to run `/clear` (or open a new session) and re-run the command.
Validation does not proceed until the user confirms the context has been cleared.

**lab validate: no guard against uncommitted changes, notebook not restored after validation** (`skill/SKILL.md`, `skill/references/lab_step3_validate.md`)

Validation simulates a student solving `exercises.ipynb`, which modifies the file.
If the notebook wasn't committed before validation, the clean version was lost permanently.
After validation the notebook was left with student solutions in the working tree.

Now the workflow:
- Runs `git status <LAB_DIR>starter/` before starting; stops with an error message if there
  are uncommitted changes, asking the user to commit first
- After validation completes, runs `git restore <LAB_DIR>starter/exercises.ipynb` to remove
  student solutions from the working copy

**figures step marked ✅ without running the script** (`skill/SKILL.md`, `skill/references/step3_figures.md`)

After generating `figures.py` and getting user approval, the skill saved the file and
immediately marked the step done — without running the script or verifying that PNG files
were created. Code that has never been run must be treated as unverified.

Now the workflow after approval:
1. Saves `figures.py`
2. Runs `python figures/figures.py` from the lecture directory
3. If errors: shows traceback, fixes the script, re-runs until clean
4. After clean run: lists generated PNGs for the user to confirm
5. Only then marks figures → ✅

### Changed

**Skill reference files made language-agnostic** (`skill/references/step4_slides.md`, `skill/references/step5_notes.md`)

Russian strings in the lecture pipeline reference files were replaced with English equivalents
and annotated with "translate to course language" instructions. The skill now works with any
course language; the output language is determined at generation time from the course context
in CLAUDE.md.

Changes:
- `step4_slides.md`: `\subtitle{Лекция N. [Title]}` → annotated placeholder that reads
  the course-language word for "Lecture" at generation time; outline frame title
  `План лекции` likewise replaced with a language-neutral placeholder
- `step5_notes.md`: entire output template translated from Russian to English;
  all Russian section headers, table headers, stage directions, and example speech replaced
  with English equivalents; each heading annotated "(translate to course language)" so the
  generated notes are still produced in the correct course language

### Added

**Language-specific template files** (`skill/templates/`)

Four new source files that serve as the language-specific content layer for each course:

- `lab_templates_ru.md` / `lab_templates_en.md` — notebook header cell, Block 0 cells
  (tasks 0.1–0.3 with code), final checklist cell, self-check cell, function/variable stub
  format, task title format, hint format, bonus marker, conftest scoring block marker,
  grade output string, datasets_info section title
- `course_conventions_ru.md` / `course_conventions_en.md` — language rule, terminology
  dictionary (English ↔ course language), "never use" list, lab goal writing rule with
  bad/good examples

These files are copied to the course root by the init wizards and edited by the professor
to match the course. The skill references read from the course-root copies, not from
`skill/templates/` directly.

### Changed

**Skill reference files made fully language-agnostic** (all `skill/references/lab_*.md`,
`skill/references/step1_plan.md`, `skill/references/step4_slides.md`,
`skill/references/step5_notes.md`, `skill/SKILL.md`, `skill/COURSE_CLAUDE_TEMPLATE.md`)

All language-specific content (Russian notebook templates, terminology dictionary,
docstring format, TODO comment style, scoring strings, section titles) has been moved
out of skill reference files into the new `skill/templates/` source files. Reference
files now point to `course_conventions.md` and `lab_templates.md` in the course root
instead of embedding the content directly.

Specific changes:
- `lab_context.md`: removed "Language and Terminology", "Notebook Structure", and
  "Notebook Task Formatting" sections; added "Required reading" block directing the
  skill to read `course_conventions.md` and `lab_templates.md` before any lab command;
  "What NOT to do" examples now reference `course_conventions.md` instead of hardcoding
  Russian examples
- `lab_step1b_notebook.md`, `lab_step2_tests.md`, `lab_step1b_datasets.md`,
  `lab_step1a_plan.md`, `lab_step1b_spec.md`, `lab_reverse_spec.md`: added
  `course_conventions.md` and/or `lab_templates.md` to "Context to Read" lists;
  replaced hardcoded Russian strings with references to the template files
- `step1_plan.md`, `step4_slides.md`, `step5_notes.md`: added `course_conventions.md`
  to "Context to gather before writing"

**`/course-maker course init` is now idempotent** (`skill/SKILL.md`)

The command can be safely re-run on an existing course — to recover missing files or
after accidental re-invocation. Restructured into four phases mirroring `lab course-init`:

- Phase 1: auto-detects `CLAUDE.md` (missing / placeholder / filled), `COURSE_STATE.md`,
  `course_conventions.md`, and directory structure
- Phase 2: asks only the questions whose answers are not already in `CLAUDE.md`
- Phase 3: creates only the files that are missing; never overwrites existing files
- Phase 4: prints a summary of what existed, what was created, and what to do next

`course_conventions.md` is created in Phase 3 (language template copied from
`skill/templates/course_conventions_{lang}.md`).

**`/course-maker lab course-init` Phase 5 creates both template files** (`skill/SKILL.md`)

Phase 5 now creates `lab_templates.md` if it does not exist (previously undocumented).
Acts as a fallback for existing courses that were set up before template files were
introduced — re-running `lab course-init` is enough to get `lab_templates.md` without
going through `course init`.

**Repository layout updated** (`skill/SKILL.md`)

Added `course_conventions.md` and `lab_templates.md` to the documented course root layout.

**`COURSE_CLAUDE_TEMPLATE.md` updated**

Added a note below the Language field explaining that `course_conventions.md` and
`lab_templates.md` are generated automatically by the init wizards and should be
edited after generation if the course conventions differ from language defaults.

---

## [2026-05-29]

### Fixed

**Wrong command suggestions after each step** (`skill/SKILL.md`, `docs/getting-started.md`, `README.md`)

Claude Code was suggesting non-existent short-form commands to the user after completing each pipeline step:
- After `/course-maker plan N`, Claude suggested `/lecture visuals N` → unknown command error
- After completing a lab step, Claude suggested `/lab tests N` → unknown command error

Root cause: `SKILL.md` documented commands in a short form (`/lecture plan N`, `/lab plan N`) that
predates the `course-maker` skill name. Claude Code resolves slash commands by looking up a skill with
that exact name — since no `lecture` or `lab` skill exists, it reports "unknown command."

Changes:
- Updated Quick reference tables (lecture and lab commands) to use full invocation form
- Updated all workflow section headers (`### /lecture plan N` → `### /course-maker plan N`, etc.)
- Updated in-text references to commands inside workflow descriptions
- Fixed chunked-generation suggestions in slides and notes workflows:
  `Type /lecture slides N next` → `Type /course-maker slides N next`
- Fixed `/course-maker lab course-init` completion message
- Added General rule: "Always use the full invocation form when suggesting next commands"
- `docs/getting-started.md`: updated all lab command examples to `/course-maker lab *` form
- `README.md`: added lab commands to the Commands table

**Command format reference (after this fix):**

| Before (broken) | After (correct) |
|---|---|
| `/lecture plan N` | `/course-maker plan N` |
| `/lecture visuals N` | `/course-maker visuals N` |
| `/lecture figures N` | `/course-maker figures N` |
| `/lecture slides N` | `/course-maker slides N` |
| `/lecture notes N` | `/course-maker notes N` |
| `/lecture status N` | `/course-maker status N` |
| `/course init` | `/course-maker course init` |
| `/course status` | `/course-maker course status` |
| `/course update` | `/course-maker course update` |
| `/lab course-init` | `/course-maker lab course-init` |
| `/lab init N` | `/course-maker lab init N` |
| `/lab plan N` | `/course-maker lab plan N` |
| `/lab notebook N` | `/course-maker lab notebook N` |
| `/lab spec N` | `/course-maker lab spec N` |
| `/lab tests N` | `/course-maker lab tests N` |
| `/lab validate N` | `/course-maker lab validate N` |
| `/lab publish N` | `/course-maker lab publish N` |
| `/lab update N` | `/course-maker lab update N` |
| `/lab reverse-spec N` | `/course-maker lab reverse-spec N` |
| `/lab status N` | `/course-maker lab status N` |

---

## [fa115d0] — 2026-05-28

### Added

- Lab assignment pipeline (`/course-maker lab *` commands):
  - Steps: plan → notebook → spec → datasets → tests → validate → publish
  - `references/lab_step1a_plan.md`, `lab_step1b_notebook.md`, `lab_step1b_spec.md`,
    `lab_step1b_datasets.md`, `lab_step2_tests.md`, `lab_step3_validate.md`, `lab_context.md`
  - `references/lab_reverse_spec.md` — generate spec from existing notebook
  - `skill/templates/`: `conftest_base.py`, `tests_template.py`, `tests.yaml`
  - `docs/LAB_PIPELINE_PLAN.md` — design document for the lab pipeline

## [cc12be7] — 2026-05-28

### Added

- `docs/LAB_PIPELINE_PLAN.md` — planning document for the lab pipeline integration

## [9af9002] — 2026-05-28

### Changed

- Updated installation instructions in README

## [cba4c8b] — 2026-05-28

### Changed

- Renamed project from `lecture-pipeline` to `course-maker`

## [70dc5d7] — 2026-05-28

### Added

- Initial release: lecture pipeline (steps 1–5: plan, visuals, figures, slides, notes)
- `skill/SKILL.md` with full workflow descriptions
- `skill/COURSE_CLAUDE_TEMPLATE.md`
- `skill/references/`: `step1_plan.md` through `step5_notes.md`
- `docs/getting-started.md`, `docs/PROJECT_CONTEXT.md`
