from .Hsm import Hsm
from .Framework import Framework


class Ahsm(Hsm):
    """An Augmented Hierarchical State Machine (AHSM); a.k.a. ActiveObject (AO).
    Adds a priority, message queue and methods to post to the queue.
    """

    def start(self, priority, initEvent=None): 
        self.priority = priority
        Framework.add(self)
        self.mq = []
        self.init(self, initEvent)
        Framework._event_loop.call_soon_threadsafe(Framework.run)


    def postLIFO(self, evt):
        self.mq.append(evt)


    def postFIFO(self, evt):
        self.mq.insert(0, evt)
