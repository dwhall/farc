import asyncio
import collections
import math
import pickle
import signal
import sys
from functools import wraps


class Spy(object):
    """Spy is the debugging system for farc.
    farc contains a handful of Spy.on_*() methods
    placed at useful locations in the framework.
    It is up to a Spy driver (such as the included VcdSpy)
    to implement the Spy.on_*() methods.
    The programmer calls Spy.enable_spy(<Spy implementation class>)
    to activate the Spy system; otherwise, Spy does nothing.
    Therefore, this class is designed so that calling Spy.anything()
    is inert unless the application first calls Spy.enable_spy()
    """
    _actv_cls = None

    @staticmethod
    def enable_spy(spy_cls):
        """Sets the Spy to use the given class
        and calls its initializer.
        """
        Spy._actv_cls = spy_cls
        spy_cls.init()


    def __getattr__(*args):
        """Returns
        1) the enable_spy static method if requested by name, or
        2) the attribute from the active class (if active class was set), or
        3) a function that swallows any arguments and does nothing.
        """
        if args[1] == "enable_spy":
            return Spy.enable_spy
        if Spy._actv_cls:
            return getattr(Spy._actv_cls, args[1])
        return lambda *x: None


# Singleton pattern:
# Turn Spy into an instance of itself so __getattribute__ works
# on anyone who calls "import Spy; Spy.foo()"
# This  prevents Spy() from creating a new instance
# and gives everyone who calls "import Spy" the same object
Spy = Spy()


class Signal(object):
    """An asynchronous stimulus that triggers reactions.
    A unique identifier that, along with a value, specifies an Event.
    p. 154
    """

    _registry = {}  # signame:str to sigid:int
    _lookup = []    # sigid:int to signame:str


    @staticmethod
    def exists(signame):
        """Returns True if signame is in the Signal registry.
        """
        return signame in Signal._registry


    @staticmethod
    def register(signame):
        """Registers the signame if it is not already registered.
        Returns the signal number for the signame.
        """
        assert type(signame) is str
        if signame in Signal._registry:
            # TODO: emit warning that signal is already registered
            return Signal._registry[signame]
        else:
            sigid = len(Signal._lookup)
            Signal._registry[signame] = sigid
            Signal._lookup.append(signame)
            Spy.on_signal_register(signame, sigid)
            return sigid


    def __getattr__(self, signame):
        assert type(signame) is str
        return Signal._registry[signame]


# Singleton pattern:
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


class Event(object):
    """Events are a coupling of a signal and a value.
    Events are passed from one AHSM to another.
    Signals are defined in each AHSM's source code by name,
    but resolve to a unique number.  Values are any python value,
    including containers that contain even more values.
    When the event is created, if the value passed to the constructor
    is not None, the value is serialized to a bytes object.
    This serialization prevents the original value from being modified
    by other AHSMs.  Each AHSM state (static method) accepts an Event
    as the parameter and handles the event based on its Signal.
    """
    def __init__(self, sigid, val):
        assert 0 <= sigid <= len(Signal._lookup)
        self.signal = sigid

        # serialize the value
        self._value = pickle.dumps(val)

    @property
    def value(self,):
        return pickle.loads(self._value)

# Instantiate the reserved (system) events
Event.EMPTY = Event(Signal.EMPTY, None)
Event.ENTRY = Event(Signal.ENTRY, None)
Event.EXIT = Event(Signal.EXIT, None)
Event.INIT = Event(Signal.INIT, None)

# Events for POSIX signals
Event.SIGINT = Event(Signal.SIGINT, None)   # (i.e. Ctrl+C)
Event.SIGTERM = Event(Signal.SIGTERM, None) # (i.e. kill <pid>)

# The order of this tuple MUST match their respective signals
Event.reserved = (Event.EMPTY, Event.ENTRY, Event.EXIT, Event.INIT)


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


    def __init__(self,):
        """Sets this Hsm's current state to Hsm.top(), the default state
        and stores the given initial state.
        """
        # self._state is the Hsm/act's current active state.
        # This instance variable references the message handler (method)
        # that will be called whenever a message is sent to this Hsm.
        # We initialize this to self.top, the default message handler
        self._state = self.top

        # Farc differs from QP here in that we hardcode
        # the initial state to be "_initial"
        assert hasattr(self, "_initial"), "All HSMs must have an _initial() state handler"
        self._initial_state = self._initial


    def _initial(self, event):
        """Raises a NotImplementedError to force the derived class
        to implement its own initial state.
        """
        raise NotImplementedError


    def state(func):
        """A decorator that identifies which methods are states.
        The presence of the farc_state attr, not the value of the attr,
        determines statehood.
        The Spy debugging system uses the farc_state attribute
        to determine which methods inside a class are actually states.
        Other uses of the attribute may come in the future.
        """
        @wraps(func)
        def func_wrap(self, evt):
            result = func(self, evt)
            Spy.on_state_handler_called(func_wrap, evt, result)
            return result

        setattr(func_wrap, "farc_state", True)
        return staticmethod(func_wrap)

    # Helper functions to process reserved events through the current state
    def trig(self, state_func, signal): return state_func(self, Event.reserved[signal])
    def enter(self, state_func): return state_func(self, Event.ENTRY)
    def exit(self, state_func): return state_func(self, Event.EXIT)

    # Other helper functions
    def handled(self, event): return Hsm.RET_HANDLED
    def tran(self, nextState): self._state = nextState; return Hsm.RET_TRAN
    def super(self, superState): self._state = superState; return Hsm.RET_SUPER # p. 158

    @state
    def top(self, event):
        """This is the default state handler.
        This handler ignores all signals except
        the POSIX-like events, SIGINT/SIGTERM.
        Handling SIGINT/SIGTERM here causes the Exit path
        to be executed from the application's active state
        to top/here.
        The application may put something useful
        or nothing at all in the Exit path.
        """
        # Handle the Posix-like events to force the HSM
        # to execute its Exit path all the way to the top
        if Event.SIGINT == event:
            return Hsm.RET_HANDLED
        if Event.SIGTERM == event:
            return Hsm.RET_HANDLED

        # All other events are quietly ignored
        return Hsm.RET_IGNORED # p. 165


    def _perform_init_chain(self, current, first_init):
        """Act on the chain of initializations required starting from current.
        """
        t = current
        tran_count = 0
        while self.trig(t if t != self.top else self._initial_state, Signal.INIT) == Hsm.RET_TRAN:
            # The state handles the INIT message and needs to make a transition.
            # The "top" state is special in that it does not handle INIT messages,
            # so we defer to self._initial_state in this case
            path = []  # Trace the path back to t via superstates
            while self._state != t:
                path.append(self._state)
                self.trig(self._state, Signal.EMPTY)
            # Restore the state to the target state
            self._state = path[0]
            assert len(path) < 32  # MAX_NEST_DEPTH
            # Perform ENTRY action for each state from current to the target
            path.reverse()  # in-place
            for s in path:
                self.enter(s)
            # The target state has now to be checked to see if it responds to the INIT message
            t = path[-1]  # -1 because path was reversed
            tran_count += 1

        if first_init:
            assert tran_count > 0, "The initial state MUST transition to another state"
        return t


    def _perform_transition(self, source, target):
        # Handle the state transition from source to target in the HSM.
        s, t = source, target
        path = [t]
        if s == t:  # Case (a), transition to self
            self.exit(s)
            self.enter(t)
        else:
            # Find parent of target
            self.trig(t, Signal.EMPTY)
            t = self._state  # t is now parent of target
            if s == t:  # Case (b), source is parent of target
                self.enter(path[0])
            else:
                # Find parent of source
                self.trig(s, Signal.EMPTY)
                if self._state == t:  # Case (c), source and target share a parent
                    self.exit(s)
                    self.enter(path[0])
                else:
                    if self._state == path[0]:  # Case (d), target is parent of source
                        self.exit(s)
                    else:  # Check if the source is an ancestor of the target (case (e))
                        lca_found = False
                        path.append(t)  # Populates path[1]
                        t = self._state  # t is now parent of source
                        # Find and save ancestors of target into path
                        #  until we find the source or hit the top
                        self._state = path[1]
                        while self._state != self.top:
                            self.trig(self._state, Signal.EMPTY)
                            path.append(self._state)
                            assert len(path) < 32  # MAX_NEST_DEPTH
                            if self._state == s:
                                lca_found = True
                                break
                        if lca_found:  # This is case (e), enter states to get to target
                            for st in reversed(path[:-1]):
                                self.enter(st)
                        else:
                            self.exit(s)  # Exit the source for cases (f), (g), (h)
                            self._state = t  # Start at parent of the source
                            while self._state not in path:
                                # Keep exiting up into superstates until we reach the LCA.
                                #  Depending on whether the EXIT signal is handled, we may also need
                                #  to send the EMPTY signal to make self._state climb to the superstate.
                                if self.exit(self._state) == Hsm.RET_HANDLED:
                                    self.trig(self._state, Signal.EMPTY)
                            t = self._state
                            # Step into children until we enter the target
                            for st in reversed(path[:path.index(t)]):
                                self.enter(st)


    def init(self,):
        """Transitions to the initial state.  Follows any INIT transitions
        from the inital state and performs ENTRY actions as it proceeds.
        Use this to pass any parameters to initialize the state machine.
        p. 172
        """
        self._state = self._perform_init_chain(Hsm.top, True)


    def dispatch(self, event):
        """Dispatches the given event to this Hsm.
        Follows the application's state transitions
        until the event is handled or top() is reached
        p. 174
        """
        Spy.on_hsm_dispatch_event(event)

        # Save the current state
        t = self._state

        # Proceed to superstates if event is not handled, we wish to find the superstate
        #  (if any) that does handle the event and to record the path to that state
        exit_path = []
        r = Hsm.RET_SUPER
        while r == Hsm.RET_SUPER:
            s = self._state
            exit_path.append(s)
            Spy.on_hsm_dispatch_pre(s)
            r = s(self, event)    # invoke state handler
        # We leave the while loop with s at the state which was able to respond
        #  to the event, or to Hsm.top if none did
        Spy.on_hsm_dispatch_post(exit_path)

        # If the state handler for s requests a transition
        if r == Hsm.RET_TRAN:
            t = self._state
            # Store target of transition
            # Exit from the current state to the state s which handles
            # the transition. We do not exit from s=exit_path[-1] itself.
            for st in exit_path[:-1]:
                r = self.exit(st)
                assert (r == Hsm.RET_SUPER) or (r == Hsm.RET_HANDLED)
            s = exit_path[-1]
            # Transition to t through the HSM
            self._perform_transition(s, t)
            # Do initializations starting at t
            t = self._perform_init_chain(t, False)

        # Restore the state
        self._state = t


class Framework(object):
    """Framework is a composite class that holds:
    - the asyncio event loop
    - the registry of AHSMs
    - the set of TimeEvents
    - the handle to the next TimeEvent
    - the table subscriptions to events
    """

    _event_loop = asyncio.get_event_loop()

    # The Framework maintains a registry of Ahsms in a list.
    _ahsm_registry = []

    # The Framework maintains a dict of priorities in use
    # to prevent duplicates.
    # An Ahsm's priority is checked against this dict
    # within the Ahsm.start() method
    # when the Ahsm is added to the Framework.
    # The dict's key is the priority (integer) and the value is the Ahsm.
    _priority_dict = {}

    # The Framework maintains a group of TimeEvents in a dict.  The next
    # expiration of the TimeEvent is the key and the event is the value.
    # Only the event with the next expiration time is scheduled for the
    # time_event_callback().  As TimeEvents are added and removed, the scheduled
    # callback must be re-evaluated.  Periodic TimeEvents should only have
    # one entry in the dict: the next expiration.  The time_event_callback() will
    # add a Periodic TimeEvent back into the dict with its next expiration.
    _time_events = {}

    # When a TimeEvent is scheduled for the time_event_callback(),
    # a handle is kept so that the callback may be cancelled if necessary.
    _tm_event_handle = None

    # The Subscriber Table is a dictionary.  The keys are signals.
    # The value for each key is a list of Ahsms that are subscribed to the
    # signal.  An Ahsm may subscribe to a signal at any time during runtime.
    _subscriber_table = {}


    @staticmethod
    def post(event, act):
        """Posts the event to the given Ahsm's event queue.
        The argument, act, is an Ahsm instance.
        """
        assert isinstance(act, Ahsm)
        act.post_fifo(event)


    @staticmethod
    def post_by_name(event, act_name):
        """Posts the event to the given Ahsm's event queue.
        The argument, act, is a string of the name of the class
        to which the event is sent.  The event will post to all actors
        having the given classname.
        """
        assert type(act_name) is str
        for act in Framework._ahsm_registry:
            if act.__class__.__name__ == act_name:
                act.post_fifo(event)


    @staticmethod
    def publish(event):
        """Posts the event to the message queue of every Ahsm
        that is subscribed to the event's signal.
        """
        if event.signal in Framework._subscriber_table:
            for act in Framework._subscriber_table[event.signal]:
                act.post_fifo(event)
        Framework.run_to_completion()


    @staticmethod
    def subscribe(signame, act):
        """Adds the given Ahsm to the subscriber table list
        for the given signal.  The argument, signame, is a string of the name
        of the Signal to which the Ahsm is subscribing.  Using a string allows
        the Signal to be created in the registry if it is not already.
        """
        sigid = Signal.register(signame)
        if sigid not in Framework._subscriber_table:
            Framework._subscriber_table[sigid] = []
        Framework._subscriber_table[sigid].append(act)


    @staticmethod
    def add_time_event(tm_event, delta):
        """Adds the TimeEvent to the list of time events in the Framework.
        The event will fire its signal (to the TimeEvent's target Ahsm)
        after the delay, delta.
        """
        expiration = Framework._event_loop.time() + delta
        Framework.add_time_event_at(tm_event, expiration)


    @staticmethod
    def add_time_event_at(tm_event, abs_time):
        """Adds the TimeEvent to the list of time events in the Framework.
        The event will fire its signal (to the TimeEvent's target Ahsm)
        at the given absolute time (_event_loop.time()).
        """
        assert tm_event not in Framework._time_events.values()
        Framework._insort_time_event(tm_event, abs_time)


    @staticmethod
    def _insort_time_event(tm_event, expiration):
        """Inserts a TimeEvent into the list of time events,
        sorted by the next expiration of the timer.
        If the expiration time matches an existing expiration,
        we add the smallest amount of time to the given expiration
        to avoid a key collision in the Dict
        and make the identically-timed events fire in a FIFO fashion.
        """
        # If the event is to happen in the past, post it now
        now = Framework._event_loop.time()
        if expiration < now:
            tm_event.act.post_fifo(tm_event)
            # TODO: if periodic, need to schedule next?

        # If an event already occupies this expiration time,
        # increase this event's expiration by the smallest measurable amount
        while expiration in Framework._time_events.keys():
            m, e = math.frexp(expiration)
            expiration = (m + sys.float_info.epsilon) * 2**e
        Framework._time_events[expiration] = tm_event

        # If this is the only active TimeEvent, schedule its callback
        if len(Framework._time_events) == 1:
            Framework._tm_event_handle = Framework._event_loop.call_at(
                expiration, Framework.time_event_callback, tm_event, expiration)

        # If there are other TimeEvents,
        # check if this one should replace the scheduled one
        else:
            if expiration < min(Framework._time_events.keys()):
                Framework._tm_event_handle.cancel()
                Framework._tm_event_handle = Framework._event_loop.call_at(
                    expiration, Framework.time_event_callback, tm_event,
                    expiration)


    @staticmethod
    def remove_time_event(tm_event):
        """Removes the TimeEvent from the list of active time events.
        Cancels the TimeEvent's callback if there is one.
        Schedules the next event's callback if there is one.
        """
        for k,v in Framework._time_events.items():
            if v is tm_event:

                # If the event being removed is scheduled for callback,
                # cancel and schedule the next event if there is one
                if k == min(Framework._time_events.keys()):
                    del Framework._time_events[k]
                    if Framework._tm_event_handle:
                        Framework._tm_event_handle.cancel()
                    if len(Framework._time_events) > 0:
                        next_expiration = min(Framework._time_events.keys())
                        next_event = Framework._time_events[next_expiration]
                        Framework._tm_event_handle = \
                            Framework._event_loop.call_at(
                                next_expiration, Framework.time_event_callback,
                                next_event, next_expiration)
                    else:
                        Framework._tm_event_handle = None
                else:
                    del Framework._time_events[k]
                break


    @staticmethod
    def time_event_callback(tm_event, expiration):
        """The callback function for all TimeEvents.
        Posts the event to the event's target Ahsm.
        If the TimeEvent is periodic, re-insort the event
        in the list of active time events.
        """
        assert expiration in Framework._time_events.keys(), (
            "Exp:%d _time_events.keys():%s" %
            (expiration, Framework._time_events.keys()))

        # Remove this expired TimeEvent from the active list
        del Framework._time_events[expiration]
        Framework._tm_event_handle = None

        # Post the event to the target Ahsm
        tm_event.act.post_fifo(tm_event)

        # If this is a periodic time event, schedule its next expiration
        if tm_event.interval > 0:
            Framework._insort_time_event(tm_event,
                expiration + tm_event.interval)

        # If not set already and there are more events, set the next event callback
        if (Framework._tm_event_handle == None and
                len(Framework._time_events) > 0):
            next_expiration = min(Framework._time_events.keys())
            next_event = Framework._time_events[next_expiration]
            Framework._tm_event_handle = Framework._event_loop.call_at(
                next_expiration, Framework.time_event_callback, next_event,
                next_expiration)

        Framework.run_to_completion()


    @staticmethod
    def add(act):
        """Makes the framework aware of the given Ahsm.
        """
        Framework._ahsm_registry.append(act)
        assert act.priority not in Framework._priority_dict, (
                "Priority MUST be unique")
        Framework._priority_dict[act.priority] = act
        Spy.on_framework_add(act)


    @staticmethod
    def run():
        """Dispatches an event to the highest priority Ahsm
        until all event queues are empty (i.e. Run To Completion).
        """
        getPriority = lambda x : x.priority

        while True:
            allQueuesEmpty = True
            sorted_acts = sorted(Framework._ahsm_registry, key=getPriority)
            for act in sorted_acts:
                if act.has_msgs():
                    event_next = act.pop_msg()
                    act.dispatch(event_next)
                    allQueuesEmpty = False
                    break
            if allQueuesEmpty:
                return


    @staticmethod
    def run_to_completion():
        Framework._event_loop.call_soon_threadsafe(Framework.run)


    @staticmethod
    def stop():
        """EXITs all Ahsms and stops the event loop.
        """
        # Disable the timer callback
        if Framework._tm_event_handle:
            Framework._tm_event_handle.cancel()
            Framework._tm_event_handle = None

        # Post EXIT to all Ahsms
        for act in Framework._ahsm_registry:
            Framework.post(Event.EXIT, act)

        # Run to completion in this context
        # and stop the asyncio event loop
        Framework.run()
        Framework._event_loop.stop()
        Spy.on_framework_stop()


    @staticmethod
    def print_info():
        """Prints the name and current state
        of each actor in the framework.
        Meant to be called when ctrl+T (SIGINFO/29) is issued.
        """
        for act in Framework._ahsm_registry:
            print(act.__class__.__name__, act.state.__name__)


    # Bind a useful set of POSIX signals to the handler
    # (ignore a NotImplementedError on Windows)
    try:
        _event_loop.add_signal_handler(signal.SIGINT, lambda: Framework.stop())
        _event_loop.add_signal_handler(signal.SIGTERM, lambda: Framework.stop())
        _event_loop.add_signal_handler(29, print_info.__func__)
    except NotImplementedError:
        pass


def run_forever():
    """Runs the asyncio event loop with and
    ensures state machines are exited upon a KeyboardInterrupt.
    """
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        Framework.stop()
    loop.close()


class Ahsm(Hsm):
    """An Augmented Hierarchical State Machine (AHSM); a.k.a. ActiveObject/AO.
    Adds a priority, message queue and methods to work with the queue.
    """

    def start(self, priority):
        # must set the priority before Framework.add() which uses the priority
        self.priority = priority
        Framework.add(self)
        self.mq = collections.deque()
        self.init()
        Framework.run_to_completion()

    def post_lifo(self, evt):
        self.mq.append(evt)
        Framework.run_to_completion()

    def post_fifo(self, evt):
        self.mq.appendleft(evt)
        Framework.run_to_completion()

    def pop_msg(self,):
        return self.mq.pop()

    def has_msgs(self,):
        return len(self.mq) > 0


class TimeEvent(object):
    """TimeEvent is a composite class that contains an Event.
    A TimeEvent is created by the application and added to the Framework.
    The Framework then emits the event after the given delay.
    A one-shot TimeEvent is created by calling either post_at() or post_in().
    A periodic TimeEvent is created by calling the post_every() method.
    """
    def __init__(self, signame):
        assert type(signame) == str
        self.signal = Signal.register(signame)
        self.value = None


    def post_at(self, act, abs_time):
        """Posts this TimeEvent to the given Ahsm at a specified time.
        """
        assert issubclass(type(act), Ahsm)
        self.act = act
        self.interval = 0
        Framework.add_time_event_at(self, abs_time)


    def post_in(self, act, delta):
        """Posts this TimeEvent to the given Ahsm after the time delta.
        """
        assert issubclass(type(act), Ahsm)
        self.act = act
        self.interval = 0
        Framework.add_time_event(self, delta)


    def post_every(self, act, delta):
        """Posts this TimeEvent to the given Ahsm after the time delta
        and every time delta thereafter until disarmed.
        """
        assert issubclass(type(act), Ahsm)
        self.act = act
        self.interval = delta
        Framework.add_time_event(self, delta)


    def disarm(self):
        """Removes this TimeEvent from the Framework's active time events.
        """
        self.act = None
        Framework.remove_time_event(self)
