# Attachment Filename Header Guard

## Status: Completed

## Context

Attachment Content-ID values and explicit MIME types were validated before MIME
header construction, but attachment basenames could still contain carriage
returns or line feeds. Python 2 serialized those characters into a folded
`Content-Disposition` filename parameter.

## Objectives

- Reject newline-bearing attachment basenames before reading files.
- Preserve valid attachment basenames and existing MIME behavior.
- Cover the behavior with the repository's Python 2 test gate.

## Work Completed

- Validated non-inline attachment basenames through the shared header guard.
- Reused the validated basename for the `Content-Disposition` parameter.
- Added a regression test backed by a real newline-containing filename.
- Updated README, SECURITY, VISION, and CHANGES guidance.

## Verification

- `make check`
- `make verify`
- `python2 -B -m unittest discover -s tests`
- `git diff --check`
