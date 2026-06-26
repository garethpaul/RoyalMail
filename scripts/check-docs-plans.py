#!/usr/bin/env python2
from __future__ import print_function

import glob
import os
import re
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
MAKE_ROOT_PLAN = os.path.join(DOCS_PLANS, '2026-06-14-make-root-override-protection.md')
SAFE_MAKE_AUTHORITY_PLAN = os.path.join(DOCS_PLANS, '2026-06-21-safe-make-authority.md')
SEND_TYPEERROR_PLAN = os.path.join(DOCS_PLANS, '2026-06-14-send-typeerror-propagation.md')
RECIPIENT_ITERATOR_PLAN = os.path.join(
    DOCS_PLANS, '2026-06-14-recipient-iterator-header-preservation.md')
MANAGER_ITERABLE_PLAN = os.path.join(
    DOCS_PLANS, '2026-06-15-manager-iterable-message-batches.md')
SMTP_PRIMARY_ERROR_PLAN = os.path.join(
    DOCS_PLANS, '2026-06-17-smtp-primary-error-preservation.md')
DEEP_REVIEW_PLAN = os.path.join(
    DOCS_PLANS, '2026-06-19-royalmail-deep-review.md')
VERIFIED_TLS_PLAN = os.path.join(
    DOCS_PLANS, '2026-06-26-verified-tls-context.md')
CI_WORKFLOW = os.path.join(ROOT, '.github', 'workflows', 'check.yml')
MAKEFILE = os.path.join(ROOT, 'Makefile')
README = os.path.join(ROOT, 'README.md')
ROYALMAIL_SOURCE = os.path.join(ROOT, 'royalmail.py')
ROYALMAIL_TESTS = os.path.join(ROOT, 'tests', 'test_royalmail.py')
MANAGER_CONTRACT = os.path.join(ROOT, 'scripts', 'manager_contract.py')
MANAGER_CONTRACT_TEST = os.path.join(ROOT, 'scripts', 'test_manager_contract.py')
SMTP_CONTRACT = os.path.join(ROOT, 'scripts', 'smtp_contract.py')
SMTP_CONTRACT_TEST = os.path.join(ROOT, 'scripts', 'test_smtp_contract.py')


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
        MAKE_ROOT_PLAN,
        SAFE_MAKE_AUTHORITY_PLAN,
        SEND_TYPEERROR_PLAN,
        RECIPIENT_ITERATOR_PLAN,
        MANAGER_ITERABLE_PLAN,
        SMTP_PRIMARY_ERROR_PLAN,
        DEEP_REVIEW_PLAN,
        VERIFIED_TLS_PLAN,
        CI_WORKFLOW,
        README,
        ROYALMAIL_SOURCE,
        ROYALMAIL_TESTS,
        MANAGER_CONTRACT,
        MANAGER_CONTRACT_TEST,
        SMTP_CONTRACT,
        SMTP_CONTRACT_TEST):
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
        'override SHELL := /bin/sh',
        'override .SHELLFLAGS := -c',
        'override PYTHON2 := python2',
        'override PYTHON3 := python3',
        'ifneq ($(strip $(MAKEFILES)),)',
        '$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)',
        'ifneq ($(origin MAKEFILE_LIST),file)',
        '$(error MAKEFILE_LIST must not be overridden)',
        'override REPOSITORY_MAKEFILE := $(value MAKEFILE_LIST)',
        'override CURRENT_MAKEFILE_LIST = $(value MAKEFILE_LIST)',
        'multiple -f Makefiles are not supported',
        'makefile=$${REPOSITORY_MAKEFILE# }',
        'override define RUN_IN_REPO',
        '$(RUN_IN_REPO) $(PYTHON2) -B scripts/check-docs-plans.py',
        '$(RUN_IN_REPO) $(PYTHON3) -B scripts/check-docs-plans.py',
        '$(RUN_IN_REPO) $(PYTHON2) -B scripts/test_workflow_contract.py',
        '$(RUN_IN_REPO) $(PYTHON3) -B scripts/test_workflow_contract.py',
        '$(RUN_IN_REPO) $(PYTHON2) -B scripts/test_manager_contract.py',
        '$(RUN_IN_REPO) $(PYTHON3) -B scripts/test_manager_contract.py',
        '$(RUN_IN_REPO) $(PYTHON2) -B scripts/test_smtp_contract.py',
        '$(RUN_IN_REPO) $(PYTHON3) -B scripts/test_smtp_contract.py',
        '$(PYTHON2) -B -m unittest discover -s tests',
        '$(PYTHON3) -B -m unittest discover -s tests',
        '$(RUN_IN_REPO) /bin/sh scripts/test-makefile-root.sh',
        'verify: root-test check-python2 check-python3',
    )
    for phrase in required_makefile_phrases:
        if phrase not in makefile:
            failures.append('Makefile must contain %s' % phrase)

    if 'command -v "$(PYTHON' in makefile or 'Skipping legacy Python 2' in makefile or 'Skipping Python 3' in makefile:
        failures.append('Makefile must require both runtime gates instead of skipping them')

    root_test_path = os.path.join(ROOT, 'scripts', 'test-makefile-root.sh')
    if os.path.isfile(root_test_path):
        root_test = read(root_test_path)
        for phrase in (
                '165 executed target/authority cases',
                '2 MAKEFILE_LIST rejections',
                '1 MAKEFILES rejection',
                '2 multi-Makefile rejections'):
            if phrase not in root_test:
                failures.append('Makefile root test must contain %s' % phrase)
    else:
        failures.append('scripts/test-makefile-root.sh is missing')

if os.path.isfile(MAKE_ROOT_PLAN):
    make_root_plan = read(MAKE_ROOT_PLAN)
    for evidence in (
            'Status: Completed',
            '`make ROOT=/tmp check` passed',
            'Python 2.7.18 and Python 3.12.8',
            'Six hostile mutations were rejected'):
        if evidence not in make_root_plan:
            failures.append('%s must record verification evidence %s' % (rel(MAKE_ROOT_PLAN), evidence))
    if os.path.isfile(README) and rel(MAKE_ROOT_PLAN) not in read(README):
        failures.append('README.md must reference %s' % rel(MAKE_ROOT_PLAN))

if os.path.isfile(SAFE_MAKE_AUTHORITY_PLAN):
    safe_make_authority_plan = read(SAFE_MAKE_AUTHORITY_PLAN)
    for evidence in (
            '165 executed target, root, shell, and dual-Python authority cases',
            'Both `MAKEFILE_LIST` override channels',
            '`MAKEFILES` preload',
            'both `-f` orderings failed closed'):
        if evidence not in safe_make_authority_plan:
            failures.append('%s must record verification evidence %s' % (
                rel(SAFE_MAKE_AUTHORITY_PLAN), evidence))
    if os.path.isfile(README) and rel(SAFE_MAKE_AUTHORITY_PLAN) not in read(README):
        failures.append('README.md must reference %s' % rel(SAFE_MAKE_AUTHORITY_PLAN))

if os.path.isfile(SEND_TYPEERROR_PLAN):
    send_typeerror_plan = read(SEND_TYPEERROR_PLAN)
    for evidence in (
            'Status: Completed',
            'Python 2.7.18 and Python 3.12.8',
            'hostile dispatch mutations were rejected',
            'repository and external-directory `make check` passed'):
        if evidence not in send_typeerror_plan:
            failures.append('%s must record verification evidence %s' % (
                rel(SEND_TYPEERROR_PLAN), evidence))
    if os.path.isfile(README) and rel(SEND_TYPEERROR_PLAN) not in read(README):
        failures.append('README.md must reference %s' % rel(SEND_TYPEERROR_PLAN))

if os.path.isfile(RECIPIENT_ITERATOR_PLAN):
    recipient_iterator_plan = read(RECIPIENT_ITERATOR_PLAN)
    for evidence in (
            'Status: Completed',
            'Python 2.7.18 and Python 3.12.8',
            'hostile recipient mutations were rejected',
            'repository and external-directory `make check` passed'):
        if evidence not in recipient_iterator_plan:
            failures.append('%s must record verification evidence %s' % (
                rel(RECIPIENT_ITERATOR_PLAN), evidence))
    if os.path.isfile(README) and rel(RECIPIENT_ITERATOR_PLAN) not in read(README):
        failures.append('README.md must reference %s' % rel(RECIPIENT_ITERATOR_PLAN))

if os.path.isfile(MANAGER_ITERABLE_PLAN):
    manager_iterable_plan = read(MANAGER_ITERABLE_PLAN)
    for evidence in (
            'Status: Completed',
            'Python 2.7.18 and Python 3.12.8',
            'hostile manager iterable mutations were rejected',
            'repository and external-directory `make check` passed'):
        if evidence not in manager_iterable_plan:
            failures.append('%s must record verification evidence %s' % (
                rel(MANAGER_ITERABLE_PLAN), evidence))
    if os.path.isfile(README) and rel(MANAGER_ITERABLE_PLAN) not in read(README):
        failures.append('README.md must reference %s' % rel(MANAGER_ITERABLE_PLAN))

if os.path.isfile(SMTP_PRIMARY_ERROR_PLAN):
    smtp_primary_error_plan = read(SMTP_PRIMARY_ERROR_PLAN)
    for evidence in (
            'Status: Completed',
            '27 tests passed on Python 2.7.18 and Python 3.12.8',
            'hostile SMTP exception mutations were rejected',
            'repository and external-directory `make check` passed',
            'Exact diff'):
        if evidence not in smtp_primary_error_plan:
            failures.append('%s must record verification evidence %s' % (
                rel(SMTP_PRIMARY_ERROR_PLAN), evidence))
    if os.path.isfile(README) and rel(SMTP_PRIMARY_ERROR_PLAN) not in read(README):
        failures.append('README.md must reference %s' % rel(SMTP_PRIMARY_ERROR_PLAN))

if os.path.isfile(DEEP_REVIEW_PLAN):
    deep_review_plan = read(DEEP_REVIEW_PLAN)
    for evidence in (
            'Status: Completed',
            '35 behavior tests',
            '12 manager mutations',
            '8 SMTP mutations',
            'Python 2.7.18 and Python 3.12.8',
            'No live SMTP',
            '`make check-python2`',
            '`make check-python3`'):
        if evidence not in deep_review_plan:
            failures.append('%s must record verification evidence %s' % (
                rel(DEEP_REVIEW_PLAN), evidence))
    if os.path.isfile(README) and rel(DEEP_REVIEW_PLAN) not in read(README):
        failures.append('README.md must reference %s' % rel(DEEP_REVIEW_PLAN))

if os.path.isfile(ROYALMAIL_SOURCE):
    source = read(ROYALMAIL_SOURCE)
    send_start = source.find('    def send(self, msg):')
    send_end = source.find('    def _send(self, server, msg):', send_start)
    send_source = source[send_start:send_end]
    for fragment in (
            'if isinstance(msg, Message):',
            'messages = (msg,)',
            'messages = msg',
            'for message in messages:',
            'self._send(server, message)'):
        if fragment not in send_source:
            failures.append('RoyalMail.send must contain %s' % fragment)
    if 'except TypeError' in send_source:
        failures.append('RoyalMail.send must not catch per-message TypeError')
    for fragment in (
            'if self.tls_context is None:',
            'server.starttls()',
            'elif sys.version_info[0] < 3:',
            "raise RuntimeError('TLS contexts require Python 3 smtplib support')",
            'server.starttls(context=self.tls_context)',
            'delivery_error = None',
            'except BaseException as error:',
            'delivery_error = error',
            'cleanup_error = None',
            'cleanup_error = error',
            'server.close()',
            'if delivery_error is not None:',
            'raise delivery_error',
            'if cleanup_error is not None:',
            'raise cleanup_error'):
        if fragment not in send_source:
            failures.append('RoyalMail.send must preserve primary failures with %s' % fragment)
    if send_source.count('server.quit()') != 1:
        failures.append('RoyalMail.send must attempt SMTP cleanup exactly once')
    if send_source.count('server.close()') != 1:
        failures.append('RoyalMail.send must fall back to direct SMTP close exactly once')

    single_send_start = source.find('    def _send(self, server, msg):')
    single_send_end = source.find('class Message(object):', single_send_start)
    single_send_source = source[single_send_start:single_send_end]
    for fragment in (
            'refused = server.sendmail(me, you, msg.as_string())',
            'if refused:',
            'raise smtplib.SMTPRecipientsRefused(refused)'):
        if fragment not in single_send_source:
            failures.append('RoyalMail._send must surface partial recipient refusal with %s' % fragment)

if os.path.isfile(ROYALMAIL_TESTS):
    tests = read(ROYALMAIL_TESTS)
    for fragment in (
            'test_batch_send_propagates_message_typeerror_without_retrying_list',
            "self.assertEqual([message], sender.attempted_messages)",
            "self.assertEqual('quit', TrackingSMTP.instances[0].calls[-1])",
            'test_send_preserves_primary_failure_when_quit_also_fails',
            "self.assertEqual('smtp send failed', str(raised.exception))",
            'test_send_propagates_quit_failure_after_successful_delivery',
            "self.assertEqual('smtp quit failed', str(raised.exception))",
            'self.assertTrue(FailingQuitSMTP.instances[0].quit_called)',
            'self.assertTrue(FailingQuitSMTP.instances[0].close_called)',
            'test_send_rejects_partial_recipient_refusal',
            'SMTPRecipientsRefused',
            'test_use_tls_forwards_caller_context_on_python3',
            'test_use_tls_rejects_context_on_python2_and_quits',
            'test_send_forwards_explicit_smtp_timeout',
            'self.assertEqual(12.5, manager.RoyalMail.timeout)',
            "self.assertIs(tls_context, manager.RoyalMail.tls_context)"):
        if fragment not in tests:
            failures.append('tests/test_royalmail.py must contain %s' % fragment)

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
    if 'primary SMTP failure' not in docs:
        failures.append('%s must document primary SMTP failure preservation' % docs_file)
    if 'TLS context' not in docs:
        failures.append('%s must document explicit TLS context behavior' % docs_file)
    if 'SMTP connection timeout' not in docs:
        failures.append('%s must document optional SMTP connection timeout behavior' % docs_file)

if os.path.isfile(ROYALMAIL_SOURCE):
    royalmail_source = read(ROYALMAIL_SOURCE)
    required_source_fragments = (
        '                 tls_context=None, timeout=None):',
        '        self.tls_context = tls_context',
        '        self.timeout = timeout',
        '            server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)',
        "                tls_context=kwargs.get('tls_context', None),",
        "                timeout=kwargs.get('timeout', None),",
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
        '            finally:\n                self.queue.task_done()',
        '                if isinstance(msg, Message):',
        '                        messages = iter(msg)',
        '                    for message in messages:',
        '                        self._send_message(message)',
        '            msg.To = to',
        '                msg.CC = cc',
        '                msg.BCC = bcc',
    )
    for fragment in required_source_fragments:
        if fragment not in royalmail_source:
            failures.append('royalmail.py must contain %s' % fragment)

    manager_run_start = royalmail_source.find('    def run(self):')
    manager_run_end = royalmail_source.find('    def send(self, msg):', manager_run_start)
    manager_run_source = royalmail_source[manager_run_start:manager_run_end]
    if 'len(msg)' in manager_run_source:
        failures.append('Manager.run must not classify queued batches with len(msg)')

if os.path.isfile(ROYALMAIL_TESTS):
    royalmail_tests = read(ROYALMAIL_TESTS)
    for fragment in (
            'test_attachment_accepts_vendor_mimetype_tokens',
            'application/vnd.example+json',
            'text/plain; charset=utf-8',
            'text/pl\\xffain',
            'test_attachment_accepts_ascii_msg_id_content_id',
            'test_rejects_malformed_attachment_content_ids_before_file_read',
            'test_unicode_subject_uses_declared_charset',
            'test_manager_acknowledges_shutdown_sentinel',
            'test_manager_acknowledges_message_and_shutdown_sentinel',
            'self.assertEqual(0, manager.queue.unfinished_tasks)',
            'test_manager_abort_wakes_blocked_worker_and_balances_sentinel',
            'test_manager_reports_batch_iterator_failure_after_finishing_queue',
            'test_constructor_consumes_one_pass_attachment_descriptor_once',
            'test_send_preserves_iterator_recipients_in_headers_and_envelope',
            "self.assertIsNone(parsed['BCC'])",
            "self.assertEqual(['bcc@example.com'], message.BCC)"):
        if fragment not in royalmail_tests:
            failures.append('tests/test_royalmail.py must contain %s' % fragment)

    iterable_test_name = '    def test_manager_sends_one_pass_iterable_batch_and_acknowledges_queue(self):'
    iterable_test_start = royalmail_tests.find(iterable_test_name)
    iterable_test_end = royalmail_tests.find('\n    def ', iterable_test_start + len(iterable_test_name))
    if iterable_test_end < 0:
        iterable_test_end = royalmail_tests.find("\n\nif __name__ == '__main__':", iterable_test_start)
    iterable_test = royalmail_tests[iterable_test_start:iterable_test_end]
    for fragment in (
            iterable_test_name,
            'manager.queue.put(iter(messages))',
            'self.assertEqual(messages, sender.messages)',
            '[manager.results[message.message_id] for message in messages]',
            '[message.message_id for message in messages]',
            'self.assertEqual(0, manager.queue.unfinished_tasks)'):
        if fragment not in iterable_test:
            failures.append('iterable Manager regression must contain %s' % fragment.strip())

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
