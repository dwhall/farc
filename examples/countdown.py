#!/usr/bin/env python3


import asyncio

import pq


class Countdown(pq.Ahsm):
    def __init__(self, count=3):
        super().__init__(Countdown.initial)
        self.count = count


    @staticmethod
    def initial(me, event):
        print("initial")
        me.te = pq.TimeEvent("TIME_TICK")
        return me.tran(me, Countdown.counting)


    @staticmethod
    def counting(me, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            print("counting")
            me.te.postIn(me, 1.0)
            return me.handled(me, event)

        elif sig == pq.Signal.TIME_TICK:
            print(me.count)

            if me.count == 0:
                return me.tran(me, Countdown.done)
            else:
                me.count -= 1
                me.te.postIn(me, 1.0)
                return me.handled(me, event)

        return me.super(me, me.top)


    @staticmethod
    def done(me, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            print("done")
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    sl = Countdown(10)
    sl.start(0)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
