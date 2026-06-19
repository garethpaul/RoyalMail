# Preserve Per-Message Type Errors

## Status: Completed

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

## Verification Results

- The focused regression and complete 23-test suite passed on host Python 2.7.18 and Python 3.12.8.
- The repository and external-directory `make check` passed after this
  completed status was recorded.
- Seven hostile dispatch mutations were rejected across the broad retry,
  message classification, single-message wrapping, loop argument, static
  implementation contract, regression assertion, and completed-plan status.
- Digest-pinned, read-only, network-isolated Python 2.7.18 and Python 3.12.8
  containers each passed their canonical runtime gate with 23 behavior tests,
  19 workflow mutations, and 7 manager mutations.
- Final exact-diff, bytecode/generated-artifact, and credential-pattern audits
  found only the intended source, test, checker, and completed-plan changes.
