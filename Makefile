.PHONY: build check lint test verify

PYTHON ?= python2
export PYTHONDONTWRITEBYTECODE = 1

lint:
	@if command -v "$(PYTHON)" >/dev/null 2>&1; then \
		$(PYTHON) -B -c 'compile(open("royalmail.py").read(), "royalmail.py", "exec")'; \
		$(PYTHON) -B scripts/check-docs-plans.py; \
	else \
		echo "Skipping legacy Python 2 RoyalMail lint checks: $(PYTHON) not found."; \
	fi

test:
	@if command -v "$(PYTHON)" >/dev/null 2>&1; then \
		$(PYTHON) -B -m unittest discover -s tests; \
	else \
		echo "Skipping legacy Python 2 RoyalMail tests: $(PYTHON) not found."; \
	fi

build: lint

verify: lint test build

check: verify
