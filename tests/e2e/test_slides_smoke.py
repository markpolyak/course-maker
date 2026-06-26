"""Level 3 smoke — `slides` must reference only existing figures and compile.

Inviolable rule: never reference a PNG in slides.tex that is not in figures/.
We parse every \\includegraphics and require the file to exist, then compile the
deck with xelatex (the fixture ships the xelatex preamble). Lecture 01 is
deck-ready (plan + visuals + figures), so slides has its prerequisites.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.e2e

INCLUDE_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


def test_slides_references_exist_and_compile(course_dir, course_maker, assert_state_consistent):
    proc = course_maker("/course-maker slides 1")
    assert proc.returncode == 0, proc.stderr or proc.stdout

    lec = course_dir / "lectures" / "01"
    tex = lec / "slides.tex"
    assert tex.exists(), "slides step did not create slides.tex"

    content = tex.read_text(encoding="utf-8")
    figdir = lec / "figures"
    for ref in INCLUDE_RE.findall(content):
        name = Path(ref).name
        exists = (figdir / name).exists() or (figdir / f"{name}.png").exists() or (lec / ref).exists()
        assert exists, f"slides.tex references a figure that does not exist: {ref}"

    # Compile with xelatex (the fixture preamble uses fontspec/polyglossia).
    xelatex = shutil.which("xelatex")
    if not xelatex:
        pytest.skip("xelatex not on PATH — checked figure references only, skipped compile")
    result = subprocess.run(
        [xelatex, "-interaction=nonstopmode", "-halt-on-error", "slides.tex"],
        cwd=lec,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, "xelatex failed to compile slides.tex:\n" + result.stdout[-3000:]
    assert (lec / "slides.pdf").exists(), "no slides.pdf produced"

    assert_state_consistent()
