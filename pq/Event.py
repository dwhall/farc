from collections import namedtuple

from .Signal import Signal


Event = namedtuple("Event", ["signal", "value"])

# Instantiate the reserved (system) events
Event.EMPTY = Event(Signal.EMPTY, None)
Event.ENTRY = Event(Signal.ENTRY, None)
Event.EXIT = Event(Signal.EXIT, None)
Event.INIT = Event(Signal.INIT, None)

Event.SIGINT = Event(Signal.SIGINT, None)
Event.SIGTERM = Event(Signal.SIGTERM, None)

# The order of this tuple MUST match their respective signals
Event.reserved = (Event.EMPTY, Event.ENTRY, Event.EXIT, Event.INIT)
