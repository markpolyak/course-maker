"""Contract tests for the read-only course_plan.md linter."""

import subprocess
import sys
import textwrap

import pytest

from _paths import SKILL_DIR


LINT = SKILL_DIR / "scripts" / "lint_plan.py"


def run(root):
    proc = subprocess.run(
        [sys.executable, str(LINT), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout


def write_plan(root, body):
    (root / "course_plan.md").write_text(textwrap.dedent(body), encoding="utf-8")


def plan(overview="1, 1, 1, 1", sessions=None, lectures=None, tail=""):
    lectures_count, seminars, labs, quizzes = overview.split(", ")
    if sessions is None:
        sessions = """\
| 1 | 1 | Lecture | Intro | |
| 2 | 1 | Seminar | Practice | no pipeline |
| 3 | 2 | Lab | First lab | labs/lab1/ |
| 4 | 3 | Quiz | Checkpoint | quizzes/01/ |
"""
    lectures = lectures if lectures is not None else """\
### Lecture 1 — Intro

**Estimated time:** 90 min
"""
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
    assert out.splitlines()[-1] == "OK        0 errors, 0 warnings"


def test_missing_plan_fails(tmp_path):
    code, out = run(tmp_path)
    assert code == 1
    assert "ERROR" in out and "course_plan.md not found" in out
    assert out.splitlines()[-1].startswith("OK")


def test_overview_counter_mismatch_fails(tmp_path):
    write_plan(tmp_path, plan(overview="2, 1, 1, 1"))
    code, out = run(tmp_path)
    assert code == 1
    assert "Lectures: 2 does not match 1" in out


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        ("| 1 | 1 | Lecture | Intro | extra | unexpected |\n", "expected 5 columns"),
        ("| one | 1 | Lecture | Intro | |\n", "# must be a number"),
        ("| 1 | 1 | Workshop | Intro | |\n", "Type must be one of"),
    ],
)
def test_malformed_session_row_fails(tmp_path, row, expected):
    write_plan(tmp_path, plan(sessions=row, lectures=""))
    code, out = run(tmp_path)
    assert code == 1
    assert expected in out


@pytest.mark.parametrize(
    ("sessions", "lectures", "expected"),
    [
        ("| 1 | 1 | Lecture | Intro | |\n", "", "Lecture 1 session has no matching subsection"),
        ("", "### Lecture 1 — Intro\n\n**Estimated time:** 90 min\n", "Lecture 1 subsection has no matching session row"),
    ],
)
def test_lecture_session_and_subsection_must_match(tmp_path, sessions, lectures, expected):
    write_plan(tmp_path, plan(overview="1, 0, 0, 0", sessions=sessions, lectures=lectures))
    code, out = run(tmp_path)
    assert code == 1
    assert expected in out


def test_todo_sections_warn_without_failing(tmp_path):
    write_plan(tmp_path, plan(tail="\n## Grading\n\n<!-- TODO: add weights -->\n"))
    code, out = run(tmp_path)
    assert code == 0, out
    assert "WARN" in out and "TODO sections: Grading" in out


def test_missing_estimated_time_warns_without_failing(tmp_path):
    write_plan(tmp_path, plan(lectures="### Lecture 1 — Intro\n\n**Topics:** basics\n"))
    code, out = run(tmp_path)
    assert code == 0, out
    assert "WARN" in out and "Lecture 1 has no **Estimated time:**" in out


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
