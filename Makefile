override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

PYTHON2 ?= python2
PYTHON3 ?= python3
export PYTHONDONTWRITEBYTECODE = 1

.PHONY: build check check-python2 check-python3 contract-test contract-test-python2 contract-test-python3 lint lint-python2 lint-python3 test test-python2 test-python3 verify

lint-python2:
	$(PYTHON2) -B "$(ROOT)/scripts/check-docs-plans.py"
	cd "$(ROOT)" && $(PYTHON2) -B -c 'compile(open("royalmail.py").read(), "royalmail.py", "exec")'

lint-python3:
	$(PYTHON3) -B "$(ROOT)/scripts/check-docs-plans.py"
	cd "$(ROOT)" && $(PYTHON3) -B -c 'compile(open("royalmail.py").read(), "royalmail.py", "exec")'

lint: lint-python2 lint-python3

contract-test-python2:
	$(PYTHON2) -B "$(ROOT)/scripts/test_workflow_contract.py"
	$(PYTHON2) -B "$(ROOT)/scripts/test_manager_contract.py"

contract-test-python3:
	$(PYTHON3) -B "$(ROOT)/scripts/test_workflow_contract.py"
	$(PYTHON3) -B "$(ROOT)/scripts/test_manager_contract.py"

contract-test: contract-test-python2 contract-test-python3

test-python2:
	cd "$(ROOT)" && $(PYTHON2) -B -m unittest discover -s tests

test-python3:
	cd "$(ROOT)" && $(PYTHON3) -B -m unittest discover -s tests

test: test-python2 test-python3

build: lint

check-python2: lint-python2 contract-test-python2 test-python2

check-python3: lint-python3 contract-test-python3 test-python3

verify: check-python2 check-python3

check: verify
