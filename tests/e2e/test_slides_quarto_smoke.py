"""Level 3 smoke — a Quarto deck must render, and only reference figures it has.

The Quarto path differs from Beamer in what "the figures exist" means: a chunk
draws its own image at render time, so the check that matters is that
`quarto render` exits clean. That is also the guarantee the Inviolable rule in
SKILL.md leans on — a chunk that raises stops the render and produces no deck.

We assert both halves:
  * every `![](...)` path the deck names is a file that exists (the PNG rule
    still binds a Quarto deck);
  * the deck renders to reveal.js without error.

The fixture course is Beamer, so the test converts its copy to Quarto first —
headmatter from the shipped template, format passed explicitly on the command.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from _paths import SKILL_DIR

pytestmark = pytest.mark.e2e

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
CHUNK_RE = re.compile(r"^\s*`{3,}\s*\{[A-Za-z][A-Za-z0-9_]*[^}]*\}", re.M)

HEADMATTER_TEMPLATE = SKILL_DIR / "templates" / "slides_headmatter_quarto.qmd"


def _make_quarto_course(course_dir):
    """Point the fixture course at the Quarto format before running the command."""
    shutil.copy(HEADMATTER_TEMPLATE, course_dir / "slides_headmatter.qmd")
    claude_md = course_dir / "CLAUDE.md"
    text = claude_md.read_text(encoding="utf-8")
    text = text.replace("## Course context", "## Course context\n\n**Slides format:** quarto", 1)
    claude_md.write_text(text, encoding="utf-8")


def test_quarto_deck_renders_and_references_only_existing_figures(
    course_dir, course_maker, assert_state_consistent
):
    quarto = shutil.which("quarto")
    if not quarto:
        pytest.skip("quarto not on PATH — install it to run the Quarto smoke test")

    _make_quarto_course(course_dir)

    proc = course_maker("/course-maker slides 1 quarto")
    assert proc.returncode == 0, proc.stderr or proc.stdout

    lec = course_dir / "lectures" / "01"
    qmd = lec / "slides.qmd"
    assert qmd.exists(), "slides step did not create slides.qmd"

    content = qmd.read_text(encoding="utf-8")

    # Slides are `##` headings — a deck built with `---` separators is broken
    # even though it renders, so check the shape too.
    assert content.count("\n## ") >= 2, "deck has no level-2 slide headings"

    for ref in IMAGE_RE.findall(content):
        if ref.startswith(("http://", "https://", "data:")):
            continue
        assert (lec / ref).exists(), f"slides.qmd references a figure that does not exist: {ref}"

    result = subprocess.run(
        [quarto, "render", "slides.qmd", "--to", "revealjs"],
        cwd=lec,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert result.returncode == 0, (
        "quarto render failed:\n" + (result.stderr or result.stdout)[-3000:]
    )
    assert (lec / "slides.html").exists(), "no slides.html produced"

    assert_state_consistent()


def test_failing_chunk_fails_the_render(tmp_path):
    """
    The guarantee the inline-figure mode rests on: a chunk that raises must stop
    the render and leave no output file. If Quarto ever defaults to `error: true`,
    the Inviolable rule about chunk-based figures silently stops meaning anything
    and this test is the tripwire.
    """
    quarto = shutil.which("quarto")
    if not quarto:
        pytest.skip("quarto not on PATH")

    deck = tmp_path / "broken.qmd"
    deck.write_text(
        "---\ntitle: Broken\nformat: revealjs\n---\n\n"
        "## Bad chunk\n\n"
        "```{python}\n"
        "import matplotlib.pyplot as plt\n"
        "plt.plot(name_that_does_not_exist)\n"
        "```\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [quarto, "render", "broken.qmd", "--to", "revealjs"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode != 0, "a raising chunk must fail the render"
    assert not (tmp_path / "broken.html").exists(), "a failed render must leave no deck"
