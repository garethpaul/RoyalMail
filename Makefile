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
override REPOSITORY_MAKEFILE := $(value MAKEFILE_LIST)
override EXPECTED_MAKEFILE_LIST := $(value MAKEFILE_LIST)
override CURRENT_MAKEFILE_LIST = $(value MAKEFILE_LIST)
export REPOSITORY_MAKEFILE EXPECTED_MAKEFILE_LIST CURRENT_MAKEFILE_LIST
override ROOT :=

override define RUN_IN_REPO
if [ "$$CURRENT_MAKEFILE_LIST" != "$$EXPECTED_MAKEFILE_LIST" ]; then \
	printf '%s\n' 'multiple -f Makefiles are not supported' >&2; \
	exit 1; \
fi; \
makefile=$${REPOSITORY_MAKEFILE# }; \
if [ -z "$$makefile" ] || [ ! -f "$$makefile" ]; then \
	printf '%s\n' 'repository Makefile path could not be resolved' >&2; \
	exit 1; \
fi; \
case "$$makefile" in \
	*/*) repository_directory=$${makefile%/*} ;; \
	*) repository_directory=. ;; \
esac; \
ROOT=$$(CDPATH= cd -- "$$repository_directory" && pwd -P); \
export ROOT; \
cd "$$ROOT" &&
endef
export PYTHONDONTWRITEBYTECODE = 1

lint-python2:
	$(RUN_IN_REPO) $(PYTHON2) -B scripts/check-docs-plans.py
	$(RUN_IN_REPO) $(PYTHON2) -B -c 'compile(open("royalmail.py").read(), "royalmail.py", "exec")'

lint-python3:
	$(RUN_IN_REPO) $(PYTHON3) -B scripts/check-docs-plans.py
	$(RUN_IN_REPO) $(PYTHON3) -B -c 'compile(open("royalmail.py").read(), "royalmail.py", "exec")'

lint: lint-python2 lint-python3

contract-test-python2:
	$(RUN_IN_REPO) $(PYTHON2) -B scripts/test_workflow_contract.py
	$(RUN_IN_REPO) $(PYTHON2) -B scripts/test_manager_contract.py
	$(RUN_IN_REPO) $(PYTHON2) -B scripts/test_smtp_contract.py
	$(RUN_IN_REPO) $(PYTHON2) -B scripts/test_behavior_mutations.py

contract-test-python3:
	$(RUN_IN_REPO) $(PYTHON3) -B scripts/test_workflow_contract.py
	$(RUN_IN_REPO) $(PYTHON3) -B scripts/test_manager_contract.py
	$(RUN_IN_REPO) $(PYTHON3) -B scripts/test_smtp_contract.py
	$(RUN_IN_REPO) $(PYTHON3) -B scripts/test_behavior_mutations.py

contract-test: contract-test-python2 contract-test-python3

test-python2:
	$(RUN_IN_REPO) $(PYTHON2) -B -m unittest discover -s tests

test-python3:
	$(RUN_IN_REPO) $(PYTHON3) -B -m unittest discover -s tests

test: test-python2 test-python3

build: lint

check-python2: lint-python2 contract-test-python2 test-python2

check-python3: lint-python3 contract-test-python3 test-python3

root-test:
	$(RUN_IN_REPO) /bin/sh scripts/test-makefile-root.sh

verify: root-test check-python2 check-python3

check: verify
