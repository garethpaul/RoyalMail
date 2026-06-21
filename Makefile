.DEFAULT_GOAL := check

.PHONY: build check check-python2 check-python3 contract-test contract-test-python2 contract-test-python3 lint lint-python2 lint-python3 root-test test test-python2 test-python3 verify

override SHELL := /bin/sh
override .SHELLFLAGS := -c
override PYTHON2 := python2
override PYTHON3 := python3
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); [ -f "$$path" ] || exit 1; directory=$$(/usr/bin/dirname -- "$$path"); CDPATH= cd -- "$$directory" && /bin/pwd -P)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif
export PYTHONDONTWRITEBYTECODE = 1

lint-python2:
	$(PYTHON2) -B "$$ROOT/scripts/check-docs-plans.py"
	cd "$$ROOT" && $(PYTHON2) -B -c 'compile(open("royalmail.py").read(), "royalmail.py", "exec")'

lint-python3:
	$(PYTHON3) -B "$$ROOT/scripts/check-docs-plans.py"
	cd "$$ROOT" && $(PYTHON3) -B -c 'compile(open("royalmail.py").read(), "royalmail.py", "exec")'

lint: lint-python2 lint-python3

contract-test-python2:
	$(PYTHON2) -B "$$ROOT/scripts/test_workflow_contract.py"
	$(PYTHON2) -B "$$ROOT/scripts/test_manager_contract.py"
	$(PYTHON2) -B "$$ROOT/scripts/test_smtp_contract.py"

contract-test-python3:
	$(PYTHON3) -B "$$ROOT/scripts/test_workflow_contract.py"
	$(PYTHON3) -B "$$ROOT/scripts/test_manager_contract.py"
	$(PYTHON3) -B "$$ROOT/scripts/test_smtp_contract.py"

contract-test: contract-test-python2 contract-test-python3

test-python2:
	cd "$$ROOT" && $(PYTHON2) -B -m unittest discover -s tests

test-python3:
	cd "$$ROOT" && $(PYTHON3) -B -m unittest discover -s tests

test: test-python2 test-python3

build: lint

check-python2: lint-python2 contract-test-python2 test-python2

check-python3: lint-python3 contract-test-python3 test-python3

root-test:
	"$$ROOT/scripts/test-makefile-root.sh"

verify: root-test check-python2 check-python3

check: verify
