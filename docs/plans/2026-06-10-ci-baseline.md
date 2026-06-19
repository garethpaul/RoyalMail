# RoyalMail CI Baseline

## Status: Completed

## Context

`RoyalMail` has a legacy Python 2 email-composition and SMTP regression
baseline behind `make check`. A hosted gate must execute that complete runtime
contract instead of turning missing Python 2 into a successful no-op.

## Objectives

- Run the existing `make check` wrapper in GitHub Actions.
- Require Python 2 syntax, unit tests, documentation, and workflow contracts.
- Use least-privilege workflow permissions and credential-free checkout.
- Pin the archived runtime image by digest and third-party actions by commit.
- Keep verification bytecode-free and independent of the caller's directory.

## Work Completed

- Added `.github/workflows/check.yml` for pushes to `master`, pull requests,
  and manual dispatches on a fixed Ubuntu 24.04 runner.
- Ran the full gate in the official Python 2.7.18 image pinned by digest.
- Pinned checkout to the reviewed v6.0.3 commit, disabled persisted checkout
  credentials, and limited the workflow token to read-only contents access.
- Made Python 2 mandatory for `make check` and removed successful skip paths.
- Made Makefile paths resolve relative to the repository.
- Added exact workflow-policy validation and hostile mutation coverage for
  triggers, credentials, actions, permissions, runner, timeout, image digest,
  failure handling, runtime proof, and the canonical command.
- Updated README, VISION, SECURITY, CHANGES, and contributor guidance with the
  enforced hosted baseline.

## Verification

- `python2 -B scripts/test_workflow_contract.py`
- `make lint`
- `make contract-test`
- `make test`
- `make build`
- `make check`
- `docker run --rm -v "$PWD:/work:ro" -w /work python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20 make check`
- `git diff --check`

## Follow-Up Candidates

- Port the email composition implementation and tests to Python 3 or document
  the repository as Python 2 archive-only.
