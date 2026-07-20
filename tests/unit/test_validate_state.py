"""Level 1 — contract tests for skill/scripts/validate_state.py.

validate_state.py is the deterministic facts engine behind `/course-maker doctor`
and is wired into external CI as a guard, so its exit codes and finding prefixes
are a contract. We drive it the way CI does: as a subprocess against a throwaway
course tree, asserting on exit code and the severity tokens it prints.

Documented contract (from the script's own docstring):
    DRIFT/STALE  -> exit 1   (status claims done but artifact missing/stale)
    UNTRACKED/SKIP -> exit 0  (informational, never fail the run)
    missing COURSE_STATE.md or a blind run -> exit 1 (no false all-clear)
"""

import os
import subprocess
import sys
import textwrap
import time

import pytest

from _paths import SKILL_DIR

VALIDATE = SKILL_DIR / "scripts" / "validate_state.py"


def run(root):
    proc = subprocess.run(
        [sys.executable, str(VALIDATE), "--root", str(root)],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout


def write_state(root, body):
    (root / "COURSE_STATE.md").write_text(textwrap.dedent(body), encoding="utf-8")


def lectures_table(rows):
    return (
        "# Course State\n\n## Lectures\n\n"
        "| # | Title | plan | visuals | figures | slides | notes | Updated |\n"
        "|---|-------|------|---------|---------|--------|-------|---------|\n"
        + rows
    )


def test_missing_state_file_fails(tmp_path):
    code, out = run(tmp_path)
    assert code == 1
    assert "COURSE_STATE.md not found" in out


def test_blind_run_fails(tmp_path):
    """A state file with no recognized sections must not give a false all-clear."""
    write_state(tmp_path, "# Course State\n\n## Notes\n\nnothing machine-readable here\n")
    code, out = run(tmp_path)
    assert code == 1
    assert "BLIND" in out


def test_clean_course_passes(tmp_path):
    write_state(tmp_path, lectures_table("| 01 | Intro | ✅ | ❌ | ❌ | ❌ | ❌ | 2026-01-01 |\n"))
    (tmp_path / "lectures" / "01").mkdir(parents=True)
    (tmp_path / "lectures" / "01" / "plan.md").write_text("plan", encoding="utf-8")
    code, out = run(tmp_path)
    assert code == 0, out
    assert "0 drift/stale" in out


def test_drift_on_missing_artifact(tmp_path):
    """plan marked ✅ but plan.md absent -> DRIFT, exit 1."""
    write_state(tmp_path, lectures_table("| 01 | Intro | ✅ | ❌ | ❌ | ❌ | ❌ | 2026-01-01 |\n"))
    (tmp_path / "lectures" / "01").mkdir(parents=True)
    code, out = run(tmp_path)
    assert code == 1
    assert "DRIFT" in out and "plan" in out


def test_untracked_does_not_fail(tmp_path):
    """plan.md exists but status is ❌ -> UNTRACKED, but exit 0."""
    write_state(tmp_path, lectures_table("| 01 | Intro | ❌ | ❌ | ❌ | ❌ | ❌ | 2026-01-01 |\n"))
    (tmp_path / "lectures" / "01").mkdir(parents=True)
    (tmp_path / "lectures" / "01" / "plan.md").write_text("plan", encoding="utf-8")
    code, out = run(tmp_path)
    assert code == 0, out
    assert "UNTRACKED" in out


def test_figures_stale_fails(tmp_path):
    """figures ✅ with PNGs older than figures.py -> STALE, exit 1."""
    write_state(tmp_path, lectures_table("| 01 | Intro | ❌ | ❌ | ✅ | ❌ | ❌ | 2026-01-01 |\n"))
    figdir = tmp_path / "lectures" / "01" / "figures"
    figdir.mkdir(parents=True)
    png = figdir / "fig01.png"
    png.write_bytes(b"\x89PNG")
    old = time.time() - 100
    os.utime(png, (old, old))
    (figdir / "figures.py").write_text("# script", encoding="utf-8")  # newer than png
    code, out = run(tmp_path)
    assert code == 1
    assert "STALE" in out


def test_figures_fresh_passes(tmp_path):
    write_state(tmp_path, lectures_table("| 01 | Intro | ❌ | ❌ | ✅ | ❌ | ❌ | 2026-01-01 |\n"))
    figdir = tmp_path / "lectures" / "01" / "figures"
    figdir.mkdir(parents=True)
    (figdir / "figures.py").write_text("# script", encoding="utf-8")
    time.sleep(0.01)
    (figdir / "fig01.png").write_bytes(b"\x89PNG")  # newer than script
    code, out = run(tmp_path)
    assert code == 0, out


def test_slides_slidev_md_counts_as_done(tmp_path):
    """slides ✅ is satisfied by slides.md (Slidev), not only slides.tex."""
    write_state(tmp_path, lectures_table("| 01 | Intro | ❌ | ❌ | ❌ | ✅ | ❌ | 2026-01-01 |\n"))
    lec = tmp_path / "lectures" / "01"
    lec.mkdir(parents=True)
    (lec / "slides.md").write_text("# deck", encoding="utf-8")
    code, out = run(tmp_path)
    assert code == 0, out
    assert "DRIFT" not in out


def test_slides_done_without_any_deck_drifts(tmp_path):
    """slides ✅ but neither slides.tex nor slides.md present -> DRIFT."""
    write_state(tmp_path, lectures_table("| 01 | Intro | ❌ | ❌ | ❌ | ✅ | ❌ | 2026-01-01 |\n"))
    (tmp_path / "lectures" / "01").mkdir(parents=True)
    code, out = run(tmp_path)
    assert code == 1
    assert "DRIFT" in out and "slides" in out


def test_quiz_published_without_export_drifts(tmp_path):
    body = (
        "# Course State\n\n## Quizzes\n\n"
        "| # | Title | plan | questions | published | Updated |\n"
        "|---|-------|------|-----------|-----------|---------|\n"
        "| 01 | Midterm | ✅ | ✅ | ✅ | 2026-01-01 |\n"
    )
    write_state(tmp_path, body)
    qdir = tmp_path / "quizzes" / "01"
    qdir.mkdir(parents=True)
    (qdir / "quiz_plan.md").write_text("plan", encoding="utf-8")
    (qdir / "quiz_questions.md").write_text("q", encoding="utf-8")
    # no quiz_student.md -> published should DRIFT
    code, out = run(tmp_path)
    assert code == 1
    assert "DRIFT" in out and "published" in out


def homework_table(rows):
    return (
        "# Course State\n\n## Homework\n\n"
        "| # | Dir | Title | task | rubric | published | Updated |\n"
        "|---|-----|-------|------|--------|-----------|---------|\n"
        + rows
    )


def test_homework_published_without_handout_drifts(tmp_path):
    """published ✅ but homework_student.md absent -> DRIFT, exit 1."""
    write_state(tmp_path, homework_table(
        "| 01 | homework/01 | HW1 | ✅ | ✅ | ✅ | 2026-01-01 |\n"))
    hwdir = tmp_path / "homework" / "01"
    hwdir.mkdir(parents=True)
    (hwdir / "task.md").write_text("task", encoding="utf-8")
    (hwdir / "rubric.md").write_text("rubric", encoding="utf-8")
    # no homework_student.md -> published should DRIFT
    code, out = run(tmp_path)
    assert code == 1
    assert "DRIFT" in out and "published" in out


def test_homework_clean_passes(tmp_path):
    write_state(tmp_path, homework_table(
        "| 01 | homework/01 | HW1 | ✅ | ✅ | ❌ | 2026-01-01 |\n"))
    hwdir = tmp_path / "homework" / "01"
    hwdir.mkdir(parents=True)
    (hwdir / "task.md").write_text("task", encoding="utf-8")
    (hwdir / "rubric.md").write_text("rubric", encoding="utf-8")
    code, out = run(tmp_path)
    assert code == 0, out
    assert "1 homework checked" in out


def test_bulky_history_warns_without_failing(tmp_path):
    """A history.md past the threshold -> BULKY finding, but exit 0 (advisory)."""
    write_state(tmp_path, lectures_table("| 01 | Intro | ✅ | ❌ | ❌ | ❌ | ❌ | 2026-01-01 |\n"))
    lec = tmp_path / "lectures" / "01"
    lec.mkdir(parents=True)
    (lec / "plan.md").write_text("plan", encoding="utf-8")
    (lec / "history.md").write_text("\n".join(f"line {i}" for i in range(300)), encoding="utf-8")
    code, out = run(tmp_path)
    assert code == 0, out
    assert "BULKY" in out and "history.md" in out


def test_small_history_does_not_warn(tmp_path):
    write_state(tmp_path, lectures_table("| 01 | Intro | ✅ | ❌ | ❌ | ❌ | ❌ | 2026-01-01 |\n"))
    lec = tmp_path / "lectures" / "01"
    lec.mkdir(parents=True)
    (lec / "plan.md").write_text("plan", encoding="utf-8")
    (lec / "history.md").write_text("a few\nshort\nlines\n", encoding="utf-8")
    code, out = run(tmp_path)
    assert code == 0, out
    assert "BULKY" not in out


def test_homework_dir_may_nest_under_seminar(tmp_path):
    """Dir is a full path from the course root, so homework can live under a
    seminar; the drift is reported against that path."""
    write_state(tmp_path, homework_table(
        "| 03 | seminars/03-arima/homework | ARIMA HW | ✅ | ❌ | ❌ | 2026-01-01 |\n"))
    # task ✅ but seminars/03-arima/homework/task.md is missing -> DRIFT there
    code, out = run(tmp_path)
    assert code == 1
    assert "DRIFT" in out and "seminars/03-arima/homework" in out and "task" in out
