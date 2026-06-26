# Security Policy

## Supported Versions

The supported security scope for `RoyalMail` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Simple python mailer that sits on SMTPLIB

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/RoyalMail` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a public sample, documentation, or utility project. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- No primary dependency manifest was detected in the repository root. If dependencies are added later, include a manifest and prefer reproducible installation instructions.
- GitHub Actions runs the shared behavior gate in digest-pinned Python 2.7.18
  and Python 3.12.8 containers; credential persistence is disabled,
  permissions are read-only, and neither runtime's syntax, unit-test, or
  workflow-policy failures can be skipped.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

Message headers, SMTP envelope addresses, and attachment Content-ID headers
should reject carriage returns and line feeds so untrusted values cannot inject
additional email headers or recipients.
Attachment Content-ID values are restricted to ASCII Content-ID tokens so
brackets, whitespace, controls, and non-ASCII bytes cannot corrupt msg-id
header syntax.
Attachment basenames used in `Content-Disposition` parameters should reject
the same newline characters before the attachment file is read.
Explicit attachment mimetypes should also reject malformed values and newline
characters before MIME headers are constructed. Both components are restricted
to ASCII MIME type tokens so parameters, whitespace, delimiters, controls, and
non-ASCII bytes cannot become attachment header syntax.
When callers request `use_tls=True`, the SMTP connection should start TLS even
if the relay does not require login credentials. That default encrypts the
connection but does not create a RoyalMail-controlled certificate-verification
policy. Python 3 callers can supply a trusted TLS context, which is forwarded
unchanged to `SMTP.starttls(context=...)`; Python 2 rejects that option because
its legacy `smtplib` cannot consume an `SSLContext` rather than silently
downgrading the caller's verification request.
Use the optional SMTP connection timeout for untrusted or failure-prone relays
so a connection attempt cannot inherit an unbounded process-wide socket
default. Omitting it preserves legacy behavior.
SMTP cleanup should always be attempted, but a primary SMTP failure must remain
visible if the server also fails while closing the connection. A failed SMTP
QUIT exchange should fall back to direct socket close. Partial recipient
refusals must remain visible because some recipients may accept a message while
others reject it; callers should inspect the refusal mapping rather than blindly
retrying every recipient.
Queued Manager batches may be one-pass iterables. They should be consumed once
without length probing so delivery, callbacks, result records, and queue
acknowledgements remain aligned. Stop signaling should wake blocked workers,
remain idempotent, reject later submissions, and surface iterator-level worker
failures without stranding queued tasks.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
