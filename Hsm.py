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

        t = me.state

        # Proceed to superstates if event is not handled
        while True:
            s = me.state
            r = s(me, event)
            if r != RET_SUPER:
                break

        if r == RET_TRAN:
            path = [me.state, t]

            while t != s:
                if Hsm.trig(me, t, Signal.EXIT):
                    Hsm.trig(me, t, Signal.EMPTY)
                t = me.state

            #p. 179
            t = path[0]

            if s == t:
                EventProcessor.exit(me, s)
                ip = 0 # ???

            else:
                EventProcessor.trig(me, t, Event.EMPTY)
                t = me.state
                if s == t:
                    ip = 0 # ???

                else:
                    EventProcessor.trig(me, s, Event.EMPTY)
                    if me.state == t:
                        EventProcessor.exit(me, s)
                        ip = 0 # ???

                    else:
                        iq = 0
                        ip = 1
                        path[1] = t
                        t = me.state
                        
                        r = EventProcessor.trig(me, path[1], Event.EMPTY)
                        while r == RET_SUPER:
                            path[++ip] = me.state
                            if me.state == s:
                                iq = 1
                                ip -= 1
                                r = RET_HANDLED

                            else:
                                r = EventProcessor.trig(me, me.state, Event.EMPTY)

                        if iq == 0:
                            EventProcessor.exit(me, s)
                            iq = ip
                            r = RET_IGNORED

                            while True:
                                if t == path[iq]:
                                    r = RET_HANDLED
                                    ip = iq - 1
                                    iq = -1

                                else:
                                    iq -= 1

                                if iq < 0: break

                            if r != RET_HANDLED:
                                r = RET_IGNORED

                                while  True:
                                    if EventProcessor.trig(me, t, Event.EXIT) == RET_HANDLED:
                                        EventProcessor.trig(me, t, Event.EMPTY)

                                    t = me.state
                                    iq = ip

                                    while True:
                                        if t == path[iq]:
                                            ip = iq - 1
                                            iq = -1
                                            r = RET_HANDLED

                                        else:
                                            iq -= 1

                                        if iq < 0: break

                                    if r == RET_HANDLED: break
            #for (12)




        me.state = t




    @staticmethod
    def isIn(me, state):
        pass

