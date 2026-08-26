"""Level 1 — contract tests for skill/scripts/site_guard.py.

`site` publishes to the open web, so the two steps that keep instructor-only
material off it must be deterministic rather than prose an agent may skip.
These tests are the reason those steps live in a script: they cover the leak
paths for free, where a Level 3 run would cost tokens and still not prove the
guard catches anything.

Both directions matter. A guard that misses a leak is useless; a guard that
fires on legitimate content gets loosened by whoever hits the false positive,
and then it is also useless. Every "clean" test below is guarding against the
second failure.
"""

import subprocess
import sys

from _paths import SKILL_DIR

GUARD = SKILL_DIR / "scripts" / "site_guard.py"


def run(*args):
    proc = subprocess.run(
        [sys.executable, str(GUARD), *map(str, args)],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


DECK_WITH_NOTES = """\
---
title: "Lecture 1"
format:
  revealjs: default
---

<!-- Slide 02 -->
## Outline

- one

<!-- course-maker:notes 02 -->
::: {.notes}
Say hello, then set up the problem.
:::

<!-- Slide 03 -->
## Content

:::: {.columns}
::: {.column width="50%"}
left
:::
::::

<!-- course-maker:notes 03 -->
::: {.notes}
Walk through the derivation slowly.
:::
"""


def test_strip_notes_removes_marked_blocks(tmp_path):
    deck = tmp_path / "slides.qmd"
    deck.write_text(DECK_WITH_NOTES, encoding="utf-8")
    out = tmp_path / "public.qmd"

    code, log = run("strip-notes", deck, out)
    assert code == 0, log

    text = out.read_text(encoding="utf-8")
    assert "course-maker:notes" not in text
    assert "{.notes}" not in text
    assert "Say hello" not in text
    assert "Walk through the derivation" not in text

    # Everything that is not a note survives, including a column div whose
    # closing ::: must not be mistaken for the end of a notes block.
    assert "## Outline" in text
    assert "## Content" in text
    assert '::: {.column width="50%"}' in text
    assert "left" in text
    assert deck.read_text(encoding="utf-8") == DECK_WITH_NOTES, "source deck must not change"


def test_strip_notes_refuses_hand_written_block(tmp_path):
    """An unmarked notes block cannot be removed without guessing — fail loudly."""
    deck = tmp_path / "slides.qmd"
    deck.write_text(
        "## Slide\n\n::: {.notes}\nI typed this myself.\n:::\n",
        encoding="utf-8",
    )
    out = tmp_path / "public.qmd"

    code, log = run("strip-notes", deck, out)
    assert code == 1
    assert "hand-written" in log
    assert not out.exists(), "no output may be written when the deck is unsafe"


def test_check_clean_site_passes(tmp_path):
    site = tmp_path / "_site"
    (site / "decks").mkdir(parents=True)
    (site / "index.html").write_text(
        "<html><body><h1>Applied Deep Learning</h1></body></html>", encoding="utf-8"
    )
    (site / "syllabus.html").write_text(
        "<html><body><p>Grading: 40% labs.</p></body></html>", encoding="utf-8"
    )
    code, log = run("check", site)
    assert code == 0, log


def test_check_catches_rendered_speaker_notes(tmp_path):
    site = tmp_path / "_site"
    site.mkdir()
    (site / "slides.html").write_text(
        '<section><h2>Slide</h2><aside class="notes">Say hello.</aside></section>',
        encoding="utf-8",
    )
    code, log = run("check", site)
    assert code == 1
    assert "rendered speaker notes" in log


def test_check_catches_deny_listed_file(tmp_path):
    site = tmp_path / "_site"
    (site / "homework").mkdir(parents=True)
    (site / "homework" / "rubric.md").write_text("5 points for ...", encoding="utf-8")
    code, log = run("check", site)
    assert code == 1
    assert "rubric.md" in log


def test_check_catches_instructor_aside(tmp_path):
    site = tmp_path / "_site"
    site.mkdir()
    (site / "hw.html").write_text("<p>Task</p><!-- instructor: expect 3 hours -->", encoding="utf-8")
    code, log = run("check", site)
    assert code == 1
    assert "instructor aside" in log


def test_check_does_not_fire_on_legitimate_content(tmp_path):
    """
    The patterns are narrow on purpose. A checkmark on a slide, the word
    "rubric" in a syllabus, and a note-taking tip are all normal student-facing
    text and must not be reported.
    """
    site = tmp_path / "_site"
    site.mkdir()
    (site / "page.html").write_text(
        "<html><body>"
        "<p>Correct answer: ✓ the gradient vanishes</p>"
        "<p>The grading rubric is published in the syllabus.</p>"
        "<p>Bring notes to the exam.</p>"
        "</body></html>",
        encoding="utf-8",
    )
    code, log = run("check", site)
    assert code == 0, log


def test_check_missing_directory_is_usage_error(tmp_path):
    code, log = run("check", tmp_path / "nope")
    assert code == 2
    assert "not found" in log
