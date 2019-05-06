#!/usr/bin/env python3


import asyncio

import farc


class Iterate(farc.Ahsm):
    def __init__(self,):
        super().__init__()
        farc.Signal.register("ITERATE")


    @farc.Hsm.state
    def _initial(me, event):
        print("_initial")
        me.iter_evt = farc.Event(farc.Signal.ITERATE, None)
        return me.tran(me, Iterate._iterating)


    @farc.Hsm.state
    def _iterating(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("_iterating")
            me.count = 10
            me.postFIFO(me.iter_evt)
            return me.handled(me, event)

        elif sig == farc.Signal.ITERATE:
            print(me.count)

            if me.count == 0:
                return me.tran(me, Iterate._exiting)
            else:
                # do work
                me.count -= 1
                me.postFIFO(me.iter_evt)
                return me.handled(me, event)

        return me.super(me, me.top)


    @farc.Hsm.state
    def _exiting(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("_exiting")
            farc.Framework.stop()
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    sl = Iterate()
    sl.start(0)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
