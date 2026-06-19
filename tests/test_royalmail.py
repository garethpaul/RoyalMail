import os
import tempfile
import time
import unittest
from email import message_from_string

import royalmail


class FakeServer(object):
    def __init__(self):
        self.calls = []

    def sendmail(self, sender, recipients, payload):
        self.calls.append((sender, recipients, payload))


class FailingSMTP(object):
    instances = []

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.quit_called = False
        FailingSMTP.instances.append(self)

    def sendmail(self, sender, recipients, payload):
        raise RuntimeError('smtp send failed')

    def quit(self):
        self.quit_called = True


class FailingQuitSMTP(object):
    instances = []
    fail_send = False

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.quit_called = False
        self.close_called = False
        FailingQuitSMTP.instances.append(self)

    def sendmail(self, sender, recipients, payload):
        if self.fail_send:
            raise RuntimeError('smtp send failed')

    def quit(self):
        self.quit_called = True
        raise RuntimeError('smtp quit failed')

    def close(self):
        self.close_called = True


class RefusingSMTP(object):
    instances = []

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.calls = []
        RefusingSMTP.instances.append(self)

    def sendmail(self, sender, recipients, payload):
        self.calls.append(('sendmail', sender, recipients, payload))
        return {'refused@example.com': (550, 'mailbox unavailable')}

    def quit(self):
        self.calls.append('quit')


class FailingSetupSMTP(object):
    instances = []
    fail_stage = None
    fail_quit = False

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.calls = []
        FailingSetupSMTP.instances.append(self)

    def ehlo(self):
        self.calls.append('ehlo')

    def starttls(self):
        self.calls.append('starttls')
        if self.fail_stage == 'starttls':
            raise RuntimeError('smtp tls failed')

    def login(self, usr, pwd):
        self.calls.append(('login', usr, pwd))
        if self.fail_stage == 'login':
            raise RuntimeError('smtp login failed')

    def sendmail(self, sender, recipients, payload):
        self.calls.append(('sendmail', sender, recipients, payload))

    def quit(self):
        self.calls.append('quit')
        if self.fail_quit:
            raise RuntimeError('smtp quit failed')

    def close(self):
        self.calls.append('close')


class TrackingSMTP(object):
    instances = []

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.calls = []
        TrackingSMTP.instances.append(self)

    def ehlo(self):
        self.calls.append('ehlo')

    def starttls(self):
        self.calls.append('starttls')

    def login(self, usr, pwd):
        self.calls.append(('login', usr, pwd))

    def sendmail(self, sender, recipients, payload):
        self.calls.append(('sendmail', sender, recipients, payload))

    def quit(self):
        self.calls.append('quit')


class NoArgFailingSender(object):
    def send(self, message):
        raise RuntimeError()


class SuccessfulSender(object):
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)


class TrackingFile(object):
    def __init__(self):
        self.closed = False

    def read(self):
        return 'attachment body'

    def close(self):
        self.closed = True


class TypeErrorTrackingRoyalMail(royalmail.RoyalMail):
    def __init__(self):
        royalmail.RoyalMail.__init__(self)
        self.attempted_messages = []

    def _send(self, server, message):
        self.attempted_messages.append(message)
        raise TypeError('message serialization failed')


class RoyalMailTests(unittest.TestCase):
    def test_unicode_subject_uses_declared_charset(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject=u'caf\u00e9',
            Body='Body',
            charset='utf-8',
        )

        self.assertIn('=?utf-8?', message.as_string().lower())

    def test_plain_text_message_headers_and_body(self):
        message = royalmail.Message(
            To=['to@example.com', 'other@example.com'],
            From='from@example.com',
            CC='cc@example.com',
            Subject='Subject',
            Body='Plain body',
            Date='Mon, 01 Jan 2024 00:00:00 +0000',
        )

        parsed = message_from_string(message.as_string())

        self.assertEqual('text/plain', parsed.get_content_type())
        self.assertEqual('Subject', parsed['Subject'])
        self.assertEqual('from@example.com', parsed['From'])
        self.assertEqual('to@example.com, other@example.com', parsed['To'])
        self.assertEqual('cc@example.com', parsed['CC'])
        self.assertEqual('Mon, 01 Jan 2024 00:00:00 +0000', parsed['Date'])
        self.assertIn('Plain body', parsed.get_payload())

    def test_html_message_uses_multipart_alternative(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Plain body',
            Html='<p>HTML body</p>',
        )

        parsed = message_from_string(message.as_string())
        parts = parsed.get_payload()

        self.assertTrue(parsed.is_multipart())
        self.assertEqual('multipart/alternative', parsed.get_content_type())
        self.assertEqual(['text/plain', 'text/html'], [part.get_content_type() for part in parts])
        self.assertIn('Plain body', parts[0].get_payload())
        self.assertIn('HTML body', parts[1].get_payload())

    def test_attachment_uses_basename_and_octet_stream_fallback(self):
        fd, attachment_path = tempfile.mkstemp(suffix='.unknown-extension')
        try:
            os.write(fd, b'attachment body')
            os.close(fd)
            fd = None
            message = royalmail.Message(
                To='to@example.com',
                From='from@example.com',
                Subject='Subject',
                Body='Plain body',
                attachments=[attachment_path],
            )

            parsed = message_from_string(message.as_string())
            parts = parsed.get_payload()
            attachment = parts[1]

            self.assertEqual('multipart/related', parsed.get_content_type())
            self.assertEqual('text/plain', parts[0].get_content_type())
            self.assertEqual('application/octet-stream', attachment.get_content_type())
            self.assertEqual(
                os.path.basename(attachment_path),
                attachment.get_filename(),
            )
            self.assertEqual('base64', attachment['Content-Transfer-Encoding'])
        finally:
            if fd is not None:
                os.close(fd)
            os.remove(attachment_path)

    def test_constructor_attachment_tuple_accepts_mimetype(self):
        fd, attachment_path = tempfile.mkstemp(suffix='.royalmail')
        try:
            os.write(fd, b'attachment body')
            os.close(fd)
            fd = None
            message = royalmail.Message(
                To='to@example.com',
                From='from@example.com',
                Subject='Subject',
                Body='Plain body',
                attachments=[(attachment_path, None, 'text/plain')],
            )

            parsed = message_from_string(message.as_string())
            attachment = parsed.get_payload()[1]

            self.assertEqual('text/plain', attachment.get_content_type())
            self.assertEqual(os.path.basename(attachment_path), attachment.get_filename())
        finally:
            if fd is not None:
                os.close(fd)
            os.remove(attachment_path)

    def test_constructor_consumes_one_pass_attachment_descriptor_once(self):
        fd, attachment_path = tempfile.mkstemp(suffix='.txt')
        try:
            os.write(fd, b'attachment body')
            os.close(fd)
            fd = None
            descriptor = (value for value in (attachment_path, None))
            message = royalmail.Message(
                To='to@example.com',
                From='from@example.com',
                Subject='Subject',
                Body='Body',
                attachments=[descriptor],
            )

            parsed = message_from_string(message.as_string())
            attachment = parsed.get_payload()[1]

            self.assertEqual('text/plain', attachment.get_content_type())
            self.assertEqual(
                'attachment body',
                attachment.get_payload(decode=True).decode('ascii'),
            )
        finally:
            if fd is not None:
                os.close(fd)
            os.remove(attachment_path)

    def test_constructor_preserves_attachment_iterator_typeerror(self):
        def broken_descriptor():
            yield 'attachment.txt'
            raise TypeError('attachment descriptor failed')

        with self.assertRaises(TypeError) as raised:
            royalmail.Message(attachments=[broken_descriptor()])

        self.assertEqual('attachment descriptor failed', str(raised.exception))

    def test_attachment_accepts_vendor_mimetype_tokens(self):
        fd, attachment_path = tempfile.mkstemp(suffix='.royalmail')
        try:
            os.write(fd, b'attachment body')
            os.close(fd)
            fd = None
            message = royalmail.Message(
                To='to@example.com',
                From='from@example.com',
                Subject='Subject',
                Body='Plain body',
                attachments=[(attachment_path, None, 'application/vnd.example+json')],
            )

            parsed = message_from_string(message.as_string())
            attachment = parsed.get_payload()[1]

            self.assertEqual('application/vnd.example+json', attachment.get_content_type())
        finally:
            if fd is not None:
                os.close(fd)
            os.remove(attachment_path)

    def test_attachment_file_is_closed_when_mime_creation_fails(self):
        tracking_file = TrackingFile()
        original_mimebase = royalmail.MIMEBase
        original_open_present = hasattr(royalmail, 'open')
        original_open = getattr(royalmail, 'open', None)

        def fake_open(filename, mode):
            self.assertEqual('attachment.bin', filename)
            self.assertEqual('rb', mode)
            return tracking_file

        def failing_mimebase(maintype, subtype):
            raise RuntimeError('mime construction failed')

        royalmail.open = fake_open
        royalmail.MIMEBase = failing_mimebase

        try:
            message = royalmail.Message(
                To='to@example.com',
                From='from@example.com',
                Subject='Subject',
                Body='Body',
            )
            message.attach('attachment.bin', mimetype='application/octet-stream')

            with self.assertRaises(RuntimeError):
                message.as_string()
        finally:
            royalmail.MIMEBase = original_mimebase
            if original_open_present:
                royalmail.open = original_open
            else:
                del royalmail.open

        self.assertTrue(tracking_file.closed)

    def test_manager_creates_default_sender_from_kwargs(self):
        manager = royalmail.Manager(
            host='smtp.example.com',
            port=2525,
            use_tls=True,
            usr='smtp-user',
            pwd='smtp-password',
        )

        self.assertIsInstance(manager.RoyalMail, royalmail.RoyalMail)
        self.assertEqual('smtp.example.com', manager.RoyalMail.host)
        self.assertEqual(2525, manager.RoyalMail.port)
        self.assertTrue(manager.RoyalMail.use_tls)
        self.assertEqual('smtp-user', manager.RoyalMail._usr)
        self.assertEqual('smtp-password', manager.RoyalMail._pwd)

    def test_bcc_is_envelope_only(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            CC='cc@example.com',
            BCC='bcc@example.com',
            Subject='Subject',
            Body='Body',
        )
        server = FakeServer()

        royalmail.RoyalMail()._send(server, message)

        sender, recipients, payload = server.calls[0]
        self.assertEqual('from@example.com', sender)
        self.assertEqual(
            ['to@example.com', 'cc@example.com', 'bcc@example.com'],
            recipients,
        )
        self.assertIn('CC: cc@example.com', payload)
        self.assertNotIn('BCC:', payload)
        self.assertNotIn('bcc@example.com', payload)

    def test_rejects_newlines_in_message_headers(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject\nBCC: injected@example.com',
            Body='Body',
        )

        with self.assertRaises(ValueError):
            message.as_string()

    def test_rejects_newlines_in_envelope_recipients(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            BCC='bcc@example.com\nRCPT TO: injected@example.com',
            Subject='Subject',
            Body='Body',
        )
        server = FakeServer()

        with self.assertRaises(ValueError):
            royalmail.RoyalMail()._send(server, message)

        self.assertEqual([], server.calls)

    def test_rejects_newlines_in_attachment_content_id(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
            attachments=[
                ('missing.txt', 'image-cid\nBCC: injected@example.com', 'text/plain'),
            ],
        )

        with self.assertRaises(ValueError):
            message.as_string()

    def test_attachment_accepts_ascii_msg_id_content_id(self):
        fd, attachment_path = tempfile.mkstemp(suffix='.txt')
        try:
            os.write(fd, b'attachment body')
            os.close(fd)
            fd = None
            content_id = "part!#$%&'*+-/=?^_`{|}~.tag@example-domain.test"
            message = royalmail.Message(
                To='to@example.com',
                From='from@example.com',
                Subject='Subject',
                Body='Body',
                attachments=[(attachment_path, content_id, 'text/plain')],
            )

            parsed = message_from_string(message.as_string())
            attachment = parsed.get_payload()[1]
            self.assertEqual('<%s>' % content_id, attachment['Content-ID'])
            self.assertEqual('inline', attachment['Content-Disposition'])
        finally:
            if fd is not None:
                os.close(fd)
            os.remove(attachment_path)

    def test_rejects_malformed_attachment_content_ids_before_file_read(self):
        invalid_content_ids = (
            '',
            'has space',
            'left<bracket',
            'right>bracket',
            'double"quote',
            'back\\slash',
            'control\x00byte',
            u'non-ascii-\u2603',
            '.leading-dot',
            'trailing-dot.',
            'double..dot',
            'two@@domains',
            42,
        )

        for content_id in invalid_content_ids:
            message = royalmail.Message(
                To='to@example.com',
                From='from@example.com',
                Subject='Subject',
                Body='Body',
                attachments=[('missing.txt', content_id, 'text/plain')],
            )

            with self.assertRaises(ValueError):
                message.as_string()

    def test_rejects_newlines_in_attachment_filename(self):
        fd, attachment_path = tempfile.mkstemp(
            prefix='report\nBCC: injected@example.com-',
            suffix='.txt',
        )
        try:
            os.write(fd, b'attachment body')
            os.close(fd)
            fd = None
            message = royalmail.Message(
                To='to@example.com',
                From='from@example.com',
                Subject='Subject',
                Body='Body',
                attachments=[(attachment_path, None, 'text/plain')],
            )

            with self.assertRaises(ValueError):
                message.as_string()
        finally:
            if fd is not None:
                os.close(fd)
            os.remove(attachment_path)

    def test_rejects_newlines_in_attachment_mimetype(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
            attachments=[
                ('missing.txt', None, 'text/plain\nContent-Disposition: inline'),
            ],
        )

        with self.assertRaises(ValueError):
            message.as_string()

    def test_rejects_malformed_attachment_mimetype(self):
        invalid_mimetypes = (
            'text',
            'text/',
            '/plain',
            'text//plain',
            'text/plain; charset=utf-8',
            'text /plain',
            'text/\tplain',
            'text/pl:ain',
            'text/pl\xffain',
            42,
        )

        for mimetype in invalid_mimetypes:
            message = royalmail.Message(
                To='to@example.com',
                From='from@example.com',
                Subject='Subject',
                Body='Body',
                attachments=[
                    ('missing.txt', None, mimetype),
                ],
            )

            with self.assertRaises(ValueError):
                message.as_string()

    def test_send_quits_smtp_connection_when_sendmail_fails(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        original_smtp = royalmail.smtplib.SMTP
        FailingSMTP.instances = []
        royalmail.smtplib.SMTP = FailingSMTP

        try:
            with self.assertRaises(RuntimeError):
                royalmail.RoyalMail('smtp.example.com', 2525).send(message)
        finally:
            royalmail.smtplib.SMTP = original_smtp

        self.assertEqual(1, len(FailingSMTP.instances))
        self.assertTrue(FailingSMTP.instances[0].quit_called)

    def test_send_preserves_primary_failure_when_quit_also_fails(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        original_smtp = royalmail.smtplib.SMTP
        FailingQuitSMTP.instances = []
        FailingQuitSMTP.fail_send = True
        royalmail.smtplib.SMTP = FailingQuitSMTP

        try:
            with self.assertRaises(RuntimeError) as raised:
                royalmail.RoyalMail('smtp.example.com', 2525).send(message)
        finally:
            royalmail.smtplib.SMTP = original_smtp

        self.assertEqual('smtp send failed', str(raised.exception))
        self.assertEqual(1, len(FailingQuitSMTP.instances))
        self.assertTrue(FailingQuitSMTP.instances[0].quit_called)
        self.assertTrue(FailingQuitSMTP.instances[0].close_called)

    def test_send_propagates_quit_failure_after_successful_delivery(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        original_smtp = royalmail.smtplib.SMTP
        FailingQuitSMTP.instances = []
        FailingQuitSMTP.fail_send = False
        royalmail.smtplib.SMTP = FailingQuitSMTP

        try:
            with self.assertRaises(RuntimeError) as raised:
                royalmail.RoyalMail('smtp.example.com', 2525).send(message)
        finally:
            royalmail.smtplib.SMTP = original_smtp

        self.assertEqual('smtp quit failed', str(raised.exception))
        self.assertEqual(1, len(FailingQuitSMTP.instances))
        self.assertTrue(FailingQuitSMTP.instances[0].quit_called)
        self.assertTrue(FailingQuitSMTP.instances[0].close_called)

    def test_send_rejects_partial_recipient_refusal(self):
        message = royalmail.Message(
            To=['accepted@example.com', 'refused@example.com'],
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        original_smtp = royalmail.smtplib.SMTP
        RefusingSMTP.instances = []
        royalmail.smtplib.SMTP = RefusingSMTP

        try:
            with self.assertRaises(royalmail.smtplib.SMTPRecipientsRefused) as raised:
                royalmail.RoyalMail('smtp.example.com', 2525).send(message)
        finally:
            royalmail.smtplib.SMTP = original_smtp

        self.assertEqual(
            {'refused@example.com': (550, 'mailbox unavailable')},
            raised.exception.recipients,
        )
        self.assertEqual('quit', RefusingSMTP.instances[0].calls[-1])

    def test_tls_failure_survives_quit_failure_and_forces_close(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        original_smtp = royalmail.smtplib.SMTP
        FailingSetupSMTP.instances = []
        FailingSetupSMTP.fail_stage = 'starttls'
        FailingSetupSMTP.fail_quit = True
        royalmail.smtplib.SMTP = FailingSetupSMTP

        try:
            with self.assertRaises(RuntimeError) as raised:
                royalmail.RoyalMail('smtp.example.com', 2525, use_tls=True).send(message)
        finally:
            royalmail.smtplib.SMTP = original_smtp

        self.assertEqual('smtp tls failed', str(raised.exception))
        self.assertEqual(['ehlo', 'starttls', 'quit', 'close'], FailingSetupSMTP.instances[0].calls)

    def test_login_failure_still_quits_connection(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        original_smtp = royalmail.smtplib.SMTP
        FailingSetupSMTP.instances = []
        FailingSetupSMTP.fail_stage = 'login'
        FailingSetupSMTP.fail_quit = False
        royalmail.smtplib.SMTP = FailingSetupSMTP

        try:
            with self.assertRaises(RuntimeError) as raised:
                royalmail.RoyalMail(
                    'smtp.example.com',
                    2525,
                    usr='smtp-user',
                    pwd='smtp-password',
                ).send(message)
        finally:
            royalmail.smtplib.SMTP = original_smtp

        self.assertEqual('smtp login failed', str(raised.exception))
        self.assertEqual(
            [('login', 'smtp-user', 'smtp-password'), 'quit'],
            FailingSetupSMTP.instances[0].calls,
        )

    def test_batch_send_propagates_message_typeerror_without_retrying_list(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        original_smtp = royalmail.smtplib.SMTP
        TrackingSMTP.instances = []
        royalmail.smtplib.SMTP = TrackingSMTP
        sender = TypeErrorTrackingRoyalMail()

        try:
            with self.assertRaises(TypeError) as raised:
                sender.send([message])
        finally:
            royalmail.smtplib.SMTP = original_smtp

        self.assertEqual('message serialization failed', str(raised.exception))
        self.assertEqual([message], sender.attempted_messages)
        self.assertEqual('quit', TrackingSMTP.instances[0].calls[-1])

    def test_send_preserves_iterator_recipients_in_headers_and_envelope(self):
        message = royalmail.Message(
            To=(address for address in ['to@example.com', 'other@example.com']),
            CC=(address for address in ['cc@example.com']),
            BCC=(address for address in ['bcc@example.com']),
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        original_smtp = royalmail.smtplib.SMTP
        TrackingSMTP.instances = []
        royalmail.smtplib.SMTP = TrackingSMTP

        try:
            royalmail.RoyalMail('smtp.example.com', 2525).send(message)
        finally:
            royalmail.smtplib.SMTP = original_smtp

        sendmail = TrackingSMTP.instances[0].calls[0]
        parsed = message_from_string(sendmail[3])
        self.assertEqual(
            ['to@example.com', 'other@example.com', 'cc@example.com', 'bcc@example.com'],
            sendmail[2],
        )
        self.assertEqual('to@example.com, other@example.com', parsed['To'])
        self.assertEqual('cc@example.com', parsed['CC'])
        self.assertIsNone(parsed['BCC'])
        self.assertEqual(['to@example.com', 'other@example.com'], message.To)
        self.assertEqual(['cc@example.com'], message.CC)
        self.assertEqual(['bcc@example.com'], message.BCC)

    def test_use_tls_starts_tls_without_login_credentials(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        original_smtp = royalmail.smtplib.SMTP
        TrackingSMTP.instances = []
        royalmail.smtplib.SMTP = TrackingSMTP

        try:
            royalmail.RoyalMail('smtp.example.com', 2525, use_tls=True).send(message)
        finally:
            royalmail.smtplib.SMTP = original_smtp

        self.assertEqual(1, len(TrackingSMTP.instances))
        server = TrackingSMTP.instances[0]
        self.assertEqual(['ehlo', 'starttls', 'ehlo'], server.calls[:3])
        self.assertEqual('sendmail', server.calls[3][0])
        self.assertEqual('quit', server.calls[-1])
        self.assertEqual(
            [],
            [call for call in server.calls if isinstance(call, tuple) and call[0] == 'login'],
        )

    def test_manager_records_no_arg_send_exception(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        callbacks = []
        manager = royalmail.Manager(
            RoyalMail=NoArgFailingSender(),
            callback=callbacks.append,
        )
        manager.queue.put(message)
        manager.queue.put(None)

        manager.run()

        self.assertEqual(
            (False, -1, 'RuntimeError'),
            manager.results[message.message_id],
        )
        self.assertEqual([message.message_id], callbacks)
        self.assertEqual(0, manager.queue.unfinished_tasks)

    def test_manager_acknowledges_shutdown_sentinel(self):
        manager = royalmail.Manager(RoyalMail=SuccessfulSender())
        manager.queue.put(None)

        manager.run()

        self.assertEqual(0, manager.queue.unfinished_tasks)

    def test_manager_acknowledges_message_and_shutdown_sentinel(self):
        message = royalmail.Message(
            To='to@example.com',
            From='from@example.com',
            Subject='Subject',
            Body='Body',
        )
        sender = SuccessfulSender()
        callbacks = []
        manager = royalmail.Manager(RoyalMail=sender, callback=callbacks.append)
        manager.queue.put(message)
        manager.queue.put(None)

        manager.run()

        self.assertEqual([message], sender.messages)
        self.assertEqual((True, 0, ''), manager.results[message.message_id])
        self.assertEqual([message.message_id], callbacks)
        self.assertEqual(0, manager.queue.unfinished_tasks)

    def test_manager_sends_one_pass_iterable_batch_and_acknowledges_queue(self):
        messages = [
            royalmail.Message(
                To='first@example.com',
                From='from@example.com',
                Subject='First',
                Body='Body',
            ),
            royalmail.Message(
                To='second@example.com',
                From='from@example.com',
                Subject='Second',
                Body='Body',
            ),
        ]
        sender = SuccessfulSender()
        callbacks = []
        manager = royalmail.Manager(RoyalMail=sender, callback=callbacks.append)
        manager.queue.put(iter(messages))
        manager.queue.put(None)

        manager.run()

        self.assertEqual(messages, sender.messages)
        self.assertEqual(
            [(True, 0, ''), (True, 0, '')],
            [manager.results[message.message_id] for message in messages],
        )
        self.assertEqual(
            [message.message_id for message in messages],
            callbacks,
        )
        self.assertEqual(0, manager.queue.unfinished_tasks)

    def test_manager_abort_wakes_blocked_worker_and_balances_sentinel(self):
        manager = royalmail.Manager(RoyalMail=SuccessfulSender())
        manager.start()
        time.sleep(0.05)

        manager.abort = True
        manager.join(1.0)

        try:
            self.assertFalse(manager.is_alive())
            self.assertEqual(0, manager.queue.unfinished_tasks)
        finally:
            if manager.is_alive():
                manager.queue.put(None)
                manager.join(1.0)

    def test_manager_stop_is_idempotent_and_rejects_new_work(self):
        manager = royalmail.Manager(RoyalMail=SuccessfulSender())
        manager.start()
        manager.abort = True
        manager.abort = True
        manager.join(1.0)

        with self.assertRaises(RuntimeError):
            manager.send(royalmail.Message())

        self.assertEqual(0, manager.queue.unfinished_tasks)

    def test_manager_reports_batch_iterator_failure_after_finishing_queue(self):
        first = royalmail.Message(
            To='first@example.com',
            From='from@example.com',
            Subject='First',
            Body='Body',
        )
        second = royalmail.Message(
            To='second@example.com',
            From='from@example.com',
            Subject='Second',
            Body='Body',
        )

        def broken_batch():
            yield first
            raise RuntimeError('batch iteration failed')

        sender = SuccessfulSender()
        manager = royalmail.Manager(RoyalMail=sender)
        manager.send(broken_batch())
        manager.send(second)
        manager.send(None)
        manager.start()

        with self.assertRaises(RuntimeError) as raised:
            manager.join(1.0)

        self.assertEqual('batch iteration failed', str(raised.exception))
        self.assertFalse(manager.is_alive())
        self.assertEqual([first, second], sender.messages)
        self.assertEqual(0, manager.queue.unfinished_tasks)


if __name__ == '__main__':
    unittest.main()
