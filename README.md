# farc

Framework for Asyncio/Actor/AHSM Run-to-completion Concurrency
written in Python3.  In other words, a cheap knock-off of
[QP](www.state-machine.com) that uses Python3 coroutines.
[This book](https://newcontinuum.dl.sourceforge.net/project/qpc/doc/PSiCC2.pdf)
describes QP and how to program [statecharts](https://statecharts.github.io)(a.k.a. hierarchical state machines).

This framework has fewer than 1000 LOC.  It allows the programmer to create
highly-concurrent programs by using a message-passing system and
run-to-completion message handlers within a state-machine architecture.
With these tools, complex, asynchronous operations are decomposed
into managable chunks of code.

Known Issue: On windows, Ctrl+C is supressed by asyncio event loop's
run_forever() ([bug report](https://bugs.python.org/issue23057)).
The workaround is to inject an event to awake the event loop.

Note:  This project used to be called "pq" but that name was taken in PyPI,
so I renamed to farc (ugh).


## Code Repository

https://github.com/dwhall/farc


## Release History

2020/11/07  0.2.0
- BREAKS API: Removed initEvent argument from Ahsm.start()
- BREAKS API: Renamed camel-case procedures with underscores
- BREAKS API: Eliminated @staticmethod and use of "me"
- BREAKS API: Removed VcdSpy (debug helper) class from default namespace
- Serialize Event values using pickle.  This might lead to a runtime error for some.
- call Framework.run() as soon as possible when an event is posted to AHSM (Max Peng).
- Reimplement HSM algorithm and include hsm_test (Sze Tan)
- Consolidated all files into `__init__.py`

2019/05/15  0.1.1
- Removed 'initialState' argument from farc.Hsm() constructor;
  framework now expects Hsm/Ahsm classes to have 'initial()' method.
- Made state methods private in examples to demonstrate a best-practice.
- Created farc.Framework.run_forever() helper function.
- Misc comment and doctring improvements

2018/10/09  0.1.0   Initial release
