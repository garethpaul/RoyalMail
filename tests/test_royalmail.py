import unittest

import royalmail


class FakeServer(object):
    def __init__(self):
        self.calls = []

    def sendmail(self, sender, recipients, payload):
        self.calls.append((sender, recipients, payload))


class RoyalMailTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
