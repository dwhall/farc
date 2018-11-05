"""
Copyright 2017 Dean Hall.  See LICENSE file for details.
"""


from .Signal import Signal
from .Framework import Framework
from .Ahsm import Ahsm


class TimeEvent(object):
    """TimeEvent is a composite class that contains an Event.
    A TimeEvent is created by the application and added to the Framework.
    The Framework then emits the event after the given delay.
    A one-shot TimeEvent is created by calling either postAt() or postIn().
    A periodic TimeEvent is created by calling the postEvery() method.
    """
    def __init__(self, signame):
        assert type(signame) == str
        self.signal = Signal.register(signame)
        self.value = None


    def postAt(self, act, abs_time):
        """Posts this TimeEvent to the given Ahsm at a specified time.
        """
        assert issubclass(type(act), Ahsm)
        self.act = act
        self.interval = 0
        Framework.addTimeEventAt(self, abs_time)


    def postIn(self, act, delta):
        """Posts this TimeEvent to the given Ahsm after the time delta.
        """
        assert issubclass(type(act), Ahsm)
        self.act = act
        self.interval = 0
        Framework.addTimeEvent(self, delta)


    def postEvery(self, act, delta):
        """Posts this TimeEvent to the given Ahsm after the time delta
        and every time delta thereafter until disarmed.
        """
        assert issubclass(type(act), Ahsm)
        self.act = act
        self.interval = delta
        Framework.addTimeEvent(self, delta)


    def disarm(self):
        """Removes this TimeEvent from the Framework's active time events.
        """
        self.act = None
        Framework.removeTimeEvent(self)
