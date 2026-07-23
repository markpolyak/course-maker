# course-maker — test entry points.
#
#   make install   install test dependencies
#   make check     Levels 0-1: static + unit. Fast, deterministic, no tokens.
#   make e2e       Level 3: behavioural smoke tests via `claude -p`. Costs tokens.
#   make test      alias for `check`.
#   make package   build dist/course-maker-<version>.zip for Cowork install.
#
# PYTHON defaults to `python` (use an interpreter that has the test deps, e.g.
# your anaconda env). Override: `make check PYTHON=python3`.

PYTHON ?= python

.PHONY: install check e2e test package

install:
	$(PYTHON) -m pip install -r tests/requirements.txt

check:
	$(PYTHON) -m pytest tests/static tests/unit

e2e:
	COURSE_MAKER_E2E=1 $(PYTHON) -m pytest tests/e2e -v

test: check

package:
	./scripts/package.sh
