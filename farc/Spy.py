"""
Copyright 2018 Dean Hall.  See LICENSE file for details.
"""


class Spy(object):
    """Spy is the debugging system for farc.
    farc contains a handful of Spy.on_foo() and Spy.on_bar() methods
    placed at critically useful locations throughout the framework.
    It is up to a Spy implementation (such as the included VcdSpy)
    to act on the Spy.on_*() methods.
    The programmer calls Spy.enable_spy(<Spy implementation class>)
    to activate the Spy system; otherwise, Spy does nothing.
    Therefore, this class is designed so that calling Spy.anything() is inert
    unless the application first calls Spy.enable_spy()
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
