"""Level 0 — cross-tool course-context wiring.

The course context is single-sourced in AGENTS.md (read natively by Codex CLI and
Cursor). Claude Code reads CLAUDE.md, which must pull AGENTS.md in via the
`@AGENTS.md` import. These checks guard the two templates from drifting back into
a duplicated or Claude-only state:

* the CLAUDE template is a thin wrapper that imports AGENTS.md;
* the CLAUDE template does NOT re-inline the course context;
* the AGENTS template actually carries that context.
"""

from _paths import SKILL_DIR

CLAUDE_TEMPLATE = SKILL_DIR / "COURSE_CLAUDE_TEMPLATE.md"
AGENTS_TEMPLATE = SKILL_DIR / "COURSE_AGENTS_TEMPLATE.md"


def test_claude_template_imports_agents():
    text = CLAUDE_TEMPLATE.read_text(encoding="utf-8")
    assert "@AGENTS.md" in text, "COURSE_CLAUDE_TEMPLATE.md must import AGENTS.md via @AGENTS.md"


def test_claude_template_does_not_reinline_context():
    """The wrapper must not carry the course context — that lives in AGENTS.md."""
    text = CLAUDE_TEMPLATE.read_text(encoding="utf-8")
    for section in ("## Course context", "## Lab context", "### Audience"):
        assert section not in text, (
            f"COURSE_CLAUDE_TEMPLATE.md should not re-inline '{section}'; "
            "it belongs in AGENTS.md"
        )


def test_agents_template_carries_context():
    text = AGENTS_TEMPLATE.read_text(encoding="utf-8")
    for section in ("## Course context", "## Lab context", "Profile:"):
        assert section in text, f"COURSE_AGENTS_TEMPLATE.md is missing '{section}'"
