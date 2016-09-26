from collections import namedtuple
from pq.Signal import Signal


Event = namedtuple("Event", ["signal", "value"])

# Instantiate the reserved (system) events
Event.EMPTY = Event(Signal.EMPTY, None)
Event.ENTRY = Event(Signal.ENTRY, None)
Event.EXIT = Event(Signal.EXIT, None)
Event.INIT = Event(Signal.INIT, None)

# The order of this tuple MUST match their respective signals
Event.Reserved = (Event.EMPTY, Event.ENTRY, Event.EXIT, Event.INIT)


class EventProcessor(object):

    @staticmethod
    def trig(me, state, signal): return state(me, Event.Reserved[signal])


    @staticmethod
    def enter(me, state): return state(me, Event.ENTRY)


    @staticmethod
    def exit(me, state): return state(me, Event.EXIT)
