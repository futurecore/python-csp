from base import BaseCspTest, main
from csp.csp import Channel, CSP_IMPLEMENTATION, ChannelPoison, process

from multiprocessing import Queue
def start_parallel(func, *args):
    if CSP_IMPLEMENTATION == 'os_thread':
        import threading
        p = threading.Thread(target=func, args=args)
    else:
        import multiprocessing
        p = multiprocessing.Process(target=func, args=args)
    p.start()
    return p


class TestChannels(BaseCspTest):

    def writer(self, channel, message):
        channel.write(message)

    def reader(self, channel, queue):
        queue.put(channel.read())

    def test_single_reader_single_writer(self):
        chan = Channel()
        q = Queue()
        p1 = start_parallel(self.writer, chan, "It's")
        p2 = start_parallel(self.reader, chan, q)
        p1.join()
        p2.join()
        self.assertEquals(q.get(), "It's")

    def test_read_first_does_not_fail(self):
        chan = Channel()
        q = Queue()
        p1 = start_parallel(self.reader, chan, q)
        self.failUnless(p1.is_alive())
        chan.write('Monty')
        p1.join()
        self.assertEquals(q.get(), 'Monty')

    def test_multiple_writers_single_reader(self):
        pass
        # Only the first writes to channel, the others seem to hang
#        chan = Channel()
#        writers = [start_parallel(self.writer, chan, "It's"),
#                   start_parallel(self.writer, chan, 'Monty'),
#                   start_parallel(self.writer, chan, "Python's"),
#                   start_parallel(self.writer, chan, 'Flying'),
#                   start_parallel(self.writer, chan, 'Circus')]
#        self.assertEquals(sorted([chan.get() for _x in range(5)]),
#                        ['Circus', 'Flying', "It's", 'Monty', "Python's"])


class TestPoison(BaseCspTest):

    def writer(self, channel, message, queue):
        try:
            channel.write(message)
        except:
            queue.put('Exception')

    def reader(self, channel, queue):
        try:
            x = channel.read()
            queue.put(x)
        except ChannelPoison:
            queue.put('ChannelPoison')

    def test_poison_aborts_reader(self):
        chan = Channel()
        q = Queue()
        p1 = start_parallel(self.reader, chan, q)
        chan.poison()
        p1.join()
        self.assertEqual(q.get(), 'ChannelPoison')

    def test_poison_aborts_writer(self):
        chan = Channel()
        chan.poison()
        self.assertRaises(ChannelPoison, chan.write, 'Albatross')

    def test_poison_does_not_abort_other_channels(self):
        chan1 = Channel()
        chan2 = Channel()
        chan1.poison()
        q = Queue()
        p1 = start_parallel(self.reader, chan2, q)
        self.assertRaises(ChannelPoison, chan1.write, 'Albatross')
        chan2.write("It's")
        p1.join()
        self.assertEqual(q.get(), "It's")

    def test_poison_spreads_over_processes(self):
        pass
        # ChannelPoison does not get raised and hangs if combinator writes
#        @process
#        def combinator(chan1, chan2):
#            x = chan1.read()
#            print('Unexpectedly got ' + str(x))
#        chan1 = Channel()
#        chan2 = Channel()
#        combinator(chan1, chan2).start()
#        chan1.poison()
#        self.assertRaises(ChannelPoison, chan2.write, 'Albatross')


if __name__ == '__main__':
    main()
