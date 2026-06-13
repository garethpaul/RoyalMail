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
MIMETYPE_TOKEN_PLAN = os.path.join(DOCS_PLANS, '2026-06-12-attachment-mimetype-token-guard.md')
PYTHON3_PLAN = os.path.join(DOCS_PLANS, '2026-06-12-python3-compatibility.md')
CI_WORKFLOW = os.path.join(ROOT, '.github', 'workflows', 'check.yml')
MAKEFILE = os.path.join(ROOT, 'Makefile')
ROYALMAIL_SOURCE = os.path.join(ROOT, 'royalmail.py')
ROYALMAIL_TESTS = os.path.join(ROOT, 'tests', 'test_royalmail.py')


def rel(path):
    return os.path.relpath(path, ROOT)


def read(path):
    with open(path, 'r') as handle:
        return handle.read()


failures = []

for required_path in (
        CANONICAL_PLAN,
        BYTECODE_PLAN,
        CI_PLAN,
        HOSTED_LEGACY_PLAN,
        MIMETYPE_TOKEN_PLAN,
        PYTHON3_PLAN,
        CI_WORKFLOW,
        ROYALMAIL_SOURCE,
        ROYALMAIL_TESTS):
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
        'PYTHON2 ?= python2',
        'PYTHON3 ?= python3',
        '$(PYTHON2) -B "$(ROOT)/scripts/check-docs-plans.py"',
        '$(PYTHON3) -B "$(ROOT)/scripts/check-docs-plans.py"',
        '$(PYTHON2) -B "$(ROOT)/scripts/test_workflow_contract.py"',
        '$(PYTHON3) -B "$(ROOT)/scripts/test_workflow_contract.py"',
        '$(PYTHON2) -B -m unittest discover -s tests',
        '$(PYTHON3) -B -m unittest discover -s tests',
        'verify: check-python2 check-python3',
    )
    for phrase in required_makefile_phrases:
        if phrase not in makefile:
            failures.append('Makefile must contain %s' % phrase)

    if 'command -v "$(PYTHON' in makefile or 'Skipping legacy Python 2' in makefile or 'Skipping Python 3' in makefile:
        failures.append('Makefile must require both runtime gates instead of skipping them')

for docs_file in ('README.md', 'VISION.md', 'SECURITY.md', 'CHANGES.md'):
    docs_path = os.path.join(ROOT, docs_file)
    docs = ' '.join(read(docs_path).split()) if os.path.isfile(docs_path) else ''
    if 'GitHub Actions' not in docs:
        failures.append('%s must document the GitHub Actions baseline' % docs_file)
    if 'ASCII MIME type tokens' not in docs:
        failures.append('%s must document ASCII MIME type tokens' % docs_file)
    if 'ASCII Content-ID tokens' not in docs:
        failures.append('%s must document ASCII Content-ID tokens' % docs_file)
    if 'Python 3.12' not in docs:
        failures.append('%s must document the Python 3.12 compatibility gate' % docs_file)

if os.path.isfile(ROYALMAIL_SOURCE):
    royalmail_source = read(ROYALMAIL_SOURCE)
    required_source_fragments = (
        'MIME_TOKEN_RE = re.compile(',
        "^[A-Za-z0-9!#$%&'*+.^_`|~-]+$",
        'len(parts) != 2',
        'not MIME_TOKEN_RE.match(parts[0])',
        'not MIME_TOKEN_RE.match(parts[1])',
        'Attachment mimetype must use ASCII maintype/subtype tokens',
        'CONTENT_ID_RE = re.compile(',
        "(?:\\.[A-Za-z0-9!#$%&'*+\\-/=?^_`{|}~]+)*",
        "(?:@[A-Za-z0-9!#$%&'*+\\-/=?^_`{|}~]+",
        'def _safe_content_id(self, cid):',
        'Content-ID must use printable ASCII msg-id token characters',
        'if cid is not None:',
        'import queue as Queue',
        'string_types = (str,)',
        'def _header_text(value, charset):',
        '_charset=self.charset',
    )
    for fragment in required_source_fragments:
        if fragment not in royalmail_source:
            failures.append('royalmail.py must contain %s' % fragment)

if os.path.isfile(ROYALMAIL_TESTS):
    royalmail_tests = read(ROYALMAIL_TESTS)
    for fragment in (
            'test_attachment_accepts_vendor_mimetype_tokens',
            'application/vnd.example+json',
            'text/plain; charset=utf-8',
            'text/pl\\xffain',
            'test_attachment_accepts_ascii_msg_id_content_id',
            'test_rejects_malformed_attachment_content_ids_before_file_read',
            'test_unicode_subject_uses_declared_charset'):
        if fragment not in royalmail_tests:
            failures.append('tests/test_royalmail.py must contain %s' % fragment)

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
