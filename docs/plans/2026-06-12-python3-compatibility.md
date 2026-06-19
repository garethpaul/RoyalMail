# Python 3 Compatibility

Status: Completed

## Context

RoyalMail's behavior suite was locked to Python 2.7 because the production
module imported `Queue`, referenced `basestring` and `unicode`, and passed byte
payloads directly to Python 3's `MIMEText`. The archived Python 2 behavior must
remain supported while a maintained runtime becomes available.

## Objectives

- Preserve the public message, attachment, SMTP, and manager APIs.
- Run the same behavioral suite on Python 2.7.18 and Python 3.12.8.
- Keep both hosted runtime images pinned by digest.
- Require each runtime's syntax, documentation, workflow-policy, and unit-test
  gate independently.
- Keep verification bytecode-free and credential-free.

## Work Completed

- Added portable queue and text-type aliases.
- Added a shared text decoding helper for encoded subjects and supplied the
  declared charset explicitly for text attachment payloads.
- Made temporary attachment fixtures byte-correct on both runtimes.
- Added explicit non-ASCII subject coverage.
- Split the Makefile into required Python 2 and Python 3 targets while retaining
  `make check` as the combined canonical gate.
- Added a digest-pinned Python 3.12.8 hosted job beside the existing Python
  2.7.18 job and extended hostile workflow-policy mutations for both.

## Verification

- `make check` passed the Python 2 and Python 3 syntax, documentation,
  workflow-policy, and 18-test behavior gates.
- Read-only, network-isolated digest-pinned Python 2.7.18 and Python 3.12.8
  containers each passed their complete runtime gate.
- `make -f /home/gjones/code/private/worktrees/royalmail-python3-compatibility/Makefile check`
  passed from `/tmp`.
- Workflow YAML parsed successfully.
- Five focused hostile mutations restoring the Python 2-only queue import,
  removing the attachment charset, restoring string writes, removing the
  Python 3 job, or changing its image digest were rejected.
- `git diff --check` passed.
