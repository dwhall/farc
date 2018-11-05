#!/usr/bin/env python3

"""
Copyright 2018 Dean Hall.  See LICENSE for details.

dpp.py - the Dining Philosopher's Problem
         implementation translated from Chaper 9.2 of PSiCC
         [https://newcontinuum.dl.sourceforge.net/project/qpc/doc/PSiCC2.pdf]
"""

import asyncio
import random

import pq


N_PHILO = 10

pq.Signal.register("EAT")
pq.Signal.register("DONE")
pq.Signal.register("TERMINATE")
pq.Signal.register("HUNGRY")

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

class Table(pq.Ahsm):
    def __init__(self, initialState):
        super(Table, self).__init__(initialState)
        self.fork = ["FREE",] * N_PHILO
        self.isHungry = [False,] * N_PHILO

    def initial(self, event):
        pq.Framework.subscribe("DONE", self)
        pq.Framework.subscribe("TERMINATE", self)
        return self.tran(self, Table.serving)

    def serving(self, event):
        sig = event.signal
        if sig == pq.Signal.HUNGRY:
            # BSP.busyDelay()
            n = event.value
            assert n < N_PHILO and not self.isHungry[n]
            print(n, "hungry")
            m = LEFT(n)
            if self.fork[m] == "FREE" and self.fork[n] == "FREE":
                self.fork[m] = "USED"
                self.fork[n] = "USED"
                e = pq.Event(pq.Signal.EAT, n)
                pq.Framework.publish(e)
                print(n, "eating")
            else:
                self.isHungry[n] = True
            return self.handled(self, event)

        elif sig == pq.Signal.DONE:
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
                e = pq.Event(pq.Signal.EAT, m)
                pq.Framework.publish(e)
                print(m, "eating")
            m = LEFT(n)
            n = LEFT(m)
            if self.isHungry[m] and self.fork[n] == "FREE":
                self.fork[m] = "USED"
                self.fork[n] = "USED"
                self.isHungry[m] = False
                e = pq.Event(pq.Signal.EAT, m)
                pq.Framework.publish(e)
                print(m, "eating")
            return self.handled(self, event)

        elif sig == pq.Signal.TERMINATE:
            pq.Framework.stop()

        return self.super(self, self.top)


class Philo(pq.Ahsm):
    def initial(self, event):
        self.timeEvt = pq.TimeEvent("TIMEOUT")
        pq.Framework.subscribe("EAT", self)
        return self.tran(self, Philo.thinking)

    def thinking(self, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            self.timeEvt.postIn(self, THINK_TIME())
            status = self.handled(self, event)

        elif sig == pq.Signal.TIMEOUT:
            status = self.tran(self, Philo.hungry)

        elif sig == pq.Signal.EAT or sig == pq.Signal.DONE:
            assert event.value != PHILO_ID(self)
            status = self.handled(self, event)

        else:
            status = self.super(self, self.top)
        return status

    def hungry(self, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            e = pq.Event(pq.Signal.HUNGRY, PHILO_ID(self))
            pq.Framework.post(e, "Table")
            status = self.handled(self, event)

        elif sig == pq.Signal.EAT:
            if event.value == PHILO_ID(self):
                status = self.tran(self,Philo.eating)
            else:
                status = self.super(self, self.top) # UNHANDLED

        elif sig == pq.Signal.DONE:
            assert event.value != PHILO_ID(self)
            status = self.handled(self, event)

        else:
            status = self.super(self, self.top)
        return status

    def eating(self, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            self.timeEvt.postIn(self, EAT_TIME())
            status = self.handled(self, event)

        elif sig == pq.Signal.EXIT:
            e = pq.Event(pq.Signal.DONE, PHILO_ID(self))
            pq.Framework.publish(e)
            status = self.handled(self, event)

        elif sig == pq.Signal.TIMEOUT:
            status = self.tran(self,Philo.thinking)

        elif sig == pq.Signal.EAT or sig == pq.Signal.DONE:
            assert event.value != PHILO_ID(self)
            status = self.handled(self, event)

        else:
            status = self.super(self, self.top)
        return status


def main():
    global philo

    table = Table(Table.initial)
    table.start(0)

    philo = []
    for n in range(N_PHILO):
        p = Philo(Philo.initial)
        p.start(n+1)
        philo.append(p)

    loop = asyncio.get_event_loop()
    loop.run_forever()
    loop.close()


if __name__ == "__main__":
    main()
