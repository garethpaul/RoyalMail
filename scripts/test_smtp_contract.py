#!/usr/bin/env python2
from __future__ import print_function

import os

from smtp_contract import validate


BASELINE = '''    def send(self, msg):
        if self.timeout is None:
            server = smtplib.SMTP(self.host, self.port)
        else:
            server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)

        if self.tls_context is None:
            server.starttls()
        elif sys.version_info[0] < 3:
            raise RuntimeError('TLS contexts require Python 3 smtplib support')
        else:
            server.starttls(context=self.tls_context)

        delivery_error = None
        try:
            deliver(msg)
        except BaseException as error:
            delivery_error = error

        cleanup_error = None
        try:
            server.quit()
        except BaseException as error:
            cleanup_error = error
            try:
                server.close()
            except BaseException:
                pass

        if delivery_error is not None:
            raise delivery_error
        if cleanup_error is not None:
            raise cleanup_error

    def _send(self, server, msg):
        refused = server.sendmail(me, you, msg.as_string())
        if refused:
            raise smtplib.SMTPRecipientsRefused(refused)

class Message(object):
    pass
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
    raise AssertionError('baseline SMTP contract is invalid: %s' % ', '.join(validate(BASELINE)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, 'royalmail.py'), 'r') as source_file:
    implementation_failures = validate(source_file.read())
if implementation_failures:
    raise AssertionError(
        'SMTP implementation is invalid: %s' % ', '.join(implementation_failures)
    )

mutations = {
    'timeout forwarding removed': mutate(
        'timeout forwarding removed',
        '            server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)\n',
        '            server = smtplib.SMTP(self.host, self.port)\n',
    ),
    'legacy no-timeout call removed': mutate(
        'legacy no-timeout call removed',
        '            server = smtplib.SMTP(self.host, self.port)\n',
        '            server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)\n',
    ),
    'legacy TLS removed': mutate(
        'legacy TLS removed',
        '            server.starttls()\n',
        '',
    ),
    'context forwarding removed': mutate(
        'context forwarding removed',
        '            server.starttls(context=self.tls_context)\n',
        '',
    ),
    'context silently downgraded': mutate(
        'context silently downgraded',
        '            server.starttls(context=self.tls_context)\n',
        '            server.starttls()\n',
    ),
    'legacy runtime rejection removed': mutate(
        'legacy runtime rejection removed',
        "            raise RuntimeError('TLS contexts require Python 3 smtplib support')\n",
        '',
    ),
    'missing delivery capture': mutate(
        'missing delivery capture',
        '            delivery_error = error\n',
        '',
    ),
    'missing quit': mutate('missing quit', '            server.quit()\n', ''),
    'missing close fallback': mutate('missing close fallback', '                server.close()\n', ''),
    'cleanup masks delivery': mutate(
        'cleanup masks delivery',
        '        if delivery_error is not None:\n            raise delivery_error\n',
        '',
    ),
    'cleanup failure hidden': mutate(
        'cleanup failure hidden',
        '        if cleanup_error is not None:\n            raise cleanup_error\n',
        '',
    ),
    'refusal result ignored': mutate(
        'refusal result ignored',
        '        if refused:\n            raise smtplib.SMTPRecipientsRefused(refused)\n',
        '',
    ),
    'wrong refusal exception': mutate(
        'wrong refusal exception',
        'raise smtplib.SMTPRecipientsRefused(refused)',
        'raise RuntimeError(refused)',
    ),
    'close before quit': mutate(
        'close before quit',
        '            server.quit()\n',
        '            server.close()\n',
    ),
}

for description, source in mutations.items():
    assert_invalid(description, source)

print('SMTP contract tests passed (%d mutations rejected).' % len(mutations))
