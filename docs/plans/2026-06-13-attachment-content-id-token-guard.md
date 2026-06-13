# Attachment Content-ID Token Guard

## Status: Completed

## Context

Attachment Content-ID values are wrapped directly in angle brackets after only
newline validation. Values containing brackets, quotes, whitespace, controls,
or non-ASCII bytes can therefore produce malformed MIME header syntax even
though they cannot inject a second header line.

## Priority

Content-ID is a serialized message header and should fail before attachment
file reads when its value cannot form the interior of a safe RFC-style msg-id.
The guard must remain compatible with Python 2 and Python 3 and preserve common
dot-atom and `name@domain` identifiers.

## Objectives

- Require Content-ID values to be strings.
- Reject CR/LF before any attachment file read.
- Restrict values to printable ASCII msg-id token characters.
- Preserve common alphanumeric, dot-atom, punctuation, and `@` identifiers.
- Add focused positive and hostile regression coverage on Python 2 and 3.
- Keep attachment filenames, MIME types, and payload behavior unchanged.

## Work Completed

- Added a Python 2/3-compatible ASCII msg-id token expression.
- Added `_safe_content_id` string, newline, and token validation.
- Treated every non-`None` Content-ID as explicitly supplied, so empty and
  non-string values fail instead of silently changing attachment disposition.
- Added broad positive punctuation coverage and hostile malformed-ID cases.
- Added fail-closed source, test, documentation, and completed-plan contracts.
- Updated README, security, vision, change, and maintenance-plan documentation.

## Verification

- Python 2 and Python 3 focused unit tests
- `make check`
- Digest-pinned, read-only, network-isolated Python 2.7.18 and Python 3.12.8
- Focused non-string, bracket, whitespace, control, non-ASCII, bypass, and
  validation-order mutations
- `git diff --check`

Both Python 2 and Python 3 suites passed 20 tests. Full `make check` and the
digest-pinned, read-only, network-isolated Python 2.7.18 and Python 3.12.8 gates
passed syntax, documentation, 19 workflow mutations, and behavior validation.

## Scope Boundary

This change validates caller-supplied Content-ID syntax. It does not generate
IDs, alter attachment disposition, or change SMTP delivery behavior.
