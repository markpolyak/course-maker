# /course-maker doctor

Diagnose a course for state drift, missing files, and configuration gaps.

**Read-only.** Doctor never edits files or fixes anything — it reports findings
and names the command that fixes each one. The user decides what to act on.

## Step 1 — facts layer (mechanical)

Run the drift checker from the course root and show its raw output:

```bash
python ~/.claude/skills/course-maker/scripts/validate_state.py
```

(If the skill is installed elsewhere, use that path. The script reads
`COURSE_STATE.md` and cross-checks every `✅` status against the artifact that
should exist on disk.) It prints findings prefixed `DRIFT` / `STALE` /
`UNTRACKED` / `BULKY` / `SKIP` and an `OK` summary line. Reproduce its output
verbatim, then translate each finding into a fix in Step 3.

`BULKY` is advisory (it does not fail the run): a unit's `history.md` has grown
past the warning threshold. There is no compaction command — the remediation is
to trim old *resolved* iterations by hand, keeping every rejection and piece of
feedback verbatim (that is the anti-repeat memory the file exists for). Report
it, but frame it as optional housekeeping, not drift.

**Blind-run check (do not skip).** A `BLIND` finding, or a summary line that
says `0 items checked`, means the script checked nothing — the `## Lectures` /
`## Seminars` / `## Labs` headings it understands were not found. Do NOT report
this as "no drift". Report it as a hard finding: the script's known sections do
not match this course's `COURSE_STATE.md` (the `sections present:` line lists
what is actually there, e.g. a translated heading). The checker covers
`## Lectures`, `## Seminars` (checked the same way as lectures — presentation
artifacts in `seminars/NN/`; a seminar's practical part is not file-checked),
`## Labs`, `## Quizzes`, and `## Homework`; sessions tracked under other
headings are not verified. Say so explicitly so the clean-looking result is
never mistaken for an all-clear.

Common cause: `COURSE_STATE.md` uses translated headings, or merges two session
types into one section, instead of the English keys. Structural vocabulary is
English-canonical (see
`repository_layout.md`). Remediation is to conform the file — split into
separate `## Lectures` / `## Seminars` / `## Labs` sections with English column
names, keeping titles in the course language — not merely to translate the
heading. A combined or translated heading will not match.

### Plan structure

Then lint the plan itself and show its raw output:

```bash
python ~/.claude/skills/course-maker/scripts/lint_plan.py
```

This is the other half of the facts layer. `validate_state.py` compares
`COURSE_STATE.md` against files on disk; `lint_plan.py` never looks at disk and
checks that `course_plan.md` is internally consistent — Overview counters
against the Sessions table, lecture rows against their `### Lecture N`
subsections, `labs/` / `quizzes/` / `no pipeline` pointers in Notes, and
leftover `<!-- TODO -->` sections. It prints `ERROR` / `WARN` findings and an
`OK` summary line; exit 1 means at least one `ERROR`.

Reproduce its output verbatim. Every finding here is fixed by the same command,
`/course-maker course plan`, so what Step 3 must carry is the offending row or
counter, not the command name.

A plan that disagrees with itself is not cosmetic: `/course-maker stats` reads
the Overview counters as planned totals and `/course-maker syllabus` renders
the plan for students, so a counter that has drifted from the Sessions table
silently misreports both.

## Step 2 — semantic checks (judgement)

These need reading intent and cannot be done by the scripts. Check each:

1. **Profile ↔ adapter consistency.**
   - Read `AGENTS.md` → `## Course context` → `Profile:` (default `local-zip`
     if absent).
   - Confirm `lms_adapter.md` exists in the course root.
   - If `Profile:` names a profile but `lms_adapter.md` is missing, or the
     adapter does not match the named profile → `/course-maker lab course-init`.
2. **Generated config files present.** These are referenced by later steps;
   flag any that are missing:
   - `course_conventions.md`, `slides_preamble.tex` → `/course-maker course init`
   - `lab_templates.md` → `/course-maker lab course-init`

## Step 3 — remediation report

Print one section per category. For every finding, name the exact command that
fixes it. Example shape:

```
Course doctor — <course name>

State drift (from validate_state.py):
  ✗ lectures/02 figures: marked ✅ but no PNG       → /course-maker figures 2
  ⚠ lectures/05 figures: PNGs older than figures.py → /course-maker figures 5
  ℹ lectures/07 slides: file exists, status ❌       → re-run /course-maker slides 7
                                                       or correct COURSE_STATE.md

Plan (from lint_plan.py):
  ✗ Overview Lectures: 12 vs 13 Lecture rows         → /course-maker course plan
  ✗ Sessions line 19: Lecture 6 has no subsection    → /course-maker course plan
  ⚠ unfilled TODO sections: Grading, Instructors     → /course-maker course plan

Config:
  ✓ course_conventions.md, slides_preamble.tex, lab_templates.md present
  ✓ Profile 'github-classroom' matches lms_adapter.md

Summary: 1 drift, 1 stale, 1 untracked, 1 plan gap. No config issues.
```

Map severities: `DRIFT`, `ERROR`, and missing files → ✗; `STALE` and `WARN` →
⚠; `UNTRACKED` and informational notes → ℹ; passing checks → ✓.

Do not modify any file. End by reminding the user that doctor only reports —
they run the suggested commands themselves.
