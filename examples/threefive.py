#!/usr/bin/env python3


import asyncio

import pq


class Three(pq.Ahsm):

    @staticmethod
    def initial(me, event):
        print("Three initial")
        me.te = pq.TimeEvent("TICK3")
        return me.tran(me, Three.running)


    @staticmethod
    def running(me, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            print("three enter")
            me.te.postEvery(me, 3)
            return me.handled(me, event)

        elif sig == pq.Signal.TICK3:
            print("three tick")
            return me.handled(me, event)

        elif sig == pq.Signal.EXIT:
            print("three exit")
            me.te.disarm()
            return me.handled(me, event)

        return me.super(me, me.top)


class Five(pq.Ahsm):

    @staticmethod
    def initial(me, event):
        print("Five initial")
        me.te = pq.TimeEvent("TICK5")
        return me.tran(me, Five.running)


    @staticmethod
    def running(me, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            print("five enter")
            me.te.postEvery(me, 5)
            return me.handled(me, event)

        elif sig == pq.Signal.TICK5:
            print("five tick")
            return me.handled(me, event)

        elif sig == pq.Signal.EXIT:
            print("five exit")
            me.te.disarm()
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    three = Three(Three.initial)
    three.start(3)

    five = Five(Five.initial)
    five.start(5)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
