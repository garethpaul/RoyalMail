# Manager Sentinel Queue Completion

## Status: Completed

## Context

`Manager.run()` removes a `None` shutdown sentinel from its queue and exits
before calling `task_done()`. Callers that use the standard `Queue.join()`
completion contract can therefore remain blocked after the manager has stopped,
even though no queued work remains.

## Priority

Queue accounting is part of the manager's public background-delivery behavior.
Every successful `get()` must have one matching `task_done()` call, including
the shutdown marker, while message results and callbacks retain their current
ordering and error handling.

## Objectives

- Acknowledge the shutdown sentinel before leaving the manager loop.
- Preserve exactly one acknowledgement for each normal queue item.
- Keep message sending, result recording, and callback behavior unchanged.
- Add deterministic Python 2 and Python 3 regression coverage without sleeps
  or timing-dependent thread assertions.
- Protect the behavior with a focused mutation-sensitive static contract.

## Implementation Units

### U1. Characterize queue completion

**Goal:** Prove the queue's unfinished-task count reaches zero for both a
normal message and the shutdown sentinel.

**Files:** `tests/test_royalmail.py`

**Approach:** Exercise `Manager.run()` synchronously with queued inputs so the
test observes queue accounting directly and does not depend on scheduler timing.

**Test scenarios:**

- A sentinel-only queue exits with no unfinished tasks.
- A successfully sent message followed by a sentinel records success, invokes
  the callback, and leaves no unfinished tasks.

**Verification:** The regression fails if either dequeued item lacks its
matching acknowledgement or if a normal item is acknowledged twice.

### U2. Balance manager queue acknowledgements

**Goal:** Match every queue `get()` with exactly one `task_done()` call.

**Dependencies:** U1

**Files:** `royalmail.py`, `tests/test_royalmail.py`

**Approach:** Move acknowledgement into a per-dequeue `finally` boundary so
normal completion, sender failures, callback failures, and the sentinel all
share the same accounting guarantee.

**Patterns to follow:** Preserve the existing result tuple and callback
ordering in `Manager.run()`.

**Test scenarios:** Existing success and exception-result tests remain green;
the new completion cases pass on both supported runtimes.

**Verification:** Focused tests and the complete repository gate pass on Python
2.7 and Python 3.12.

### U3. Record the maintenance contract

**Goal:** Keep verification documentation synchronized with the reliability
behavior.

**Dependencies:** U1, U2

**Files:** `README.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-13-manager-sentinel-queue-completion.md`

**Approach:** Document balanced queue completion and record actual validation
only after implementation succeeds.

**Test expectation:** Documentation contracts require the completed plan and
canonical `make check` evidence.

**Verification:** Documentation validation rejects a missing completion claim
or missing canonical verification command.

## Scope Boundary

This change does not add cancellation APIs, alter daemon-thread behavior,
change callback signatures, or redesign queue batching.

## Work Completed

- Moved queue acknowledgement into a per-dequeue `finally` boundary.
- Acknowledged the `None` shutdown sentinel before the manager exits.
- Added deterministic success, sender-failure, and sentinel queue-accounting
  assertions without starting background threads or using sleeps.
- Added a Python 2/3 static manager contract that validates the implementation
  and rejects seven acknowledgement and sentinel-control-flow mutations.
- Added the manager contract to both canonical runtime gates and protected its
  Makefile commands through documentation validation.
- Synchronized README, vision, and change-history documentation.

## Verification

- Focused manager completion tests passed on Python 2 and Python 3.
- The static manager contract passed on Python 2 and Python 3 with all seven
  hostile mutations rejected.
- `make check` passed documentation, syntax, 19 workflow mutations, 7 manager
  mutations, and all 22 behavior tests on both Python 2 and Python 3.
- Digest-pinned, read-only, network-isolated Python 2.7.18 and Python 3.12.8
  containers passed their complete runtime gates with the same test counts.
- `git diff --check` is required before shipping.
