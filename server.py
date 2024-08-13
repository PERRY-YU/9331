import socket
import threading
import time
import random
import datetime

class DNSRecord:
    def __init__(self, domain_name, record_type, record_data):
        self.domain_name = domain_name
        self.record_type = record_type
        self.record_data = record_data

    def __str__(self):
        return f"{self.domain_name} {self.record_type} {self.record_data}"

def load_dns_records(filename):
    records = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            records.append(DNSRecord(parts[0], parts[1], parts[2]))
    return records

def resolve_query(query_name, query_type, dns_cache):
    answers, authorities, additionals = [], [], []
    visited = set()
    search_queue = [(query_name, query_type)]

    while search_queue:
        current_name, current_type = search_queue.pop(0)
        if (current_name, current_type) in visited:
            continue
        visited.add((current_name, current_type))

        matched = match_records(current_name, current_type, dns_cache, answers, authorities, search_queue, query_type)

        if not matched:
            handle_referral(current_name, dns_cache, authorities, additionals)
            break

    return answers, authorities, additionals

def match_records(current_name, current_type, dns_cache, answers, authorities, search_queue, query_type):
    matched = False
    for record in dns_cache:
        if record.domain_name == current_name:
            matched = True
            if record.record_type == current_type:
                answers.append(record)
            elif record.record_type == 'CNAME':
                answers.append(record)
                search_queue.append((record.record_data, query_type))
            elif record.record_type == 'NS':
                authorities.append(record)
    return matched

def handle_referral(current_name, dns_cache, authorities, additionals):
    closest_ns_records = find_closest_ns(current_name, dns_cache)
    if closest_ns_records:
        authorities.extend(closest_ns_records)
        for ns_record in closest_ns_records:
            additionals.extend(find_a_records(ns_record.record_data, dns_cache))

def find_closest_ns(query_name, dns_cache):
    labels = query_name.split('.')
    while labels:
        domain = '.'.join(labels)
        ns_records = [record for record in dns_cache if record.domain_name == domain and record.record_type == 'NS']
        if ns_records:
            return ns_records
        labels.pop(0)
    return [record for record in dns_cache if record.domain_name == '.' and record.record_type == 'NS']

def find_a_records(domain, dns_cache):
    return [record for record in dns_cache if record.domain_name == domain and record.record_type == 'A']

def process_query(data, addr, sock, dns_cache, delay):
    try:
        query_id, query_name, query_type = data.split()
        query_id = int(query_id)

        answers, authorities, additionals = resolve_query(query_name, query_type, dns_cache)

        response = build_response(query_id, query_name, query_type, answers, authorities, additionals)

        log_query(addr[1], query_id, query_name, query_type, "snd", delay)
        sock.sendto(response.encode(), addr)
    except Exception as e:
        print(f"Error processing query: {e}")

def build_response(query_id, query_name, query_type, answers, authorities, additionals):
    response = f"{query_id}\n{query_name} {query_type}\n"
    response += "\n".join(str(record) for record in answers) + "\n\n"
    response += "\n".join(str(record) for record in authorities) + "\n\n"
    response += "\n".join(str(record) for record in additionals) + "\n"
    return response

def log_query(client_port, query_id, query_name, query_type, direction, delay):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"{timestamp} {direction} {client_port}: {query_id} {query_name} {query_type} (delay: {delay}s)")

def run_dns_server(port):
    if not (49152 <= port <= 65535):
        port = random.randint(49152, 65535)
        print(f"Port out of range. Using random port: {port}")

    dns_cache = load_dns_records('master.txt')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', port))

    print(f"Server listening on port {port}")

    while True:
        try:
            data, addr = sock.recvfrom(2048)
            delay = random.randint(0, 4)
            query_id, query_name, query_type = data.decode().split()
            log_query(addr[1], query_id, query_name, query_type, "rcv", delay)
            threading.Thread(target=lambda: (time.sleep(delay), process_query(data.decode(), addr, sock, dns_cache, delay))).start()
        except ConnectionResetError as e:
            print(f"Connection reset error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 server.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    run_dns_server(port)
