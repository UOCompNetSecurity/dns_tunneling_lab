from dnslib.server import DNSServer, DNSLogger
from tunnel_resolver import TunnelResolver
from term_iface import TerminalIFace
import queue
import curses


def main(stdscr): 

    command_queue = queue.Queue()
    print_queue   = queue.Queue()

    t_iface = TerminalIFace(stdscr, command_queue, print_queue)

    server = DNSServer(
        TunnelResolver(command_queue, print_queue),
        logger=DNSLogger(logf=lambda s:()),
        port=53,
        address="0.0.0.0",
        tcp=False
    )

    server.start_thread()

    t_iface.run()

if __name__ == "__main__":
    curses.wrapper(main)

