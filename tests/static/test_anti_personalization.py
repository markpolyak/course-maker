"""Level 0 — anti-personalization guard.

The skill must be universal: one instructor's conventions must not be baked into
the universal machinery (SKILL.md + references/*.md). Personal grading config —
the per-student variant-assignment formula and any external-CI grade label —
lives in opt-in extensions (skill/extensions/{variants,reporters}/) and in the
user's own out-of-repo defaults, never inline in the universal files.

Design note — why this file hardcodes *no* personal literal:
A leak detector has to describe what it looks for, but it must not embed one
instructor's actual values (their variant formula, their CI label) — that would
just relocate the personalization from references/ into tests/. So:

* the structural check flags the *shape* of a per-student variant-assignment
  formula in the universal files, using a generic pattern, not the verbatim
  formula. This is now a hard guard (the formula has moved to the variants
  extension); the universal files must stay formula-free.
* the profile-driven check reads whatever a profile *declares* as its own
  grading values and asserts none of them appear in the universal files. No
  literal is written here; it is read from the profile that owns it.
"""

import re

import pytest

from _paths import PROFILES_DIR, REFERENCES_DIR, SKILL_MD

# Shape of a per-student variant-assignment formula (not any instructor's exact
# string): an assignment derived from a student id. Generic on purpose.
VARIANT_FORMULA_SHAPE = re.compile(r"=\s*\(?\s*Student_ID\b", re.IGNORECASE)

# Profile keys whose values are personal grading config that must stay out of the
# universal files. Populated by wave 4; read from the profile, never hardcoded.
PERSONAL_PROFILE_KEYS = ("grade_label", "grade_output_label", "variant_formula")


def universal_files():
    return [SKILL_MD, *sorted(REFERENCES_DIR.glob("*.md"))]


def declared_personal_values():
    """Values a profile declares as its own grading config (yaml leaf strings
    under PERSONAL_PROFILE_KEYS). Empty until wave 4 introduces the field."""
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed")
    values = []
    for path in sorted(PROFILES_DIR.rglob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if isinstance(data, dict):
            for key in PERSONAL_PROFILE_KEYS:
                val = data.get(key)
                if isinstance(val, str) and val.strip():
                    values.append((path.name, key, val.strip()))
    return values


def structural_leaks():
    found = []
    for path in universal_files():
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if VARIANT_FORMULA_SHAPE.search(line):
                found.append(f"{path.name}:{n}")
    return found


def test_no_variant_formula_in_universal_files():
    leaks = structural_leaks()
    assert not leaks, (
        "a per-student variant-assignment formula is inlined in universal files "
        "(should live in skill/extensions/variants/): " + ", ".join(leaks)
    )


def test_profile_declared_values_absent_from_universal_files():
    """Permanent guard: nothing a profile declares as its own grading config may
    appear in the universal files. A no-op until a profile declares such a field;
    written generically so it never embeds an instructor's literal."""
    declared = declared_personal_values()
    bad = []
    for path in universal_files():
        text = path.read_text(encoding="utf-8")
        for profile_name, key, value in declared:
            if value in text:
                bad.append(f"{path.name} contains {profile_name}:{key}")
    assert not bad, "personal profile values leaked into universal files:\n" + "\n".join(bad)
