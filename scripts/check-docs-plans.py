#!/usr/bin/env python2
from __future__ import print_function

import glob
import os
import sys

from workflow_contract import validate as validate_workflow


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCS_PLANS = os.path.join(ROOT, 'docs', 'plans')
CANONICAL_PLAN = os.path.join(DOCS_PLANS, '2026-06-08-royalmail-baseline.md')
BYTECODE_PLAN = os.path.join(DOCS_PLANS, '2026-06-09-bytecode-free-verification.md')
CI_PLAN = os.path.join(DOCS_PLANS, '2026-06-10-ci-baseline.md')
HOSTED_LEGACY_PLAN = os.path.join(DOCS_PLANS, '2026-06-10-hosted-legacy-validation.md')
CI_WORKFLOW = os.path.join(ROOT, '.github', 'workflows', 'check.yml')
MAKEFILE = os.path.join(ROOT, 'Makefile')


def rel(path):
    return os.path.relpath(path, ROOT)


def read(path):
    with open(path, 'r') as handle:
        return handle.read()


failures = []

for required_path in (CANONICAL_PLAN, BYTECODE_PLAN, CI_PLAN, HOSTED_LEGACY_PLAN, CI_WORKFLOW):
    if not os.path.isfile(required_path):
        failures.append('%s is missing' % rel(required_path))

plans = sorted(glob.glob(os.path.join(DOCS_PLANS, '*.md')))
if not plans:
    failures.append('docs/plans must contain at least one completed plan')

for plan_path in plans:
    plan = read(plan_path)
    if 'Status: Completed' not in plan or 'make check' not in plan:
        failures.append('%s must record completed status and make check verification' % rel(plan_path))

if os.path.isfile(CI_WORKFLOW):
    for requirement in validate_workflow(read(CI_WORKFLOW)):
        failures.append('%s must %s' % (rel(CI_WORKFLOW), requirement))

if os.path.isfile(MAKEFILE):
    makefile = read(MAKEFILE)
    required_makefile_phrases = (
        'ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))',
        'PYTHON ?= python2',
        '$(PYTHON) -B "$(ROOT)/scripts/check-docs-plans.py"',
        '$(PYTHON) -B "$(ROOT)/scripts/test_workflow_contract.py"',
        '$(PYTHON) -B -m unittest discover -s tests',
        'verify: lint contract-test test',
    )
    for phrase in required_makefile_phrases:
        if phrase not in makefile:
            failures.append('Makefile must contain %s' % phrase)

    if 'command -v "$(PYTHON)"' in makefile or 'Skipping legacy Python 2' in makefile:
        failures.append('Makefile must require Python 2 verification instead of skipping it')

for docs_file in ('README.md', 'VISION.md', 'SECURITY.md', 'CHANGES.md'):
    docs_path = os.path.join(ROOT, docs_file)
    if not os.path.isfile(docs_path) or 'GitHub Actions' not in read(docs_path):
        failures.append('%s must document the GitHub Actions baseline' % docs_file)

bytecode_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if '.git' in dirnames:
        dirnames.remove('.git')
    if '__pycache__' in dirnames:
        bytecode_files.append(rel(os.path.join(dirpath, '__pycache__')))
        dirnames.remove('__pycache__')
    for filename in filenames:
        if filename.endswith(('.pyc', '.pyo')):
            bytecode_files.append(rel(os.path.join(dirpath, filename)))

if bytecode_files:
    failures.append('Python bytecode must not be present: %s' % ', '.join(sorted(bytecode_files)))

if failures:
    print('Documentation plan checks failed:\n- %s' % '\n- '.join(failures), file=sys.stderr)
    sys.exit(1)

print('Documentation plan checks passed')
