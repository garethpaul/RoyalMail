# SMTP Primary Error Preservation

Status: Completed

## Context

`RoyalMail.send()` always calls `SMTP.quit()` after delivery, but its `finally`
block allows a cleanup failure to replace an earlier TLS, login, serialization,
or `sendmail` failure. A server that rejects delivery and then fails during
shutdown therefore reports only the less useful shutdown error.

## Requirements

- Always attempt `SMTP.quit()` after the connection is created.
- Preserve and re-raise the primary send-path exception when send and cleanup
  both fail.
- Continue propagating a cleanup exception when the send path succeeded.
- Preserve successful single-message, batch, TLS, login, and unconditional
  cleanup behavior on Python 2.7 and Python 3.12.
- Add mutation-sensitive behavior and static contracts plus completed
  verification evidence.

## Approach

- Capture the active send-path exception before cleanup without changing the
  public API or SMTP call ordering.
- Attempt cleanup in a separate guarded block, suppressing its exception only
  when a primary exception is already pending.
- Re-raise the captured primary exception after cleanup and otherwise leave a
  cleanup-only exception visible.

## Scope Boundaries

- Do not add retries, reconnects, SMTP response translation, logging, or new
  dependencies.
- Do not change message composition, recipient normalization, manager queueing,
  TLS policy, authentication policy, or callback behavior.
- Do not weaken the unconditional cleanup requirement.

## Implementation Units

- `royalmail.py`: preserve the send-path exception across cleanup.
- `tests/test_royalmail.py`: cover dual failure and cleanup-only failure.
- `scripts/check-docs-plans.py`: protect implementation, regression, and plan
  evidence contracts.
- `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`: document exception
  precedence at the SMTP cleanup boundary.

## Verification

- Run focused tests and complete repository-root and external-directory
  `make check` on Python 2.7 and Python 3.12.
- Reject hostile mutations that restore `finally` masking, swallow a
  cleanup-only failure, remove cleanup, or weaken regression/evidence checks.
- Audit the exact diff, bytecode and generated artifacts, credentials,
  conflicts, modes, binaries, dependencies, workflows, and upstream equality.

## Risks

- Re-raising a stored exception must remain syntax-compatible with both
  supported Python lines.
- Cleanup suppression must apply only when a primary send-path exception is
  already pending.

## Work Completed

- Preserved the active send-path exception across an unconditional SMTP cleanup
  attempt without changing successful call ordering.
- Kept cleanup-only exceptions visible while suppressing a competing cleanup
  exception only when a primary failure is pending.
- Added dual-runtime regressions, static contracts, documentation, and plan
  evidence for both exception-precedence branches.

## Verification Results

- 27 tests passed on Python 2.7.18 and Python 3.12.8, including focused dual-
  failure and cleanup-only regressions.
- Eight hostile SMTP exception mutations were rejected across primary capture,
  cleanup-only propagation, unconditional cleanup, source and test contracts,
  guidance, completed status, and exact test evidence.
- The projected final tree repository and external-directory `make check` passed
  with bytecode generation disabled on both supported runtimes.
- Exact diff, artifact, credential, conflict, mode, binary, dependency,
  workflow, and upstream audits passed with only the eight intended paths.
