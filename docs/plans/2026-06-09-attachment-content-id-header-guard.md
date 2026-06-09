# Attachment Content-ID Header Guard

## Status: Completed

## Context

Attachment `cid` values are serialized into the MIME `Content-ID` header for
inline attachments. The main message headers and SMTP envelope addresses already
reject carriage returns and line feeds; attachment `Content-ID` values need the
same guard before MIME serialization.

## Objectives

- Preserve existing attachment tuple and `attach()` behavior.
- Reject newline characters in attachment `Content-ID` values.
- Raise the validation error before attachment file reads.
- Cover the behavior with Python 2 unit tests.

## Work Completed

- Reused the existing `Message._safe_header_value()` helper for attachment
  `Content-ID` values.
- Added a regression test that rejects a newline-bearing attachment `cid`
  without requiring the attachment file to exist.
- Updated README, SECURITY, VISION, and CHANGES notes for the guard.

## Verification

- `python2 -m py_compile royalmail.py`
- `python2 -m unittest discover -s tests`
- `python2 scripts/check-docs-plans.py`
- `make lint`
- `make test`
- `make build`
- `make verify`
- `make check`
- `git diff --check`
