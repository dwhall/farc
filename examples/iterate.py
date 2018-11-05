#!/usr/bin/env python3


import asyncio

import pq


class Iterate(pq.Ahsm):
    def __init__(self, count=3):
        super().__init__(Iterate.initial)
        pq.Signal.register("ITERATE")
        self.count = count


    @pq.Hsm.state
    def initial(me, event):
        print("initial")
        me.iter_evt = pq.Event(pq.Signal.ITERATE, None)
        return me.tran(me, Iterate.iterating)


    @pq.Hsm.state
    def iterating(me, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            print("iterating")
            me.postFIFO(me.iter_evt)
            return me.handled(me, event)

        elif sig == pq.Signal.ITERATE:
            print(me.count)

            if me.count == 0:
                return me.tran(me, Iterate.done)
            else:
                # do work
                me.count -= 1
                me.postFIFO(me.iter_evt)
                return me.handled(me, event)

        return me.super(me, me.top)


    @pq.Hsm.state
    def done(me, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            print("done")
            pq.Framework.stop()
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    sl = Iterate(10)
    sl.start(0)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
