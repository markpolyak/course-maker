"""Base conftest.py for course-maker labs.

Copied to labs/<LAB_DIR>/starter/conftest.py by /course-maker lab init.

Per-lab modifications happen ONLY in the SCORING block at the bottom
(TEST_POINTS, TEST_BLOCKS, DATASETS) plus the customizable strings at the
top. Everything else — IPython mocking, notebook importer, fixtures,
pytest hooks — should not be modified per lab.

This file ships as a working universal template. Override the strings at
the top to localize the grade output for your CI / language. See the
project's lab_templates.md for the conventional values.

Critical invariants (see also course-maker Inviolable rules):
- dataset_id = (Student_ID - 1) % len(DATASETS) is verbatim in pytest_sessionfinish
- The grade-output line is read by external CI; if your CI relies on a
  specific format, set GRADE_OUTPUT_LABEL accordingly and do not change the
  print() format string.
"""

import builtins
import os
import sys
import types
from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Customizable strings — override per course via lab_templates.md values
# ─────────────────────────────────────────────────────────────────────────────
# These defaults work for any language. For Russian/English courses, the
# values come from lab_templates.md (see /course-maker lab tests step).

TASKID_LABEL = "TASKID"
GRADE_OUTPUT_LABEL = "PRELIMINARY GRADE"
NOTEBOOK_FILENAME = "exercises.ipynb"
SCORING_HEADER = "LAB SCORING SYSTEM"


# ─────────────────────────────────────────────────────────────────────────────
# IPython / display mocking — DO NOT MODIFY
# ─────────────────────────────────────────────────────────────────────────────
# Student notebooks routinely call get_ipython(), display(), and input() at
# module level. Under pytest these would fail or block. Mock them.

class _DummyIPython:
    def run_line_magic(self, *args, **kwargs): pass
    def run_cell_magic(self, *args, **kwargs): pass
    def system(self, *args, **kwargs): pass
    def magic(self, *args, **kwargs): pass


def get_ipython():
    return _DummyIPython()


def _fake_input(prompt=""):
    return ""


def _fake_display(*args, **kwargs):
    pass


builtins.input = _fake_input


# ─────────────────────────────────────────────────────────────────────────────
# Notebook importer — DO NOT MODIFY
# ─────────────────────────────────────────────────────────────────────────────

def _import_student_notebook(notebook_path: str) -> types.ModuleType:
    """Read an .ipynb file and exec its code cells as a module.

    Strips Jupyter line magics (`!cmd`, `%magic`, `?help`). Injects mocked
    display() and get_ipython() so IPython-style cells run under pytest.
    """
    try:
        import nbformat
    except ImportError:
        pytest.exit(
            "nbformat is required to run lab tests. "
            "Add `nbformat` to requirements.txt."
        )

    nb = nbformat.read(notebook_path, as_version=4)
    code_chunks: list[str] = []
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        cell_lines: list[str] = []
        for line in cell.source.splitlines():
            stripped = line.lstrip()
            if stripped.startswith(("!", "%", "?")):
                continue
            cell_lines.append(line)
        if cell_lines:
            code_chunks.append("\n".join(cell_lines))

    code = "\n\n".join(code_chunks)

    module = types.ModuleType("student_notebook")
    module.__file__ = notebook_path
    module.display = _fake_display
    module.get_ipython = get_ipython

    try:
        exec(compile(code, notebook_path, "exec"), module.__dict__)
    except Exception as exc:
        pytest.exit(
            f"Failed to execute student notebook {notebook_path}:\n"
            f"  {type(exc).__name__}: {exc}"
        )
    return module


# ─────────────────────────────────────────────────────────────────────────────
# student_module fixture — DO NOT MODIFY
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def student_module():
    """Import the student notebook once per test session.

    Tests access student-defined variables/functions as attributes on this
    module, e.g. `student_module.df`, `student_module.compute_something(x)`.
    """
    nb_path = Path(__file__).parent / NOTEBOOK_FILENAME
    if not nb_path.exists():
        pytest.exit(f"Student notebook not found: {nb_path}")
    return _import_student_notebook(str(nb_path))


# ─────────────────────────────────────────────────────────────────────────────
# Test outcome tracking — DO NOT MODIFY
# ─────────────────────────────────────────────────────────────────────────────

_test_outcomes: dict[str, str] = {}  # test_name → "passed" | "failed" | "skipped"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        _test_outcomes[item.name] = report.outcome


# =============================================================================
# LAB SCORING SYSTEM — UPDATE PER LAB
# =============================================================================
# Everything below is updated per lab from lab_spec.md.
# Marker (do not delete this line; the lab tests step locates the section by it):
#   LAB SCORING SYSTEM

TEST_POINTS: dict[str, int] = {
    # Map: test function name → points awarded if test passes.
    # Sum should equal the mandatory points total in lab_spec.md
    # (excluding bonus tasks).
    #
    # Example:
    # "test_data_loaded": 5,
    # "test_observations_shape": 10,
    # "test_model_fit": 15,
}

TEST_BLOCKS: dict[str, str] = {
    # Map: TestClass name → primary test function name in that class.
    # Used by pytest_sessionfinish to print per-block status.
    #
    # Example:
    # "TestTask1_DataLoading": "test_data_loaded",
    # "TestTask2_ModelFit":   "test_model_fit",
}

DATASETS: list[tuple] = [
    # Paste verbatim from Block 0 of exercises.ipynb. Must match exactly —
    # student variants are derived from this list via the dataset_id formula.
    #
    # Format: (dataset_type, description, source) — or whatever shape
    # Block 0 uses in this lab.
    #
    # Example:
    # ("sp500", "S&P 500 Index, ticker ^GSPC, 2010-2023, yfinance", "^GSPC"),
]


# ─────────────────────────────────────────────────────────────────────────────
# pytest_sessionfinish — prints student-visible grade summary
# ─────────────────────────────────────────────────────────────────────────────
# Permitted edits per lab:
#   - Add a manual-grading note if some points are graded by the instructor
#   - Remove the bonus line if the lab has no bonus tasks
#   - Adjust the numerator inside the grade-output line to include bonus
# Forbidden edits:
#   - Changing the dataset_id formula
#   - Changing the format of the TASKID and grade-output print lines
#   (both are read by external CI grading)

def pytest_sessionfinish(session, exitstatus):
    # ── Variant ID (verbatim formula — DO NOT MODIFY) ──
    try:
        student_id = int(os.environ.get("STUDENT_ID", "1"))
    except ValueError:
        student_id = 1
    if not DATASETS:
        dataset_id = 0
    else:
        dataset_id = (student_id - 1) % len(DATASETS)

    # ── Earned points ──
    mandatory_earned = sum(
        points for name, points in TEST_POINTS.items()
        if _test_outcomes.get(name) == "passed"
    )
    mandatory_total = sum(TEST_POINTS.values())

    # ── Bonus points (tests in classes named TestBonus*) ──
    bonus_earned = 0
    bonus_total = 0
    for name, outcome in _test_outcomes.items():
        # Bonus convention: test points may be looked up in TEST_POINTS or
        # default to 1 if the test is not registered there (bonus tasks
        # often use pytest.skip).
        if name.startswith("test_bonus_"):
            pts = TEST_POINTS.get(name, 1)
            bonus_total += pts
            if outcome == "passed":
                bonus_earned += pts

    # ── Output ──
    print()
    print("=" * 60)
    print(f"  {SCORING_HEADER}")
    print("=" * 60)
    print(f"  {TASKID_LABEL} is {dataset_id + 1}")

    for cls_name, primary_test in TEST_BLOCKS.items():
        outcome = _test_outcomes.get(primary_test, "not_run")
        marker = {"passed": "✓", "failed": "✗", "skipped": "○"}.get(outcome, "?")
        print(f"  {marker} {cls_name}: {outcome}")

    print()
    if bonus_total > 0:
        print(
            f"  {GRADE_OUTPUT_LABEL}: "
            f"{mandatory_earned + bonus_earned} / {mandatory_total} "
            f"(+ {bonus_earned} bonus of {bonus_total})"
        )
    else:
        print(f"  {GRADE_OUTPUT_LABEL}: {mandatory_earned} / {mandatory_total}")
    print("=" * 60)
