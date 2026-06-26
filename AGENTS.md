# AGENTS.md

## Repository purpose

`garethpaul/RoyalMail` is a public sample, documentation, or utility project. Simple python mailer that sits on SMTPLIB

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `tests` - tests and fixtures
- `plans` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Python (1).
- Prefer dependency-free tests or stdlib checks when legacy packages are unavailable.

## Testing guidance

- Test-related files detected: `plans/2026-06-08-manager-regression-tests.md`, `tests/`, `tests/test_royalmail.py`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-royalmail-baseline.md` for the canonical Python 2 message-composition verification baseline.
- See `docs/plans/2026-06-08-smtp-cleanup-on-failure.md` for the SMTP cleanup regression baseline.
- See `docs/plans/2026-06-09-header-newline-guard.md` for the message header and envelope newline guard.
- See `docs/plans/2026-06-26-verified-tls-context.md` for explicit TLS context
  forwarding and the Python 2 verification boundary.
- SMTP connection timeouts are opt-in and must forward through both
  `RoyalMail` and `Manager` without changing the no-timeout constructor call.
- Hosted checks must run the complete Python 2 gate in the reviewed
  digest-pinned container with credential-free checkout and read-only
  permissions; missing Python 2 must not become a successful skip.
- Run `make contract-test` after workflow changes. Duplicate, relocated, or
  contradictory credential settings and other policy drift must fail closed.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
