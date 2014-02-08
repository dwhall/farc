"""Usage::

    import pq
"""


from pq.Signal import Signal


class Hsm(object):
    """A Hierarchical State Machine (HSM) framework.
    Full support for hierarchical state nesting.
    Guaranteed entry/exit action execution on arbitrary state transitions.
    Full support of nested initial transitions.
    Fully reentrant event processor code with minimal stack requirements.
    Support for events with arbitrary parameters.
    """

    # Every state handler must return one of these values
    RET_HANDLED = 0
    RET_IGNORED = 1
    RET_TRAN = 2
    RET_SUPER = 3


    def __init__(me, initialState): me.state = me.top; me.initialState = initialState
    def handled(me, event): return RET_HANDLED
    def tran(me, nextState): me.state = nextState; return RET_TRAN
    def super(me, superState): me.state = superState; return RET_SUPER # p. 158


    @staticmethod
    def top(me, event): return RET_IGNORED # p. 163


    def initialize(me, event = None):
        """Transitions to the initial state.  Follows any INIT transitions
        from the inital state and performs ENTRY actions as it proceeds.
        Use this to pass any parameters to initialize the state machine.
        p. 172
        """

        # There MUST be an initial transition
        assert me.state(me, event) == RET_TRAN

        t = Hsm.top

        while True:

            # From the designated initial state, record the path to top
            path = []
            EventProcessor.trig(me, me.state, Signal.EMPTY)
            while me.state != t:
                path.append(me.state)
                EventProcessor.trig(me, me.state, Signal.EMPTY)
            me.state = path[0]

            # Perform ENTRY action for each state from after-top to initial
            path.reverse()
            for s in path:
                me.state = s
                EventProcessor.enter(me, me.state)

            # Current state becomes new source (-1 because path is reversed)
            t = path[-1]

            if EventProcessor.trig(me, t, Signal.INIT) != RET_TRAN:
                break

        # Current state is set to the final leaf state
        me.state = t


    def dispatch(me, event):
        """Follow the transitions until the event is handled or Top is reached
        """
        pass


    @staticmethod
    def isIn(me, state):
        pass

