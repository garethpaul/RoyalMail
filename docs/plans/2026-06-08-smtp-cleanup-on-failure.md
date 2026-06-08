# SMTP Cleanup on Failure

## Status: Completed

## Context

`RoyalMail.send()` creates a new SMTP connection for each send call. The normal
path quits the server, but exceptions during login or `sendmail` skipped
`server.quit()`. Email helpers should close transport connections even when
delivery fails.

## Objectives

- Preserve the existing `RoyalMail.send()` API and error propagation behavior.
- Ensure SMTP connections are quit when login or message sending raises.
- Add Python 2 regression coverage for the `sendmail` failure path.
- Keep existing message-composition, envelope, and manager tests intact.

## Work Completed

- Wrapped the login and send path in a `finally` block that calls
  `server.quit()`.
- Added a fake SMTP server test proving `quit()` runs when `sendmail` raises.
- Updated README, VISION, and CHANGES.

## Verification

- `python2 -m py_compile royalmail.py`
- `python2 -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add explicit attachment-path validation behavior before changing MIME
  handling.
- Document TLS expectations and supported Python versions for callers.
