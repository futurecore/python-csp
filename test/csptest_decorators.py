from unittest import TestCase, main
from csp.csp import Channel, process, CSPProcess
from csp.csp import forever, CSPServer, CSP_IMPLEMENTATION

@process
def unbound_process(message, channel):
    channel.write(message)

@forever
def unbound_forever(message, channel):
    channel.write(message)
    yield
    # TODO: background process dies with StopIteration

class TestUnbound(TestCase):

    def test_process(self):
        channel = Channel()
        pp = unbound_process('Albatross', channel)
        self.assertEqual(type(pp), CSPProcess)
        pp.start()
        self.assertEqual(channel.read(), 'Albatross')

    def test_forever(self):
        channel = Channel()
        pp = unbound_forever('Albatross?', channel)
        self.assertEqual(type(pp), CSPServer)
        pp.start()
        self.assertEqual(channel.read(), 'Albatross?')


class TestBound(TestCase):

    def setUp(self):
        self.channel = Channel()

    @process
    def bound_process(self, message):
        self.channel.write(message)

    @forever
    def bound_forever(self, message):
        self.channel.write(message)
        yield

    def test_process(self):
        pp = self.bound_process('Albatross')
        self.assertEqual(type(pp), CSPProcess)
        pp.start()
        self.assertEqual(self.channel.read(), 'Albatross')

    def test_forever(self):
        pp = self.bound_forever('Albatross?')
        self.assertEqual(type(pp), CSPServer)
        pp.start()
        self.assertEqual(self.channel.read(), 'Albatross?')


if __name__ == '__main__':
    main()
