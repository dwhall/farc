#!/usr/bin/env python3


import farc


class Mississippi(farc.Ahsm):

    @farc.Hsm.state
    def _initial(self, event):
        print("_initial")
        self.teCount = farc.TimeEvent("COUNT")
        self.tePrint = farc.TimeEvent("PRINT")
        return self.tran(Mississippi._counting)


    @farc.Hsm.state
    def _counting(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("_counting enter")
            self._count = 0
            self.teCount.postEvery(self, 0.001)
            self.tePrint.postEvery(self, 1.000)
            return self.handled(event)

        elif sig == farc.Signal.COUNT:
            self._count += 1
            return self.handled(event)

        elif sig == farc.Signal.PRINT:
            print(self._count, "millis")
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    print("Check to see how much CPU% a simple 1ms periodic function uses.")
    ms = Mississippi()
    ms.start(0)

    farc.run_forever()
