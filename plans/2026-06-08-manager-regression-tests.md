# Manager Regression Tests

## Problem

`Manager()` is supposed to create a default `RoyalMail` sender from keyword
arguments when no sender instance is injected. The constructor parameter named
`RoyalMail` shadowed the class, so the default path attempted to call `None`.

## TDD Evidence

1. Added Python 2 unit tests for default manager sender creation and BCC
   envelope-only behavior.
2. Ran `make test` before the source fix and confirmed
   `test_manager_creates_default_sender_from_kwargs` failed with
   `TypeError: 'NoneType' object is not callable`.
3. Fixed default sender construction while preserving the existing injection
   keyword, then reran the verification gate.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `git diff --check`
