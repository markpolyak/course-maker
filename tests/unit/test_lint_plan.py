"""Contract tests for the read-only course_plan.md linter.

Each case is built so that exactly the rule under test fires: the assertions
check the summary line as well as the message, so a test cannot pass on a
finding it did not mean to provoke.
"""

import subprocess
import sys
import textwrap

import pytest

from _paths import SKILL_DIR


LINT = SKILL_DIR / "scripts" / "lint_plan.py"

LECTURE_1 = """\
### Lecture 1 — Intro

**Estimated time:** 90 min
"""


def run(root):
    proc = subprocess.run(
        [sys.executable, str(LINT), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout


def write_plan(root, body):
    (root / "course_plan.md").write_text(textwrap.dedent(body), encoding="utf-8")


def summary(out):
    """Return the trailing OK line, normalized to '<errors> errors, <warnings> warnings'."""
    return out.splitlines()[-1].removeprefix("OK").strip()


def plan(overview="1, 1, 1, 1", sessions=None, lectures=None, tail=""):
    lectures_count, seminars, labs, quizzes = overview.split(", ")
    if sessions is None:
        sessions = """\
| 1 | 1 | Lecture | Intro | |
| 2 | 1 | Seminar | Practice | no pipeline |
| 3 | 2 | Lab | First lab | labs/lab1/ |
| 4 | 3 | Quiz | Checkpoint | quizzes/01/ |
"""
    lectures = lectures if lectures is not None else LECTURE_1
    return f"""\
# Course Plan — Test

## Overview

**Weeks:** 3  **Lectures:** {lectures_count}  **Seminars:** {seminars}  **Labs:** {labs}
**Quizzes:** {quizzes}  **Standard duration:** 90 min

## Sessions

| # | Week | Type | Title / Topic | Notes |
|---|------|------|---------------|-------|
{sessions}
## Lectures

{lectures}
{tail}"""


def test_clean_plan_passes(tmp_path):
    write_plan(tmp_path, plan())
    code, out = run(tmp_path)
    assert code == 0, out
    assert summary(out) == "0 errors, 0 warnings"


def test_missing_plan_fails(tmp_path):
    code, out = run(tmp_path)
    assert code == 1
    assert "ERROR" in out and "course_plan.md not found" in out
    assert out.splitlines()[-1].startswith("OK")


def test_lecture_numbers_follow_lecture_order_not_session_numbers(tmp_path):
    """`### Lecture 2` is the second lecture, even when it is session #3.

    This is the shape of the canonical example in references/course_plan.md.
    """
    write_plan(tmp_path, plan(
        overview="2, 1, 0, 0",
        sessions="""\
| 1 | 1 | Lecture | Introduction | |
| 2 | 1 | Seminar | Practice | no pipeline |
| 3 | 2 | Lecture | Forward algorithm | |
""",
        lectures="""\
### Lecture 1 — Introduction

**Estimated time:** 90 min

### Lecture 2 — Forward algorithm

**Estimated time:** 90 min
""",
    ))
    code, out = run(tmp_path)
    assert code == 0, out
    assert summary(out) == "0 errors, 0 warnings"


def test_overview_counter_mismatch_fails(tmp_path):
    write_plan(tmp_path, plan(overview="2, 1, 1, 1"))
    code, out = run(tmp_path)
    assert code == 1
    assert "Lectures: 2 does not match 1" in out
    assert summary(out) == "1 errors, 0 warnings"


@pytest.mark.parametrize(
    ("row", "overview", "lectures", "expected"),
    [
        ("| 1 | 1 | Lecture | Intro | | extra |\n", "1, 0, 0, 0", LECTURE_1, "expected 5 columns, found 6"),
        ("| one | 1 | Lecture | Intro | |\n", "1, 0, 0, 0", LECTURE_1, "# must be a number"),
        ("| 1 | 1 | Workshop | Intro | |\n", "0, 0, 0, 0", "", "Type must be one of"),
    ],
)
def test_malformed_session_row_fails(tmp_path, row, overview, lectures, expected):
    write_plan(tmp_path, plan(overview=overview, sessions=row, lectures=lectures))
    code, out = run(tmp_path)
    assert code == 1
    assert expected in out
    assert summary(out) == "1 errors, 0 warnings"


def test_duplicate_session_number_fails(tmp_path):
    write_plan(tmp_path, plan(
        overview="0, 2, 0, 0",
        sessions="""\
| 1 | 1 | Seminar | Practice | no pipeline |
| 1 | 2 | Seminar | More practice | no pipeline |
""",
        lectures="",
    ))
    code, out = run(tmp_path)
    assert code == 1
    assert "# 1 is already used" in out
    assert summary(out) == "1 errors, 0 warnings"


@pytest.mark.parametrize(
    ("sessions", "overview", "lectures", "expected"),
    [
        ("| 1 | 1 | Lecture | Intro | |\n", "1, 0, 0, 0", "", "Lecture 1 session has no matching subsection"),
        ("", "0, 0, 0, 0", LECTURE_1, "Lecture 1 subsection has no matching session row"),
    ],
)
def test_lecture_session_and_subsection_must_match(tmp_path, sessions, overview, lectures, expected):
    write_plan(tmp_path, plan(overview=overview, sessions=sessions, lectures=lectures))
    code, out = run(tmp_path)
    assert code == 1
    assert expected in out
    assert summary(out) == "1 errors, 0 warnings"


def test_duplicate_lecture_subsection_fails(tmp_path):
    write_plan(tmp_path, plan(
        overview="1, 0, 0, 0",
        sessions="| 1 | 1 | Lecture | Intro | |\n",
        lectures=LECTURE_1 + "\n" + LECTURE_1,
    ))
    code, out = run(tmp_path)
    assert code == 1
    assert "Lecture 1 subsection is declared twice" in out
    assert summary(out) == "1 errors, 0 warnings"


@pytest.mark.parametrize("separator", ["-", "–", ":"])
def test_non_canonical_heading_separator_warns_but_still_matches(tmp_path, separator):
    """A stray separator must not be reported as a missing subsection."""
    write_plan(tmp_path, plan(
        overview="1, 0, 0, 0",
        sessions="| 1 | 1 | Lecture | Intro | |\n",
        lectures=f"### Lecture 1 {separator} Intro\n\n**Estimated time:** 90 min\n",
    ))
    code, out = run(tmp_path)
    assert code == 0, out
    assert "expected an em dash" in out
    assert "no matching subsection" not in out
    assert summary(out) == "0 errors, 1 warnings"


def test_todo_sections_warn_without_failing(tmp_path):
    write_plan(tmp_path, plan(tail="\n## Grading\n\n<!-- TODO: add weights -->\n"))
    code, out = run(tmp_path)
    assert code == 0, out
    assert "WARN" in out and "TODO sections: Grading" in out
    assert summary(out) == "0 errors, 1 warnings"


def test_missing_estimated_time_warns_without_failing(tmp_path):
    write_plan(tmp_path, plan(lectures="### Lecture 1 — Intro\n\n**Topics:** basics\n"))
    code, out = run(tmp_path)
    assert code == 0, out
    assert "WARN" in out and "Lecture 1 has no **Estimated time:**" in out
    assert summary(out) == "0 errors, 1 warnings"


@pytest.mark.parametrize("kind", ["Lab", "Quiz"])
def test_lab_and_quiz_notes_need_a_valid_pointer(tmp_path, kind):
    overview = "0, 0, 1, 0" if kind == "Lab" else "0, 0, 0, 1"
    write_plan(tmp_path, plan(
        overview=overview,
        sessions=f"| 1 | 1 | {kind} | Assessment | details later |\n",
        lectures="",
    ))
    code, out = run(tmp_path)
    assert code == 0, out
    assert "WARN" in out and f"{kind} Notes has no" in out
    assert summary(out) == "0 errors, 1 warnings"
