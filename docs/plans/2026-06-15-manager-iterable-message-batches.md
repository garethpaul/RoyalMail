# Manager Iterable Message Batches

Status: Planned

## Context

`Manager.run` decides whether queued work is one message or a batch by calling
`len(msg)`. One-pass iterables such as generators and list iterators have no
length, so the manager wraps the iterator as a message and then crashes while
reading `message_id`. The current queue item is acknowledged, but the queued
shutdown sentinel remains unfinished and batch messages are never sent.

## Requirements

- Accept one-pass iterable message batches without requiring `len()` or a
  second traversal.
- Preserve single-message, list/tuple batch, callback, result-recording,
  exception, and shutdown-sentinel behavior.
- Consume an iterable batch only once and keep queue completion balanced after
  the batch and sentinel are processed.
- Cover the behavior on supported Python 2.7 and Python 3.12 lanes.

## Approach

- Detect the library's `Message` type as a single item; otherwise ask Python
  for an iterator and fall back to a one-item tuple only for non-iterables.
- Iterate the resulting object directly so generators are not materialized or
  consumed twice.
- Add focused manager tests for generator delivery, callbacks, result records,
  and zero unfinished queue tasks.

## Scope Boundaries

- Do not redesign manager threading, callbacks, result storage, SMTP behavior,
  recipient normalization, or shutdown signaling.
- Do not add dependencies or remove Python 2 compatibility.
- Do not swallow exceptions raised while advancing a malformed batch iterator.

## Verification

- Run the focused tests and complete Make gate on Python 2.7 and Python 3.12
  from repository and external working directories.
- Reject hostile mutations that restore `len(msg)` classification or remove the
  iterable-batch queue-completion assertions.
- Audit the exact diff, bytecode, generated artifacts, credentials, conflicts,
  modes, binaries, large files, and upstream head.

## Risks

- Strings and arbitrary iterables are not valid message batches; failures should
  remain visible rather than being silently reinterpreted as mail messages.

## Implementation Units

- `royalmail.py`: classify one message versus an iterable batch without length
  probing or repeated consumption.
- `tests/test_royalmail.py`: prove generator delivery, callbacks, results, and
  queue completion.
- `scripts/check-docs-plans.py`: protect the implementation and regression.
- `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`: document the manager
  iterable boundary.
