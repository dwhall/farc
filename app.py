#!/usr/bin/env python


import asyncio, signal


def on_sigint():
    print("Bye.")
    loop.stop()


loop = asyncio.get_event_loop()
loop.add_signal_handler(signal.SIGINT, on_sigint)
loop.add_signal_handler(signal.SIGTERM, on_sigint)

print("Event loop running forever, press CTRL+c to quit.")
loop.run_forever()
