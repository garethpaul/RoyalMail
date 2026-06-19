#!/usr/bin/env python2
from __future__ import print_function

from workflow_contract import CHECKOUT_ACTION, CONTAINER_IMAGE, PYTHON3_CONTAINER_IMAGE, validate


BASELINE = '''name: Check

on:
  push:
    branches: [master]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  legacy-python:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    container:
      image: python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Show Python runtime
        run: python2 --version
      - name: Run full legacy verification
        run: make check-python2

  modern-python:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    container:
      image: python:3.12.8@sha256:e74938514dc67ad3eade8798aa929f5dd569e463758c83243636d4e1b54aa559
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Show Python runtime
        run: python3 --version
      - name: Run full modern verification
        run: make check-python3
'''


def mutate(description, target, replacement):
    mutated = BASELINE.replace(target, replacement, 1)
    if mutated == BASELINE:
        raise AssertionError('%s mutation did not alter the fixture' % description)
    return mutated


def assert_invalid(description, workflow):
    if not validate(workflow):
        raise AssertionError('%s mutation was accepted' % description)


if validate(BASELINE):
    raise AssertionError('baseline workflow is invalid: %s' % ', '.join(validate(BASELINE)))

mutations = {
    'contradictory credentials': mutate(
        'contradictory credentials',
        'persist-credentials: false',
        'persist-credentials: false\n          persist-credentials: true',
    ),
    'relocated credentials': mutate(
        'relocated credentials',
        '        with:\n          persist-credentials: false\n',
        '',
    ).replace('permissions:', 'persist-credentials: false\n\npermissions:', 1),
    'floating checkout action': mutate('floating checkout action', CHECKOUT_ACTION, 'actions/checkout@v6'),
    'extra action': mutate(
        'extra action',
        '      - name: Show Python runtime',
        '      - uses: example/unreviewed-action@v1\n      - name: Show Python runtime',
    ),
    'write permission': mutate('write permission', 'contents: read', 'contents: read\n  issues: write'),
    'missing push': mutate('missing push', '  push:\n    branches: [master]\n', ''),
    'missing pull request': mutate('missing pull request', '  pull_request:\n', ''),
    'missing manual dispatch': mutate('missing manual dispatch', '  workflow_dispatch:\n', ''),
    'duplicate runner': mutate(
        'duplicate runner',
        '    runs-on: ubuntu-24.04',
        '    runs-on: ubuntu-24.04\n    runs-on: ubuntu-24.04',
    ),
    'unbounded job': mutate('unbounded job', '    timeout-minutes: 10\n', ''),
    'floating Python 2 container': mutate(
        'floating Python 2 container',
        CONTAINER_IMAGE,
        'python:2.7.18',
    ),
    'wrong Python 2 container digest': mutate(
        'wrong Python 2 container digest',
        'c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20',
        '0000000000000000000000000000000000000000000000000000000000000000',
    ),
    'floating Python 3 container': mutate(
        'floating Python 3 container',
        PYTHON3_CONTAINER_IMAGE,
        'python:3.12.8',
    ),
    'missing Python 3 job': mutate(
        'missing Python 3 job',
        '\n  modern-python:',
        '\n  disabled-modern-python:',
    ),
    'continued failure': mutate(
        'continued failure',
        '    steps:',
        '    continue-on-error: true\n    steps:',
    ),
    'skipped Python 2 runtime proof': mutate('skipped Python 2 runtime proof', 'run: python2 --version', 'run: true'),
    'skipped Python 3 runtime proof': mutate('skipped Python 3 runtime proof', 'run: python3 --version', 'run: true'),
    'weakened Python 2 gate': mutate('weakened Python 2 gate', 'run: make check-python2', 'run: make lint-python2'),
    'weakened Python 3 gate': mutate('weakened Python 3 gate', 'run: make check-python3', 'run: make lint-python3'),
}

for description, workflow in mutations.items():
    assert_invalid(description, workflow)

print('workflow contract tests passed (%d mutations rejected).' % len(mutations))
