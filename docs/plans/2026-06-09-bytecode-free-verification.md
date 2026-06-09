# Bytecode-Free Verification

## Status: Completed

## Context

The legacy Python 2 verification path used `py_compile`, which writes `.pyc`
files by default. Ignoring bytecode keeps git clean, but generated files still
leave local checkout noise and can hide whether verification is reproducible.

## Objectives

- Keep `make check` from creating Python bytecode files.
- Fail the documentation-plan checker when `.pyc` or `.pyo` files are present.
- Preserve the existing Python 2 syntax and unit-test verification behavior.
- Keep the bytecode ignore rules available for accidental local interpreter
  output.

## Work Completed

- Updated `Makefile` to run Python with bytecode disabled.
- Replaced the `py_compile` lint step with an in-memory syntax compile.
- Extended `scripts/check-docs-plans.py` to reject Python bytecode files.
- Updated README, VISION, and CHANGES notes for the bytecode-free guard.

## Verification

- `python2 -B -c 'compile(open("royalmail.py").read(), "royalmail.py", "exec")'`
- `python2 -B scripts/check-docs-plans.py`
- `python2 -B -m unittest discover -s tests`
- `make lint`
- `make test`
- `make check`
- `make verify`
- `git diff --check`
