#!/usr/bin/env python3


import asyncio

import farc


class Stoplight(farc.Ahsm):

    @farc.Hsm.state
    def _initial(me, event):
        print("Stoplight _initial")

        te = farc.TimeEvent("TIME_TICK")
        te.postEvery(me, 2.0)

        return me.tran(me, Stoplight._red)


    @farc.Hsm.state
    def _red(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("_red enter")
            return me.handled(me, event)

        elif sig == farc.Signal.TIME_TICK:
            print("_red next")
            return me.tran(me, Stoplight._green)

        elif sig == farc.Signal.EXIT:
            print("_red exit")
            return me.handled(me, event)

        return me.super(me, me.top)


    @farc.Hsm.state
    def _green(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("_green enter")
            return me.handled(me, event)

        elif sig == farc.Signal.TIME_TICK:
            print("_green next")
            return me.tran(me, Stoplight._red)

        elif sig == farc.Signal.EXIT:
            print("_green exit")
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    sl = Stoplight()
    sl.start(0)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
