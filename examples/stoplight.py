#!/usr/bin/env python3


import asyncio

import farc


class Stoplight(farc.Ahsm):

    @farc.Hsm.state
    def initial(me, event):
        print("Stoplight initial")

        te = farc.TimeEvent("TIME_TICK")
        te.postEvery(me, 2.0)

        return me.tran(me, Stoplight.red)


    @farc.Hsm.state
    def red(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("red enter")
            return me.handled(me, event)

        elif sig == farc.Signal.TIME_TICK:
            print("red next")
            return me.tran(me, Stoplight.green)

        elif sig == farc.Signal.EXIT:
            print("red exit")
            return me.handled(me, event)

        return me.super(me, me.top)


    @farc.Hsm.state
    def green(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("green enter")
            return me.handled(me, event)

        elif sig == farc.Signal.TIME_TICK:
            print("green next")
            return me.tran(me, Stoplight.red)

        elif sig == farc.Signal.EXIT:
            print("green exit")
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    sl = Stoplight(Stoplight.initial)
    sl.start(0)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
