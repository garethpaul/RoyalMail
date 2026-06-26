# Changes

## 2026-06-26 10:04:57 PDT

- Priority: reliability / bounded network setup.
- Added an optional SMTP connection timeout and forwarded it through `Manager`
  while preserving the exact legacy constructor call when omitted.
- Files: `royalmail.py`, `tests/test_royalmail.py`, SMTP and Manager contract
  harnesses, `docs/plans/2026-06-26-smtp-connect-timeout.md`, and synchronized
  repository guidance.
- Tests: 38 behavior tests pass on pinned Python 2.7.18 and Python 3.12.8;
  19 workflow, 13 Manager, and 14 SMTP hostile mutations are rejected on both
  runtimes; root and absolute external `make check` pass with 165 Make
  authority cases. Hosted Python 2.7/3.12 and CodeQL for Actions and Python
  pass on implementation commit `74b3185`.
- Findings: no open pull requests or issues overlap this change.
- Blockers: Codex review authentication may be unavailable and will be skipped
  after one HTTP 401 attempt.
- Next action: push the completed evidence contract and merge only its exact
  hosted-green head.

## 2026-06-26

- Added optional caller-supplied TLS context forwarding for authenticated
  Python 3 STARTTLS without changing the legacy no-context call path.
- Rejected TLS context requests clearly on Python 2, whose `smtplib` cannot
  consume an `SSLContext`, while preserving SMTP cleanup and Manager forwarding.
- Documented that default STARTTLS encrypts the connection but does not create
  a RoyalMail-controlled certificate-verification policy.

## 2026-06-21

- Made every Make quality gate safe for spaced and shell-sensitive checkout
  paths and rejected caller-controlled root, Python, shell, preload, and
  Makefile-list authority without changing RoyalMail behavior.
- Removed platform-specific root helpers and rejected extra Makefiles in either
  `-f` ordering before repository checks run.

## 2026-06-19

- Surfaced partial SMTP recipient refusals and added direct socket cleanup when
  SMTP `quit()` fails without masking delivery, TLS, or authentication errors.
- Preserved two-field one-pass attachment descriptors and their internal
  `TypeError` failures.
- Made Manager stop signaling idempotent, woke blocked workers, rejected work
  after stop, drained later queue items after batch iterator failures, and
  surfaced worker failures from `join()`.
- Added 35 cross-runtime behavior tests plus 12 manager, 8 SMTP, and 19 workflow
  hostile mutations.

## 2026-06-17

- Preserved the primary SMTP failure when delivery and connection cleanup both
  fail, while continuing to expose cleanup-only failures.

## 2026-06-15

- Accepted one-pass iterable message batches in `Manager` while preserving
  delivery order, callbacks, result records, and balanced queue completion.

## 2026-06-14

- Preserved `To` and `CC` headers when one-shot recipient iterables are used,
  while keeping iterator-backed BCC recipients envelope-only.

## 2026-06-13

- Balanced `Manager` queue acknowledgements for normal work, failed sends, and
  the shutdown sentinel, with deterministic cross-runtime and mutation tests.
- Restricted caller-supplied attachment identifiers to ASCII Content-ID tokens
  before file reads, preserving common dot-atom and `name@domain` values.

## 2026-06-12

- Added Python 3.12 compatibility without dropping Python 2.7, running the same
  18 message, attachment, SMTP, and manager tests in both digest-pinned GitHub
  Actions containers.
- Restricted explicit attachment maintypes and subtypes to ASCII MIME type
  tokens before MIME construction or file reads, with Python 2 regression and
  checker coverage.

## 2026-06-10

- Rejected newline characters in attachment filenames before file reads or
  `Content-Disposition` header serialization, with Python 2 regression coverage.
- Added a least-privilege GitHub Actions workflow that runs `make check` on
  pushes, pull requests, and manual dispatches with credential-free checkout
  pinned by commit.
- Replaced the prepared skip-based job with full syntax, contract, and unit-test
  validation in a digest-pinned Python 2.7.18 container.
- Made `make check` root-independent and fail when Python 2 is unavailable.
- Added exact workflow-policy validation and 15 hostile mutations covering
  triggers, credentials, actions, permissions, runner, timeout, image digest,
  failure handling, runtime proof, and the canonical command.

## 2026-06-09

- Kept Python verification bytecode-free and added checker coverage to reject
  generated `.pyc` and `.pyo` files.
- Started TLS whenever `use_tls=True`, including unauthenticated SMTP sends,
  with Python 2 regression coverage.
- Rejected malformed or newline-bearing explicit attachment mimetypes before
  MIME construction, with Python 2 regression coverage.
- Accepted constructor-supplied `(filename, cid, mimetype)` attachment tuples
  and added Python 2 regression coverage.
- Closed attachment file handles before MIME construction can fail and added a
  Python 2 regression test for the cleanup path.
- Rejected newline characters in attachment Content-ID values before MIME header
  serialization, with Python 2 regression coverage.
- Fixed `Manager.run()` so no-argument sender exceptions are recorded as
  failed message results instead of crashing the manager error handler.
- Added newline validation for message headers and SMTP envelope addresses to
  prevent header or recipient injection, with Python 2 regression coverage.

## 2026-06-08

- Ensured SMTP connections are quit when sending or login fails, with Python 2
  regression coverage.
- Added `make check` as the shared repository verification alias.
- Added Python 2 unit tests for manager setup and BCC envelope behavior.
- Fixed `Manager()` default sender construction when no sender instance is
  injected.
- Added `make verify` for syntax checks and tests, plus Python bytecode ignores.
- Added Python 2 coverage for plain text headers, HTML alternative payloads,
  and attachment MIME fallback behavior.
- Added canonical `docs/plans` coverage and a Python 2 docs-plan checker under
  `make check`.
