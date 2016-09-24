from pq.Event import Event


class EventProcessor(object):

    @staticmethod
    def trig(me, state, signal): return state(me, Event.Reserved[signal])


    @staticmethod
    def enter(me, state): return state(me, Event.ENTRY)


    @staticmethod
    def exit(me, state): return state(me, Event.EXIT)
