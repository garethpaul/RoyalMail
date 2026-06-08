# Message Composition Coverage

## Status

Completed

## Context

`RoyalMail` has regression tests for manager construction and BCC envelope
behavior. The next risk is message-format drift: plain text, HTML alternative,
and attachment composition should be covered before changing MIME handling or
attachment validation.

## Objectives

- Add Python 2 tests for plain text message headers and body.
- Add tests for HTML messages using multipart alternative payloads.
- Add tests for attachment filename and MIME fallback behavior.
- Preserve runtime behavior.

## Verification

- `make test`
- `make verify`
- `git diff --check`
