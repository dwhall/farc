from pq.Hsm import Hsm


class Ahsm(Hsm):
    """An Augmented Hierarchical State Machine (AHSM); a.k.a. ActiveObject (AO).
    Adds a priority, message queue and methods to post to the queue.
    """

    def __init__(me, initialState, priority):
        Hsm.__init__(me, initialState)
        me.priority = priority
        me.mq = []
        # TODO: add thread/coroutine

    def postLIFO(me, evt):
        me.mq.append(evt)


    def postFIFO(me, evt):
        me.mq.insert(0, evt)
