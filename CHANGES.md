# Changes

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
