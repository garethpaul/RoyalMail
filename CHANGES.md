# Changes

## 2026-06-08

- Added `make check` as the shared repository verification alias.
- Added Python 2 unit tests for manager setup and BCC envelope behavior.
- Fixed `Manager()` default sender construction when no sender instance is
  injected.
- Added `make verify` for syntax checks and tests, plus Python bytecode ignores.
- Added Python 2 coverage for plain text headers, HTML alternative payloads,
  and attachment MIME fallback behavior.
- Added canonical `docs/plans` coverage and a Python 2 docs-plan checker under
  `make check`.
