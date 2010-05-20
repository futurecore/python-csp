from csp.cspprocess import Guard
import Channel as chnl
import cPickle
import uuid


DEBUG = False

class CChannel(Guard):

    def __init__(self):
        Guard.__init__(self)
        p = uuid.uuid4().int & 0xffffff
        av = uuid.uuid4().int & 0xffffff
        tak = uuid.uuid4().int & 0xffffff
        shm = uuid.uuid4().int & 0xffffff
        
        self.channel = chnl.getChannel(p, av, tak, shm)
        return

    def put(self,item):
        a = cPickle.dumps(item)
        chnl.put(self.channel,a)
        return

    def get(self):
        ret = None
        chnl.get(self.channel, ret)
        item = cPickle.loads(ret)
        if DEBUG: print item
        return item

    def is_selectable(self):
        a = chnl.is_selectable(self.channel)

        if a == 1:
            return True
        else:
            return False
        return

    def write(self,item):
        a = cPickle.dumps(item)
        chnl._write(self.channel,a,len(a))
        return

    def read(self):
        ret = chnl._read(self.channel)
        if DEBUG: print ret
        item = cPickle.loads(ret)
        if DEBUG: print item
        return item

    def enable(self):
        chnl.enable(self.channel)
        return

    def disable(self):
        chnl.disable(self.channel)
        return

    def select(self):
        ret = chnl._select(self.channel)
        item = cPickle.loads(ret)
        if DEBUG: print item
        return item

    def poison(self):
        chnl.poison(self.channel);
        return

    def getStatus(self):
        chnl.getStatus(self.channel)
        return

    def checkpoison(self):
        chnl.checkpoison()
        return
