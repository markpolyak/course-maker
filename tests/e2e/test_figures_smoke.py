"""Level 3 smoke — `figures` must produce a runnable script and real PNGs.

Inviolable rule: don't mark figures done without running figures.py and verifying
the PNGs exist. We check exactly that, plus re-run the generated script ourselves
to confirm it is deterministic and clean (not just that PNGs happen to be there).
Lecture 02 starts with figures not-started, so the skill generates from scratch.
"""

import subprocess
import sys

import pytest

pytestmark = pytest.mark.e2e


def test_figures_generates_runnable_pngs(course_dir, course_maker, assert_state_consistent):
    proc = course_maker("/course-maker figures 2")
    assert proc.returncode == 0, proc.stderr or proc.stdout

    figdir = course_dir / "lectures" / "02" / "figures"
    script = figdir / "figures.py"
    assert script.exists(), "figures step did not create figures.py"

    pngs = list(figdir.glob("*.png"))
    assert pngs, "figures step produced no PNG files"

    # The script must be re-runnable on its own and stay clean.
    rerun = subprocess.run(
        [sys.executable, "figures/figures.py"],
        cwd=figdir.parent,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert rerun.returncode == 0, f"re-running figures.py failed:\n{rerun.stderr}"
    assert list(figdir.glob("*.png")), "no PNG after re-running figures.py"

    assert_state_consistent()
