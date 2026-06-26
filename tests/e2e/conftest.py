"""Level 3 — behavioural smoke harness.

These tests drive the real skill through `claude -p` against a throwaway copy of
the fixture course, then assert deterministic post-conditions on the artifacts it
produces. They cost tokens and are non-deterministic, so they are OPT-IN:

    COURSE_MAKER_E2E=1 python -m pytest tests/e2e -v

Without that env var (and a `claude` binary on PATH) every test here is skipped,
so the default `pytest` run stays pure and fast.

Approval gates: the skill normally waits for the user to approve output before
saving. We don't change the skill — instead the runner's prompt grants approval
in advance (a legitimate user message), so a single non-interactive turn writes
the files we then check. The Agent SDK path (scripted multi-turn approver, needed
for chunked `... next` steps) can be added later behind the same fixtures.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from _paths import SKILL_DIR  # tests/ is on pythonpath (pytest.ini)

FIXTURE_COURSE = Path(__file__).parent / "fixtures" / "course"
LOG_DIR = Path(__file__).parent / "logs"
E2E_ENABLED = os.environ.get("COURSE_MAKER_E2E") == "1"
# Pin the model for reproducibility; without it `claude -p` uses your CLI default
# model (the same one normal sessions resolve), which can drift as settings
# change. e.g. COURSE_MAKER_E2E_MODEL=opus
E2E_MODEL = os.environ.get("COURSE_MAKER_E2E_MODEL")
CLAUDE_BIN = shutil.which("claude")
VALIDATE = SKILL_DIR / "scripts" / "validate_state.py"


@pytest.fixture(autouse=True)
def _require_e2e():
    if not E2E_ENABLED:
        pytest.skip("e2e disabled — set COURSE_MAKER_E2E=1 to run behavioural smoke tests")
    if not CLAUDE_BIN:
        pytest.skip("`claude` CLI not found on PATH")


def _ensure_skill_discoverable(course_dir):
    """Make the working-tree skill the one `claude` loads. If the global install
    is already a symlink to this repo's skill/, nothing to do; otherwise drop a
    project-level skill symlink into the fixture (covers CI / fresh checkouts)."""
    global_link = Path.home() / ".claude" / "skills" / "course-maker"
    try:
        if global_link.resolve() == SKILL_DIR.resolve():
            return
    except OSError:
        pass
    proj = course_dir / ".claude" / "skills"
    proj.mkdir(parents=True, exist_ok=True)
    target = proj / "course-maker"
    if not target.exists():
        target.symlink_to(SKILL_DIR, target_is_directory=True)


@pytest.fixture
def course_dir(tmp_path):
    """A fresh, internally-consistent copy of the fixture course in a temp dir.

    Lecture 01 ships deck-ready (figures marked done) but its PNGs are generated
    here rather than committed as binaries, so the copy matches its own state and
    validate_state.py is clean before any command runs.
    """
    dst = tmp_path / "course"
    shutil.copytree(FIXTURE_COURSE, dst)
    subprocess.run(
        [sys.executable, "figures/figures.py"],
        cwd=dst / "lectures" / "01",
        check=True,
        capture_output=True,
        text=True,
    )
    _ensure_skill_discoverable(dst)
    return dst


def _wrap(command):
    return (
        "This is an automated, non-interactive test run of the course-maker skill.\n"
        f"Execute exactly this command to completion: {command}\n\n"
        "Approval is granted in advance: save all generated files directly to disk; "
        "do not pause for confirmation between chunks or steps; do not ask questions. "
        "Run whatever scripts the workflow requires (for example figures.py). "
        "If anything is ambiguous, pick the most reasonable default and proceed.\n"
        "When fully finished, print the single line: COURSE_MAKER_DONE"
    )


def _slug(command):
    return re.sub(r"[^a-z0-9]+", "-", command.lower()).strip("-")[:60] or "command"


@pytest.fixture
def course_maker(course_dir):
    """Return run(command) -> CompletedProcess, executing a course-maker command
    headlessly inside the fixture course.

    Every run captures the full turn-by-turn transcript (--verbose
    --output-format stream-json) and writes it to tests/e2e/logs/<command>.jsonl,
    so you can inspect exactly what claude did. View it with: `jq . <file>`.
    """

    def run(command, timeout=900):
        LOG_DIR.mkdir(exist_ok=True)
        log_path = LOG_DIR / f"{_slug(command)}.jsonl"
        cmd = [
            CLAUDE_BIN, "-p", _wrap(command),
            "--dangerously-skip-permissions",
            "--verbose", "--output-format", "stream-json",
        ]
        if E2E_MODEL:
            cmd += ["--model", E2E_MODEL]
        proc = subprocess.run(
            cmd, cwd=course_dir, capture_output=True, text=True, timeout=timeout
        )
        log_path.write_text(proc.stdout or "", encoding="utf-8")
        # Visible on failure (pytest shows captured stdout) and with `pytest -s`.
        print(f"\n[course-maker e2e] '{command}' transcript -> {log_path}")
        return proc

    return run


@pytest.fixture
def assert_state_consistent(course_dir):
    """Run the deterministic drift checker over the resulting course and require a
    clean bill (exit 0). Ties the Level 1 facts engine into the e2e assertions."""

    def check():
        proc = subprocess.run(
            [sys.executable, str(VALIDATE), "--root", str(course_dir)],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, "validate_state reported drift:\n" + proc.stdout

    return check
