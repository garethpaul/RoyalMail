from __future__ import print_function


def validate(source):
    failures = []
    send_start = source.find('    def send(self, msg):')
    send_end = source.find('    def _send(self, server, msg):', send_start)
    single_send_end = source.find('class Message(object):', send_end)
    send_source = source[send_start:send_end]
    single_send_source = source[send_end:single_send_end]

    send_fragments = (
        'if self.tls_context is None:',
        'server.starttls()',
        'elif sys.version_info[0] < 3:',
        "raise RuntimeError('TLS contexts require Python 3 smtplib support')",
        'server.starttls(context=self.tls_context)',
        'delivery_error = None',
        'delivery_error = error',
        'cleanup_error = None',
        'cleanup_error = error',
        'server.quit()',
        'server.close()',
        'if delivery_error is not None:',
        'raise delivery_error',
        'if cleanup_error is not None:',
        'raise cleanup_error',
    )
    for fragment in send_fragments:
        if fragment not in send_source:
            failures.append('preserve SMTP send contract %s' % fragment)

    if send_source.count('server.starttls()') != 1:
        failures.append('preserve one legacy STARTTLS call')
    if send_source.count('server.starttls(context=self.tls_context)') != 1:
        failures.append('forward one explicit TLS context')

    if send_source.count('server.quit()') != 1:
        failures.append('attempt SMTP quit exactly once')
    if send_source.count('server.close()') != 1:
        failures.append('attempt SMTP close fallback exactly once')

    ordered_fragments = (
        'delivery_error = None',
        'delivery_error = error',
        'cleanup_error = None',
        'server.quit()',
        'cleanup_error = error',
        'server.close()',
        'if delivery_error is not None:',
        'if cleanup_error is not None:',
    )
    positions = [send_source.find(fragment) for fragment in ordered_fragments]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        failures.append('preserve SMTP delivery and cleanup precedence')

    close_fallback = (
        '        except BaseException as error:\n'
        '            cleanup_error = error\n'
        '            try:\n'
        '                server.close()\n'
        '            except BaseException:\n'
        '                pass'
    )
    if close_fallback not in send_source:
        failures.append('close the SMTP socket when quit fails')

    refusal_fragments = (
        'refused = server.sendmail(me, you, msg.as_string())',
        'if refused:',
        'raise smtplib.SMTPRecipientsRefused(refused)',
    )
    for fragment in refusal_fragments:
        if fragment not in single_send_source:
            failures.append('surface partial SMTP refusal with %s' % fragment)

    return failures
