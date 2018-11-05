#!/usr/bin/env python3

"""UDP Relay AHSM for pq
Relays UDP messages to/from the pq framework.

References:
- https://www.pythonsheets.com/notes/python-asyncio.html
- https://docs.python.org/3.4/library/asyncio.html
"""

import asyncio

import pq


UDP_PORT = 4242


class UdpServer:
    def connection_made(self, transport):
        pass

    def datagram_received(self, data, addr):
        UdpRelayAhsm.on_datagram(data, addr)

    def error_received(self, error):
        UdpRelayAhsm.on_error(error)


class UdpRelayAhsm(pq.Ahsm):

    @pq.Hsm.state
    def initial(me, event):
        pq.Framework.subscribe("NET_ERR", me)
        pq.Framework.subscribe("NET_RXD", me)
        me.tmr = pq.TimeEvent("FIVE_COUNT")

        loop = asyncio.get_event_loop()
        server = loop.create_datagram_endpoint(UdpServer, local_addr=("localhost", UDP_PORT))
        me.transport, me.protocol = loop.run_until_complete(server)
        return me.tran(me, UdpRelayAhsm.waiting)


    @pq.Hsm.state
    def waiting(me, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            return me.handled(me, event)

        elif sig == pq.Signal.NET_RXD:
            me.latest_msg, me.latest_addr = event.value
            print("RelayFrom(%s): %r" % (me.latest_addr, me.latest_msg.decode()))
            return me.tran(me, UdpRelayAhsm.relaying)

        elif sig == pq.Signal.SIGTERM:
            return me.tran(me, UdpRelayAhsm.exiting)

        return me.super(me, me.top)


    @pq.Hsm.state
    def relaying(me, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            me.tmr.postEvery(me, 5.000)
            return me.handled(me, event)

        elif sig == pq.Signal.NET_RXD:
            me.latest_msg, me.latest_addr = event.value
            print("RelayFrom(%s): %r" % (me.latest_addr, me.latest_msg.decode()))
            return me.handled(me, event)

        elif sig == pq.Signal.FIVE_COUNT:
            me.transport.sendto(b"Latest: %r\n" % me.latest_msg, me.latest_addr)
            return me.handled(me, event)

        elif sig == pq.Signal.NET_ERR:
            return me.tran(me, UdpRelayAhsm.waiting)

        elif sig == pq.Signal.SIGTERM:
            me.tmr.disarm()
            return me.tran(me, UdpRelayAhsm.exiting)

        return me.super(me, me.top)


    def exiting(me, event):
        sig = event.signal
        if sig == pq.Signal.ENTRY:
            print("exiting")
            me.transport.close()
            return me.handled(me, event)
        return me.super(me, me.top)


    # Callbacks interact via messaging
    @staticmethod
    def on_datagram(data, addr):
        e = pq.Event(pq.Signal.NET_RXD, (data,addr))
        pq.Framework.publish(e)

    @staticmethod
    def on_error(error):
        e = pq.Event(pq.Signal.NET_ERR, (error))
        pq.Framework.publish(e)


if __name__ == "__main__":
    relay = UdpRelayAhsm(UdpRelayAhsm.initial)
    relay.start(0)

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pq.Framework.stop()
    loop.close()
