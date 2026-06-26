# Verified TLS Context

Status: Completed

## Context

`RoyalMail(use_tls=True)` upgrades SMTP connections with STARTTLS, but the
current no-argument `smtplib.SMTP.starttls()` call does not give callers an
explicit certificate-verification policy. Python 3.12 accepts an `SSLContext`
for STARTTLS, while Python 2.7.18 exposes only legacy key and certificate file
arguments and cannot consume a verification context through `smtplib`.

## Requirements

- Preserve the existing `use_tls=True` call sequence when no TLS context is
  supplied.
- Accept an optional caller-supplied TLS context without creating or owning
  trust policy inside RoyalMail.
- Pass that exact context to `SMTP.starttls()` on the supported Python 3 path.
- Reject a supplied TLS context clearly on Python 2 before invoking legacy
  STARTTLS rather than silently dropping certificate verification.
- Keep SMTP cleanup and primary-error preservation unchanged on every path.
- Forward the option through `Manager` when it constructs the default sender.
- Document that default STARTTLS provides encryption but not an explicit
  RoyalMail-controlled certificate-verification policy.

## Approach

- Add a `tls_context` constructor option stored by `RoyalMail`.
- Keep the legacy no-argument `starttls()` call for compatibility when the
  option is absent.
- On Python 3, call `starttls(context=tls_context)` when the option is present.
- On Python 2, raise a focused runtime error before STARTTLS and still execute
  the existing cleanup path.
- Cover default, verified, manager-forwarding, and unsupported-runtime behavior
  in the shared dual-runtime unit suite and static contracts.

## Scope Boundaries

- Do not create a default context, choose CA bundles, disable hostname checks,
  add implicit TLS, or change the default transport policy.
- Do not remove Python 2.7 compatibility or alter authentication ordering.
- Do not add retries, SMTP response translation, dependencies, or logging.

## Verification

- First add regressions that fail because `tls_context` is not accepted or
  forwarded.
- Run the focused unit tests in Python 3.12 and Python 2.7.18.
- Run repository-root and external-directory `make check` through both pinned
  runtime containers.
- Reject hostile source and test mutations that drop context forwarding,
  bypass the Python 2 rejection, or weaken documentation of the default.

## Risks

- Calling `starttls(context=...)` on Python 2 would fail with an ambiguous
  keyword error after callers requested verification; the version boundary
  must be checked explicitly.
- The additive constructor option must remain compatible with positional users
  and with `Manager` keyword construction.

## Work Completed

- Added an optional `tls_context` constructor argument without changing the
  existing positional parameters or no-context STARTTLS behavior.
- Forwarded the exact caller context through Python 3 `SMTP.starttls()` and
  through Manager-created senders.
- Rejected context requests on Python 2 before legacy STARTTLS while preserving
  the existing SMTP cleanup and primary-error precedence path.
- Added runtime regressions, static contracts, hostile mutations, security
  guidance, public usage documentation, and roadmap reconciliation.

## Verification Results

- The RED baseline failed because `RoyalMail` did not accept `tls_context` and
  Manager-created senders did not expose it.
- 37 unit tests passed on Python 3.12.8 and Python 2.7.18; each runtime skipped
  only the regression dedicated to the other runtime's TLS-context boundary.
- Twelve SMTP, twelve Manager, and nineteen workflow hostile mutations were
  rejected on both supported runtimes.
- Repository-root and external-directory `make check` passed in a disposable
  dual-runtime image assembled from the exact pinned Python 2.7.18 and Python
  3.12.8 workflow images, including 165 Make authority cases.
