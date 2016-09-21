from pq.Event import Event


class EventProcessor(object):

    @staticmethod
    def trig(me, state, signal): state(me, Event.Reserved[signal])

    @staticmethod
    def enter(me, state): state(me, Event.ENTRY)

    @staticmethod
    def exit(me, state): state(me, Event.EXIT)
