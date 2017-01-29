#!/usr/bin/env python3


import asyncio

from pq import *


class Three(Ahsm):

    @staticmethod
    def initial(me, event):
        print("Three initial")
    
        me.te = TimeEvent("TICK3")
        me.te.postEvery(me, 3)

        return me.tran(me, Three.three)


    @staticmethod
    def three(me, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            print("three enter")
            return me.handled(me, event)

        elif sig == Signal.TICK3:
            print("three tick")
            return me.handled(me, event)

        elif sig == Signal.EXIT:
            print("three exit")
            me.te.disarm()
            return me.handled(me, event)

        return me.super(me, me.top)


class Five(Ahsm):

    @staticmethod
    def initial(me, event):
        print("Five initial")
    
        me.te = TimeEvent("TICK5")
        me.te.postEvery(me, 5)

        return me.tran(me, Five.five)


    @staticmethod
    def five(me, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            print("five enter")
            return me.handled(me, event)

        elif sig == Signal.TICK5:
            print("five tick")
            return me.handled(me, event)

        elif sig == Signal.EXIT:
            print("five exit")
            me.te.disarm()
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    three = Three(Three.initial)
    three.start(0)

    five = Five(Five.initial)
    five.start(0)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()
