"""Usage::

    import pq
"""


class Hsm(object):
    """A Hierarchical State Machine (HSM) framework.
    Full support for hierarchical state nesting.
    Guaranteed entry/exit action execution on arbitrary state transitions.
    Full support of nested initial transitions.
    Fully reentrant event processor code with minimal stack requirements.
    Support for events with arbitrary parameters.
    """

    # Every state handler function must return one of these values
    RET_HANDLED = 0
    RET_IGNORED = 1
    RET_TRAN = 2
    RET_PARENT = 3


    def __init__(me, initialState): me.state = initialState # Ctor p. 162
    def handled(me, event): return RET_HANDLED
    def tran(me, nextState): me.state = nextState; return RET_TRAN
    def parent(me, parentState): me.state = parentState; return RET_PARENT # super
    def top(me, event): return RET_IGNORED # p. 165


    def initial(me, event = None):
        """Transitions to the initial state.  Follows any INIT transitions
        from the inital state and performs ENTRY actions as it proceeds.
        p. 172
        """

        # There MUST be an initial transition
        assert me.state(me, event) == RET_TRAN

        # From the designated initial state, record the path to top
        path = []
        while me.state != Hsm.top:
            path.append(me.state)
            EventProcessor.trig(me.state, Signal.EMPTY)

        # Perform ENTRY action for each state from after-top to initial
        path.reverse()
        for s in path:
            me.state = s
            EventProcessor.enter(me.state)

        # Follow any downstream INIT transitions and their ENTRY actions
        while RET_TRAN == EventProcessor.trig(me.state, Signal.INIT):
            s = me.state
            EventProcessor.enter(me.state)
        me.state = s


    def dispatch(me, event):
        """Follow the transitions until the event is handled or Top is reached
        """
        pass


    @staticmethod
    def isIn(state):
        pass

