from collections import namedtuple

from pq import Signal


Event = namedtuple("Event", ["signal", "value"])

# Instantiate the reserved (system) events
Event.EMPTY = Event(Signal.EMPTY, None)
Event.ENTRY = Event(Signal.ENTRY, None)
Event.EXIT = Event(Signal.EXIT, None)
Event.INIT = Event(Signal.INIT, None)

# The order of this tuple MUST match their respective signals
Event.Reserved = (Event.EMPTY, Event.ENTRY, Event.EXIT, Event.INIT)


class TimeEvent(Event):
    """TimeEvent is an Event that is emitted after a given delay.
    A one-shot TimeEvent is created by calling the postIn() method.
    A periodic TimeEvent is created by calling the postEvery() method.
    """
    def __new__(cls, sig, val):
        return super(TimeEvent, cls).__new__(cls, sig, val)


    def postIn(me, act, delta):
        """Posts this TimeEvent to the given Ahsm after the time delta.
        """
        me.act = act
        me.interval = 0
        return Framework.addTimeEvent(me, act, delta)


    def postEvery(me, act, delta):
        """Posts this TimeEvent to the given Ahsm after the time delta
        and every time delta thereafter until disarmed.
        """
        assert issubclass(type(act), Ahsm)
        me.act = act
        me.interval = delta
        return Framework.addTimeEvent(me, act, delta)


    def disarm(me):
        """Removes this TimeEvent from the Framework's active time events.
        """
        me.act = None
        Framework.removeTimeEvent(me)


# Key Events
# at init time, either copy from app6.py or use urwid

