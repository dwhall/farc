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
    # In C code but not in book
    #RET_UNHANDLED
    #RET_ENTRY
    #RET_EXIT
    #RET_INITIAL


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
        assert me.initialState(me, event) == RET_TRAN

        t = Hsm.top

        while True:

            # From the designated initial state, record the path to top
            path = [me.initialState]
            EventProcessor.trig(me, me.initialState, Signal.EMPTY)
            while me.initialState != t:
                path.append(me.initialState)
                EventProcessor.trig(me, me.initialState, Signal.EMPTY)
            me.initialState = path[0]

            # Perform ENTRY action for each state from after-top to initial
            path.reverse()
            for s in path:
                EventProcessor.enter(me, s)

            # Current state becomes new source (-1 because path is reversed)
            t = path[-1]

            if EventProcessor.trig(me, t, Signal.INIT) != RET_TRAN:
                break

        # Current state is set to the final leaf state
        me.state = t


    def dispatch(me, event):
        """Follow the transitions until the event is handled or Top is reached
        p. 174
        """

        # Proceed to superstates if event is not handled
        exit_path = []
        r = RET_SUPER
        while r == RET_SUPER:
            s = me.state
            exit_path.append(s)
            r = s(me, event)    # possibly pass event to st handler

        if r == RET_TRAN:
            t = me.state

            # Record path from source to top
            while r != RET_IGNORED:
                s = me.state
                exit_path.append(s)
                r = Hsm.trig(me, s, Signal.EXIT)

            # Record path from target to top
            me.state = t
            entry_path = []
            r = RET_TRAN
            while r != RET_IGNORED:
                t = me.state
                entry_path.append(t)
                r = Hsm.trig(me, t, Signal.EXIT)

            # Find the Least Common Ancestor between the source and target
            i = -1
            while exit_path[i] == entry_path[i]:
                i -= 1

            # Exit all states in the exit path
            for st in exit_path[1:i]:
                r = Hsm.trig(me, st, Signal.EXIT)
                assert (r == RET_SUPER) or (r == RET_EXIT)

            # Enter all states in the entry path
            # This is done in the reverse order of the path
            for st in entry_path[i:0:-1]:
                r = Hsm.trig(me, st, Signal.ENTRY)
                assert r == RET_ENTRY

            # Pass the event to the target state
            st = entry_path[0]
            Hsm.trig(me, st, event)


    @staticmethod
    def isIn(me, state):
        pass

