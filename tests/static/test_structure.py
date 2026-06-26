"""Level 0 — structural integrity of the skill.

Every command dispatcher in SKILL.md names a `references/*.md` file with the full
workflow ("Read: `references/foo.md`"). Two failure modes this guards against:

* a dispatcher points at a reference file that does not exist (dangling link);
* a reference file exists but no dispatcher ever names it (orphan / dead doc).

Both are silent rot that the manual eyeball pass tends to miss.
"""

import re

from _paths import REFERENCES_DIR, SKILL_MD

REF_PATTERN = re.compile(r"references/([A-Za-z0-9_]+\.md)")


def referenced_files():
    text = SKILL_MD.read_text(encoding="utf-8")
    return set(REF_PATTERN.findall(text))


def existing_files():
    return {p.name for p in REFERENCES_DIR.glob("*.md")}


def test_all_referenced_files_exist():
    missing = sorted(referenced_files() - existing_files())
    assert not missing, (
        "SKILL.md points at reference files that do not exist: " + ", ".join(missing)
    )


def test_no_orphan_reference_files():
    orphans = sorted(existing_files() - referenced_files())
    assert not orphans, (
        "reference files exist but are never named in SKILL.md: " + ", ".join(orphans)
    )


def test_skill_md_has_frontmatter():
    """The skill is unusable without a name/description frontmatter block."""
    text = SKILL_MD.read_text(encoding="utf-8")
    assert text.startswith("---\n"), "SKILL.md must open with a YAML frontmatter block"
    assert "name: course-maker" in text
    assert "description:" in text
