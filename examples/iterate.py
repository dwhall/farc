#!/usr/bin/env python3


import asyncio

import farc


class Iterate(farc.Ahsm):
    def __init__(self, count=3):
        super().__init__(Iterate.initial)
        farc.Signal.register("ITERATE")
        self.count = count


    @farc.Hsm.state
    def initial(me, event):
        print("initial")
        me.iter_evt = farc.Event(farc.Signal.ITERATE, None)
        return me.tran(me, Iterate.iterating)


    @farc.Hsm.state
    def iterating(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("iterating")
            me.postFIFO(me.iter_evt)
            return me.handled(me, event)

        elif sig == farc.Signal.ITERATE:
            print(me.count)

            if me.count == 0:
                return me.tran(me, Iterate.done)
            else:
                # do work
                me.count -= 1
                me.postFIFO(me.iter_evt)
                return me.handled(me, event)

        return me.super(me, me.top)


    @farc.Hsm.state
    def done(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("done")
            farc.Framework.stop()
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    sl = Iterate(10)
    sl.start(0)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
