#!/usr/bin/env python3


import asyncio

from pq import *


class Mississippi(Ahsm):

    @staticmethod
    def initial(me, event):
        print("initial")
    
        me.teCount = TimeEvent("COUNT")
        me.teCount.postEvery(me, 0.001)

        me.tePrint = TimeEvent("PRINT")
        me.tePrint.postEvery(me, 1)

        me._count = 0

        return me.tran(me, Mississippi.count)


    @staticmethod
    def count(me, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            print("count enter")
            return me.handled(me, event)

        elif sig == Signal.PRINT:
            print(me._count, "millis")
            return me.handled(me, event)

        elif sig == Signal.COUNT:
            me._count += 1
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    print("Check to see how much CPU% a simple 1ms periodic function uses.")
    ms = Mississippi(Mississippi.initial)
    ms.start(0)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
