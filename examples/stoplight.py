#!/usr/bin/env python3


import asyncio, signal

from pq import *


class Stoplight(Ahsm):

    @staticmethod
    def initial(me, event):
        print("Stoplight initial")
    
        te = TimeEvent("TIME_TICK")
        te.postEvery(me, 2.0)

        return me.tran(me, Stoplight.red)


    @staticmethod
    def red(me, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            print("red enter")
            return me.handled(me, event)

        elif sig == Signal.TIME_TICK:
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

        elif sig == Signal.TIME_TICK:
            print("green next")
            return me.tran(me, Stoplight.red)

        elif sig == Signal.EXIT:
            print("green exit")
            return me.handled(me, event)

        return me.super(me, me.top)


def on_sigint(loop):
    """Callback for when ctrl+c is pressed
    """
    print("Bye.")
    loop.stop()


if __name__ == "__main__":
    sl = Stoplight(Stoplight.initial)
    sl.start(0)

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, on_sigint, loop)
    loop.add_signal_handler(signal.SIGTERM, on_sigint, loop)
    loop.run_forever()
    loop.close()
