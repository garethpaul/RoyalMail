## RoyalMail Vision

RoyalMail is a legacy Python helper for composing and sending email through
SMTP, including plain text, HTML, CC/BCC, attachments, TLS login, and queued
message support.

The repository is useful as a compact wrapper around `smtplib` and the standard
email modules for older Python environments.

The goal is to preserve the email-composition behavior while making Python
version, transport security, and credential handling explicit.

The current focus is:

Priority:

- Preserve the `RoyalMail` sender and `Message` composition API
- Keep SMTP credentials caller-provided and out of source control
- Maintain attachment and multipart message behavior
- Keep constructor attachment tuples aligned with `attach()` mimetype support
- Restrict explicit attachment maintypes and subtypes to ASCII MIME type tokens
  before MIME construction or attachment reads
- Keep attachment file handles closed on MIME construction failures
- Start TLS whenever callers request `use_tls=True`
- Keep SMTP connections closed on send or login failures
- Reject newline characters in message headers and SMTP envelope addresses
- Reject newline characters in attachment Content-ID headers
- Restrict attachment identifiers to ASCII Content-ID tokens before file reads
- Reject newline characters in attachment filename header parameters
- Keep Manager failure results stable for sender exceptions without arguments
- Keep every Manager queue dequeue paired with one acknowledgement, including
  shutdown sentinels and failed sends
- Accept one-pass iterable Manager batches without length probing or repeated
  consumption
- Keep completed maintenance plans under `docs/plans`
- Keep verification runs from leaving Python bytecode in the checkout
- Keep the shared Python 2 and Python 3 syntax, unit-test, and documentation
  gates running in digest-pinned Python 2.7.18 and Python 3.12.8 GitHub Actions
  containers with credential-free checkout
- Keep hosted workflow policy protected by dependency-free hostile mutations
- Treat Python 2 compatibility code as legacy context while preserving the
  supported Python 3.12 path

Next priorities:

- Document TLS expectations
- Validate attachment paths and MIME type handling
- Return clearer errors for SMTP failures

Contribution rules:

- One PR = one focused message, SMTP, attachment, test, or documentation change.
- Do not commit SMTP credentials or real message content.
- Keep transport-security changes explicit.
- Keep `.github/workflows/check.yml` aligned with both guarded runtime baselines.
- Add fixtures for message-format behavior changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Email helpers can expose credentials, recipients, and message contents. The
library should avoid logging sensitive fields, should support secure transport
configuration, and should keep BCC handling correct.

## What We Will Not Merge (For Now)

- Checked-in credentials or real recipient lists
- Hidden bulk-mail behavior
- Logging full message bodies by default
- Transport-security downgrades without explicit rationale

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
