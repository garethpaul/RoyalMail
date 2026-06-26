# RoyalMail

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/RoyalMail` is a public sample, documentation, or utility project. Simple python mailer that sits on SMTPLIB

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python (1).

## Repository Contents

- `README.md` - project overview and local usage notes
- `CHANGES.md` - maintenance history for test and verification coverage
- `Makefile` - local verification entry points
- `docs/plans` - completed maintenance plans for the current baseline
- `plans` - historical implementation notes
- `scripts` - documentation-plan validators
- `tests` - shared Python 2 and Python 3 unit tests for email composition and sender behavior
- `royalmail.py` - email composition and SMTP sender implementation
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: no top-level source directories detected
- Dependency and build manifests: none detected
- Entry points or build surfaces: none detected
- Test-looking files: tests/test_royalmail.py

## Getting Started

### Prerequisites

- Git
- Python 2.7.18 and Python 3.12 for the complete local compatibility gate

### Setup

```bash
git clone https://github.com/garethpaul/RoyalMail.git
cd RoyalMail
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- No single runtime entry point was identified. Start by reading the source files and manifests listed above.

## Testing and Verification

- Make verification derives one canonical checked-in root, freezes both Python
  commands and shell authority, and rejects preloaded or ambiguous Makefiles.
- `make check` runs the same syntax checks and unit tests on Python 2 and Python
  3 for plain text, HTML,
  attachment, envelope, header-injection rejection, SMTP cleanup, and manager
  behavior, including no-argument sender exception recording and attachment
  file cleanup when MIME construction fails. Manager coverage also verifies
  that normal work and the shutdown sentinel leave queue completion balanced.
  Attachment tests also cover
  constructor-supplied `(filename, cid, mimetype)` tuples and Content-ID
  and filename newline rejection, explicit ASCII MIME type tokens, ASCII
  Content-ID tokens, and TLS startup when `use_tls=True` without login
  credentials. One-shot `To`, `CC`, and `BCC` iterables are materialized once
  so recipient headers and envelope delivery remain aligned while BCC stays
  envelope-only. Manager queues also accept one-pass iterable message batches
  without probing their length or consuming them twice. SMTP cleanup still runs
  after failures, while a primary SMTP failure remains visible if shutdown also
  fails. Partial recipient refusals are surfaced, failed SMTP `quit()` calls
  fall back to direct socket close, and stopped Manager workers reject new work
  while reporting iterator-level failures from `join()`.
- `make check` runs a static manager contract on both runtimes and rejects
  mutations that remove, duplicate, relocate, or bypass queue acknowledgement,
  stop signaling, or worker-error propagation. It also rejects SMTP mutations
  that hide refusal results, mask primary errors, or remove cleanup fallback.
- `make check` also requires completed canonical plans under `docs/plans`.
- `make check` runs with Python bytecode disabled and fails if `.pyc` or `.pyo`
  files are present in the checkout.
- GitHub Actions runs explicit Python 2 and Python 3 targets through
  `.github/workflows/check.yml`. The jobs use digest-pinned Python 2.7.18 and
  Python 3.12.8 containers, credential-free pinned checkout, and read-only
  permissions. They fail if syntax, unit tests, repository contracts, or
  workflow-policy mutation tests fail; neither runtime can be skipped.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.

### TLS Verification

`use_tls=True` preserves the legacy STARTTLS behavior and encrypts the SMTP
connection, but RoyalMail does not create or choose a certificate-verification
policy by default. On Python 3, callers that require authenticated TLS should
pass an `ssl.SSLContext` configured for their trust requirements:

```python
import ssl

sender = RoyalMail(
    'smtp.example.com',
    587,
    use_tls=True,
    tls_context=ssl.create_default_context(),
)
```

The exact TLS context is forwarded to `SMTP.starttls(context=...)`. Python
2.7's `smtplib` cannot accept an `SSLContext`; supplying `tls_context` there
raises a clear runtime error instead of silently falling back to unverified
legacy STARTTLS. Use Python 3 or an externally authenticated TLS tunnel when
certificate verification is required.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include royalmail.py.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include royalmail.py.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include royalmail.py.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-royalmail-baseline.md` for the canonical Python 2
  message-composition verification baseline.
- See `docs/plans/2026-06-08-smtp-cleanup-on-failure.md` for the SMTP cleanup
  regression baseline.
- See `docs/plans/2026-06-09-header-newline-guard.md` for the message header
  and envelope newline guard.
- See `docs/plans/2026-06-09-manager-no-arg-error.md` for the Manager
  no-argument exception recording guard.
- See `docs/plans/2026-06-09-attachment-read-cleanup.md` for the attachment
  file cleanup guard.
- See `docs/plans/2026-06-09-attachment-mimetype-tuple.md` for constructor
  attachment mimetype tuple coverage.
- See `docs/plans/2026-06-09-attachment-content-id-header-guard.md` for
  attachment Content-ID newline rejection.
- See `docs/plans/2026-06-09-attachment-mimetype-guard.md` for explicit
  attachment mimetype validation.
- See `docs/plans/2026-06-09-unauthenticated-tls-start.md` for the
  unauthenticated STARTTLS regression guard.
- See `docs/plans/2026-06-09-bytecode-free-verification.md` for the
  bytecode-free verification guard.
- See `docs/plans/2026-06-10-ci-baseline.md` for the GitHub Actions baseline.
- See `docs/plans/2026-06-10-hosted-legacy-validation.md` for the enforced
  Python 2.7 hosted validation boundary.
- See `docs/plans/2026-06-10-attachment-filename-header-guard.md` for
  attachment filename newline rejection.
- See `docs/plans/2026-06-12-attachment-mimetype-token-guard.md` for explicit
  ASCII MIME type tokens enforced before attachment files are read.
- See `docs/plans/2026-06-12-python3-compatibility.md` for the shared Python
  2.7 and Python 3.12 behavior and hosted validation contract.
- See `docs/plans/2026-06-13-attachment-content-id-token-guard.md` for ASCII
  Content-ID tokens enforced before attachment files are read.
- See `docs/plans/2026-06-13-manager-sentinel-queue-completion.md` for balanced
  manager queue completion across normal work and shutdown.
- See `docs/plans/2026-06-14-make-root-override-protection.md` for the
  caller-resistant, location-independent dual-runtime Make root.
- See `docs/plans/2026-06-14-send-typeerror-propagation.md` for single-attempt
  propagation of per-message send failures.
- See `docs/plans/2026-06-14-recipient-iterator-header-preservation.md` for
  aligned recipient headers and envelope delivery from one-shot iterables.
- See `docs/plans/2026-06-15-manager-iterable-message-batches.md` for one-pass
  Manager batch delivery and balanced queue completion.
- See `docs/plans/2026-06-17-smtp-primary-error-preservation.md` for primary
  SMTP failure preservation across a competing cleanup failure.
- See `docs/plans/2026-06-19-royalmail-deep-review.md` for partial-refusal,
  cleanup-fallback, attachment-iterator, and Manager lifecycle remediation.
- See `docs/plans/2026-06-21-safe-make-authority.md` for spaced-checkout root
  resolution and fail-closed dual-runtime Make authority.
- See `docs/plans/2026-06-26-verified-tls-context.md` for explicit Python 3
  TLS context forwarding and the Python 2 verification boundary.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
