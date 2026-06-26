# SMTP Connect Timeout

Status: Completed

## Goal

Allow callers to bound SMTP connection setup without changing the legacy
constructor call when no timeout is configured.

## Problem

`RoyalMail.send()` currently constructs `smtplib.SMTP(host, port)` with no
timeout. Python documents the optional SMTP timeout as the bound for blocking
operations such as connection attempts; without one, behavior falls back to
the process-wide socket default and can block a caller indefinitely.

## Design

1. Add a regression proving an explicit timeout reaches `smtplib.SMTP`.
2. Store an optional constructor timeout on `RoyalMail`.
3. Preserve the exact two-positional-argument SMTP call when timeout is `None`.
4. Forward `timeout=` only when the caller opts in.
5. Verify Python 2.7 and Python 3.12 behavior, hostile mutations, and hosted
   workflow evidence before merge.

## Evidence

- Python `smtplib.SMTP` documentation:
  https://docs.python.org/3/library/smtplib.html

## Verification

- The focused constructor and Manager-forwarding regressions passed.
- All 38 behavior tests passed in the exact pinned Python 2.7.18 and Python
  3.12.8 workflow images; each runtime skipped only the regression dedicated
  to the other runtime's TLS-context boundary.
- Nineteen workflow, thirteen Manager, and fourteen SMTP hostile mutations were
  rejected on both runtimes, including removal of timeout forwarding and the
  legacy no-timeout constructor branch.
- Repository-root and absolute external-directory `make check` passed in a
  clean disposable dual-runtime image, including 165 Make authority cases.
- Verification created no bytecode artifacts and used no live SMTP relay or
  credentials.
