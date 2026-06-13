#!/usr/bin/env python2
from __future__ import print_function

import os

from manager_contract import validate


BASELINE = '''        while self.abort is False:
            msg = self.queue.get(block=True)
            try:
                if msg is None:
                    break

                process(msg)
            finally:
                self.queue.task_done()
'''


def mutate(description, target, replacement):
    mutated = BASELINE.replace(target, replacement, 1)
    if mutated == BASELINE:
        raise AssertionError('%s mutation did not alter the fixture' % description)
    return mutated


def assert_invalid(description, source):
    if not validate(source):
        raise AssertionError('%s mutation was accepted' % description)


if validate(BASELINE):
    raise AssertionError('baseline manager loop is invalid: %s' % ', '.join(validate(BASELINE)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, 'royalmail.py'), 'r') as source_file:
    implementation_failures = validate(source_file.read())
if implementation_failures:
    raise AssertionError(
        'manager implementation is invalid: %s' % ', '.join(implementation_failures)
    )

mutations = {
    'missing protected block': mutate('missing protected block', '            try:\n', ''),
    'truthy sentinel check': mutate('truthy sentinel check', 'if msg is None:', 'if msg:'),
    'continued sentinel': mutate('continued sentinel', '                    break', '                    continue'),
    'missing acknowledgement': mutate(
        'missing acknowledgement',
        '            finally:\n                self.queue.task_done()\n',
        '',
    ),
    'unprotected acknowledgement': mutate(
        'unprotected acknowledgement',
        '            finally:\n                self.queue.task_done()',
        '            self.queue.task_done()',
    ),
    'duplicate acknowledgement': mutate(
        'duplicate acknowledgement',
        '                self.queue.task_done()',
        '                self.queue.task_done()\n                self.queue.task_done()',
    ),
    'acknowledgement before sentinel': mutate(
        'acknowledgement before sentinel',
        '            finally:\n                self.queue.task_done()\n',
        '',
    ).replace(
        '            try:\n',
        '            finally:\n                self.queue.task_done()\n            try:\n',
        1,
    ),
}

for description, source in mutations.items():
    assert_invalid(description, source)

print('manager contract tests passed (%d mutations rejected).' % len(mutations))
