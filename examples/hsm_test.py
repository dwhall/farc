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
    def _initial(self, event):
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
        self.running = True
        self.foo = 0
        return self.tran(FarcTest._s2)

    @farc.Hsm.state
    def _s(self, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return self.tran(FarcTest._s11)
        elif sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.i:
            if self.foo:
                self.foo = 0
                return self.handled(event)
        elif sig == farc.Signal.e:
            return self.tran(FarcTest._s11)
        elif sig == farc.Signal.t:
            return self.tran(FarcTest._exiting)
        return self.super(self.top)

    @farc.Hsm.state
    def _s1(self, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return self.tran(FarcTest._s11)
        elif sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.a:
            return self.tran(FarcTest._s1)
        elif sig == farc.Signal.b:
            return self.tran(FarcTest._s11)
        elif sig == farc.Signal.c:
            return self.tran(FarcTest._s2)
        elif sig == farc.Signal.d:
            if not self.foo:
                self.foo = 1
                # print(f"foo={self.foo}")
                return self.tran(FarcTest._s)
        elif sig == farc.Signal.f:
            return self.tran(FarcTest._s211)
        elif sig == farc.Signal.i:
            return self.handled(event)
        return self.super(FarcTest._s)

    @farc.Hsm.state
    def _s11(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.d:
            if self.foo:
                self.foo = 0
                # print(f"foo={self.foo}")
                return self.tran(FarcTest._s1)
        elif sig == farc.Signal.g:
            return self.tran(FarcTest._s211)
        elif sig == farc.Signal.h:
            return self.tran(FarcTest._s)
        return self.super(FarcTest._s1)

    @farc.Hsm.state
    def _s2(self, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return self.tran(FarcTest._s211)
        elif sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.c:
            return self.tran(FarcTest._s1)
        elif sig == farc.Signal.f:
            return self.tran(FarcTest._s11)
        elif sig == farc.Signal.i:
            if not self.foo:
                self.foo = 1
                # print(f"foo={self.foo}")
                return self.handled(event)
        return self.super(FarcTest._s)

    @farc.Hsm.state
    def _s21(self, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return self.tran(FarcTest._s211)
        elif sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.a:
            return self.tran(FarcTest._s21)
        elif sig == farc.Signal.b:
            return self.tran(FarcTest._s211)
        elif sig == farc.Signal.g:
            return self.tran(FarcTest._s1)
        return self.super(FarcTest._s2)

    @farc.Hsm.state
    def _s211(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.d:
            return self.tran(FarcTest._s21)
        elif sig == farc.Signal.h:
            return self.tran(FarcTest._s)
        return self.super(FarcTest._s21)

    @farc.Hsm.state
    def _exiting(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            self.running = False
            farc.Framework.stop()
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    farc.Spy.enable_spy(Spy)
    run_interactive = False
    tst_ahsm = FarcTest()
    Spy.on_framework_add(tst_ahsm)
    #
    if run_interactive:
        farc.Hsm.init(tst_ahsm)
        while tst_ahsm.running:
            sig_name = input('\tEvent --> ')
            try:
                sig = getattr(farc.Signal, sig_name)
            except LookupError:
                print("\nInvalid signal name", end="")
                continue
            event = farc.Event(sig, None)
            tst_ahsm.dispatch(event)

        print("\nTerminated")
    else:
        # seq = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a', 't']
        seq = ['g', 'i', 'a', 'd', 'd', 'c', 'e', 'e', 'g', 'i', 'i', 't']
        tst_ahsm.start(0)
        for sig in seq:
            event = farc.Event(getattr(farc.Signal, sig), None)
            tst_ahsm.post_fifo(event)
        farc.run_forever()
