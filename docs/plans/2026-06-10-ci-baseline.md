# RoyalMail CI Baseline

## Status: Completed

## Context

`RoyalMail` has a legacy Python 2 email-composition and SMTP regression
baseline behind `make check`. Hosted Linux runners normally provide Python 3
but not Python 2. CI must still enforce repository contracts instead of
turning the entire verification command into a successful no-op.

## Objectives

- Run the existing `make check` wrapper in GitHub Actions.
- Always run the Python 3-compatible documentation and repository guard.
- Preserve Python 2 syntax and unit tests on hosts where `python2` exists.
- Use least-privilege workflow permissions and a bounded job timeout.

## Work Completed

- Added `.github/workflows/check.yml` for pushes, pull requests, and manual
  dispatches with read-only contents permission, a five-minute timeout, and
  `actions/checkout` pinned to the verified `v4` commit.
- Split the Makefile interpreters so the Python 3 guard always runs while
  unavailable legacy Python 2 checks report explicit skips.
- Extended `scripts/check-docs-plans.py` to require the CI workflow security
  settings, guarded Makefile behavior, documentation, and this completed plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python3 -B scripts/check-docs-plans.py`
- `make check PYTHON=python2-unavailable`
- `git diff --check`

## Follow-Up Candidates

- Port the email composition implementation and tests to Python 3 or document
  the repository as Python 2 archive-only.

## Superseded Limitation

The successful Python 2 skip behavior described above was replaced on
2026-06-10 by the pinned full-runtime gate in
`docs/plans/2026-06-10-hosted-legacy-validation.md`.
