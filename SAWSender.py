import socket
import time
import random
import os

INPUT_FILE = "COSC635_P2_DataSent.txt"
MAX_PAYLOAD = 16
TIMEOUT = 2.0

receiver_ip = input("Enter receiver IP: ")
receiver_port = int(input("Enter receiver port: "))
loss_rate = int(input("Enter packet loss rate (0–99): "))

random.seed(time.time())

if not os.path.exists(INPUT_FILE):
    print(f"ERROR: {INPUT_FILE} does not exist.")
    exit(1)

with open(INPUT_FILE, "rb") as f:
    data = f.read()

chunks = [data[i:i + MAX_PAYLOAD] for i in range(0, len(data), MAX_PAYLOAD)]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.5)

total_pdus_sent = 0
total_pdus_lost = 0
data_bytes_sent = 0

print(f"Sending {len(chunks)} packets...")

start_time = time.time()

for payload in chunks:
    while True:
        r = random.randint(0, 99)
        if r < loss_rate:
            print("[LOSS] simulated drop")
            total_pdus_lost += 1
            total_pdus_sent += 1
            time.sleep(TIMEOUT)
        else:
            sock.sendto(payload, (receiver_ip, receiver_port))
            print("Sent", len(payload), "bytes")
            total_pdus_sent += 1

        try:
            ack, _ = sock.recvfrom(1024)
            if ack.decode().strip() == "ACK":
                data_bytes_sent += len(payload)
                break
        except socket.timeout:
            print("Timeout, resending...")

sock.sendto(b"END", (receiver_ip, receiver_port))

elapsed = time.time() - start_time

print("\n--- SAW Sender ---")
print("Total PDUs sent:", total_pdus_sent)
print("Simulated PDUs lost:", total_pdus_lost)
print("Data bytes sent:", data_bytes_sent)
print(f"Elapsed time: {elapsed:.3f} s")

sock.close()
