"""
Copyright 2017 Dean Hall.  See LICENSE file for details.
"""

from .Signal import Signal
from .Event import Event


class Hsm(object):
    """A Hierarchical State Machine (HSM).
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
    # TODO: the following are in qp's C code
    # but not described in book:
    # RET_UNHANDLED
    # RET_ENTRY
    # RET_EXIT
    # RET_INITIAL


    def __init__(self, initialState):
        self.state = self.top
        self.initialState = initialState


    # Three helper functions to process reserved events through the current state
    @staticmethod
    def trig(me, state, signal): return state(me, Event.reserved[signal])
    @staticmethod
    def enter(me, state): return state(me, Event.ENTRY)
    @staticmethod
    def exit(me, state): return state(me, Event.EXIT)

    # Other helper functions
    @staticmethod
    def handled(me, event): return Hsm.RET_HANDLED
    @staticmethod
    def tran(me, nextState): me.state = nextState; return Hsm.RET_TRAN
    @staticmethod
    def super(me, superState): me.state = superState; return Hsm.RET_SUPER # p. 158
    @staticmethod
    def top(me, event):
        # Handle the Posix-like events to force the HSM
        # to execute its Exit path all the way to the top
        if Event.SIGINT == event:
            return Hsm.RET_HANDLED
        if Event.SIGTERM == event:
            return Hsm.RET_HANDLED

        # All other events are quietly ignored
        return Hsm.RET_IGNORED # p. 165


    @staticmethod
    def init(me, event = None):
        """Transitions to the initial state.  Follows any INIT transitions
        from the inital state and performs ENTRY actions as it proceeds.
        Use this to pass any parameters to initialize the state machine.
        p. 172
        """

        # The initial state MUST transition to another state
        assert me.initialState(me, event) == Hsm.RET_TRAN

        # HSM starts in the top state
        t = Hsm.top

        # Drill into the target
        while True:

            # Store the target of the initial transition
            path = [me.state]

            # From the designated initial state, record the path to top
            Hsm.trig(me, me.state, Signal.EMPTY)
            while me.state != t:
                path.append(me.state)
                Hsm.trig(me, me.state, Signal.EMPTY)

            # Restore the target of the initial transition
            me.state = path[0]
            assert len(path) < 32 # MAX_NEST_DEPTH (32 is arbitrary)

            # Perform ENTRY action for each state from after-top to initial
            path.reverse()
            for s in path:
                Hsm.enter(me, s)

            # Current state becomes new source (-1 because path was reversed)
            t = path[-1]

            if Hsm.trig(me, t, Signal.INIT) != Hsm.RET_TRAN:
                break

        # Current state is set to the final leaf state
        me.state = t


    @staticmethod
    def dispatch(me, event):
        """Follow the transitions until the event is handled or Top is reached
        p. 174
        """

        # Save the current state
        t = me.state

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
            Hsm.trig(me, me.state, Signal.EMPTY)
            while me.state != Hsm.top:
                exit_path.append(me.state)
                Hsm.trig(me, me.state, Signal.EMPTY)

            # Record path from target to top
            me.state = t
            entry_path = []
            r = Hsm.RET_TRAN
            while me.state != Hsm.top:
                entry_path.append(me.state)
                Hsm.trig(me, me.state, Signal.EMPTY)

            # Find the Least Common Ancestor between the source and target
            i = -1
            while exit_path[i] == entry_path[i]:
                i -= 1
            n = len(exit_path) + i + 1

            # Exit all states in the exit path
            for st in exit_path[0:n]:
                r = Hsm.exit(me, st)
                assert (r == Hsm.RET_SUPER) or (r == Hsm.RET_HANDLED)

            # Enter all states in the entry path
            # This is done in the reverse order of the path
            for st in entry_path[n::-1]:
                r = Hsm.enter(me, st)
                assert r == Hsm.RET_HANDLED, "Expected ENTRY to return HANDLED transitioning to {0}".format(t)

            # Arrive at the target state
            me.state = t

        # Restore the current state
        me.state = t


    @staticmethod
    def state(func):
        """A decorator that helps outsiders identify which
        methods are meant to be states.
        The presence of the pq_state attr, not its value,
        determines statehood.
        """
        setattr(func, "pq_state", True)
        return staticmethod(func)
