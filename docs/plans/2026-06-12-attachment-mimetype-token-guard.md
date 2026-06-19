# Attachment Mimetype Token Guard

## Status: Completed

## Context

Explicit attachment mimetypes currently require one non-empty slash-separated
pair and reject carriage returns or line feeds. They still accept parameters,
spaces, tabs, delimiters, and non-ASCII bytes that are not valid MIME type
tokens and can create ambiguous or malformed `Content-Type` headers.

## Priority

Attachment metadata crosses a message-header boundary before file content is
read. Callers should be able to supply only an explicit `maintype/subtype`
pair, not parameters or other header syntax.

## Requirements

- R1. Preserve the public explicit `maintype/subtype` attachment API.
- R2. Require both components to contain only ASCII MIME token characters.
- R3. Reject whitespace, controls, delimiters, parameters, empty components,
  extra separators, and non-string values before opening the attachment.
- R4. Preserve accepted standard and vendor MIME types.
- R5. Cover valid and invalid boundaries in the Python 2 unit suite.
- R6. Protect implementation, tests, documentation, and completed plan in the
  dependency-free repository checker.

## Scope Boundaries

- Do not change guessed MIME type behavior.
- Do not port the library to Python 3 in this focused change.
- Do not add dependencies or alter SMTP behavior.

## Verification Plan

- `python2 -B -m unittest discover -s tests -p test_royalmail.py`
- `make lint`
- `make test`
- `make check`
- digest-pinned Python 2.7.18 container validation
- focused hostile mimetype-token mutations
- `git diff --check`

## Work Completed

- Added one dependency-free ASCII MIME-token expression for explicit
  attachment maintypes and subtypes.
- Rejected parameters, whitespace, controls, delimiters, extra separators,
  non-ASCII bytes, empty components, and non-string values before file reads.
- Preserved standard and vendor MIME types, including
  `application/vnd.example+json`.
- Expanded Python 2 regression coverage and repository checker requirements for
  the implementation, tests, documentation, and this completed plan.

## Verification

- `python2 -B -m unittest discover -s tests -p test_royalmail.py` passed 17
  tests.
- `make lint`, `make test`, and `make check` passed.
- The full gate passed in the reviewed digest-pinned Python 2.7.18 container
  with a read-only checkout and no network access.
- 12 focused hostile mimetype-token mutations were rejected, covering the
  token expression, separator and component checks, non-string values,
  validation bypass and ordering, positive and negative tests, documentation,
  and completed-plan status.
- `git diff --check` passed.
