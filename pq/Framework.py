import asyncio, signal, sys

from .Event import Event
from .Signal import Signal


class Framework(object):
    _event_loop = asyncio.get_event_loop()

    # The Framework maintains a registry of Ahsms in a dict.
    # The name of the Ahsm is the key and the instance is the value.
    _ahsm_registry = {}

    # The Framework maintains a group of TimeEvents in a dict.
    # The next expiration of the TimeEvent is the key and the event is the value.
    # Only the event with the next expiration time is scheduled for the timeEventCallback().
    # As TimeEvents are added and removed, the scheduled callback must be re-evaluated.
    # Periodic TimeEvents should only have one entry in the dict: the next expiration.
    # The timeEventCallback() will add a Periodic TimeEvent back into the dict with its next expiration.
    _time_events = {} 

    # When a TimeEvent is scheduled for the timeEventCallback(), 
    # a handle is kept so that the callback may be cancelled if necessary.
    _tm_event_handle = None

    # The message queue is priority based.  Messages are added to the queue
    # through the post() and publish() methods.  post() adds one message
    # to the queue directed at a specific Ahsm.  publish() copies one message
    # to every Ahsm that has subscribed to the Signal
    _mq = asyncio.PriorityQueue()

    # The Subscriber Table is a dictionary.  The keys are signals.
    # The value for each key is a list of Ahsms that are subscribed to the signal.
    # An Ahsm may subscribe to a signal at any time during runtime.
    _subscriberTable = {}

    
    @staticmethod
    def post(event, actname):
        """Posts the event to the given Ahsm's event queue. (act name for greater decoupling).
        """
        act = Framework._ahsm_registry[actname]
        act.postFIFO(event)


    @staticmethod
    def psInit():
        """Initialize the publish/subscribe system.
        """
        Framework._subscriberTable = {} # Key is Signal, Value is list of subscribers (instances of Ahsm)


    @staticmethod
    def publish(event):
        """Posts the event to the message queue of every Ahsm
        that is subscribed to the event's signal.
        """
        if event.signal in Framework._subscriberTable:
            for act in Framework._subscriberTable[event.signal]:
                act.postFIFO(event)
        # Run to completion
        Framework._event_loop.call_soon_threadsafe(Framework.run)


    @staticmethod
    def subscribe(signame, act):
        """Adds the given Ahsm to the subscriber table list
        for the given signal (signal name for greater decoupling).
        """
        sigid = Signal.register(signame)
        if sigid not in Framework._subscriberTable:
            Framework._subscriberTable[sigid] = []
        Framework._subscriberTable[sigid].append(act)


    @staticmethod
    def addTimeEvent(tm_event, delta):
        """Adds the TimeEvent to the list of active time events in the Framework.
        The event will fire its signal (to the TimeEvent's target Ahsm) after the delay, delta.
        """
        assert tm_event not in Framework._time_events.values()

        # Calculate the TimeEvent's expiration 
        expiration = Framework._event_loop.time() + delta

        Framework._insortTimeEvent(tm_event, expiration)


    @staticmethod
    def _insortTimeEvent(tm_event, expiration):
        """Inserts a TimeEvent into the list of active time events,
        sorted by the next expiration of the timer.
        No two timers should expire at the same time (key collision in the Dict),
        so we add the smallest amount of time to any duplicate expiration time.
        """
        # If an event already occupies this expiration time, 
        # increase this event's expiration by the smallest measurable amount
        while expiration in Framework._time_events.keys():
            expiration += sys.float_info.epsilon
        Framework._time_events[expiration] = tm_event

        # If this is the only active TimeEvent, schedule its callback
        if len(Framework._time_events) == 1:
            Framework._tm_event_handle = Framework._event_loop.call_at(expiration, Framework.timeEventCallback, tm_event, expiration)

        # If there are other TimeEvents, check if this one should replace the scheduled one
        else:
            if expiration < min(Framework._time_events.keys()):
                Framework._tm_event_handle.cancel()
                Framework._tm_event_handle = Framework._event_loop.call_at(expiration, Framework.timeEventCallback, tm_event, expiration)


    @staticmethod
    def removeTimeEvent(tm_event):
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
                        Framework._tm_event_handle = Framework._event_loop.call_at(next_expiration, Framework.timeEventCallback, next_event, next_expiration)
                    else:
                        Framework._tm_event_handle = None
                else:
                    del Framework._time_events[k]
                break


    @staticmethod
    def timeEventCallback(tm_event, expiration):
        """The callback function for all TimeEvents.
        Posts the event to the event's target Ahsm.
        If the TimeEvent is periodic, re-insort the event 
        in the list of active time events.
        """
        assert expiration in Framework._time_events.keys(), "Exp:%d _time_events.keys():%s" % ( expiration, Framework._time_events.keys() )

        # Remove this expired TimeEvent from the active list
        del Framework._time_events[expiration]
        Framework._tm_event_handle = None

        # Post the event to the target Ahsm
        tm_event.act.postFIFO(tm_event)

        # If this is a periodic time event, schedule its next expiration
        if tm_event.interval > 0:
            Framework._insortTimeEvent(tm_event, expiration + tm_event.interval)

        # If not set already and there are more events, set the next event callback
        if Framework._tm_event_handle == None and len(Framework._time_events) > 0:
            next_expiration = min(Framework._time_events.keys())
            next_event = Framework._time_events[next_expiration]
            Framework._tm_event_handle = Framework._event_loop.call_at(next_expiration, Framework.timeEventCallback, next_event, next_expiration)

        # Run to completion
        Framework._event_loop.call_soon_threadsafe(Framework.run)


    @staticmethod
    def add(act):
        """Makes the framework aware of the given Ahsm.
        """
        assert act.__class__.__name__ not in Framework._ahsm_registry
        Framework._ahsm_registry[act.__class__.__name__] = act


    @staticmethod
    def run():
        """Dispatches an event to the highest priority Ahsm
        until all event queues are empty (i.e. Run To Completion).
        """
        getPriority = lambda x : x.priority

        while True:
            allQueuesEmpty = True
            sorted_acts = sorted(Framework._ahsm_registry.values(), key=getPriority)
            for act in sorted_acts:
                if len(act.mq) > 0:
                    event_next = act.mq.pop()
#TODO: logging:      print("Dispatch: {0} to {1}".format(event_next, act))
                    act.dispatch(act, event_next)
                    allQueuesEmpty = False
                    break
            if allQueuesEmpty:
                return


    @staticmethod
    def stop():
        """EXITs all Ahsms and stops the event loop.
        """
        # Disable the timer callback
        if Framework._tm_event_handle:
            Framework._tm_event_handle.cancel()
            Framework._tm_event_handle = None

        # Post SIGTERM to all Ahsms so they execute their EXIT handler
        for act in Framework._ahsm_registry.keys():
            Framework.post(Event.SIGTERM, act)

        # Run to completion so each Ahsm will process SIGTERM
        Framework.run()
        Framework._event_loop.stop()


    @staticmethod
    def handle_posix_signal(sig):
        """Translates a POSIX signal to a pq event
        and dispatches the even to the Framework, usually in a special way.

        POSIX.SIGINT induces the Framework to issue an event that causes
        all SMs to execute their exit handlers all the way to the top of the hierarchy.

        NOTE: POSIX  signals come from the "signal" module
              and pq Signals come from the "Signal" module.
        """
        if sig == signal.SIGINT:
            # TODO:  replace stop() with code to re-init all Ahsms
            Framework.stop()

        elif sig == signal.SIGTERM:
            Framework.stop()


    # Bind a useful set of POSIX signals to the handler
    _event_loop.add_signal_handler(signal.SIGINT, handle_posix_signal.__func__, signal.SIGINT)
    _event_loop.add_signal_handler(signal.SIGTERM, handle_posix_signal.__func__, signal.SIGTERM)
