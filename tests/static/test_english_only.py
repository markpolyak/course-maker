"""Level 0 — English-only guard.

CLAUDE.md rule: "All text in skill/SKILL.md and skill/references/*.md must be in
English." The skill machinery is what Claude reads as instructions; it stays
English regardless of the course language. skill/extensions/*.md (opt-in
reporter/variant docs) are machinery too and are held to the same rule.
Localized course-content templates (templates/*_ru.md) are deliberately NOT
covered — Cyrillic there is expected.

Intent of the rule is "no non-English natural-language prose" (in practice:
Cyrillic, since the courses are Russian), NOT "no mathematical notation". So the
classifier allows:
  * Latin letters (incl. accented: café, naïve);
  * Greek letters — standard math notation in examples (σ, λ, Ω);
  * the Letterlike Symbols block U+2100–U+214F (e.g. the ℹ info glyph).
Any other script (Cyrillic, CJK, …) is flagged. Status marks (✅ 🔄 ❌ ⚠️ ✓),
arrows and dashes are symbols, not letters, and never trip the check.

If you would rather forbid Greek too (spell it out in LaTeX form instead),
tighten ALLOWED_LETTER_NAME_TAGS below to ("LATIN",).
"""

import unicodedata

import pytest

from _paths import EXTENSIONS_DIR, REFERENCES_DIR, SKILL_MD, SCRIPTS_DIR, load_module

nonlatin = load_module(SCRIPTS_DIR / "nonlatin.py", "nonlatin")

ALLOWED_LETTER_NAME_TAGS = ("LATIN", "GREEK")
LETTERLIKE_BLOCK = range(0x2100, 0x2150)  # U+2100–U+214F


def is_foreign_letter(ch):
    if not unicodedata.category(ch).startswith("L"):
        return False  # not a letter at all
    if ord(ch) in LETTERLIKE_BLOCK:
        return False  # ℹ, ℃, № … typographic, not a language
    name = unicodedata.name(ch, "")
    return not any(tag in name for tag in ALLOWED_LETTER_NAME_TAGS)


def english_only_files():
    # extensions/ is skill machinery too (opt-in reporters/variants docs), so it
    # is held to the same English-only rule as SKILL.md + references/.
    return [
        SKILL_MD,
        *sorted(REFERENCES_DIR.glob("*.md")),
        *sorted(EXTENSIONS_DIR.rglob("*.md")),
    ]


def non_english_lines(path):
    offenders = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if any(is_foreign_letter(ch) for ch in line):
            offenders.append((n, line.strip()))
    return offenders


@pytest.mark.parametrize("path", english_only_files(), ids=lambda p: p.name)
def test_no_non_english_letters(path):
    offenders = non_english_lines(path)
    assert not offenders, "Non-English letters in instruction file:\n" + "\n".join(
        f"  {path.name}:{n}: {text}" for n, text in offenders
    )


def test_guard_catches_cyrillic():
    """Sanity: a green run means something — Cyrillic and CJK are still caught,
    while Greek math and the strict standalone classifier behave as expected."""
    assert is_foreign_letter("п")  # Cyrillic
    assert is_foreign_letter("本")  # CJK
    assert not is_foreign_letter("σ")  # Greek math — allowed
    assert not is_foreign_letter("a")  # Latin
    # The standalone script stays intentionally strict (flags Greek too).
    assert nonlatin.contains_non_english_letters("привет")
