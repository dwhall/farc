"""Usage::

    import pq
    SIG = pq.SignalRegistry()
    SIG.register("ACK")
    SIG.register("BYE")
    print SIG.ACK
"""


_registry = {}


def genCount():
    i = 0
    while True:
        yield i
        i += 1
counter = genCount()


class SignalRegistry(object):
    """Signal Registry

    Create an instance of this class,
    then register as many signals as necessary.
    Each signal is assigned a unique number (monotonic, increasing)
    and the signal and value are kept in a dict.
    All instances of this class share the same dict
    so that signals are accessible to all.
    """

    def register(self, signame):
        global _registry
        assert signame not in _registry
        _registry[signame] = counter.next()

    def __getattr__(self, name):
        return _registry[name]
