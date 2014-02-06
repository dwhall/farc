__usage__ = """
    from Signal import Signal
    Signal.register("KEYPRESS")
    evt_kp = Event(Signal.KEYPRESS, 42)
    evt_kp.signal
    evt_kp.value
"""


from pq.Signal import Signal


class Event(object):
    """An event is an occurrence of significance to the system
    consisting of a Signal and a value.
    """

    def __init__(self, signal, value):
        self._signal = signal
        self._value = value


    @property
    def signal(self,):
        return self._signal


    @property
    def value(self,):
        return self._value


# Instantiate the reserved (system) events
Event.EMPTY = Event(Signal.EMPTY, None)
Event.ENTRY = Event(Signal.ENTRY, None)
Event.EXIT = Event(Signal.EXIT, None)
Event.INIT = Event(Signal.INIT, None)
