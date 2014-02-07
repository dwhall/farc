"""Usage::

    import pq
    pq.EventProcessor.trig(state, Si)
"""


class EventProcessor(object):

    @staticmethod
    def trig(me, state, signal): state(me, Event.Reserved(signal))

    @staticmethod
    def enter(me, state,): state(me, Event.ENTRY)
