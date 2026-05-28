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
| `slides` and `notes` commands hang on 20-slide lectures | Fixed in v2 | Chunked generation |
| No native slash commands (only `/course-maker`) | By design | Claude Code skills work this way; `.claude/commands/` is legacy format |
| Manual edits to files not auto-detected | Partial | `/course update` does `git diff`; mid-pipeline detection not yet automated |

---

## Roadmap (priority order)

### Near-term (next 1–3 lectures of real use)

1. **Test on a real new course** — run the full pipeline on one lecture, log every
   step where >2 iteration rounds were needed, fix the corresponding reference file.

2. **`step4_slides.md` expansion** — add a catalog of specific Beamer compilation
   errors encountered in practice, with exact fixes. Currently has the anti-overfull
   checklist but no error-specific entries.

3. **Example materials** — add `examples/stochastic-processes/` with at least
   lectures 01 and 02 fully populated (plan, visuals, slides.tex, speaker_notes.md).
   This is the most important documentation for new users.

### Medium-term

4. **Lab assignment pipeline** — separate skill or extension of this one.
   The professor has an existing pipeline for lab creation that should be
   captured similarly. Key differences from lectures:
   - Output: Jupyter notebook (`exercises.ipynb`) + test suite (pytest)
   - Grading: GitHub Actions CI, `nbconvert` to `.py`, tolerance-based assertions
   - Variants: `Student_ID` determines dataset + parameters
   - Peer review component for ЛР2 and ЛР4

5. **Syllabus auto-generation** — from `course_plan.md` → formatted PDF syllabus.
   Low complexity, high value for bureaucratic purposes.

6. **pptx output** — alternative to Beamer for non-LaTeX users. Use the `pptx`
   skill already available in `~/.claude/skills/public/pptx/`.

### Long-term (multi-agent / multi-harness)

7. **Agent-agnostic core** — see "Architecture for multi-agent support" section below.

8. **Overleaf integration** — compile slides in the cloud instead of locally.

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
course-maker/               ← the skill itself (goes to ~/.claude/skills/)
  SKILL.md                  ← main skill file (Claude Code format)
  COURSE_CLAUDE_TEMPLATE.md ← template CLAUDE.md for new course repos
  references/
    step1_plan.md
    step2_visuals.md
    step3_figures.md
    step4_slides.md
    step5_notes.md

docs/
  README.md                 ← GitHub repository README
  getting-started.md        ← full walkthrough
  PROJECT_CONTEXT.md        ← this file
  contributing.md           ← (TODO)
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
