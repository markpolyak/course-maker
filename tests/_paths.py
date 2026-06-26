"""Shared paths and helpers for the course-maker test suite.

A plain module (not conftest) so both tests/conftest.py and tests/e2e/conftest.py
can import it without the two conftest files colliding on the module name
`conftest`. tests/ is on sys.path via pytest.ini (pythonpath = tests).
"""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skill"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES_DIR = SKILL_DIR / "references"
TEMPLATES_DIR = SKILL_DIR / "templates"
PROFILES_DIR = SKILL_DIR / "profiles"
SCRIPTS_DIR = REPO_ROOT / "scripts"


def load_module(path, name):
    """Import a standalone .py file by path, without it being on sys.path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
