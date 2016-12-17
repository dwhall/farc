from pq import Hsm
from pq import Framework


class Ahsm(Hsm):
    """An Augmented Hierarchical State Machine (AHSM); a.k.a. ActiveObject (AO).
    Adds a priority, message queue and methods to post to the queue.
    """

    def start(self, priority, initEvent): 
        self.priority = priority
        Framework.add(self)
        self.mq = []
        self.init(self, initEvent)


    def postLIFO(self, evt):
        self.mq.append(evt)


    def postFIFO(self, evt):
        self.mq.insert(0, evt)

    def subscribe(self, sigstr): pass
    def unsubscribe(self, sig): pass
