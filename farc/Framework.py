"""
Copyright 2017 Dean Hall.  See LICENSE file for details.
"""

import asyncio
import math
import signal
import sys

from .Spy import Spy
from .Signal import Signal
from .Event import Event
from .Hsm import Hsm


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
    # timeEventCallback().  As TimeEvents are added and removed, the scheduled
    # callback must be re-evaluated.  Periodic TimeEvents should only have
    # one entry in the dict: the next expiration.  The timeEventCallback() will
    # add a Periodic TimeEvent back into the dict with its next expiration.
    _time_events = {}

    # When a TimeEvent is scheduled for the timeEventCallback(),
    # a handle is kept so that the callback may be cancelled if necessary.
    _tm_event_handle = None

    # The Subscriber Table is a dictionary.  The keys are signals.
    # The value for each key is a list of Ahsms that are subscribed to the
    # signal.  An Ahsm may subscribe to a signal at any time during runtime.
    _subscriber_table = {}


    @staticmethod
    def post(event, act):
        """Posts the event to the given Ahsm's event queue.
        The argument, act, is either a string of the name of the class
        to which the event is sent or the Ahsm instance itself.
        If the argument is a string, the event will post to all actors
        having the given classname.
        """
        if type(act) is str:
            # I'm not convinced this is appropriate for the long term.
            # post() should target one actor and publish() targets many.
            # This was created to support legacy apps which use
            # an actor's class name as the target.
            # If this goes away, apps will need to adapt.
            [a.postFIFO(event) for a in Framework._ahsm_registry
                    if a.__class__.__name__ == act]
        else:
            assert isinstance(act, Hsm)
            act.postFIFO(event)


    @staticmethod
    def publish(event):
        """Posts the event to the message queue of every Ahsm
        that is subscribed to the event's signal.
        """
        if event.signal in Framework._subscriber_table:
            for act in Framework._subscriber_table[event.signal]:
                act.postFIFO(event)
        # Run to completion
        Framework._event_loop.call_soon_threadsafe(Framework.run)


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
    def addTimeEvent(tm_event, delta):
        """Adds the TimeEvent to the list of time events in the Framework.
        The event will fire its signal (to the TimeEvent's target Ahsm)
        after the delay, delta.
        """
        expiration = Framework._event_loop.time() + delta
        Framework.addTimeEventAt(tm_event, expiration)


    @staticmethod
    def addTimeEventAt(tm_event, abs_time):
        """Adds the TimeEvent to the list of time events in the Framework.
        The event will fire its signal (to the TimeEvent's target Ahsm)
        at the given absolute time (_event_loop.time()).
        """
        assert tm_event not in Framework._time_events.values()
        Framework._insortTimeEvent(tm_event, abs_time)


    @staticmethod
    def _insortTimeEvent(tm_event, expiration):
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
            tm_event.act.postFIFO(tm_event)
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
                expiration, Framework.timeEventCallback, tm_event, expiration)

        # If there are other TimeEvents,
        # check if this one should replace the scheduled one
        else:
            if expiration < min(Framework._time_events.keys()):
                Framework._tm_event_handle.cancel()
                Framework._tm_event_handle = Framework._event_loop.call_at(
                    expiration, Framework.timeEventCallback, tm_event,
                    expiration)


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
                        Framework._tm_event_handle = \
                            Framework._event_loop.call_at(
                                next_expiration, Framework.timeEventCallback,
                                next_event, next_expiration)
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
        assert expiration in Framework._time_events.keys(), (
            "Exp:%d _time_events.keys():%s" %
            (expiration, Framework._time_events.keys()))

        # Remove this expired TimeEvent from the active list
        del Framework._time_events[expiration]
        Framework._tm_event_handle = None

        # Post the event to the target Ahsm
        tm_event.act.postFIFO(tm_event)

        # If this is a periodic time event, schedule its next expiration
        if tm_event.interval > 0:
            Framework._insortTimeEvent(tm_event,
                expiration + tm_event.interval)

        # If not set already and there are more events, set the next event callback
        if (Framework._tm_event_handle == None and
                len(Framework._time_events) > 0):
            next_expiration = min(Framework._time_events.keys())
            next_event = Framework._time_events[next_expiration]
            Framework._tm_event_handle = Framework._event_loop.call_at(
                next_expiration, Framework.timeEventCallback, next_event,
                next_expiration)

        # Run to completion
        Framework._event_loop.call_soon_threadsafe(Framework.run)


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
        for act in Framework._ahsm_registry:
            Framework.post(Event.SIGTERM, act)

        # Run to completion so each Ahsm will process SIGTERM
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
