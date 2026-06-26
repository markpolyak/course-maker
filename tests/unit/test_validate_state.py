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
