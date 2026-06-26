#coding: UTF8
"""
RoyalMail module

Simple front end to the smtplib and email modules,
to simplify sending email.

A lot of this code was taken from the online examples in the
email module documentation:
http://docs.python.org/library/email-examples.html

Released under MIT license.

Version 0.5 is based on a patch by Douglas Mayle

Sample code:

    import RoyalMail

    message = RoyalMail.Message()
    message.From = "me@example.com"
    message.To = "you@example.com"
    message.Subject = "My Vacation"
    message.Body = open("letter.txt", "rb").read()
    message.attach("picture.jpg")

    sender = RoyalMail.RoyalMail('mail.example.com')
    sender.send(message)

"""
import smtplib
import sys
import threading
import uuid
import re

try:
    import Queue
except ImportError:
    import queue as Queue

try:
    string_types = (basestring,)
    text_type = unicode
except NameError:
    string_types = (str,)
    text_type = str

# this is to support name changes
# from version 2.4 to version 2.5
try:
    from email import encoders
    from email.header import make_header
    from email.message import Message
    from email.mime.audio import MIMEAudio
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
except ImportError:
    from email import Encoders as encoders
    from email.Header import make_header
    from email.MIMEMessage import Message
    from email.MIMEAudio import MIMEAudio
    from email.MIMEBase import MIMEBase
    from email.MIMEImage import MIMEImage
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText

# For guessing MIME type based on file name extension
import mimetypes
import time

from os import path

MIME_TOKEN_RE = re.compile(r"^[A-Za-z0-9!#$%&'*+.^_`|~-]+$")
CONTENT_ID_RE = re.compile(
    r"^[A-Za-z0-9!#$%&'*+\-/=?^_`{|}~]+"
    r"(?:\.[A-Za-z0-9!#$%&'*+\-/=?^_`{|}~]+)*"
    r"(?:@[A-Za-z0-9!#$%&'*+\-/=?^_`{|}~]+"
    r"(?:\.[A-Za-z0-9!#$%&'*+\-/=?^_`{|}~]+)*)?\Z")


def _header_text(value, charset):
    if isinstance(value, text_type):
        return value
    return value.decode(charset)

class RoyalMail(object):
    """
    Represents an SMTP connection.

    Use login() to log in with a username and password.
    """

    def __init__(self, host="localhost", port=0, use_tls=False, usr=None, pwd=None,
                 tls_context=None):
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self._usr = usr
        self._pwd = pwd
        self.tls_context = tls_context

    def login(self, usr, pwd):
        self._usr = usr
        self._pwd = pwd

    def send(self, msg):
        """
        Send one message or a sequence of messages.

        Every time you call send, the RoyalMail creates a new
        connection, so if you have several emails to send, pass
        them as a list:
        RoyalMail.send([msg1, msg2, msg3])
        """
        server = smtplib.SMTP(self.host, self.port)

        delivery_error = None
        try:
            if self.use_tls is True:
                server.ehlo()
                if self.tls_context is None:
                    server.starttls()
                elif sys.version_info[0] < 3:
                    raise RuntimeError('TLS contexts require Python 3 smtplib support')
                else:
                    server.starttls(context=self.tls_context)
                server.ehlo()

            if self._usr and self._pwd:
                server.login(self._usr, self._pwd)

            if isinstance(msg, Message):
                messages = (msg,)
            else:
                messages = msg

            for message in messages:
                self._send(server, message)
        except BaseException as error:
            delivery_error = error

        cleanup_error = None
        try:
            server.quit()
        except BaseException as error:
            cleanup_error = error
            try:
                server.close()
            except BaseException:
                pass

        if delivery_error is not None:
            raise delivery_error
        if cleanup_error is not None:
            raise cleanup_error

    def _send(self, server, msg):
        """
        Sends a single message using the server
        we created in send()
        """
        me = msg._safe_header_value('From', msg.From)
        if isinstance(msg.To, string_types):
            to = msg._safe_header_values('To', [msg.To])
        else:
            to = msg._safe_header_values('To', list(msg.To))
            msg.To = to

        cc = []
        if msg.CC:
            if isinstance(msg.CC, string_types):
                cc = msg._safe_header_values('CC', [msg.CC])
            else:
                cc = msg._safe_header_values('CC', list(msg.CC))
                msg.CC = cc

        bcc = []
        if msg.BCC:
            if isinstance(msg.BCC, string_types):
                bcc = msg._safe_header_values('BCC', [msg.BCC])
            else:
                bcc = msg._safe_header_values('BCC', list(msg.BCC))
                msg.BCC = bcc

        you = to + cc + bcc
        refused = server.sendmail(me, you, msg.as_string())
        if refused:
            raise smtplib.SMTPRecipientsRefused(refused)

class Message(object):
    """
    Represents an email message.

    Set the To, From, Subject, and Body attributes as plain-text strings.
    Optionally, set the Html attribute to send an HTML email, or use the
    attach() method to attach files.

    Use the charset property to send messages using other than us-ascii

    If you specify an attachments argument, it should be a list of
    attachment filenames: ["file1.txt", "file2.txt"]

    `To` should be a string for a single address, and a sequence
    of strings for multiple recipients (castable to list)

    Send using the RoyalMail class.
    """

    def __init__(self, To=None, From=None, CC=None, BCC=None, Subject=None, Body=None, Html=None,
                 Date=None, attachments=None, charset=None):
        self.attachments = []
        if attachments:
            for attachment in attachments:
                self.attachments.append(self._attachment_details(attachment))
        self.To = To
        self.CC = CC
        self.BCC = BCC
        """string or iterable"""
        self.From = From
        """string"""
        self.Subject = Subject
        self.Body = Body
        self.Html = Html
        self.Date = Date or time.strftime("%a, %d %b %Y %H:%M:%S %z", time.gmtime())
        self.charset = charset or 'us-ascii'

        self.message_id = self.make_key()

    def make_key(self):
        return str(uuid.uuid4())

    def _attachment_details(self, attachment):
        if isinstance(attachment, string_types):
            return (attachment, None, None)
        try:
            values = iter(attachment)
        except TypeError:
            return (attachment, None, None)
        values = tuple(values)
        if len(values) == 2:
            return (values[0], values[1], None)
        if len(values) == 3:
            return values
        raise ValueError('Attachment descriptors must contain two or three values')

    def as_string(self):
        """Get the email as a string to send in the RoyalMail"""

        if not self.attachments:
            return self._plaintext()
        else:
            return self._multipart()

    def _plaintext(self):
        """Plain text email with no attachments"""

        if not self.Html:
            msg = MIMEText(self.Body, 'plain', self.charset)
        else:
            msg  = self._with_html()

        self._set_info(msg)
        return msg.as_string()

    def _with_html(self):
        """There's an html part"""

        outer = MIMEMultipart('alternative')

        part1 = MIMEText(self.Body, 'plain', self.charset)
        part2 = MIMEText(self.Html, 'html', self.charset)

        outer.attach(part1)
        outer.attach(part2)

        return outer

    def _set_info(self, msg):
        subject = self._safe_header_value('Subject', self.Subject)
        if self.charset == 'us-ascii':
            msg['Subject'] = subject
        else:
            msg['Subject'] = str(make_header([(_header_text(subject, self.charset), self.charset)]))

        msg['From'] = self._safe_header_value('From', self.From)

        if isinstance(self.To, string_types):
            msg['To'] = self._safe_header_value('To', self.To)
        else:
            self.To = self._safe_header_values('To', list(self.To))
            msg['To'] = ", ".join(self.To)

        if self.CC:
            if isinstance(self.CC, string_types):
                msg['CC'] = self._safe_header_value('CC', self.CC)
            else:
                self.CC = self._safe_header_values('CC', list(self.CC))
                msg['CC'] = ", ".join(self.CC)

        msg['Date'] = self._safe_header_value('Date', self.Date)

    def _safe_header_value(self, name, value):
        if isinstance(value, string_types) and ('\n' in value or '\r' in value):
            raise ValueError('%s header must not contain newlines' % name)
        return value

    def _safe_header_values(self, name, values):
        return [self._safe_header_value(name, value) for value in values]

    def _safe_mimetype(self, mimetype):
        if not isinstance(mimetype, string_types):
            raise ValueError('Attachment mimetype must be a string')
        if '\n' in mimetype or '\r' in mimetype:
            raise ValueError('Attachment mimetype must not contain newlines')
        parts = mimetype.split('/')
        if (len(parts) != 2 or
                not MIME_TOKEN_RE.match(parts[0]) or
                not MIME_TOKEN_RE.match(parts[1])):
            raise ValueError('Attachment mimetype must use ASCII maintype/subtype tokens')
        return mimetype

    def _safe_content_id(self, cid):
        if not isinstance(cid, string_types):
            raise ValueError('Content-ID must be a string')
        if '\n' in cid or '\r' in cid:
            raise ValueError('Content-ID header must not contain newlines')
        if not CONTENT_ID_RE.match(cid):
            raise ValueError('Content-ID must use printable ASCII msg-id token characters')
        return cid

    def _multipart(self):
        """The email has attachments"""

        msg = MIMEMultipart('related')

        if self.Html:
            outer = MIMEMultipart('alternative')

            part1 = MIMEText(self.Body, 'plain', self.charset)
            part1.add_header('Content-Disposition', 'inline')

            part2 = MIMEText(self.Html, 'html', self.charset)
            part2.add_header('Content-Disposition', 'inline')

            outer.attach(part1)
            outer.attach(part2)
            msg.attach(outer)
        else:
            msg.attach(MIMEText(self.Body, 'plain', self.charset))

        self._set_info(msg)
        msg.preamble = self.Subject

        for filename, cid, mimetype in self.attachments:
            self._add_attachment(msg, filename, cid, mimetype)

        return msg.as_string()

    def _add_attachment(self, outer, filename, cid, mimetype):
        """
        If mimetype is None, it will try to guess the mimetype
        """
        if cid is not None:
            cid = self._safe_content_id(cid)
            attachment_name = None
        else:
            attachment_name = self._safe_header_value(
                'Attachment filename', path.basename(filename))

        if mimetype is not None:
            ctype = self._safe_mimetype(mimetype)
            encoding = None
        else:
            ctype, encoding = mimetypes.guess_type(filename)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        fp = open(filename, 'rb')
        try:
            payload = fp.read()
        finally:
            fp.close()

        if maintype == 'text':
            # Note: we should handle calculating the charset
            msg = MIMEText(payload, _subtype=subtype, _charset=self.charset)
        elif maintype == 'image':
            msg = MIMEImage(payload, _subtype=subtype)
        elif maintype == 'audio':
            msg = MIMEAudio(payload, _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(payload)
            # Encode the payload using Base64
            encoders.encode_base64(msg)

        # Set the content-ID header
        if cid is not None:
            msg.add_header('Content-ID', '<%s>' % cid)
            msg.add_header('Content-Disposition', 'inline')
        else:
            # Set the filename parameter
            msg.add_header('Content-Disposition', 'attachment', filename=attachment_name)
        outer.attach(msg)

    def attach(self, filename, cid=None, mimetype=None):
        """
        Attach a file to the email. Specify the name of the file;
        Message will figure out the MIME type and load the file.

        Specify mimetype to set the MIME type manually.
        """

        self.attachments.append((filename, cid, mimetype))


class Manager(threading.Thread):
    """
    Manages the sending of email in the background

    you can supply it with an instance of class Mailler or pass in the same
    parameters that you would have used to create an instance of Mailler

    if a message was succesfully sent, self.results[msg.message_id] returns a 3
    element tuple (True/False, err_code, err_message)
    """

    def __init__(self, RoyalMail=None, callback=None, **kwargs):
        threading.Thread.__init__(self)

        self.queue = Queue.Queue()
        self.RoyalMail = RoyalMail
        self._abort = False
        self._stop_enqueued = False
        self.callback = callback
        self._results = {}
        self._result_lock = threading.RLock()
        self._state_lock = threading.RLock()
        self._worker_error = None

        if self.RoyalMail is None:
            sender_cls = globals()['RoyalMail']
            self.RoyalMail = sender_cls(
                host=kwargs.get('host', 'localhost'),
                port=kwargs.get('port', 25),
                use_tls=kwargs.get('use_tls', False),
                usr=kwargs.get('usr', None),
                pwd=kwargs.get('pwd', None),
                tls_context=kwargs.get('tls_context', None),
            )

    def __getattr__(self, name):
        if name == 'results':
            with self._result_lock:
                return self._results
        else:
            return None

    @property
    def abort(self):
        with self._state_lock:
            return self._abort

    @abort.setter
    def abort(self, value):
        if value:
            self._request_stop()
        else:
            with self._state_lock:
                if not self._stop_enqueued:
                    self._abort = False

    def _request_stop(self):
        with self._state_lock:
            if self._stop_enqueued:
                return
            self._abort = True
            self._stop_enqueued = True
            self.queue.put(None)

    def _record_worker_error(self, error):
        with self._state_lock:
            if self._worker_error is None:
                self._worker_error = error

    def _set_result(self, message_id, result):
        with self._result_lock:
            self._results[message_id] = result

    def _send_message(self, message):
        message_id = message.message_id
        self._set_result(message_id, (False, -1, ''))
        try:
            self.RoyalMail.send(message)
            self._set_result(message_id, (True, 0, ''))
        except Exception as error:
            if len(error.args) >= 2:
                err_code, err_message = error.args[0], error.args[1]
            elif len(error.args) == 1:
                err_code, err_message = -1, error.args[0]
            else:
                err_code, err_message = -1, error.__class__.__name__
            self._set_result(message_id, (False, err_code, err_message))

        if self.callback:
            try:
                self.callback(message_id)
            except:
                pass

    def run(self):

        while True:
            msg = self.queue.get(block=True)
            try:
                if msg is None:
                    with self._state_lock:
                        self._abort = True
                        self._stop_enqueued = True
                    break

                try:
                    if isinstance(msg, Message):
                        messages = (msg,)
                    else:
                        try:
                            messages = iter(msg)
                        except TypeError:
                            messages = (msg,)

                    for message in messages:
                        self._send_message(message)
                except Exception as error:
                    self._record_worker_error(error)

            finally:
                self.queue.task_done()

    def send(self, msg):
        if msg is None:
            self._request_stop()
            return
        with self._state_lock:
            if self._abort:
                raise RuntimeError('Manager has been stopped')
            self.queue.put(msg)

    def join(self, timeout=None):
        threading.Thread.join(self, timeout)
        if self.is_alive():
            return
        with self._state_lock:
            worker_error = self._worker_error
        if worker_error is not None:
            raise worker_error
