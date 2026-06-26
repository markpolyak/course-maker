"""Level 0 — syntax of shipped code and config.

A broken template or unparseable YAML only surfaces when a user runs the command
that copies it. These checks catch it at commit time instead.

* every *.py under skill/ and scripts/ byte-compiles;
* every *.yaml under skill/ parses as YAML.

PyYAML is a test-only dependency (see tests/requirements.txt); if it is absent
the YAML test is skipped rather than failing, so the suite still runs bare.
"""

import py_compile

import pytest

from _paths import SCRIPTS_DIR, SKILL_DIR


def python_files():
    files = sorted(SKILL_DIR.rglob("*.py"))
    files += sorted(SCRIPTS_DIR.rglob("*.py"))
    return [p for p in files if "__pycache__" not in p.parts]


def yaml_files():
    return sorted(SKILL_DIR.rglob("*.yaml")) + sorted(SKILL_DIR.rglob("*.yml"))


@pytest.mark.parametrize("path", python_files(), ids=lambda p: str(p.name))
def test_python_compiles(path):
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        pytest.fail(f"{path}: {exc}")


@pytest.mark.parametrize("path", yaml_files(), ids=lambda p: str(p.name))
def test_yaml_parses(path):
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed (pip install pyyaml)")
    try:
        list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    except yaml.YAMLError as exc:
        pytest.fail(f"{path}: {exc}")
