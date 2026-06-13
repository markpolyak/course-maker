# Project Context — Design Decisions and Roadmap

This file captures the key decisions, rationale, and plans from the initial
design conversation (Claude.ai chat, May 2026). Read this when continuing
development in Claude Code or any other environment to restore context
without re-reading the full chat.

---

## Origin and motivation

The pipeline was built for a specific use case: a university professor preparing
lecture materials for multiple simultaneous courses. The existing workflow was:

1. Iterative course plan creation with an LLM (Markdown file)
2. Detailed per-lecture slide plan (with LLM, ~1–15 rounds of iteration)
3. Visualization list + Python figure scripts (iterative debugging)
4. LaTeX/Beamer presentation (most painful step, ~8 iteration rounds due to layout issues)
5. Speaker notes (live text, not a summary)

The goal was to reduce iteration rounds by: using richer context, more precise prompts,
and persistent state that survives across sessions.

The reference inspiration was GSD (get-shit-done), but domain-specific: academic
lecture preparation rather than software development.

---

## Key architectural decisions

### One repository per course (not one repo for all courses)

**Rationale:** Multiple courses run simultaneously at different paces. Separate repos
avoid branch conflicts, allow per-course `CLAUDE.md` context, and make it easy to
give collaborators access per-course. Downside: the skill must be copied or symlinked
to each repo. Mitigation: skill lives in `~/.claude/skills/` (global), course repos
just need `CLAUDE.md` pointing to it.

### State stored in Markdown files (not a database)

**Rationale:** Works with git naturally. No setup required. Human-readable.
`COURSE_STATE.md` is a status table; `history.md` per lecture is a decision log.
Both are committed alongside the materials they describe.

### `history.md` as anti-repetition memory

**Core insight:** The main driver of iteration rounds is Claude re-proposing ideas
the user already rejected (because each session starts fresh). `history.md` is
read at the start of every step and logs: what was tried, what feedback was given,
what decision was made. This makes rejections persistent across sessions.

### Chunked generation for slides and speaker notes

**Problem:** A 20-slide Beamer file is ~600–900 lines. Generating it in one shot
causes Claude Code to hang for 10–20+ minutes with no output.
**Solution:** Slides are generated as: preamble chunk → blocks of 5 slides → closing.
Each chunk is shown to the user, approved, then appended to the file.
Resume is supported: `/course-maker slides N next` reads the existing file,
finds the last completed slide, and continues.
Same pattern for speaker notes.

### Claude Code skill format (`.claude/skills/`)

The skill uses Anthropic's native skill format: `SKILL.md` with YAML frontmatter
(name + description for triggering) + a `references/` subdirectory for
step-specific instructions loaded on demand. This keeps `SKILL.md` under ~300 lines
while full detail lives in reference files.

**Current trigger:** `/course-maker` (the skill name). In Claude Code, skills
support both slash-command invocation and autonomous triggering based on description.

---

## Known issues and their status

| Issue | Status | Notes |
|---|---|---|
| `slides` and `notes` commands hang on 20-slide lectures | Fixed | Chunked generation (5 slides per chunk) |
| Skill triggered by slash invocation only via `/course-maker` | By design | Claude Code skills work this way; `.claude/commands/` is the legacy format |
| Manual edits to files not auto-detected mid-pipeline | Partial | `/course-maker course update` does `git diff`; step-by-step detection is in IMPROVEMENT_PLAN.md wave 6 |
| Critical rules pass through skipped reference files | Fixed (wave 1) | `## Inviolable rules` block in `SKILL.md` is loaded unconditionally |
| Skill not bootstrappable from a clean clone (placeholder templates) | Fixed (wave 2) | `conftest_base.py`, `tests.yaml`, `tests_template.py` ship as working universal templates |

---

## Roadmap (priority order)

**The authoritative roadmap is `docs/IMPROVEMENT_PLAN.md`** (added 2026-06).
It defines 7 execution waves with atomic steps; waves 1 and 2 are completed,
waves 3+ are pending. The list below preserves the original design intent for
context; consult IMPROVEMENT_PLAN.md for current status and priorities.

### Original design intent

1. **Test on a real new course** — still relevant; iteration logs from real
   teaching go into per-lecture `history.md` and surface improvements to
   `references/step*.md`.

2. **`step4_slides.md` expansion** — add a catalog of specific Beamer compilation
   errors encountered in practice, with exact fixes. The anti-overfull checklist
   exists; error-specific entries grow as real bugs are encountered.

3. **Example materials** — `examples/` exists as a stub. A real example must be
   produced by running the skill, not hand-assembled (see lesson in commit
   `e41d224`).

4. **Lab assignment pipeline** — done (see CHANGELOG `2026-05-28` and earlier).
   Outputs Jupyter notebook + pytest suite, GHC sync via `gh api`, variant via
   `dataset_id = (Student_ID - 1) % len(DATASETS)`. Peer-review variant is not
   yet implemented.

5. **Syllabus auto-generation** — from `course_plan.md` → formatted PDF syllabus.
   Pending (IMPROVEMENT_PLAN.md wave 5, step 5.1).

6. **pptx output** — alternative to Beamer for non-LaTeX users.
   Pending (IMPROVEMENT_PLAN.md wave 7, step 7.1).

### Long-term

7. **Agent-agnostic core** — multi-harness support (Cursor, Codex, Cline)
   via shared `core/` + per-harness adapter files. See "Architecture for
   multi-agent support" section below. IMPROVEMENT_PLAN.md groups this under
   the broader profiles/adapters work in waves 4 and 7.

8. **Overleaf integration** — compile slides in the cloud instead of locally.
   Independent of agent-agnostic work; targets users without a local LaTeX
   distribution. No design notes yet.

---

## Architecture for multi-agent support (future)

GSD Redux achieves harness-agnostic operation by separating:
- **Core logic** (`get-shit-done/` directory): pure Markdown instructions,
  no harness-specific syntax
- **Adapter files** per harness: `CLAUDE.md` (Claude Code), `.clinerules` (Cline),
  `AGENTS.md` (Codex/OpenAI), `.cursorrules` (Cursor)
- Each adapter file says: "read `get-shit-done/AGENTS.md` and follow it"

**Recommended approach for this project (when the time comes):**

Step 1 — Refactor `SKILL.md` into two parts:
- `core/AGENTS.md` — pure instructions, no `$ARGUMENTS`, no Claude-specific syntax
- `adapters/claude/SKILL.md` — thin wrapper that reads `core/AGENTS.md`, adds Claude-specific frontmatter

Step 2 — Add adapter files:
```
course-maker/
  core/
    AGENTS.md             ← harness-agnostic instructions
    references/           ← step1–step5 reference files (unchanged)
  adapters/
    claude/SKILL.md       ← reads core/AGENTS.md, adds Claude-specific frontmatter
    cursor/.cursorrules   ← reads core/AGENTS.md
    codex/AGENTS.md       ← reads core/AGENTS.md (Codex uses this filename natively)
    cline/.clinerules     ← reads core/AGENTS.md
```

**What to avoid:** putting harness-specific syntax (`$ARGUMENTS`, YAML frontmatter,
`allowed-tools`) in the core instructions. Keep those strictly in adapters.

**Do this now (zero-cost architectural prep):**
- Keep all step logic in `references/step*.md` — these are already harness-agnostic
- Keep `SKILL.md` as a thin dispatcher (it mostly already is)
- Don't use Claude-specific features in the actual pipeline logic

This means the refactor in Step 1 above will be minimal when the time comes.

---

## Files in this repository

```
course-maker/                       ← repo root
  README.md                         ← GitHub repository README
  CHANGELOG.md                      ← release notes
  CLAUDE.md                         ← in-repo conventions for the skill itself
  LICENSE
  .gitignore

  skill/                            ← the skill (symlinked or copied to ~/.claude/skills/course-maker/)
    SKILL.md                        ← main dispatcher (≤300 lines) + Inviolable rules
    COURSE_CLAUDE_TEMPLATE.md       ← template CLAUDE.md for new course repos
    references/
      repository_layout.md          ← directory structure + state file formats
      course_init.md                ← /course-maker course init
      course_plan.md                ← /course-maker course plan
      step1_plan.md ... step5_notes.md   ← lecture pipeline
      lab_context.md                ← required reading for any /course-maker lab * command
      lab_course_init.md            ← /course-maker lab course-init
      lab_init.md                   ← /course-maker lab init
      lab_step1a_plan.md            ← /course-maker lab plan
      lab_step1b_notebook.md        ← /course-maker lab notebook
      lab_step1b_spec.md            ← /course-maker lab spec (plan/notebook auto-detect)
      lab_step1b_datasets.md        ← /course-maker lab datasets
      lab_step2_tests.md            ← /course-maker lab tests
      lab_step3_validate.md         ← /course-maker lab validate
      lab_publish.md                ← /course-maker lab publish
    templates/
      course_conventions_{en,ru}.md ← per-language terminology and rules
      lab_templates_{en,ru}.md      ← per-language notebook header + grade labels
      slides_preamble_{pdflatex,xelatex}.tex
      conftest_base.py              ← working universal pytest conftest
      tests_template.py             ← style reference for generated tests.py
      tests.yaml                    ← working GitHub Actions CI

  docs/
    README.md (project)             ← repository overview (in repo root)
    getting-started.md              ← full walkthrough
    PROJECT_CONTEXT.md              ← this file
    IMPROVEMENT_PLAN.md             ← authoritative roadmap (7 waves)
    archive/                        ← completed planning documents

  examples/                         ← stub; real examples must be produced by running the skill
    README.md

  scripts/
    nonlatin.py                     ← lints skill/ for non-Latin text
```

---

## Conventions used in this project

- Language: skill instructions in English (for reliable LLM instruction-following);
  all generated materials (slides, speaker notes, figures) use whatever language
  is specified in `CLAUDE.md` → Course context — any language is supported
- Slide chunk size: 5 slides per chunk (chosen empirically; may need tuning
  for very dense slides with lots of TikZ)
- Figure naming: `figNN_snake_case.png` where NN matches the V-number in `visuals.md`
- History format: reverse-chronological append (newest entry at bottom — easier to append,
  last 3 entries are shown in `/course-maker status N`)

---

## Open questions (unresolved as of initial design)

1. **Optimal chunk size for slides.** 5 slides is conservative. Some lectures may
   have dense slides (many TikZ diagrams) where 5 is still too much; others could
   handle 8–10. Consider making chunk size configurable in `CLAUDE.md` course context.

2. **Peer review pipeline.** The professor uses structured peer review for ЛР2 and ЛР4
   (theory.md + two reviewers per student). This is a separate workflow from lecture prep
   and should probably be a separate skill extension rather than part of this one.

3. **Git diff for manual edit detection.** Currently Step 1 of each subsequent step
   suggests checking `git diff` for manual edits to the prerequisite file. This is
   not automatic — Claude has to be asked. Could be made automatic with a `pre-step`
   hook pattern, but this may over-engineer for now.
