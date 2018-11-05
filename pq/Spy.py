"""
Copyright 2018 Dean Hall.  See LICENSE file for details.
"""


class NopType(type):
    def __getattribute__(*args):
        """Returns a function that swallows any arguments and does nothing.
        So that Spy.anything() is inert.
        """
        return lambda *x: None

class Spy(metaclass=NopType):
    """Spy is designed so that calling Spy.anything() is inert
    unless the application first calls Framework.enable_spy()
    """
    pass
