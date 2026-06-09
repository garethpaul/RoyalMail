import os
import tempfile
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


class NoArgFailingSender(object):
    def send(self, message):
        raise RuntimeError()


class TrackingFile(object):
    def __init__(self):
        self.closed = False

    def read(self):
        return 'attachment body'

    def close(self):
        self.closed = True


class RoyalMailTests(unittest.TestCase):
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
            os.write(fd, 'attachment body')
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
            os.write(fd, 'attachment body')
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


if __name__ == '__main__':
    unittest.main()
