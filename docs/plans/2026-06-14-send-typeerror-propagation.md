# Preserve Per-Message Type Errors

## Status: In Progress

## Context

`RoyalMail.send` currently wraps sequence detection and every `_send` call in
one `TypeError` handler. If a message raises `TypeError` during serialization
or dispatch, the handler retries the entire sequence as one message, masking
the original dispatch boundary and invoking `_send` twice.

## Requirements

- Classify the library's `Message` object as a single message before sending.
- Treat other inputs as iterables without catching per-message `TypeError`.
- Preserve one SMTP connection and the existing unconditional `quit()`
  cleanup behavior.
- Propagate the original `TypeError` after exactly one `_send` attempt.
- Preserve Python 2.7 and Python 3.12 behavior for successful single and batch
  sends.
- Add behavior and static mutation-sensitive coverage.

## Scope Boundaries

- Do not change SMTP authentication, TLS, envelope recipient handling,
  attachment validation, Manager queue behavior, or public method names.

## Verification

- focused dual-runtime regression test
- repository and external-directory dual-runtime `make check`
- digest-pinned read-only network-isolated Python 2.7 and Python 3.12 gates
- hostile dispatch classification, retry, test, and completed-plan mutations
- exact diff, bytecode/generated-artifact, and credential-pattern audits
