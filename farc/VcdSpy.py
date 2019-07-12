"""
Copyright 2018 Dean Hall.  See LICENSE file for details.
"""


import datetime
import inspect
import tempfile

from . import Signal
from . import Framework

class SpyType(type):
    # This is used so that unimplemented static methods
    #  swallow their arguments and return None
    def __getattr__(cls, key):
        # print(f'Called class attribute {key}')
        return lambda *args, **kwargs: None

class VcdSpy(metaclass=SpyType):
    """VcdSpy is a visual tracing system that, if enabled,
    generates a Value Change Dump (vcd) file.  A vcd viewer
    application such as GTKWave allows you to see a timeline of
    [A]Hsms, states, signals and any instrumented debug IDs
    which will help you make sense of what happened at run time.
    """


    @staticmethod
    def init():
        """Creates a temporary file to hold VCD data
        and registers variables that will be written to it.
        """
        # VcdSpy: Import vcd here (rather than at top of file)
        # so that the pyvcd package is only required if VcdSpy is used
        global vcd
        import vcd # pip3 install pyvcd

        datestring = datetime.datetime.isoformat(datetime.datetime.now())
        VcdSpy._vcd_file = tempfile.NamedTemporaryFile(
                mode='w', suffix=".vcd", delete=False)
        VcdSpy._vcd_writer = vcd.VCDWriter(
                VcdSpy._vcd_file, timescale='1 us', date=datestring,
                init_timestamp=VcdSpy._get_timestamp())
        VcdSpy._vcd_var_state = {}
        VcdSpy._vcd_var_sig = {}
        # Handle signals that were registered before
        # the application selected VcdSpy as the Spy class
        for nm, id in Signal._registry.items():
            VcdSpy.on_signal_register(nm, id)


    @staticmethod
    def _get_timestamp():
        """Returns microsecond timestamp as an integer
        """
        return round(1e6 * Framework._event_loop.time())


    @staticmethod
    def on_framework_add(act):
        """Registers the given Ahsm and creates VCDWriter vars
        used to trace the Ahsm's execution and state.
        """
        # for each state in the Actor's state machine
        for nm, st in inspect.getmembers(
                act.__class__, predicate=inspect.isfunction):
            if hasattr(st, "farc_state"):
                st_lbl = "St%d_%s_%s" % (
                    act.priority, act.__class__.__name__, nm)
                act_var = VcdSpy._vcd_writer.register_var(
                    "tsk", st_lbl, "wire", size=1, init=0)
                VcdSpy._vcd_var_state[st.__hash__()] = act_var


    @staticmethod
    def on_framework_stop():
        """Closes the VcdWriter file and prints the filename to stdout
        """
        fn = VcdSpy._vcd_file.name
        VcdSpy._vcd_writer.close()
        VcdSpy._vcd_file.close()
        print("VcdSpy file: %s" % fn)


    @staticmethod
    def on_hsm_dispatch_event(evt):
        """Writes changes to the VCD file for the given Event
        """
        ts = VcdSpy._get_timestamp()
        VcdSpy._vcd_writer.change(VcdSpy._vcd_var_sig[evt.signal], ts, 1)


    @staticmethod
    def on_hsm_dispatch_pre(st):
        """Writes changes to the VCD file for pre-dispatch
        of an event to the given State
        """
        ts = VcdSpy._get_timestamp()
        act_var = VcdSpy._vcd_var_state[st.__hash__()]
        VcdSpy._vcd_writer.change(act_var, ts, 1)


    @staticmethod
    def on_hsm_dispatch_post(st_list):
        """Writes changes to the VCD file for post-dispatch.
        Argument is a list of state handlers
        """
        ts = VcdSpy._get_timestamp()
        for st in st_list:
            act_var = VcdSpy._vcd_var_state[st.__hash__()]
            VcdSpy._vcd_writer.change(act_var, ts, 0)


    @staticmethod
    def on_signal_register(signame, sigid):
        """Registers a signal with the VcdWriter when that signal is registered with farc
        """
        sig_lbl = "Sig%d_%s" % (sigid, signame)
        VcdSpy._vcd_var_sig[sigid] = VcdSpy._vcd_writer.register_var(
            "tsk", sig_lbl, "event", size=1, init=0)
