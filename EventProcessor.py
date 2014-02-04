"""Usage::

    import pq
    pq.EventProcessor.trig(state, Sig.SIG_ACK)
"""


class EventProcessor(object):
    """The EvenProcessor calls the state handler function
    with the active signal.
    """

    @staticmethod
    def trig(state, signal): state(signal)

    @staticmethod
    def enter(state,): state(Signal.ENTER)
