# Hosted Python 2 Legacy Validation

Status: Completed

## Context

The initial GitHub Actions baseline ran on a modern Ubuntu host where `python2`
was unavailable. The canonical `make check` command therefore reported success
after skipping RoyalMail syntax validation and all 15 unit tests. This legacy
SMTP library still requires Python 2 for its real behavioral contract.

## Objectives

- Run the complete Python 2.7 syntax, unit-test, and documentation gate in CI.
- Pin the archived runtime image by digest and third-party actions by commit.
- Remove all successful skip paths from the canonical Makefile gate.
- Keep verification bytecode-free and independent of the caller's directory.

## Work Completed

- Changed hosted validation to the official Python 2.7.18 image pinned by
  digest on a fixed Ubuntu 24.04 runner.
- Pinned checkout to its reviewed v6.0.3 commit.
- Made Python 2 mandatory for `make check` and removed unavailable-runtime
  success paths.
- Made Makefile paths resolve relative to the repository.
- Extended the repository checker to enforce the runtime, action, and no-skip
  contracts.

## Verification

- `docker run --rm -v "$PWD:/work:ro" -w /work python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20 make check`
- `git diff --check`
