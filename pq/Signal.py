

class Signal(object):
    """An asynchronous stimulus that triggers reactions.
    A unique identifier that, along with a value, specifies an Event.
    p. 154
    """

    _registry = {}
    _lookup = []


    @staticmethod
    def exists(signame):
        return signame in _registry


    @staticmethod
    def register(signame):
        """Registers the signame if it is not already registered.
        Returns the signal number for the signame.
        """
        assert type(signame) is str
        if signame in Signal._registry:
            # TODO: emit warning that signal is already registrered
            return Signal._registry[signame]
        else:
            sigid = len(Signal._lookup)
            Signal._registry[signame] = sigid
            Signal._lookup.append(signame)
            return sigid


    def __getattr__(self, name):
        return Signal._registry[name]


# Turn Signal into an instance of itself so getattr works.
# This also prevents Signal() from creating a new instance.
Signal = Signal()


# Register the reserved (system) signals
Signal.register("EMPTY") # 0
Signal.register("ENTRY") # 1
Signal.register("EXIT")  # 2
Signal.register("INIT")  # 3

# Signals that mirror POSIX signals
Signal.register("SIGINT")  # (i.e. Ctrl+C)
Signal.register("SIGTERM") # (i.e. kill <pid>)
