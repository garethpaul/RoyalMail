ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

PYTHON ?= python2
export PYTHONDONTWRITEBYTECODE = 1

.PHONY: build check contract-test lint test verify

lint:
	$(PYTHON) -B "$(ROOT)/scripts/check-docs-plans.py"
	cd "$(ROOT)" && $(PYTHON) -B -c 'compile(open("royalmail.py").read(), "royalmail.py", "exec")'

contract-test:
	$(PYTHON) -B "$(ROOT)/scripts/test_workflow_contract.py"

test:
	cd "$(ROOT)" && $(PYTHON) -B -m unittest discover -s tests

build: lint

verify: lint contract-test test

check: verify
