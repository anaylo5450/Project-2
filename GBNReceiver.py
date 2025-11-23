import socket
import random
import time
import os

LOCAL_PORT = 12345
MAX_PAYLOAD = 16
OUTPUT_FILE = "COSC635_P2_DataRecieved.txt"
SENT_FILE = "COSC635_P2_DataSent.txt"

loss_rate = int(input("Enter packet loss rate (0-99): "))
print(f"Simulating {loss_rate}% packet loss on data packets...")

random.seed(time.time())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", LOCAL_PORT))
sock.settimeout(1.0)

print(f"GBN Receiver listening on port {LOCAL_PORT}")

expected_seq = 0
packets_received = 0
packets_lost_simulated = 0
data_bytes_received = 0

f_out = open(OUTPUT_FILE, "wb")

while True:
    try:
        pkt, addr = sock.recvfrom(1024)
    except socket.timeout:
        continue

    if pkt == b"END":
        print("Received END, closing.")
        break

    r = random.randint(0, 99)
    if r < loss_rate:
        print("[LOSS] simulated drop of incoming data packet")
        packets_lost_simulated += 1
        # no ACK sent
        continue

    packets_received += 1

    try:
        header, payload = pkt.split(b"|", 1)
        seq = int(header.decode().strip())
    except Exception:
        print("Malformed packet, ignoring.")
        continue

    if seq == expected_seq:
        f_out.write(payload)
        data_bytes_received += len(payload)
        expected_seq += 1
        print(f"Accepted seq {seq}, wrote {len(payload)} bytes")
    else:
        print(f"Out-of-order or duplicate seq {seq}, expected {expected_seq}")

    ack_msg = f"ACK {expected_seq}".encode()
    sock.sendto(ack_msg, addr)
    print(f"Sent ACK {expected_seq}")

f_out.close()

print("\n--- GBN Receiver ---")
print("Packets received (after sim loss):", packets_received)
print("Simulated packet losses:", packets_lost_simulated)
print("Data bytes received:", data_bytes_received)
print("Output file:", OUTPUT_FILE)

if os.path.exists(SENT_FILE):
    sent_size = os.path.getsize(SENT_FILE)
    recv_size = os.path.getsize(OUTPUT_FILE)
    if sent_size == recv_size:
        print(f"FILE INTEGRITY: PASS ({sent_size} bytes)")
    else:
        print(f"FILE INTEGRITY: FAIL (Sent: {sent_size}, Recv: {recv_size})")
else:
    print("Warning: Original file not found for comparison.")

sock.close()
