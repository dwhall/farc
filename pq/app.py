#!/usr/bin/env python


import asyncio, signal


def on_sigint():
    global loop
    print("Bye.")
    loop.stop()


def main():
    global loop
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, on_sigint)
    loop.add_signal_handler(signal.SIGTERM, on_sigint)

    print("Event loop running forever, press CTRL+c to quit.")
    loop.run_forever()


if __name__ == "__main__":
    main()
