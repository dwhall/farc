# farc

Framework for Asyncio/Actor/AHSM Run-to-completion Concurrency
written in Python3.
In other words, a cheap knock-off of QP (www.state-machine.com)
that uses coroutines instead of threads.
[This book](https://newcontinuum.dl.sourceforge.net/project/qpc/doc/PSiCC2.pdf)
describes QP and how to program hierarchical state machines.

This framework has fewer than 1000 LOC.  It allows the programmer to create highly-concurrent
programs by using a message-passing system and run-to-completion message handlers
within a state-machine architecture.  With these tools, complex, asynchronous operations
are decomposed into managable chunks of code.

Known Issue: On windows, Ctrl+C is supressed by asyncio event loop's run_forever() ([bug report](https://bugs.python.org/issue23057)).
The workaround is to inject an event to awake the event loop.

History:  This project used to be called "farc" but that name was taken in PyPI,
so I settled on farc.  If you see "farc" in the code anywhere, it means farc.
