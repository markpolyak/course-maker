"""Suite-wide pytest config.

Shared paths/helpers live in tests/_paths.py (a normal module) to avoid a name
clash between this conftest and tests/e2e/conftest.py. Layout:

    tests/static/  — Level 0: deterministic checks on the skill itself.
    tests/unit/    — Level 1: contract tests for the real scripts.
    tests/e2e/     — Level 3: behavioural smoke tests via `claude -p` (opt-in).

Levels 0 and 1 are pure and fast and run on every push. Level 3 is opt-in and
costs tokens; it is gated behind COURSE_MAKER_E2E=1 (see tests/e2e/conftest.py).
"""
