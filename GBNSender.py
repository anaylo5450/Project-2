import socket
import random
import time
import os

MAX_PAYLOAD = 16
WINDOW_SIZE = 4           # GBN window size
TIMEOUT = 0.5             # seconds
INPUT_FILE = "COSC635_P2_DataSent.txt"

receiver_ip = input("Enter receiver IP: ")
receiver_port = int(input("Enter receiver port: "))
loss_rate = int(input("Enter packet loss rate (0-99): "))
print(f"Simulating {loss_rate}% packet loss on outgoing data packets...")

random.seed(time.time())

if not os.path.exists(INPUT_FILE):
    print(f"Input file {INPUT_FILE} not found.")
    exit(1)

with open(INPUT_FILE, "rb") as f:
    file_data = f.read()

chunks = [file_data[i:i + MAX_PAYLOAD] for i in range(0, len(file_data), MAX_PAYLOAD)]
num_packets = len(chunks)
print(f"Total data size: {len(file_data)} bytes, total packets: {num_packets}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)

base = 0
next_seq = 0
total_packets_sent = 0
simulated_losses = 0
start_time = time.time()

while base < num_packets:
    while next_seq < base + WINDOW_SIZE and next_seq < num_packets:
        header = f"{next_seq}|".encode()
        payload = chunks[next_seq]
        packet = header + payload

        r = random.randint(0, 99)
        if r < loss_rate:
            print(f"[LOSS] Simulated drop of seq {next_seq}")
            simulated_losses += 1
        else:
            sock.sendto(packet, (receiver_ip, receiver_port))
            print(f"Sent seq {next_seq} ({len(payload)} bytes)")

        total_packets_sent += 1

        if base == next_seq:
            last_send_time = time.time()

        next_seq += 1

    try:
        data, _ = sock.recvfrom(1024)
        msg = data.decode().strip()
        if msg.startswith("ACK"):
            parts = msg.split()
            if len(parts) == 2:
                ack_num = int(parts[1])
                print(f"Received {msg}")
                if ack_num > base:
                    base = ack_num
                    last_send_time = time.time()
    except socket.timeout:
        if base < next_seq:
            print(f"Timeout occurred, resending window from seq {base} to {next_seq - 1}")
            for seq in range(base, next_seq):
                header = f"{seq}|".encode()
                payload = chunks[seq]
                packet = header + payload

                r = random.randint(0, 99)
                if r < loss_rate:
                    print(f"[LOSS] Simulated drop of retransmitted seq {seq}")
                    simulated_losses += 1
                else:
                    sock.sendto(packet, (receiver_ip, receiver_port))
                    print(f"Resent seq {seq} ({len(payload)} bytes)")

                total_packets_sent += 1
            last_send_time = time.time()

for _ in range(3):
    sock.sendto(b"END", (receiver_ip, receiver_port))
    time.sleep(0.1)

end_time = time.time()
elapsed = end_time - start_time

print("\n--- GBN Sender ---")
print("Total packets (original chunks):", num_packets)
print("Total packets sent (incl. retransmissions):", total_packets_sent)
print("Simulated packet losses:", simulated_losses)
print(f"Total time: {elapsed:.3f} seconds")
print("Input file:", INPUT_FILE)
print("Input file size:", len(file_data), "bytes")

sock.close()
