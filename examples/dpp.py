#!/usr/bin/env python3

"""
Copyright 2018 Dean Hall.  See LICENSE for details.

dpp.py - the Dining Philosopher's Problem
         implementation translated from Chaper 9.2 of PSiCC
         [https://newcontinuum.dl.sourceforge.net/project/qpc/doc/PSiCC2.pdf]
"""

import asyncio
import random

import farc


N_PHILO = 10

farc.Signal.register("EAT")
farc.Signal.register("DONE")
farc.Signal.register("TERMINATE")
farc.Signal.register("HUNGRY")

def PHILO_ID(act):
    global philo
    return philo.index(act)

def RIGHT(n):
    return (n + N_PHILO - 1) % N_PHILO

def LEFT(n):
    return (n + 1) % N_PHILO

def THINK_TIME():
    return random.randrange(1, 9)

def EAT_TIME():
    return random.randrange(1, 9)

class Table(farc.Ahsm):
    def __init__(self,):
        super().__init__()
        self.fork = ["FREE",] * N_PHILO
        self.isHungry = [False,] * N_PHILO

    @farc.Hsm.state
    def _initial(self, event):
        farc.Framework.subscribe("DONE", self)
        farc.Framework.subscribe("TERMINATE", self)
        return self.tran(Table._serving)

    @farc.Hsm.state
    def _serving(self, event):
        sig = event.signal
        if sig == farc.Signal.HUNGRY:
            # BSP.busyDelay()
            n = event.value
            assert n < N_PHILO and not self.isHungry[n]
            print(n, "hungry")
            m = LEFT(n)
            if self.fork[m] == "FREE" and self.fork[n] == "FREE":
                self.fork[m] = "USED"
                self.fork[n] = "USED"
                e = farc.Event(farc.Signal.EAT, n)
                farc.Framework.publish(e)
                print(n, "eating")
            else:
                self.isHungry[n] = True
            return self.handled(event)

        elif sig == farc.Signal.DONE:
            # BSP.busyDelay()
            n = event.value
            assert n < N_PHILO and not self.isHungry[n]
            print(n, "thinking")
            m = LEFT(n)
            assert self.fork[n] == "USED" and self.fork[m] == "USED"
            self.fork[m] = "FREE"
            self.fork[n] = "FREE"
            m = RIGHT(n)
            if self.isHungry[m] and self.fork[m] == "FREE":
                self.fork[n] = "USED"
                self.fork[m] = "USED"
                self.isHungry[m] = False
                e = farc.Event(farc.Signal.EAT, m)
                farc.Framework.publish(e)
                print(m, "eating")
            m = LEFT(n)
            n = LEFT(m)
            if self.isHungry[m] and self.fork[n] == "FREE":
                self.fork[m] = "USED"
                self.fork[n] = "USED"
                self.isHungry[m] = False
                e = farc.Event(farc.Signal.EAT, m)
                farc.Framework.publish(e)
                print(m, "eating")
            return self.handled(event)

        elif sig == farc.Signal.TERMINATE:
            farc.Framework.stop()

        return self.super(self.top)


class Philo(farc.Ahsm):

    @farc.Hsm.state
    def _initial(self, event):
        self.timeEvt = farc.TimeEvent("TIMEOUT")
        farc.Framework.subscribe("EAT", self)
        return self.tran(Philo._thinking)

    @farc.Hsm.state
    def _thinking(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            self.timeEvt.postIn(self, THINK_TIME())
            status = self.handled(event)

        elif sig == farc.Signal.TIMEOUT:
            status = self.tran(Philo._hungry)

        elif sig == farc.Signal.EAT or sig == farc.Signal.DONE:
            assert event.value != PHILO_ID(self)
            status = self.handled(event)

        else:
            status = self.super(self.top)
        return status

    @farc.Hsm.state
    def _hungry(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            e = farc.Event(farc.Signal.HUNGRY, PHILO_ID(self))
            farc.Framework.post_by_name(e, "Table")
            status = self.handled(event)

        elif sig == farc.Signal.EAT:
            if event.value == PHILO_ID(self):
                status = self.tran(Philo._eating)
            else:
                status = self.super(self.top) # UNHANDLED

        elif sig == farc.Signal.DONE:
            assert event.value != PHILO_ID(self)
            status = self.handled(event)

        else:
            status = self.super(self.top)
        return status

    @farc.Hsm.state
    def _eating(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            self.timeEvt.postIn(self, EAT_TIME())
            status = self.handled(event)

        elif sig == farc.Signal.EXIT:
            e = farc.Event(farc.Signal.DONE, PHILO_ID(self))
            farc.Framework.publish(e)
            status = self.handled(event)

        elif sig == farc.Signal.TIMEOUT:
            status = self.tran(Philo._thinking)

        elif sig == farc.Signal.EAT or sig == farc.Signal.DONE:
            assert event.value != PHILO_ID(self)
            status = self.handled(event)

        else:
            status = self.super(self.top)
        return status


def main():
    global philo

    table = Table()
    table.start(0)

    philo = []
    for n in range(N_PHILO):
        p = Philo()
        p.start(n+1)
        philo.append(p)

    farc.run_forever()


if __name__ == "__main__":
    main()
