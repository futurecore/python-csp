import Channel as chnl
import cPickle
import uuid
from csp.guards import Guard 

class CChannel(Guard):

    def __init__(self):
        p = uuid.uuid4().int & 0xffffff
        av = uuid.uuid4().int & 0xffffff
        tak = uuid.uuid4().int & 0xffffff
        shm = uuid.uuid4().int & 0xffffff

        self.channel = chnl.getChannel(p,av,tak,shm)
        self.name = uuid.uuid1()
        return

    def __del__(self):
        chnl.removeChannel(self.channel)
        self.channel = None
        return

    def put(self,item):
        a = cPickle.dumps(item)
        chnl.put(self.channel,a);
        return

    def get(self):
        chnl.get(self.channel,ret)
        item = cPickle.loads(ret)
        print(item)
        return item

    def is_selectable(self):
        #print ( "is_selectable has been called" )
        a = chnl.is_selectable(self.channel)
        #print ( "is_selectable got ", a )
        if a == 1:
            return True
        else:
            return False;

    def write(self,item):
        a = cPickle.dumps(item)
        chnl._write(self.channel,a,len(a));
        return

    def read(self):
        print("invoked read")
        ret = chnl._read(self.channel)
        print(ret)
        item = cPickle.loads(ret)
        print(item)
        return item

    def enable(self):
        #print("ENABLED CALLED")
        chnl.enable(self.channel)
        #print("returning from enable")
        return

    def disable(self):
        chnl.disable(self.channel)
        return

    def select(self):
        #print("calling _select")
        ret = chnl._select(self.channel)
        item = cPickle.loads(ret)
        print(item)
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
