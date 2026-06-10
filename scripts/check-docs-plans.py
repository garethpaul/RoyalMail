#!/usr/bin/env python2
from __future__ import print_function

import glob
import os
import sys


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

if not os.path.isfile(CANONICAL_PLAN):
    failures.append('%s is missing' % rel(CANONICAL_PLAN))

if not os.path.isfile(BYTECODE_PLAN):
    failures.append('%s is missing' % rel(BYTECODE_PLAN))
if not os.path.isfile(CI_PLAN):
    failures.append('%s is missing' % rel(CI_PLAN))
if not os.path.isfile(HOSTED_LEGACY_PLAN):
    failures.append('%s is missing' % rel(HOSTED_LEGACY_PLAN))
if not os.path.isfile(CI_WORKFLOW):
    failures.append('%s is missing' % rel(CI_WORKFLOW))

plans = sorted(glob.glob(os.path.join(DOCS_PLANS, '*.md')))
if not plans:
    failures.append('docs/plans must contain at least one completed plan')

for plan_path in plans:
    plan = read(plan_path)
    if 'Status: Completed' not in plan or 'make check' not in plan:
        failures.append('%s must record completed status and make check verification' % rel(plan_path))

if os.path.isfile(CI_WORKFLOW):
    workflow = read(CI_WORKFLOW)
    required_workflow_phrases = (
        'runs-on: ubuntu-24.04',
        'uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10',
        'python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20',
        'permissions:',
        'contents: read',
        'timeout-minutes: 10',
        'run: make check',
    )
    for phrase in required_workflow_phrases:
        if phrase not in workflow:
            failures.append('%s must contain %s' % (rel(CI_WORKFLOW), phrase))

    for line in workflow.splitlines():
        stripped = line.strip()
        if stripped.startswith('uses:'):
            revision = stripped.split('@', 1)[-1].split()[0]
            if len(revision) != 40 or any(character not in '0123456789abcdef' for character in revision):
                failures.append('%s actions must be pinned to full commit SHAs' % rel(CI_WORKFLOW))
                break

    if 'continue-on-error' in workflow:
        failures.append('%s must not allow legacy verification failures' % rel(CI_WORKFLOW))

if os.path.isfile(MAKEFILE):
    makefile = read(MAKEFILE)
    required_makefile_phrases = (
        'ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))',
        'PYTHON ?= python2',
        '$(PYTHON) -B "$(ROOT)/scripts/check-docs-plans.py"',
        '$(PYTHON) -B -m unittest discover -s tests',
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
    for filename in filenames:
        if filename.endswith(('.pyc', '.pyo')):
            bytecode_files.append(rel(os.path.join(dirpath, filename)))

if bytecode_files:
    failures.append('Python bytecode must not be present: %s' % ', '.join(sorted(bytecode_files)))

if failures:
    print('Documentation plan checks failed:\n- %s' % '\n- '.join(failures), file=sys.stderr)
    sys.exit(1)

print('Documentation plan checks passed')
