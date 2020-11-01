#!/usr/bin/env python3
"""This unit test proves that event values are immutable.
An event with a global-scope array is declared.
A simple state machine event handler modifies the value
of the event it is given.
The state machine is called with the global-scope array
and the framework is stopped.
The test passess if the global-scope array is unchanged.
"""


import asyncio
import unittest

import farc


# arbitrary mutable value
v = ["one",2,3]


class SimpleSM(farc.Ahsm):
    @farc.Hsm.state
    def _initial(self, event):
        return self.tran(SimpleSM.ready)


    @farc.Hsm.state
    def ready(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.APPEND:
            event.value.append("four")
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)

        return self.super(self.top)


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper


class TestSerialization(unittest.TestCase):
    def setUp(self):
        global v

        # create an event with the mutable value
        farc.Signal.register("APPEND")
        self.event = farc.Event(farc.Signal.APPEND, v)

        self.sm = SimpleSM()
        self.sm.start(0)


    @async_test
    def test_event_value_modification(self,):
        self.sm.postFIFO(self.event)
        farc.Framework.stop()
        self.assertEqual(v, ["one",2,3])


if __name__ == '__main__':
    unittest.main()
