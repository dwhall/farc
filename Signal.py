__usage__ = """
    from Signal import Signal
    Signal.register("KEYPRESS")
    e = Event(Signal.KEYPRESS, 42)
"""


class Signal(object):
    """An asynchronous stimulus that triggers reactions.
    A unique identifier that, along with a value, specifies an Event.
    """

    _registry = {}
    _id = 0


    @staticmethod
    def register(signame):
        assert signame not in Signal._registry
        Signal._registry[signame] = Signal._id
        Signal._id += 1


    def __getattr__(self, name):
        return Signal._registry[name]


# Turn Signal into an instance of itself so getattr works
# this also prevents the creation of other instances of Signal
Signal = Signal()
