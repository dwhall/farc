from collections import namedtuple

from pq import Signal


Event = namedtuple("Event", ["signal", "value"])

# Instantiate the reserved (system) events
Event.EMPTY = Event(Signal.EMPTY, None)
Event.ENTRY = Event(Signal.ENTRY, None)
Event.EXIT = Event(Signal.EXIT, None)
Event.INIT = Event(Signal.INIT, None)

# The order of this tuple MUST match their respective signals
Event.reserved = (Event.EMPTY, Event.ENTRY, Event.EXIT, Event.INIT)


class TimeEvent(Event):
    """TimeEvent is a composite class that contains an Event.
    A TimeEvent is created by the application and added to the Framework.
    The Framework then emits the event after the given delay.
    A one-shot TimeEvent is created by calling the postIn() method.
    A periodic TimeEvent is created by calling the postEvery() method.
    """
    def __init__(self, signame):
        sigid = Signal.register(signame)
        self.signal = sigid
        self.value = None


    def postIn(self, act, delta):
        """Posts this TimeEvent to the given Ahsm after the time delta.
        """
        assert issubclass(type(act), Ahsm)
        self.act = act
        self.interval = 0
        Framework.addTimeEvent(self, act, delta)


    def postEvery(self, act, delta):
        """Posts this TimeEvent to the given Ahsm after the time delta
        and every time delta thereafter until disarmed.
        """
        assert issubclass(type(act), Ahsm)
        self.act = act
        self.interval = delta
        Framework.addTimeEvent(self, act, delta)


    def disarm(self):
        """Removes this TimeEvent from the Framework's active time events.
        """
        self.act = None
        Framework.removeTimeEvent(self)


# Key Events
# at init time, either copy from app6.py or use urwid

