#!/usr/bin/env python3


import asyncio

#kludge to import pq
import sys; sys.path.append("..")
from pq import *


class Stoplight(Ahsm):

    # Register Signals used by this AHSM
    Signal.register("STOPLIGHT_NEXT")


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

        elif sig == Signal.STOPLIGHT_NEXT:
            print("red next")
            return me.tran(me, Stoplight.green)

        elif sig == Signal.EXIT:
            print("red exit")
            return me.handled(me, event)

        return me.super(me, me.top)


    @staticmethod
    def green(me, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            print("green enter")
            return me.handled(me, event)

        elif sig == Signal.STOPLIGHT_NEXT:
            print("green next")
            return me.tran(me, Stoplight.red)

        elif sig == Signal.EXIT:
            print("green exit")
            return me.handled(me, event)

        return me.super(me, me.top)


# This is a stand-in function to dispatch events while the Framework is being constructed
@asyncio.coroutine
def ahsm_runner():

    sl = Stoplight(Stoplight.initial)
    event_next = Event(Signal.STOPLIGHT_NEXT, None)
    sl.start(0, event_next)

    while True:
        yield from asyncio.sleep(2.0)
        print("Dispatch: {0} to {1}".format(event_next, sl.state))
        sl.dispatch(sl, event_next)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ahsm_runner())
    loop.close()
