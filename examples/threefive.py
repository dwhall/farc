#!/usr/bin/env python3


import farc


class Three(farc.Ahsm):

    @farc.Hsm.state
    def _initial(me, event):
        print("Three _initial")
        me.te = farc.TimeEvent("TICK3")
        return me.tran(me, Three._running)


    @farc.Hsm.state
    def _running(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("three enter")
            me.te.postEvery(me, 3)
            return me.handled(me, event)

        elif sig == farc.Signal.TICK3:
            print("three tick")
            return me.handled(me, event)

        elif sig == farc.Signal.EXIT:
            print("three exit")
            me.te.disarm()
            return me.handled(me, event)

        return me.super(me, me.top)


class Five(farc.Ahsm):

    @farc.Hsm.state
    def _initial(me, event):
        print("Five _initial")
        me.te = farc.TimeEvent("TICK5")
        return me.tran(me, Five._running)


    @farc.Hsm.state
    def _running(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("five enter")
            me.te.postEvery(me, 5)
            return me.handled(me, event)

        elif sig == farc.Signal.TICK5:
            print("five tick")
            return me.handled(me, event)

        elif sig == farc.Signal.EXIT:
            print("five exit")
            me.te.disarm()
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    # Uncomment this line to get a visual execution trace (to demonstrate debugging)
    #farc.Spy.enable_spy(farc.VcdSpy)

    three = Three()
    five = Five()

    three.start(3)
    five.start(5)

    farc.run_forever()
