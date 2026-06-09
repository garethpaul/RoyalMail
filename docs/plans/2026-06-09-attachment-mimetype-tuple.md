# Attachment Mimetype Tuple

## Status: Completed

## Context

`Message.attach()` supports an explicit `mimetype` argument, but constructor
attachments only normalized string filenames or two-item `(filename, cid)`
tuples. Passing a constructor attachment tuple with `(filename, cid, mimetype)`
raised `ValueError` before the message could be composed.

## Objectives

- Preserve existing string and two-item attachment constructor behavior.
- Accept three-item constructor attachment tuples with explicit mimetypes.
- Add a Python 2 regression test that exercises constructor-supplied mimetype
  attachments.

## Work Completed

- Extended constructor attachment normalization to accept
  `(filename, cid, mimetype)` tuples.
- Added a unit test proving constructor-supplied `text/plain` mimetypes are
  applied to attachment MIME parts.
- Updated README, VISION, and CHANGES notes for the attachment tuple guard.

## Verification

- `python2 -m unittest discover -s tests`
- `python2 -m py_compile royalmail.py`
- `python2 scripts/check-docs-plans.py`
- `make check`
- `make verify`
- `git diff --check`
