"""Level 1 — unit tests for scripts/nonlatin.py.

contains_non_english_letters underpins the English-only guard, so its behaviour
is pinned: only letters are inspected, Latin letters (including accented ones)
pass, any other script fails, and non-letters are ignored entirely.
"""

import pytest

from _paths import SCRIPTS_DIR, load_module

nonlatin = load_module(SCRIPTS_DIR / "nonlatin.py", "nonlatin")
f = nonlatin.contains_non_english_letters


@pytest.mark.parametrize(
    "text",
    [
        "hello world",
        "café résumé naïve",  # accented Latin still counts as Latin
        "",
        "123 + 456 = 579",
        "status: done ✅ 🔄 ❌ ⚠️ — arrow →",  # symbols, not letters
        "`dataset_id = (Student_ID - 1) % len(DATASETS)`",  # ASCII code
    ],
)
def test_latin_and_nonletters_pass(text):
    assert f(text) is False


@pytest.mark.parametrize(
    "text",
    [
        "привет",
        "mixed английский text",
        "日本語",
        "Ωmega",
    ],
)
def test_non_latin_letters_flagged(text):
    assert f(text) is True
