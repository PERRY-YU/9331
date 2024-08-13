import socket
import random


def run_client(server_port, qname, qtype, timeout):
    qid = random.randint(0, 65535)
    query = f"{qid} {qname} {qtype}"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        sock.sendto(query.encode(), ('127.0.0.1', server_port))
        data, _ = sock.recvfrom(2048)
        print_response(data.decode())
    except socket.timeout:
        print("timed out")
    except ConnectionResetError as e:
        print(f"Connection reset error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        sock.close()


def print_response(response):
    lines = response.strip().split("\n")
    qid = lines[0]
    qname, qtype = lines[1].split()
    answers = lines[2:]

    print(f"ID: {qid}")
    print("QUESTION SECTION:")
    print(f"{qname}  {qtype}")

    sections = ["ANSWER SECTION", "AUTHORITY SECTION", "ADDITIONAL SECTION"]
    current_section = 0
    for answer in answers:
        if answer.strip() == "":
            current_section += 1
            continue
        if current_section < len(sections):
            print(f"{sections[current_section]}:")
        print(answer)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 5:
        print("Usage: python3 client.py <server_port> <qname> <qtype> <timeout>")
        sys.exit(1)
    server_port = int(sys.argv[1])
    qname = sys.argv[2]
    qtype = sys.argv[3]
    timeout = int(sys.argv[4])
    run_client(server_port, qname, qtype, timeout)
