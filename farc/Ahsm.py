"""
Copyright 2017 Dean Hall.  See LICENSE file for details.
"""

import collections

from .Hsm import Hsm
from .Framework import Framework


class Ahsm(Hsm):
    """An Augmented Hierarchical State Machine (AHSM); a.k.a. ActiveObject/AO.
    Adds a priority, message queue and methods to work with the queue.
    """

    def start(self, priority, initEvent=None):
        # must set the priority before Framework.add() which uses the priority
        self.priority = priority
        Framework.add(self)
        self.mq = collections.deque()
        self.init(self, initEvent)
        # Run to completion
        Framework._event_loop.call_soon_threadsafe(Framework.run)

    def postLIFO(self, evt):
        self.mq.append(evt)

    def postFIFO(self, evt):
        self.mq.appendleft(evt)

    def pop_msg(self,):
        return self.mq.pop()

    def has_msgs(self,):
        return len(self.mq) > 0
