#!/usr/bin/env python3

import unittest

import farc


class TestEventEquality(unittest.TestCase):
    def test_events_equal(self,):
        e1 = farc.Event(0, 0)
        e2 = farc.Event(1 - 1, 2 - 2)
        # First prove the events are separate objects
        self.assertNotEqual(id(e1), id(e2))
        # Now prove the event equality method works
        self.assertTrue(e1 == e2)

    def test_events_not_equal(self,):
        e1 = farc.Event(4, "four")
        e2 = farc.Event(2, "two")   # both fields differ
        e3 = farc.Event(2, "four")  # signal differs
        e4 = farc.Event(4, "four!") # value differs

        self.assertFalse(e1 == e2)
        self.assertFalse(e1 == e3)
        self.assertFalse(e1 == e4)

if __name__ == '__main__':
    unittest.main()
