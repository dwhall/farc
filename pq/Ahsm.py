"""
Copyright 2017 Dean Hall.  See LICENSE file for details.
"""


from .Hsm import Hsm
from .Framework import Framework


class Ahsm(Hsm):
    """An Augmented Hierarchical State Machine (AHSM); a.k.a. ActiveObject (AO).
    Adds a priority, message queue and methods to post to the queue.
    """

    def start(self, priority, initEvent=None):
        # must set the priority before Framework.add() which uses the priority
        self.priority = priority
        # must create a name before Framework.add() which uses the name
        self.name = "%s_%d" % (self.__class__.__name__, priority)
        Framework.add(self)
        self.mq = []
        self.init(self, initEvent)
        # Run to completion
        Framework._event_loop.call_soon_threadsafe(Framework.run)


    def postLIFO(self, evt):
        self.mq.append(evt)


    def postFIFO(self, evt):
        self.mq.insert(0, evt)
