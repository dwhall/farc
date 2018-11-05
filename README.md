# pq

A hierarchical state machine + message passing + run-to-completion framework
written in Python3 using asyncio

In other words, a cheap knock-off of QP (www.state-machine.com).

[This book](https://newcontinuum.dl.sourceforge.net/project/qpc/doc/PSiCC2.pdf)
describes QP and how to program hierarchical state machines.

Known Issue: On windows, Ctrl+C is supressed by asyncio event loop's run_forever() ([bug report](https://bugs.python.org/issue23057)).
Workaround is to inject an event to awake the event loop.
