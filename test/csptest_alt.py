from base import BaseCspTest, main
from csp.csp import Alt, Channel, process
import time
from multiprocessing import Queue

class TestAlt(BaseCspTest):

    def setUp(self):
        self.queue = Queue()
    def tearDown(self):
        self.queue.close()

    @process
    def writer(self, channel, message, delay):
        time.sleep(delay)
        channel.write(message)

    @process
    def chooser(self, *channels):
        alt = Alt(*channels)
        self.queue.put(alt.select())
        self.queue.put(alt.select())
        self.queue.put(alt.select())

    @process
    def or_chooser(self, channel1, channel2):
        self.queue.put(channel1 | channel2)
        self.queue.put(channel1 | channel2)

    def testAltSelectsFastest(self):
        c1, c2, c3 = Channel(), Channel(), Channel()
        self.chooser(c1, c2, c3) // (self.writer(c1, 'slowest', 0.4),
                                     self.writer(c2, 'fastest', 0),
                                     self.writer(c3, 'medium', 0.2))
        time.sleep(0.5)
        self.assertEqual(self.queue.get(), 'fastest')
        self.assertEqual(self.queue.get(), 'medium')
        self.assertEqual(self.queue.get(), 'slowest')

    def testOrSelectsFastest(self):
        c1, c2 = Channel(), Channel()
        self.or_chooser(c1, c2) // (self.writer(c1, 'slowest', 0.2),
                                    self.writer(c2, 'fastest', 0))
        time.sleep(0.3)
        self.assertEqual(self.queue.get(), 'fastest')
        self.assertEqual(self.queue.get(), 'slowest')

if __name__ == '__main__':
    main()
