from unittest import TestCase, main
from csp.csp import process, Channel, Par, CSP_IMPLEMENTATION
import tempfile

if CSP_IMPLEMENTATION == 'os_thread':
    from threading import Event
else:
    from multiprocessing import Event

@process
def sender(message, channel):
    channel.write(message)

@process
def receiver(channel, temp_file, event):
    temp_file.write(channel.read())
    temp_file.flush()
    event.set()


class TestUnbound(TestCase):

    def test_works(self):
        event = Event()
        channel = Channel()
        temp_file = tempfile.TemporaryFile()
        Par(sender('123', channel), receiver(channel, temp_file, event)).start()
        event.wait()
        temp_file.seek(0)
        self.assertEqual(temp_file.read(), '123')


class TestBound(TestCase):

    def setUp(self):
        self.channel = Channel()
        self.event = Event()

    @process
    def sender(self, message):
        self.channel.write(message)

    @process
    def receiver(self):
        self.result = self.channel.read()
        self.event.set()

    def test_works(self):
        Par(self.sender('123'), self.receiver()).start()
        self.event.wait()
        self.assertEqual(self.result, '123')


if __name__ == '__main__':
    main()
