# Multi-harness support plan (Claude Code · Codex CLI · Cursor)

**Date:** 2026-07-21
**Status:** Phases 0–3 done — skill verified loading on Claude Code, Codex CLI, and Cursor.

Goal: run course-maker on **Claude Code**, **OpenAI Codex CLI**, and **Cursor**
from a single source of truth, without forking the skill or duplicating content.
Consumer ChatGPT / Custom GPTs are **out of scope** — they have no local shell or
filesystem, so the pipeline (running `figures.py`, `nbconvert`, `pytest`, git,
pandoc) cannot execute there.

## Key facts (verified 2026-07, see Sources)

- **`SKILL.md` is a cross-tool open standard** ("Agent Skills", agentskills.io),
  read by Claude Code, Codex CLI, and Cursor alike: a directory with `SKILL.md`
  (`name` + `description` frontmatter) plus `references/`, `scripts/`, `assets/`.
  Progressive disclosure (preload name+description, load the body on demand) is
  the same across all three. **Our skill already conforms — it ports as-is.**
- **Install locations differ; the skill does not.** All three support a global
  (user-level) skills directory:
  - Claude Code — reads only `~/.claude/skills/<name>/`.
  - Codex CLI — `~/.agents/skills/<name>/` (legacy `~/.codex/skills/`); repo-scoped
    `.agents/skills/`.
  - Cursor — per the official docs (https://cursor.com/docs/skills) loads from
    **eight** locations: `~/.agents/skills`, `~/.cursor/skills`, `~/.claude/skills`,
    `~/.codex/skills` (global) and the four project-level equivalents. It reads
    the Claude Code and Codex dirs "for compatibility".
  - Consequence: **Cursor never needs its own symlink** — it piggybacks on the
    Claude Code / Codex dirs. Installing for both Claude Code and Codex means
    Cursor finds the skill in two dirs; the docs define no dedup, but in practice
    Cursor shows it **once** (observed with symlinks to the same directory).
- **`AGENTS.md` is a different layer** from the skill: always-on project guidance
  (plain markdown, no frontmatter), read natively by Codex, Cursor, Copilot,
  Gemini, etc. **Claude Code does not read `AGENTS.md`** — it reads `CLAUDE.md`,
  which supports `@path` imports, so `@AGENTS.md` expands `AGENTS.md` inline.
- This maps cleanly onto course-maker's two existing layers (below).

## Architecture: two layers, single source each

| Layer | Today | Cross-tool form |
|---|---|---|
| Skill machinery | `SKILL.md` + `references/` | Unchanged. One Agent Skill; installed per tool's location (symlink). No content fork. |
| Per-course context | per-course `CLAUDE.md` | `AGENTS.md` = source of truth; `CLAUDE.md` = `@AGENTS.md` + Claude-only overrides. |

The only "duplication" is the skill's **install location** (a symlink per tool),
not its content. Course context is single-sourced in `AGENTS.md`.

## Decisions

- **Global install for all three.** Symlink per non-Cursor tool you use:
  `~/.claude/skills` (Claude Code), `~/.agents/skills` (Codex CLI). Cursor needs
  no dedicated symlink — it reads both. Documented in README + getting-started,
  with the both-Claude-and-Codex duplicate caveat.
- Consumer ChatGPT / Custom GPT: **not supported** (no shell/filesystem).
- The **Claude chat app (claude.ai / Claude Desktop)**: **not supported for the
  pipeline.** It does support custom Skills (uploaded as a zip in Settings →
  Features), but they run in a sandboxed cloud VM — not on your machine — so there
  is no local course repo, git, or LaTeX/pandoc/pytest/jupyter toolchain, and the
  VM is ephemeral (state files can't persist in your repo). Only pure text steps
  (e.g. drafting a plan) would work; the real pipeline can't. Note: **Claude *Code*
  for Desktop** is just Claude Code and is fully supported. (Official runtime/
  surface docs: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

## Phased plan

### Phase 0 — declaudize wording ✅ done
Generalize the few Claude Code-specific phrasings in `SKILL.md` / `references/`
so they read for any agent, without changing behavior:
- Chunking rationale: "one-shot generation causes Claude Code to hang" →
  "…exceeds a single generation / context budget" (keep the chunking rule).
- `lab validate` isolation: "run `/clear`" → "start a fresh session/context
  (Claude Code: `/clear`; Codex/Cursor: a new chat/session)".
- Audit for other Claude-only assumptions (tool names, slash-command phrasing).

### Phase 1 — install/distribution ✅ shipped
Single skill, symlinked globally into the dir each non-Cursor tool reads
(`~/.claude/skills`, `~/.agents/skills`); Cursor piggybacks on those. Documented
in README + getting-started.

### Phase 2 — cross-tool per-course context layer ✅ done
- `course init` generates **`AGENTS.md`** with the course context (`## Course
  context`, `## Lab context`, recurring rules, notes) as source of truth, plus a
  thin **`CLAUDE.md`** = `@AGENTS.md` + any Claude-only overrides.
  (`skill/COURSE_AGENTS_TEMPLATE.md` + the CLAUDE template as import wrapper.)
- Every "CLAUDE.md → ## Course/Lab context" reference across `SKILL.md`,
  `references/`, `templates/`, `profiles/`, and `extensions/` was renamed to
  `AGENTS.md` (the real fix — no `#define`-style redirect rule). `CLAUDE.md` is
  named only where it is literally the wrapper file (its template, the layout
  entry, and `course init` create/migrate steps). SKILL.md § Inviolable rules
  states the fact (context file = `AGENTS.md`; `CLAUDE.md` = the `@AGENTS.md`
  wrapper) without any "treat X as Y" redirection.
- **Migration** (idempotent): an existing course with inline `CLAUDE.md` and no
  `AGENTS.md` → `course init` offers to split context into `AGENTS.md` and
  rewrite `CLAUDE.md` as the import wrapper (copy-verify-then-trim).

### Phase 3 — verify + keep in sync
- ✅ Static test (`tests/static/test_agents_wrapper.py`): the CLAUDE template
  imports `AGENTS.md`, does not re-inline context, and the AGENTS template
  carries the context — guards the two files from drift.
- ✅ Manual smoke (instructor-run, 2026-07): skill installed via symlinks in
  `~/.claude/skills` + `~/.agents/skills`; discovered and available in Claude
  Code, Codex CLI, and Cursor. Cursor de-duplicates the double install (shows the
  skill once). Cross-tool load path confirmed.

## Risks / limitations

- **Weaker models on other harnesses may skip referenced files** more often —
  the long-standing failure mode. Inline Inviolable rules / CRITICAL blocks
  mitigate it, but full parity on a weaker model is not guaranteed. State this
  explicitly in docs.
- Standards are young (2025–2026) and paths may shift (e.g. Codex legacy
  `~/.codex/skills`); re-verify install paths against official docs when tooling
  updates. (An earlier draft of this plan wrongly claimed Cursor had no global
  skills dir, based on a third-party blog; the official docs show `~/.agents/skills`
  and `~/.cursor/skills` are global — prefer primary sources.)

## Sources

- Codex — Build skills: https://learn.chatgpt.com/docs/build-skills
- Codex issue #10493 (user-scope `~/.agents/skills`): https://github.com/openai/codex/issues/10493
- Cursor — Skills (official; global `~/.agents/skills` + `~/.cursor/skills`): https://cursor.com/docs/skills
- Claude Code `@AGENTS.md` import patterns: https://gist.github.com/yurukusa/d36197848911f025add142abefcde685
- Claude Code issue #6235 (AGENTS.md support): https://github.com/anthropics/claude-code/issues/6235
- AGENTS.md standard adoption: https://codersera.com/blog/agents-md-vs-claude-md-vs-cursor-rules-comparison-2026/
