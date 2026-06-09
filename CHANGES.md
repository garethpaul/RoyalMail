# Changes

## 2026-06-09

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
