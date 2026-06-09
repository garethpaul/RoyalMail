# Attachment Mimetype Guard

## Status: Completed

## Context

`Message.attach()` and constructor attachment tuples support caller-supplied
explicit mimetypes. Those values are later split into MIME maintype and subtype
fields. Without validation, malformed values or newline-bearing strings could
reach MIME header construction.

## Objectives

- Validate explicit attachment mimetypes before MIME object construction.
- Reject newline characters in explicit mimetype values.
- Reject malformed values that are not exactly `maintype/subtype`.
- Cover the behavior with Python 2 regression tests that do not need real
  attachment files.

## Work Completed

- Added `Message._safe_mimetype()` validation for type, newline, and
  `maintype/subtype` shape.
- Applied the guard whenever an explicit attachment mimetype is provided.
- Added Python 2 tests for newline-bearing and malformed explicit mimetypes.
- Updated README, SECURITY, VISION, and CHANGES notes for the mimetype guard.

## Verification

- `python2 -m py_compile royalmail.py`
- `python2 -m unittest discover -s tests`
- `python2 scripts/check-docs-plans.py`
- `make check`
- `make verify`
- `git diff --check`
