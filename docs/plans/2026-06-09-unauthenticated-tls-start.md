# Unauthenticated TLS Start

## Status: Completed

## Context

`RoyalMail.send()` accepted `use_tls=True`, but the TLS handshake only ran when
SMTP login credentials were also present. That meant callers using an
unauthenticated SMTP relay with STARTTLS requested could still send without
calling `starttls()`.

## Objectives

- Start TLS whenever `use_tls=True`.
- Preserve optional SMTP login behavior after the TLS handshake.
- Keep SMTP connection cleanup behavior unchanged.
- Cover unauthenticated TLS sends with Python 2 regression tests.

## Work Completed

- Moved the `EHLO`, `STARTTLS`, `EHLO` sequence outside the login-only branch.
- Added a fake SMTP regression test for `use_tls=True` without `usr`/`pwd`.
- Updated README, SECURITY, VISION, and CHANGES notes for the TLS behavior.

## Verification

- `python2 -m py_compile royalmail.py`
- `python2 -m unittest discover -s tests`
- `python2 scripts/check-docs-plans.py`
- `make lint`
- `make test`
- `make check`
- `make verify`
- `git diff --check`
