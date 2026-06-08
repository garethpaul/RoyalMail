# RoyalMail Baseline

## Status: Completed

## Context

`RoyalMail` is a legacy Python 2 helper around `smtplib` and the standard
email package. The repository now has coverage for message composition,
envelope recipient behavior, and manager sender construction, so the remaining
baseline is to keep those checks easy to run and documented.

## Objectives

- Preserve the `RoyalMail` sender and `Message` composition APIs.
- Keep SMTP credentials caller-provided and out of source control.
- Validate plain text, HTML alternative, attachment fallback, BCC envelope, and
  manager construction behavior.
- Keep Python 2 syntax and unit tests available through `make check`.
- Maintain completed maintenance plans under `docs/plans`.

## Work Completed

- Confirmed `make check` runs Python 2 syntax checks and unit tests.
- Added canonical `docs/plans` coverage for the current maintenance baseline.
- Added a Python 2-compatible docs-plan checker and wired it into `make lint`.
- Updated README, VISION, and CHANGES to make the baseline discoverable.

## Verification

- `python2 -m py_compile royalmail.py`
- `python2 -m unittest discover -s tests`
- `python2 scripts/check-docs-plans.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add explicit attachment-path validation behavior before changing MIME
  handling.
- Document TLS expectations and supported Python versions for callers.
