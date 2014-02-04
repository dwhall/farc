"""Usage::

    import pq
    # Signals already created
    ev = pq.Event(Sig.SIG_ACK, 0)
"""


class Event(object):
    """An event is a pairing of a signal and a value.
    """

    def __init__(self, signal, value):
        self.signal = signal
        self.value = value

    @property
    def signal(self,):
        return self.signal

    @property
    def value(self,):
        return self.value
