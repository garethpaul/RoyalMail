.PHONY: build check lint test verify

PYTHON ?= python2
CHECK_PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE = 1

lint:
	$(CHECK_PYTHON) -B scripts/check-docs-plans.py
	@if command -v "$(PYTHON)" >/dev/null 2>&1; then \
		$(PYTHON) -B -c 'compile(open("royalmail.py").read(), "royalmail.py", "exec")'; \
	else \
		echo "Skipping legacy Python 2 RoyalMail syntax check: $(PYTHON) not found."; \
	fi

test:
	@if command -v "$(PYTHON)" >/dev/null 2>&1; then \
		$(PYTHON) -B -m unittest discover -s tests; \
	else \
		echo "Skipping legacy Python 2 RoyalMail tests: $(PYTHON) not found."; \
	fi

build: lint

verify: lint test

check: verify
