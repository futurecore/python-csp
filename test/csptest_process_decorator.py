from unittest import TestCase, main
from csp.csp import process, Channel, Par
import tempfile

@process
def sender(message, channel):
    channel.write(message)

@process
def receiver(channel, temp_file):
    temp_file.write(channel.read())
    temp_file.flush()


class TestUnbound(TestCase):

    def test_works(self):
        channel = Channel()
        temp_file = tempfile.TemporaryFile()
        Par(sender('123', channel), receiver(channel, temp_file)).start()
        temp_file.seek(0)
        self.assertEqual(temp_file.read(), '123')


class TestBound(TestCase):

    def setUp(self):
        self.channel = Channel()

    @process
    def sender(self, message):
        self.channel.write(message)

    @process
    def receiver(self):
        self.result = self.channel.read()

    def test_workd(self):
        Par(self.sender('123'), self.receiver()).start()
        self.assertEqual(self.result, '123')


if __name__ == '__main__':
    main()
