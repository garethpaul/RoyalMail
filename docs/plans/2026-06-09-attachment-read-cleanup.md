# Attachment Read Cleanup

## Status: Completed

## Context

`Message._add_attachment()` opened an attachment file and closed it only after
the MIME object was built and encoded. If MIME construction failed after the
file was read, the file handle could remain open.

## Objectives

- Preserve attachment MIME type handling and payload encoding.
- Close attachment file handles even when MIME object construction fails.
- Cover the failure path with a dependency-free Python 2 regression test.
- Avoid changing the public `Message.attach()` API.

## Work Completed

- Read attachment payloads inside a `try/finally` that always closes the file
  handle before MIME object construction continues.
- Reused the read payload across text, image, audio, and fallback MIME paths.
- Added a regression test that injects a tracking file object and failing MIME
  constructor, then verifies the file is closed after the exception.
- Updated README, VISION, and CHANGES notes for the attachment cleanup guard.

## Verification

- `python2 -m py_compile royalmail.py`
- `python2 -m unittest discover -s tests`
- `python2 scripts/check-docs-plans.py`
- `make check`
- `git diff --check`
