#!/usr/bin/env python
import sys
import asyncio
import farc
import logging

datefmt = '%Y-%m-%d %H:%M:%S'
# format = "%(asctime)s.%(msecs)03d, %(message)s"
format = "[%(asctime)s.%(msecs)03d][%(module)-25s][L#%(lineno)04d] %(funcName)s() - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=format, datefmt=datefmt)


class OnOffSwitch(farc.Ahsm):
    """
    Refer https://statecharts.github.io/on-off-state-machine.html
    """
    @farc.Hsm.state
    def _initial(self, event):
        logging.debug("OnOffSwitch _initial")
        return self.tran(OnOffSwitch.off)


    @farc.Hsm.state
    def off(self, event):
        """
        Actually this is a static method.

        :param event:
        :return:
        """
        sig = event.signal
        #logging.debug("<off> in sig: %d", sig)
        if sig == farc.Signal.ENTRY:
            logging.debug("<off> enter")
            return self.handled(event)
        elif sig == farc.Signal.FLICK:
            logging.debug("<off> flick")
            return self.tran(OnOffSwitch.on)
        elif sig == farc.Signal.EXIT:
            logging.debug("<off> exit")
            return self.handled(event)

        return self.super(self.top)


    @farc.Hsm.state
    def on(self, event):
        """
        Actually this is a static method.

        :param event:
        :return:
        """
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            logging.debug("<on> enter - turn light on")
            return self.handled(event)
        elif sig == farc.Signal.FLICK:
            logging.debug("<on> flick")
            return self.tran(OnOffSwitch.off)
        elif sig == farc.Signal.EXIT:
            logging.debug("<on> exit - turn light off ")
            return self.handled(event)

        return self.super(self.top)


def postFlickEvent(sw, event):
    logging.debug("post FLICK event")
    sw.post_fifo(event)


def mainFunction():
    # create an flick event.
    farc.Signal.register("FLICK")
    event = farc.Event(farc.Signal.FLICK, None)

    sw = OnOffSwitch()
    sw.start(0)

    loop = asyncio.get_event_loop()
    loop.call_later(2.0, postFlickEvent, sw, event)

    farc.run_forever()


if __name__ == '__main__':
    sys.exit(mainFunction())
