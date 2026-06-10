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
- Validate explicit attachment mimetypes before MIME construction
- Keep attachment file handles closed on MIME construction failures
- Start TLS whenever callers request `use_tls=True`
- Keep SMTP connections closed on send or login failures
- Reject newline characters in message headers and SMTP envelope addresses
- Reject newline characters in attachment Content-ID headers
- Keep Manager failure results stable for sender exceptions without arguments
- Keep completed maintenance plans under `docs/plans`
- Keep verification runs from leaving Python bytecode in the checkout
- Keep the Python 3 documentation guard running in GitHub Actions even when
  legacy Python 2 checks are unavailable
- Treat Python 2 compatibility code as legacy context

Next priorities:

- Document supported Python versions and TLS expectations
- Validate attachment paths and MIME type handling
- Return clearer errors for SMTP failures

Contribution rules:

- One PR = one focused message, SMTP, attachment, test, or documentation change.
- Do not commit SMTP credentials or real message content.
- Keep transport-security changes explicit.
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
