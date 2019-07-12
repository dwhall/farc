import inspect
from . import Framework, Hsm, Signal

class SpyType(type):
    # This is used so that unimplemented static methods
    #  swallow their arguments and return None
    def __getattr__(cls, key):
        # print(f'Called class attribute {key}')
        return lambda *args, **kwargs: None

class SimpleSpy(metaclass=SpyType):
    _sig_names = {}
    _sig_id = {}
    _state_names = {}
    _log_lines = []

    @staticmethod
    def clear_log():
        __class__._log_lines = []

    @staticmethod
    def get_log():
        return __class__._log_lines.copy()

    @staticmethod
    def logger(msg):
        print(msg, end='')
        __class__._log_lines.append(msg)

    @staticmethod
    def init():
        for sig_name, sig_id in Signal._registry.items():
            __class__._sig_names[sig_id] = sig_name

    @staticmethod
    def on_signal_register(sig_name, sig_id):
        __class__._sig_names[sig_id] = sig_name

    @staticmethod
    def on_state_handler_called(state, evt, result):
        if evt is not None and evt.signal not in [Signal.EMPTY]:
            if (result != Hsm.RET_SUPER) or evt.signal in [Signal.ENTRY, Signal.EXIT]:
                __class__.logger(f"{__class__._state_names[state]}-{__class__._sig_names[evt.signal]};")

    @staticmethod
    def on_framework_add(act):
        for name, state in inspect.getmembers(act.__class__, predicate=inspect.isfunction):
            if hasattr(state, "farc_state"):
                __class__._state_names[state] = name

    @staticmethod
    def on_hsm_dispatch_event(evt):
        __class__.logger(f"\n<{__class__._sig_names[evt.signal]}> ")
