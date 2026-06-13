from __future__ import print_function

import re


GET_PATTERN = re.compile(
    r'^            msg = self\.queue\.get\(block=True\)$',
    re.MULTILINE,
)
SENTINEL_PATTERN = re.compile(
    r'^            try:\n'
    r'                if msg is None:\n'
    r'                    break$',
    re.MULTILINE,
)
ACKNOWLEDGEMENT_PATTERN = re.compile(
    r'^            finally:\n'
    r'                self\.queue\.task_done\(\)$',
    re.MULTILINE,
)
TASK_DONE_PATTERN = re.compile(r'^\s*self\.queue\.task_done\(\)$', re.MULTILINE)


def validate(source):
    failures = []
    gets = list(GET_PATTERN.finditer(source))
    sentinels = list(SENTINEL_PATTERN.finditer(source))
    acknowledgements = list(ACKNOWLEDGEMENT_PATTERN.finditer(source))
    task_done_calls = list(TASK_DONE_PATTERN.finditer(source))

    if len(gets) != 1:
        failures.append('dequeue manager work exactly once')
    if len(sentinels) != 1:
        failures.append('handle the shutdown sentinel inside the protected block')
    if len(acknowledgements) != 1 or len(task_done_calls) != 1:
        failures.append('acknowledge every dequeued item in exactly one finally block')
    if gets and sentinels and acknowledgements:
        if not (gets[0].start() < sentinels[0].start() < acknowledgements[0].start()):
            failures.append('acknowledge only after protected queue processing')

    return failures
