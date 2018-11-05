"""
Copyright 2018 Dean Hall.  See LICENSE file for details.
"""


import datetime
import tempfile

from .Framework import Framework



class VcdSpy(object):
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
        # so that the pyvcd package is only required if it is used
        global vcd
        import vcd # pip3 install pyvcd
        datestring = datetime.datetime.isoformat(datetime.datetime.now())
        VcdSpy._vcd_file = tempfile.NamedTemporaryFile(mode='w', suffix=".vcd", delete=False)
        w = vcd.VCDWriter(VcdSpy._vcd_file, timescale='1 us', date=datestring, init_timestamp=VcdSpy._get_timestamp())
        VcdSpy._vcd_writer = w
        VcdSpy._vcd_var_evnt = w.register_var("tsk", "evnt", "event")
        VcdSpy._vcd_var_evnt_sig = w.register_var("tsk", "evnt_sig", "integer")
        VcdSpy._vcd_var_evnt_dst = w.register_var("tsk", "evnt_dst", "integer")
        VcdSpy._vcd_var_ahsm = {}


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
        VcdSpy._vcd_var_ahsm[act.name] = (
            VcdSpy._vcd_writer.register_var("tsk", act.name, "wire", size=1),
            VcdSpy._vcd_writer.register_var("tsk", act.name + "_st", "integer")
        )


    @staticmethod
    def on_framework_run_pre_dispatch(act, evt):
        """Writes changes to the VCD file for the given Event
        that is sent to the given Ahsm.
        """
        ts = VcdSpy._get_timestamp()
        # Changes for pq.Event
        VcdSpy._vcd_writer.change(VcdSpy._vcd_var_evnt, ts, 1)
        VcdSpy._vcd_writer.change(VcdSpy._vcd_var_evnt_sig, ts, evt.signal)
        VcdSpy._vcd_writer.change(VcdSpy._vcd_var_evnt_dst, ts, act.priority)
        # TODO: Changes for pq.Ahsm


    @staticmethod
    def on_framework_run_post_dispatch(act):
        """Writes changes to the VCD file for the given Event
        that is sent to the given Ahsm.
        """
        ts = VcdSpy._get_timestamp()
        # TODO: Changes for pq.Ahsm
        # VcdSpy._vcd_writer.change(VcdSpy._vcd_var_evnt, ts, 0)

    @staticmethod
    def on_framework_stop():
        """Closes the VcdWriter file and prints the filename to stdout
        """
        fn = VcdSpy._vcd_file.name
        VcdSpy._vcd_writer.close()
        VcdSpy._vcd_file.close()
        print("VcdSpy file: %s" % fn)
