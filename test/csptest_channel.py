from base import BaseCspTest, main
from csp.csp import Channel, Par

class TestChannels(BaseCspTest):

    def test_single_source_sink_channel(self):
        chan = Channel()
        self.source('012345', chan) // (self.sink(6, chan), )
        self.assertEquals(self.output(), '012345')

    def test_multiple_source_sink_channel_triples(self):
        chans = [Channel() for x in range(5)]
        srces = Par(*[self.source(str(ii), ch) for ii, ch in enumerate(chans)])
        sinks = Par(*[self.sink(1, ch) for ch in chans])
        Par(srces, sinks).start()
        self.assertEquals(''.join(sorted(self.output())), '01234')

    def test_multiple_source_sink_tuples_one_channel(self):
        channel = Channel()
        srces = Par(*[self.source(str(ii), channel) for ii in range(5)])
        sinks = Par(*[self.sink(1, channel) for ii in range(5)])
        Par(srces, sinks).start()
        self.assertEquals(''.join(sorted(self.output())), '01234')


class TestPoison(BaseCspTest):

    def test_poison_aborts_channel(self):
        channel = Channel()
        channel.poison()
        Par(self.source('012345', channel),
            self.sink(6, channel)).start()
        self.assertEquals(self.output(), '')

    def test_poison_does_not_abort_other_channels(self):
        poisoned_channel = Channel()
        clean_channel = Channel()
        poisoned_channel.poison()
        Par(self.source('012345', clean_channel),
            self.sink(6, clean_channel)).start()
        self.assertEquals(self.output(), '012345')


class TestOverread(BaseCspTest):

    def do_not_test_overread(self): # as it will hang
        channel = Channel()
        self.source('012345', channel) // (self.sink(12, channel), )
        self.assertEquals(self.output(), '012345')


if __name__ == '__main__':
    main()
