#!/usr/bin/env python3


import asyncio

import farc


class Iterate(farc.Ahsm):
    def __init__(self,):
        super().__init__()
        farc.Signal.register("ITERATE")


    @farc.Hsm.state
    def _initial(self, event):
        print("_initial")
        self.iter_evt = farc.Event(farc.Signal.ITERATE, None)
        return self.tran(Iterate._iterating)


    @farc.Hsm.state
    def _iterating(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("_iterating")
            self.count = 10
            self.postFIFO(self.iter_evt)
            return self.handled(event)

        elif sig == farc.Signal.ITERATE:
            print(self.count)

            if self.count == 0:
                return self.tran(Iterate._exiting)
            else:
                # do work
                self.count -= 1
                self.postFIFO(self.iter_evt)
                return self.handled(event)

        return self.super(self.top)


    @farc.Hsm.state
    def _exiting(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("_exiting")
            farc.Framework.stop()
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    sl = Iterate()
    sl.start(0)

    farc.run_forever()