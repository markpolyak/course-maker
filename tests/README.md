# course-maker tests

Automated checks for the skill, so the manual eyeball pass over every command
isn't the only safety net. Three levels, by cost and determinism.

## Quick start

```bash
make install        # test deps (pytest, PyYAML, matplotlib) into your env
make check          # Levels 0 + 1 — fast, deterministic, no tokens
make e2e            # Level 3 — behavioural smoke tests (needs `claude`, costs tokens)
```

`make` defaults to `python`; use an interpreter that has the deps (e.g. an
anaconda env) or override: `make check PYTHON=python3`.

## Levels

### Level 0 — static skill checks (`tests/static/`)
Deterministic checks on the skill files themselves. No tokens.

* **English-only** — `SKILL.md` + `references/*.md` carry no non-English letters
  (Greek math and the ℹ-style letterlike glyphs are allowed; Cyrillic/CJK are
  not). Localized `templates/*_ru.md` are out of scope by design.
* **Structure** — every `references/*.md` named in `SKILL.md` exists, and no
  reference file is orphaned.
* **Syntax** — every shipped `*.py` byte-compiles; every `*.yaml` parses.
* **Anti-personalization** *(xfail until IMPROVEMENT_PLAN wave 4)* — one
  instructor's variant formula / CI label must not live in the universal files.
  It is xfail, not skip: when wave 4 cleans the leak the test XPASSes — a signal
  to drop the marker and make it a hard guard. It hardcodes no personal literal
  (reads them from the profile that owns them).

### Level 1 — unit tests (`tests/unit/`)
Contract tests for the real scripts. No tokens.

* **`validate_state.py`** — driven as a subprocess like CI does: exit codes and
  DRIFT/STALE/UNTRACKED/BLIND findings against throwaway course trees.
* **`nonlatin.py`** — the letter classifier behind the English-only guard.

### Level 3 — behavioural smoke tests (`tests/e2e/`)
Drive the real skill through `claude -p` against a throwaway copy of the fixture
course in `tests/e2e/fixtures/course/`, then assert deterministic post-conditions
on the artifacts. **Opt-in** (costs tokens, non-deterministic):

```bash
COURSE_MAKER_E2E=1 make e2e
```

Without `COURSE_MAKER_E2E=1` and a `claude` binary on PATH, these tests skip, so
the default run stays pure. Coverage today (smoke — the riskiest commands):

* **figures** — generates a runnable `figures.py` and real PNGs (re-run to prove
  it's clean).
* **slides** — references only existing figures and compiles with xelatex (the
  compile is skipped if xelatex is absent; references are still checked).
* **quiz publish** — the student export carries no answer markers.

Each e2e test also runs `validate_state.py` over the result and requires a clean
bill, tying the Level 1 facts engine into the behavioural checks.

**Seeing what claude did.** Every e2e run writes the full turn-by-turn transcript
(tool calls + results) to `tests/e2e/logs/<command>.jsonl` (gitignored). Read it
with `jq . tests/e2e/logs/course-maker-quiz-publish-1.jsonl`. The transcript path
is also printed on failure and under `pytest -s`.

**Model.** The runner does not pin a model, so `claude -p` uses your CLI default
model (the same one normal `claude` sessions resolve when you don't override),
which can drift with your settings. For reproducible runs pin it:
`COURSE_MAKER_E2E_MODEL=opus make e2e` (accepts an alias like `opus`/`sonnet` or a
full model id).

The harness grants approval in advance via the runner's prompt, so a single
non-interactive turn writes the files (the skill is unchanged). Chunked
`... next` steps need a scripted multi-turn approver (Claude Agent SDK) — a
planned addition behind the same fixtures.

## How the skill is found
On a dev machine `~/.claude/skills/course-maker` is usually a symlink to this
repo's `skill/`, so `claude` loads the working tree directly. If it isn't, the
e2e harness drops a project-level skill symlink into the fixture copy (covers CI
and fresh checkouts).

## CI
* `.github/workflows/checks.yml` — Levels 0-1 on every push / PR.
* `.github/workflows/e2e.yml` — Level 3 nightly + manual dispatch; needs an
  `ANTHROPIC_API_KEY` secret.
