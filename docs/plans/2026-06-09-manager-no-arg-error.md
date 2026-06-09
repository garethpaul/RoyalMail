# Manager No-Arg Error Recording

## Status: Completed

## Context

`Manager.run()` catches sender exceptions and stores a result tuple for each
message. The error path assumed every exception had at least one argument, so a
sender raising a bare `RuntimeError()` caused an `IndexError` before the
manager could record the failed send or invoke the callback.

## Objectives

- Preserve the existing `(success, err_code, err_message)` result shape.
- Keep one-argument and two-argument exception handling compatible.
- Record a stable fallback message for exceptions with no args.
- Add Python 2 regression coverage for the Manager failure path.

## Work Completed

- Added a regression test for a sender that raises `RuntimeError()` with no
  arguments.
- Updated `Manager.run()` to branch explicitly across two-arg, one-arg, and
  no-arg exceptions.
- Used the exception class name as the fallback no-arg error message.
- Updated README, VISION, and CHANGES notes for the Manager error guard.

## Verification

- `python2 -m unittest discover -s tests`
- `make check`
- `make verify`
- `git diff --check`
