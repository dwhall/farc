from pq.Hsm import Hsm


class Ahsm(Hsm):
    """An Augmented Hierarchical State Machine (AHSM); a.k.a. ActiveObject (AO).
    Adds a priority, message queue and methods to post to the queue.
    """

    def __init__(self, initialState, priority):
        Hsm.__init__(self, initialState)
        self.priority = priority
        self.mq = []


    def postLIFO(self, evt):
        self.mq.append(evt)


    def postFIFO(self, evt):
        self.mq.insert(0, evt)
