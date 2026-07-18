#!/usr/bin/env python2
"""Prove the behavior suite gates instead of merely existing.

The static contract checkers pin source text, and `tests/test_royalmail.py`
is pinned fragment by fragment, but nothing observed the suite *rejecting* a
real defect. Text pins cannot cover an unpinned guard, cannot survive a
functionally identical rewrite, and cannot notice a neutered assertion
mechanism or an added `tests/test_*.py` module that no pinned file mentions.

This harness plants hostile mutations into a throwaway copy of the checkout,
runs the real suite against each one, and requires every mutation to be
rejected. A suite that has been disabled always passes, so every mutation
survives and this harness fails. The clean-tree control distinguishes genuine
detection from universal failure.
"""
from __future__ import print_function

import os
import shutil
import subprocess
import sys
import tempfile


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_NAME = 'royalmail.py'
IGNORED = ('.git', '__pycache__', '*.pyc', '*.pyo')

# Each mutation is a real defect in the shipped security or delivery surface.
# The guards below are deliberately chosen because no static checker pins the
# lines being mutated, so the behavior suite is their only defense.
MUTATIONS = (
    (
        'header newline guard disabled',
        "        if isinstance(value, string_types) and ('\\n' in value or '\\r' in value):",
        '        if False:',
    ),
    (
        'attachment mimetype newline guard disabled',
        "        if '\\n' in mimetype or '\\r' in mimetype:",
        '        if False:',
    ),
    (
        'content id token guard use site disabled',
        '        if not CONTENT_ID_RE.match(cid):',
        '        if False:',
    ),
    (
        'attachment mimetype type guard disabled',
        '        if not isinstance(mimetype, string_types):',
        '        if False:',
    ),
    (
        'recipient refusal ignored',
        '        if refused:',
        '        if False:',
    ),
)


def build_tree(destination):
    shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(*IGNORED))


def run_suite(tree):
    environment = dict(os.environ)
    environment['PYTHONDONTWRITEBYTECODE'] = '1'
    process = subprocess.Popen(
        [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests'],
        cwd=tree,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=environment,
    )
    output = process.communicate()[0]
    if not isinstance(output, str):
        output = output.decode('utf-8', 'replace')
    return process.returncode, output


def apply_mutation(tree, description, target, replacement):
    path = os.path.join(tree, SOURCE_NAME)
    with open(path, 'r') as handle:
        source = handle.read()
    if source.count(target) != 1:
        raise AssertionError(
            '%s mutation must match exactly one %s line, matched %d'
            % (description, SOURCE_NAME, source.count(target))
        )
    mutated = source.replace(target, replacement, 1)
    if mutated == source:
        raise AssertionError('%s mutation did not alter %s' % (description, SOURCE_NAME))
    with open(path, 'w') as handle:
        handle.write(mutated)


def main():
    workspace = tempfile.mkdtemp(prefix='royalmail-behavior-mutations-')
    try:
        control = os.path.join(workspace, 'control')
        build_tree(control)
        returncode, output = run_suite(control)
        if returncode != 0:
            raise AssertionError(
                'clean-tree control suite failed, so mutation results would be '
                'meaningless:\n%s' % output
            )

        for index, (description, target, replacement) in enumerate(MUTATIONS):
            tree = os.path.join(workspace, 'mutation-%d' % index)
            build_tree(tree)
            apply_mutation(tree, description, target, replacement)
            returncode, output = run_suite(tree)
            if returncode == 0:
                raise AssertionError(
                    '%s hostile mutation survived the behavior suite:\n%s'
                    % (description, output)
                )
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    print(
        'behavior mutation tests passed (%d hostile mutations rejected).'
        % len(MUTATIONS)
    )


if __name__ == '__main__':
    main()
