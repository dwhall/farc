from pq.Signal import Signal
from pq.EventProcessor import EventProcessor


class Hsm(object):
    """A Hierarchical State Machine (HSM) framework.
    Full support for hierarchical state nesting.
    Guaranteed entry/exit action execution on arbitrary state transitions.
    Full support of nested initial transitions.
    Support for events with arbitrary parameters.
    """

    # Every state handler must return one of these values
    RET_HANDLED = 0
    RET_IGNORED = 1
    RET_TRAN = 2
    RET_SUPER = 3
    # In C code but not in book
    # RET_UNHANDLED
    # RET_ENTRY
    # RET_EXIT
    # RET_INITIAL


    def __init__(self, initialState): self.state = self.top; self.initialState = initialState


    @staticmethod
    def handled(me, event): return Hsm.RET_HANDLED


    @staticmethod
    def tran(me, nextState): me.state = nextState; return Hsm.RET_TRAN


    @staticmethod
    def super(me, superState): me.state = superState; return Hsm.RET_SUPER # p. 158


    @staticmethod
    def top(me, event): return Hsm.RET_IGNORED # p. 165


    @staticmethod
    def init(me, event = None):
        """Transitions to the initial state.  Follows any INIT transitions
        from the inital state and performs ENTRY actions as it proceeds.
        Use this to pass any parameters to initialize the state machine.
        p. 172
        """

        # There MUST be an initial transition
        assert me.initialState(me, event) == Hsm.RET_TRAN

        # HWM starts in the top state
        t = Hsm.top

        # Drill into the target
        while True:

            # Store the target of the initial transition
            path = [me.state]

            # From the designated initial state, record the path to top
            EventProcessor.trig(me, me.state, Signal.EMPTY)
            while me.state != t:
                path.append(me.state)
                EventProcessor.trig(me, me.state, Signal.EMPTY)

            # Restore the target of the initial transition
            me.state = path[0]
            assert len(path) < 32 # MAX_NEST_DEPTH (32 is arbitrary)

            # Perform ENTRY action for each state from after-top to initial
            path.reverse()
            for s in path:
                EventProcessor.enter(me, s)

            # Current state becomes new source (-1 because path was reversed)
            t = path[-1]

            if EventProcessor.trig(me, t, Signal.INIT) != Hsm.RET_TRAN:
                break

        # Current state is set to the final leaf state
        me.state = t


    @staticmethod
    def dispatch(me, event):
        """Follow the transitions until the event is handled or Top is reached
        p. 174
        """

        # Proceed to superstates if event is not handled
        exit_path = []
        r = Hsm.RET_SUPER
        while r == Hsm.RET_SUPER:
            s = me.state
            exit_path.append(s)
            r = s(me, event)    # invoke state handler

        # If the state handler indicates a transition
        if r == Hsm.RET_TRAN:

            # Store target of transition
            t = me.state

            # Record path to top
            EventProcessor.trig(me, me.state, Signal.EMPTY)
            while me.state != Hsm.top:
                exit_path.append(me.state)
                EventProcessor.trig(me, me.state, Signal.EMPTY)

            # Record path from target to top
            me.state = t
            entry_path = []
            r = Hsm.RET_TRAN
            while me.state != Hsm.top:
                t = me.state
                entry_path.append(t)
                EventProcessor.trig(me, t, Signal.EMPTY)

            # Find the Least Common Ancestor between the source and target
            i = -1
            while exit_path[i] == entry_path[i]:
                i -= 1
            n = len(exit_path) + i + 1

            # Exit all states in the exit path
            for st in exit_path[0:n]:
                r = EventProcessor.exit(me, st)
                assert (r == Hsm.RET_SUPER) or (r == Hsm.RET_HANDLED)

            # Enter all states in the entry path
            # This is done in the reverse order of the path
            for st in entry_path[n::-1]:
                r = EventProcessor.enter(me, st)
                assert r == Hsm.RET_HANDLED

            # Arrive at the target state
            me.state = t


    @staticmethod
    def isIn(me, state):
        pass
