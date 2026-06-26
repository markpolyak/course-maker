"""Level 3 smoke — `quiz publish` must strip every answer marker.

Inviolable rule: the student-facing export must never carry the answer key. This
is the single highest-stakes leak in the skill (it would hand students the
answers), and it is fully deterministic to check: grep the export for any answer
marker and require none.
"""

import pytest

pytestmark = pytest.mark.e2e


def test_publish_strips_answers(course_dir, course_maker, assert_state_consistent):
    proc = course_maker("/course-maker quiz publish 1")
    assert proc.returncode == 0, proc.stderr or proc.stdout

    qdir = course_dir / "quizzes" / "01"
    exports = list(qdir.glob("quiz_student.md")) + list(qdir.glob("quiz_variant_*.md"))
    assert exports, f"no student export produced; quiz dir holds: {[p.name for p in qdir.iterdir()]}"

    for path in exports:
        text = path.read_text(encoding="utf-8")
        assert "✓" not in text, f"answer marker ✓ leaked into {path.name}"
        assert "- [x]" not in text.lower(), f"checked answer box leaked into {path.name}"
        assert "**Answer:**" not in text, f"answer line leaked into {path.name}"

    # the question bank (answer key) must remain present and untouched as a file
    assert (qdir / "quiz_questions.md").exists(), "answer key disappeared"

    assert_state_consistent()
