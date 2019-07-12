#!/usr/bin/env python3

import farc
from farc.SimpleSpy import SimpleSpy as Spy


class FarcTest(farc.Ahsm):
    def __init__(self):
        super().__init__()
        # Define signals that this chart subscribes to
        self.foo = None
        self.running = None

    @farc.Hsm.state
    def _initial(me, event):
        farc.Signal.register("a")
        farc.Signal.register("b")
        farc.Signal.register("c")
        farc.Signal.register("d")
        farc.Signal.register("e")
        farc.Signal.register("f")
        farc.Signal.register("g")
        farc.Signal.register("h")
        farc.Signal.register("i")
        farc.Signal.register("t")
        me.running = True
        me.foo = 0
        return me.tran(me, FarcTest._s2)

    @farc.Hsm.state
    def _s(me, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return me.tran(me, FarcTest._s11)
        elif sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.i:
            if me.foo:
                me.foo = 0
                return me.handled(me, event)
        elif sig == farc.Signal.e:
            return me.tran(me, FarcTest._s11)
        elif sig == farc.Signal.t:
            return me.tran(me, FarcTest._exiting)
        return me.super(me, me.top)

    @farc.Hsm.state
    def _s1(me, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return me.tran(me, FarcTest._s11)
        elif sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.a:
            return me.tran(me, FarcTest._s1)
        elif sig == farc.Signal.b:
            return me.tran(me, FarcTest._s11)
        elif sig == farc.Signal.c:
            return me.tran(me, FarcTest._s2)
        elif sig == farc.Signal.d:
            if not me.foo:
                me.foo = 1
                # print(f"foo={me.foo}")
                return me.tran(me, FarcTest._s)
        elif sig == farc.Signal.f:
            return me.tran(me, FarcTest._s211)
        elif sig == farc.Signal.i:
            return me.handled(me, event)
        return me.super(me, FarcTest._s)

    @farc.Hsm.state
    def _s11(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.d:
            if me.foo:
                me.foo = 0
                # print(f"foo={me.foo}")
                return me.tran(me, FarcTest._s1)
        elif sig == farc.Signal.g:
            return me.tran(me, FarcTest._s211)
        elif sig == farc.Signal.h:
            return me.tran(me, FarcTest._s)
        return me.super(me, FarcTest._s1)

    @farc.Hsm.state
    def _s2(me, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return me.tran(me, FarcTest._s211)
        elif sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.c:
            return me.tran(me, FarcTest._s1)
        elif sig == farc.Signal.f:
            return me.tran(me, FarcTest._s11)
        elif sig == farc.Signal.i:
            if not me.foo:
                me.foo = 1
                # print(f"foo={me.foo}")
                return me.handled(me, event)
        return me.super(me, FarcTest._s)

    @farc.Hsm.state
    def _s21(me, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return me.tran(me, FarcTest._s211)
        elif sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.a:
            return me.tran(me, FarcTest._s21)
        elif sig == farc.Signal.b:
            return me.tran(me, FarcTest._s211)
        elif sig == farc.Signal.g:
            return me.tran(me, FarcTest._s1)
        return me.super(me, FarcTest._s2)

    @farc.Hsm.state
    def _s211(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.d:
            return me.tran(me, FarcTest._s21)
        elif sig == farc.Signal.h:
            return me.tran(me, FarcTest._s)
        return me.super(me, FarcTest._s21)

    @farc.Hsm.state
    def _exiting(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            me.running = False
            farc.Framework.stop()
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)

        return me.super(me, me.top)


if __name__ == "__main__":
    farc.Spy.enable_spy(Spy)
    run_interactive = True
    me = FarcTest()
    Spy.on_framework_add(me)
    #
    if run_interactive:
        farc.Hsm.init(me)
        while me.running:
            sig_name = input('\tEvent --> ')
            try:
                sig = getattr(farc.Signal, sig_name)
            except LookupError:
                print("\nInvalid signal name", end="")
                continue
            event = farc.Event(sig, None)
            farc.Hsm.dispatch(me, event)

        print("\nTerminated")
    else:
        # seq = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a', 't']
        seq = ['g', 'i', 'a', 'd', 'd', 'c', 'e', 'e', 'g', 'i', 'i', 't']
        me.start(0)
        for sig in seq:
            event = farc.Event(getattr(farc.Signal, sig), None)
            me.postFIFO(event)
        farc.run_forever()
