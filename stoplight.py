#!/usr/bin/env python3


import asyncio

#kludge to import pq
import sys; sys.path.append("..")
from pq import *


class Stoplight(Ahsm):

    @staticmethod
    def initial(me, event):
        print("Stoplight initial")
        return me.tran(me, Stoplight.red)


    @staticmethod
    def red(me, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            print("red enter")
            return me.handled(me, event)

        if sig == Signal.STOPLIGHT_NEXT:
            print("red next")
            return me.tran(me, Stoplight.green)

        if sig == Signal.EXIT:
            print("red exit")
            return me.handled(me, event)

        return me.super(me, me.top)


    @staticmethod
    def green(me, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            print("green enter")
            return me.handled(me, event)

        if sig == Signal.STOPLIGHT_NEXT:
            print("green next")
            return me.tran(me, Stoplight.red)

        if sig == Signal.EXIT:
            print("green exit")
            return me.handled(me, event)

        return me.super(me, me.top)


@asyncio.coroutine
def ahsm_runner(loop):
    event_next = Event(Signal.STOPLIGHT_NEXT, None)

    sl = Stoplight(Stoplight.initial, 0)
    sl.init(sl, event_next)
    print("runner init")

    while True:
        yield from asyncio.sleep(2.0)
        sl.dispatch(sl, event_next)
        print("runner dispatch", sl.state)


if __name__ == "__main__":
    Signal.register("STOPLIGHT_NEXT")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(ahsm_runner(loop))
    loop.close()
