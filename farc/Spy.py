"""
Copyright 2018 Dean Hall.  See LICENSE file for details.
"""


class Spy(object):
    """Spy - the farc framework debugging system

    farc source code has calls to various Spy.on_foo() methods
    placed in locations where very important things happen.
    By itself, Spy does nothing.
    When a farc application calls Spy.enable_spy(arg)
    with a class as the argument, that's when the farc framework's
    calls to Spy.on_foo() actually do something.

    See the VcdSpy module and class for an example of how
    to create a Spy debugging system.  In VcdSpy's case,
    it outputs farc message indicators and message handler
    execution timelines to a Value Change Dump (VCD) file.
    """
    _actv_cls = None

    @staticmethod
    def enable_spy(spy_cls):
        """Sets the Spy to use the given class
        and calls its initializer.
        """
        Spy._actv_cls = spy_cls
        spy_cls.init()


    def __getattr__(*args):
        """Returns
        1) the enable_spy static method if requested by name, or
        2) the attribute from the active class (if active class was set), or
        3) a function that swallows any arguments and does nothing.
        """
        if args[1] == "enable_spy":
            return Spy.enable_spy
        if Spy._actv_cls:
            return getattr(Spy._actv_cls, args[1])
        return lambda *x: None


# Singleton pattern:
# Turn Spy into an instance of itself so __getattribute__ works
# on anyone who calls "import Spy; Spy.foo()"
# This  prevents Spy() from creating a new instance
# and gives everyone who calls "import Spy" the same object
Spy = Spy()
