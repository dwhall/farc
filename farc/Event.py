"""
Copyright 2017 Dean Hall.  See LICENSE file for details.
"""

from collections import namedtuple

from .Signal import Signal


Event = namedtuple("Event", ["signal", "value"])

Event.__doc__ = """Events are a tuple of (signal, value) that are passed from
    one AHSM to another.  Signals are defined in each AHSM's source code
    by name, but resolve to a unique number.  Values are any python value,
    including containers that contain even more values.  Each AHSM state
    (static method) accepts an Event as the parameter and handles the event
    based on its Signal."""

# Instantiate the reserved (system) events
Event.EMPTY = Event(Signal.EMPTY, None)
Event.ENTRY = Event(Signal.ENTRY, None)
Event.EXIT = Event(Signal.EXIT, None)
Event.INIT = Event(Signal.INIT, None)

# Events for POSIX signals
Event.SIGINT = Event(Signal.SIGINT, None)   # (i.e. Ctrl+C)
Event.SIGTERM = Event(Signal.SIGTERM, None) # (i.e. kill <pid>)

# The order of this tuple MUST match their respective signals
Event.reserved = (Event.EMPTY, Event.ENTRY, Event.EXIT, Event.INIT)
