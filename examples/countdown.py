#!/usr/bin/env python3


import asyncio

import farc


class Countdown(farc.Ahsm):
    def __init__(self, count=3):
        super().__init__(Countdown.initial)
        self.count = count


    @farc.Hsm.state
    def initial(me, event):
        print("initial")
        me.te = farc.TimeEvent("TIME_TICK")
        return me.tran(me, Countdown.counting)


    @farc.Hsm.state
    def counting(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("counting")
            me.te.postIn(me, 1.0)
            return me.handled(me, event)

        elif sig == farc.Signal.TIME_TICK:
            print(me.count)

            if me.count == 0:
                return me.tran(me, Countdown.done)
            else:
                me.count -= 1
                me.te.postIn(me, 1.0)
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
    sl = Countdown(10)
    sl.start(0)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
