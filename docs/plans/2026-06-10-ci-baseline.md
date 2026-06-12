# RoyalMail CI Baseline

## Status: Completed

## Context

`RoyalMail` has a legacy Python 2 email-composition and SMTP regression
baseline behind `make check`. Hosted Linux runners usually do not include
Python 2, so CI needs to run the same wrapper while letting the Makefile skip
Python 2-specific checks when the interpreter is unavailable.

## Objectives

- Run the existing `make check` wrapper in GitHub Actions.
- Preserve Python 2 syntax and unit tests on hosts where `python2` exists.
- Keep hosted CI useful by checking repository contracts without requiring
  Python 2 availability.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on pushes, pull
  requests, and manual dispatches.
- Guarded Python 2 Makefile targets so they run locally when `python2` is
  available and report a skip otherwise.
- Extended `scripts/check-docs-plans.py` to require the CI workflow, guarded
  Makefile behavior, and this completed plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python2 -B scripts/check-docs-plans.py`
- `git diff --check`

## Follow-Up Candidates

- Port the email composition tests to Python 3 or document the repository as
  Python 2 archive-only.
