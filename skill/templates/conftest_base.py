"""Base conftest.py for course-maker labs.

Copied to labs/<LAB_DIR>/starter/conftest.py by /course-maker lab init.

This is the UNIVERSAL test harness. Its only jobs are:
  - import the student notebook and expose it as a fixture;
  - run the lab's pytest test classes;
  - track per-test outcomes;
  - hand those outcomes to an OPTIONAL grade reporter.

It deliberately knows nothing about scoring, grade-output formatting, an
external CI contract, or per-student dataset variants. Those are pluggable,
opt-in concerns so the harness stays universal across courses:

  - Grade reporting: drop a `grade_report.py` next to this file defining
    `report(outcomes: dict[str, str]) -> None`. It is called once at the end
    of the session with a mapping of test name -> outcome
    ("passed" | "failed" | "skipped"). If no `grade_report.py` is present,
    nothing extra is printed (pytest's own summary still applies).
    A ready-made reporter lives in skill/extensions/reporters/.
  - Per-student dataset variants: see skill/extensions/variants/.

Per-lab edits to THIS file should be unnecessary. The only lab-specific file
is the test module itself (tests.py) and, if used, grade_report.py.
"""

import builtins
import importlib.util
import types
from pathlib import Path

import pytest


# Filename of the notebook the student submits. Override only if a lab uses a
# different name.
NOTEBOOK_FILENAME = "exercises.ipynb"


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


# ─────────────────────────────────────────────────────────────────────────────
# Grade-report seam — DO NOT MODIFY
# ─────────────────────────────────────────────────────────────────────────────
# Optional. If a `grade_report.py` sits next to this conftest and defines
# report(outcomes), it is called with the collected outcomes at session end.
# No reporter -> no extra output (plain pytest). This keeps scoring,
# grade-output formatting, and any autograder contract out of the universal
# harness. See skill/extensions/reporters/ for a ready-made reporter.

def _load_grade_reporter():
    path = Path(__file__).parent / "grade_report.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("grade_report", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # a broken reporter must not crash the test run
        print(f"[course-maker] grade_report.py failed to load: {exc}")
        return None
    reporter = getattr(module, "report", None)
    return reporter if callable(reporter) else None


def pytest_sessionfinish(session, exitstatus):
    reporter = _load_grade_reporter()
    if reporter is not None:
        reporter(dict(_test_outcomes))
