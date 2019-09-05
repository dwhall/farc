#!/usr/bin/env python3
"""This test exercises an HSM that is known to
contain all possible transition topologies.
The state machine comes from PSiCC2 Figure 2.11, p. 88.
"""


import unittest

import farc

# This lets us run the framework sequentially/synchronously to ease testing
farc.Framework.run_to_completion = farc.Framework.run


class AllTransitionsHsm(farc.Ahsm):
    """Hypothetical state machine that contains
    all possible state transition topologies
    up to four levels of state nesting.
    [PSiCC2 p.88]
    """
    def __init__(self):
        super().__init__()
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
        self.foo = None
        self.running = None

    @farc.Hsm.state
    def _initial(me, event):
        me.running = True
        me.foo = 0
        return me.tran(me, AllTransitionsHsm._s2)


    @farc.Hsm.state
    def _s(me, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return me.tran(me, AllTransitionsHsm._s11)
        elif sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.i:
            if me.foo:
                me.foo = 0
                return me.handled(me, event)
        elif sig == farc.Signal.e:
            return me.tran(me, AllTransitionsHsm._s11)
        elif sig == farc.Signal.t:
            return me.tran(me, AllTransitionsHsm._exiting)
        return me.super(me, me.top)


    @farc.Hsm.state
    def _s1(me, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return me.tran(me, AllTransitionsHsm._s11)
        elif sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.a:
            return me.tran(me, AllTransitionsHsm._s1)
        elif sig == farc.Signal.b:
            return me.tran(me, AllTransitionsHsm._s11)
        elif sig == farc.Signal.c:
            return me.tran(me, AllTransitionsHsm._s2)
        elif sig == farc.Signal.d:
            if not me.foo:
                me.foo = 1
                return me.tran(me, AllTransitionsHsm._s)
        elif sig == farc.Signal.f:
            return me.tran(me, AllTransitionsHsm._s211)
        elif sig == farc.Signal.i:
            return me.handled(me, event)
        return me.super(me, AllTransitionsHsm._s)


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
                return me.tran(me, AllTransitionsHsm._s1)
        elif sig == farc.Signal.g:
            return me.tran(me, AllTransitionsHsm._s211)
        elif sig == farc.Signal.h:
            return me.tran(me, AllTransitionsHsm._s)
        return me.super(me, AllTransitionsHsm._s1)


    @farc.Hsm.state
    def _s2(me, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return me.tran(me, AllTransitionsHsm._s211)
        elif sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.c:
            return me.tran(me, AllTransitionsHsm._s1)
        elif sig == farc.Signal.f:
            return me.tran(me, AllTransitionsHsm._s11)
        elif sig == farc.Signal.i:
            if not me.foo:
                me.foo = 1
                return me.handled(me, event)
        return me.super(me, AllTransitionsHsm._s)


    @farc.Hsm.state
    def _s21(me, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return me.tran(me, AllTransitionsHsm._s211)
        elif sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.a:
            return me.tran(me, AllTransitionsHsm._s21)
        elif sig == farc.Signal.b:
            return me.tran(me, AllTransitionsHsm._s211)
        elif sig == farc.Signal.g:
            return me.tran(me, AllTransitionsHsm._s1)
        return me.super(me, AllTransitionsHsm._s2)


    @farc.Hsm.state
    def _s211(me, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            return me.handled(me, event)
        elif sig == farc.Signal.EXIT:
            return me.handled(me, event)
        elif sig == farc.Signal.d:
            return me.tran(me, AllTransitionsHsm._s21)
        elif sig == farc.Signal.h:
            return me.tran(me, AllTransitionsHsm._s)
        return me.super(me, AllTransitionsHsm._s21)


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


class TestHsmTransitions(unittest.TestCase):
    def setUp(self):
        self.sm = AllTransitionsHsm()
        self.sm.start(0)


    def test_transitions(self,):
        trans_seq = (
            ("_s211", "g"),
            ("_s11", "i"),
            ("_s11", "a"),
            ("_s11", "d"),
            ("_s11", "d"),
            ("_s11", "c"),
            ("_s211", "e"),
            ("_s11", "e"),
            ("_s11", "g"),
            ("_s211", "i"),
            ("_s211", "i"),
            ("_s211", "t"),
            ("_exiting", "t") ) # this last input is irrelevant; test that we reached the exiting state

        for st,sig in trans_seq:
            self.assertEqual(self.sm.state.__name__, st) # check the current state
            event = farc.Event(getattr(farc.Signal, sig), None) # create event from the input signal
            self.sm.postFIFO(event)


if __name__ == '__main__':
    unittest.main()
