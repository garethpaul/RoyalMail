#!/usr/bin/env python2
from __future__ import print_function

import os

from manager_contract import validate


BASELINE = '''    def __init__(self, **kwargs):
        self.RoyalMail = RoyalMail(
            timeout=kwargs.get('timeout', None),
        )

    def _request_stop(self):
        with self._state_lock:
            if self._stop_enqueued:
                return
            self._abort = True
            self._stop_enqueued = True
            self.queue.put(None)

    def run(self):
        while True:
            msg = self.queue.get(block=True)
            try:
                if msg is None:
                    self._stop_enqueued = True
                    break

                try:
                    process(msg)
                except Exception as error:
                    self._record_worker_error(error)
            finally:
                self.queue.task_done()

    def send(self, msg):
        if msg is None:
            self._request_stop()
            return
        with self._state_lock:
            if self._abort:
                raise RuntimeError('Manager has been stopped')
            self.queue.put(msg)

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)
        if self.is_alive():
            return
        worker_error = self._worker_error
        if worker_error is not None:
            raise worker_error
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
    'timeout forwarding removed': mutate(
        'timeout forwarding removed',
        "            timeout=kwargs.get('timeout', None),\n",
        '',
    ),
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
    'duplicate stop sentinel': mutate(
        'duplicate stop sentinel',
        '            if self._stop_enqueued:\n                return\n',
        '',
    ),
    'missing stop sentinel': mutate(
        'missing stop sentinel',
        '            self.queue.put(None)\n',
        '',
    ),
    'swallowed batch iterator failure': mutate(
        'swallowed batch iterator failure',
        '                    self._record_worker_error(error)',
        '                    pass',
    ),
    'send after stop accepted': mutate(
        'send after stop accepted',
        "            if self._abort:\n                raise RuntimeError('Manager has been stopped')\n",
        '',
    ),
    'worker error hidden from join': mutate(
        'worker error hidden from join',
        '            raise worker_error',
        '            return',
    ),
}

for description, source in mutations.items():
    assert_invalid(description, source)

print('manager contract tests passed (%d mutations rejected).' % len(mutations))
