# RoyalMail Deep Review Remediation

Status: Completed

## Context

The stacked maintenance PRs improved Python 3 compatibility, header and
attachment validation, queue acknowledgement, iterable handling, and SMTP
exception precedence. Evidence-first review of the combined tree found
remaining delivery, cleanup, iterator, and worker-lifecycle failure modes.

## Findings

- `SMTP.sendmail()` partial-refusal dictionaries were ignored, so a message
  rejected for some recipients was reported as fully successful.
- A failed `SMTP.quit()` did not fall back to `SMTP.close()`, leaving the socket
  cleanup dependent on the server completing the QUIT exchange.
- Two-field one-pass attachment descriptors were consumed during failed
  three-field unpacking and then misclassified as filenames.
- Setting `Manager.abort = True` could not wake a worker blocked in `queue.get()`.
- Exceptions raised while advancing a batch iterator terminated the worker,
  hid the failure from `join()`, and stranded later queue items.

## Remediation

- Raise `SMTPRecipientsRefused` with the refusal mapping when any recipient is
  rejected. Some recipients may already have accepted the message, so callers
  must not blindly retry the complete recipient set.
- Preserve delivery, TLS, or authentication failures as primary while using
  `close()` as a best-effort fallback after failed `quit()`.
- Normalize two- and three-field attachment descriptors from one iterator and
  preserve iterator-internal `TypeError` failures.
- Use one idempotent stop sentinel, reject work submitted after stop, continue
  processing queued work after malformed batch iterators, and raise the first
  worker-level failure from `Manager.join()` after shutdown.
- Protect the behavior with fake-SMTP regressions, concurrency tests, and
  dependency-free hostile manager, SMTP, and workflow mutations.

## Provenance

- Partial refusal handling, attachment tuple fallback, and the non-waking abort
  flag were carried forward from the 2012 initial implementation.
- PR #8 made one-pass Manager batches supported but allowed iterator advancement
  failures to escape the worker.
- PR #9 preserved primary SMTP errors but did not close the socket when QUIT
  itself failed.

## Verification

- 35 behavior tests passed on the hosted Python 2.7.18 and Python 3.12.8 lanes.
- 19 workflow mutations, 12 manager mutations, and 8 SMTP mutations were
  rejected on both hosted runtimes.
- Repository-root and external-directory `make check-python3` passed locally on
  Python 3.11; `make check-python3` also passed locally on Python 3.12 with
  unrelated host Blake2 warnings.
- Hosted `make check-python2`, `make check-python3`, and CodeQL passed on the
  reviewed implementation head.
- The repository has no third-party runtime dependency manifest to audit.

## Residual Risk

No live SMTP relay, TLS certificate exchange, authenticated provider, or real
mailbox delivery was exercised. Partial refusal can mean partial delivery
already occurred before the exception is raised. Queue behavior was validated
with local threads and deterministic fakes rather than production workloads.
