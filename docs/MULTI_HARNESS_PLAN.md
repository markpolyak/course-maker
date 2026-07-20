# Multi-harness support plan (Claude Code · Codex CLI · Cursor)

**Date:** 2026-07-21
**Status:** install path shipped; deeper parity planned.

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
- **Install locations differ; the skill does not:**
  - Claude Code — global `~/.claude/skills/<name>/`
  - Codex CLI — global `~/.agents/skills/<name>/` (legacy `~/.codex/skills/`);
    repo-scoped `.agents/skills/`
  - Cursor — **no global skills dir**; project-scoped `.cursor/skills/<name>/`
    only. Global sharing is a per-project symlink / dotfiles workaround.
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

- **Global install** for Claude Code and Codex CLI (symlink into `~/.claude/skills`
  and `~/.agents/skills`). Documented in README + getting-started.
- **Cursor is project-scoped** by design — symlink into each course repo's
  `.cursor/skills/` and gitignore it. No global option exists; documented honestly.
- Consumer ChatGPT / Custom GPT: **not supported** (no shell/filesystem).

## Phased plan

### Phase 0 — declaudize wording (small; content-neutral)
Generalize the few Claude Code-specific phrasings in `SKILL.md` / `references/`
so they read for any agent, without changing behavior:
- Chunking rationale: "one-shot generation causes Claude Code to hang" →
  "…exceeds a single generation / context budget" (keep the chunking rule).
- `lab validate` isolation: "run `/clear`" → "start a fresh session/context
  (Claude Code: `/clear`; Codex/Cursor: a new chat/session)".
- Audit for other Claude-only assumptions (tool names, slash-command phrasing).

### Phase 1 — install/distribution ✅ shipped
Single skill, symlinked per tool. README + getting-started updated with the
correct global paths (Claude Code, Codex) and the project-scoped Cursor recipe.

### Phase 2 — cross-tool per-course context layer
- `course init` generates **`AGENTS.md`** with the course context (current
  `## Course context`, `## Lab context`, recurring rules, etc.) as source of
  truth, plus a thin **`CLAUDE.md`** = `@AGENTS.md` + any Claude-only overrides.
- Add `skill/COURSE_AGENTS_TEMPLATE.md`; make the CLAUDE template the import wrapper.
- Point references that read "course context" at `AGENTS.md` (Claude Code still
  sees it via the `CLAUDE.md` import; Codex/Cursor read `AGENTS.md` natively).
- **Migration** (idempotent): an existing course with inline `CLAUDE.md` and no
  `AGENTS.md` → `course init` offers to split context into `AGENTS.md` and
  rewrite `CLAUDE.md` as the import wrapper.

### Phase 3 — verify + keep in sync
- Manual smoke on Codex CLI and Cursor: run `course init` → a lecture step →
  a lab step; confirm the skill loads and references are read.
- A static test (like `tests/static`) asserting the generated `CLAUDE.md`
  correctly imports `AGENTS.md` and the two do not drift.

## Risks / limitations

- **Weaker models on other harnesses may skip referenced files** more often —
  the long-standing failure mode. Inline Inviolable rules / CRITICAL blocks
  mitigate it, but full parity on a weaker model is not guaranteed. State this
  explicitly in docs.
- Cursor's project-scoping means the skill is not "install once" there; the
  per-repo symlink is the accepted workaround.
- Standards are young (2025–2026) and paths may shift (e.g. Codex legacy
  `~/.codex/skills`); re-verify install paths when tooling updates.

## Sources

- Codex — Build skills: https://learn.chatgpt.com/docs/build-skills
- Codex issue #10493 (user-scope `~/.agents/skills`): https://github.com/openai/codex/issues/10493
- Cursor skills storage (project-scoped only): https://www.agensi.io/learn/where-are-cursor-skills-stored
- Cursor rules vs SKILL.md: https://www.agensi.io/learn/cursor-rules-vs-skill-md-complete-guide
- Claude Code `@AGENTS.md` import patterns: https://gist.github.com/yurukusa/d36197848911f025add142abefcde685
- Claude Code issue #6235 (AGENTS.md support): https://github.com/anthropics/claude-code/issues/6235
- AGENTS.md standard adoption: https://codersera.com/blog/agents-md-vs-claude-md-vs-cursor-rules-comparison-2026/
