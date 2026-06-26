"""Level 0 — anti-personalization tracker (expected to fail until wave 4).

The skill must be universal: one instructor's conventions must not be baked into
the universal machinery (SKILL.md + references/*.md). Per the IMPROVEMENT_PLAN
wave 4, personal grading config (the per-student variant-assignment formula and
the external-CI grade label) moves out of the universal files into a profile.

Design note — why this file hardcodes *no* personal literal:
A leak detector has to describe what it looks for, but it must not embed one
instructor's actual values (their variant formula, their CI label) — that would
just relocate the personalization from references/ into tests/. So:

* the profile-driven check reads whatever a profile *declares* as its own
  grading values and asserts none of them appear in the universal files. No
  literal is written here; it is read from the profile that owns it. This is the
  permanent guard and becomes meaningful once wave 4 creates that profile field.
* the interim structural check flags the *shape* of the known current leak — an
  inlined per-student variant-assignment formula in the universal files — using
  a generic pattern, not the verbatim formula.

Marked xfail (not skip): the suite stays green while wave 4 is pending, but the
moment the leak is gone the test XPASSes — a loud signal to drop the xfail and
turn this into a hard guard.
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


def interim_structural_leaks():
    found = []
    for path in universal_files():
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if VARIANT_FORMULA_SHAPE.search(line):
                found.append(f"{path.name}:{n}")
    return found


@pytest.mark.xfail(
    reason="IMPROVEMENT_PLAN wave 4: per-student variant formula must move out of "
    "SKILL.md + references/ into a profile",
    strict=False,
)
def test_no_variant_formula_in_universal_files():
    leaks = interim_structural_leaks()
    assert not leaks, (
        "a per-student variant-assignment formula is inlined in universal files "
        "(should live in a profile): " + ", ".join(leaks)
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
