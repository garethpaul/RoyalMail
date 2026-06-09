# Header Newline Guard

## Status: Completed

## Context

`RoyalMail.Message` writes `Subject`, `From`, `To`, `CC`, and `Date` values
directly into email headers, while `RoyalMail._send` also uses recipient fields
to build the SMTP envelope. Values containing carriage returns or line feeds
could be ambiguous and should be rejected before message serialization or SMTP
submission.

## Objectives

- Preserve the legacy Python 2 message-composition API.
- Reject newline characters in message headers.
- Reject newline characters in SMTP envelope sender and recipient values,
  including BCC values that are not serialized into the message body.
- Cover the behavior with mocked, dependency-free tests.

## Work Completed

- Added private header-value validation helpers on `Message`.
- Applied validation in both message header serialization and SMTP envelope
  construction.
- Added Python 2 tests for newline rejection in headers and BCC envelope
  recipients.
- Updated README, SECURITY, VISION, and CHANGES notes for the guard.

## Verification

- `python2 -m py_compile royalmail.py`
- `python2 -m unittest discover -s tests`
- `python2 scripts/check-docs-plans.py`
- `make check`
- `make verify`
- `git diff --check`
