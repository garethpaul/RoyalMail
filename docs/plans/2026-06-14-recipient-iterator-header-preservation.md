# Preserve Iterator-Backed Recipient Headers

## Status: Planned

## Context

`RoyalMail.send` materializes non-string `To` and `CC` values for the SMTP
envelope before `Message.as_string` renders the message. One-shot iterators are
therefore exhausted before header serialization: delivery targets remain
correct, but the resulting `To` and `CC` headers are empty.

## Requirements

- Materialize non-string `To`, `CC`, and `BCC` recipient collections once per
  send operation.
- Reuse the validated `To` and `CC` lists for both envelope delivery and header
  serialization.
- Keep BCC recipients in the SMTP envelope without adding a `BCC` message
  header.
- Preserve newline rejection before SMTP dispatch.
- Preserve string-recipient behavior, single-message and batch sending, and
  Python 2.7/Python 3.12 compatibility.
- Add runtime and static mutation-sensitive coverage for one-shot iterators.

## Implementation Units

### Recipient Normalization

File: `royalmail.py`

- Normalize each non-string recipient collection before message serialization.
- Store validated reusable lists on the message only where later header
  rendering consumes them.
- Keep the existing SMTP connection, TLS, login, send, and cleanup ordering.

### Regression Coverage

Files: `tests/test_royalmail.py`, `scripts/check-docs-plans.py`

- Prove generator-backed `To` and `CC` values appear in both the envelope and
  serialized headers.
- Prove generator-backed BCC remains envelope-only.
- Reject implementation, assertion, documentation, and completed-plan
  mutations.

### Documentation

Files: `README.md`, `CHANGES.md`

- Document reusable iterator-backed recipients without broadening the public
  API beyond the existing iterable contract.

## Verification

- focused regression on host Python 2.7.18 and Python 3.12.8
- repository and external-directory `make check`
- digest-pinned read-only network-isolated runtime gates when cached images are
  available
- hostile recipient normalization and plan-evidence mutations
- exact diff, bytecode/generated-artifact, conflict-marker, and changed-line
  credential audits

## Scope Boundaries

- Do not alter attachment handling, message body encoding, SMTP authentication,
  TLS behavior, Manager queue behavior, or public method names.
- Do not merge or close stacked pull requests without explicit authorization.
