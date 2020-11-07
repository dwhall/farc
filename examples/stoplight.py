#!/usr/bin/env python3


import farc


class Stoplight(farc.Ahsm):

    @farc.Hsm.state
    def _initial(self, event):
        print("Stoplight _initial")

        te = farc.TimeEvent("TIME_TICK")
        te.post_every(self, 2.0)

        return self.tran(Stoplight._red)


    @farc.Hsm.state
    def _red(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("_red enter")
            return self.handled(event)

        elif sig == farc.Signal.TIME_TICK:
            print("_red next")
            return self.tran(Stoplight._green)

        elif sig == farc.Signal.EXIT:
            print("_red exit")
            return self.handled(event)

        return self.super(self.top)


    @farc.Hsm.state
    def _green(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("_green enter")
            return self.handled(event)

        elif sig == farc.Signal.TIME_TICK:
            print("_green next")
            return self.tran(Stoplight._red)

        elif sig == farc.Signal.EXIT:
            print("_green exit")
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    sl = Stoplight()
    sl.start(0)

    farc.run_forever()
