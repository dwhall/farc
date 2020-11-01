#!/usr/bin/env python3


import farc


class Countdown(farc.Ahsm):
    def __init__(self, count=3):
        super().__init__()
        self.count = count


    @farc.Hsm.state
    def _initial(self, event):
        print("_initial")
        self.te = farc.TimeEvent("TIME_TICK")
        return self.tran(Countdown._counting)


    @farc.Hsm.state
    def _counting(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("_counting")
            self.te.postIn(self, 1.0)
            return self.handled(event)

        elif sig == farc.Signal.TIME_TICK:
            print(self.count)

            if self.count == 0:
                return self.tran(Countdown._exiting)
            else:
                self.count -= 1
                self.te.postIn(self, 1.0)
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
    sl = Countdown(10)
    sl.start(0)

    farc.run_forever()
