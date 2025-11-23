import socket
import random
import time
import os

# ====== CONFIG ======
RECEIVER_IP = "127.0.0.1"   # change to receiver’s IP if needed
RECEIVER_PORT = 12345       # must match LOCAL_PORT in receiver
MAX_PAYLOAD = 16
WINDOW_SIZE = 4             # GBN window size
TIMEOUT = 0.5               # seconds
INPUT_FILE = "COSC635_P2_DataSent.txt"

# ====== LOSS RATE INPUT ======
loss_rate = int(input("Enter packet loss rate (0-99): "))
print(f"Simulating {loss_rate}% packet loss on outgoing data packets...")

random.seed(time.time())

# ====== READ FILE & CHUNK INTO PACKETS ======
if not os.path.exists(INPUT_FILE):
    print(f"Input file {INPUT_FILE} not found.")
    exit(1)

with open(INPUT_FILE, "rb") as f:
    file_data = f.read()

chunks = [file_data[i:i+MAX_PAYLOAD] for i in range(0, len(file_data), MAX_PAYLOAD)]
num_packets = len(chunks)
print(f"Total data size: {len(file_data)} bytes, total packets: {num_packets}")

# ====== SOCKET SETUP ======
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)

base = 0              # first unACKed packet
next_seq = 0          # next sequence number to send
total_packets_sent = 0
simulated_losses = 0
start_time = time.time()

# ====== GBN MAIN LOOP ======
while base < num_packets:
    # Send packets within the window
    while next_seq < base + WINDOW_SIZE and next_seq < num_packets:
        header = f"{next_seq}|".encode()
        payload = chunks[next_seq]
        packet = header + payload

        r = random.randint(0, 99)
        if r < loss_rate:
            print(f"[LOSS] Simulated drop of seq {next_seq}")
            simulated_losses += 1
            # Do NOT actually send
        else:
            sock.sendto(packet, (RECEIVER_IP, RECEIVER_PORT))
            print(f"Sent seq {next_seq} ({len(payload)} bytes)")

        total_packets_sent += 1

        # If this is the first unACKed packet, (re)start timer
        if base == next_seq:
            last_send_time = time.time()

        next_seq += 1

    # Try to receive ACKs
    try:
        data, _ = sock.recvfrom(1024)
        msg = data.decode().strip()
        if msg.startswith("ACK"):
            parts = msg.split()
            if len(parts) == 2:
                ack_num = int(parts[1])
                print(f"Received {msg}")

                # ack_num is the NEXT expected seq at receiver (cumulative)
                if ack_num > base:
                    base = ack_num
                    last_send_time = time.time()  # reset timer
    except socket.timeout:
        # Check for timeout: if there are unACKed packets, resend from base
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
                    sock.sendto(packet, (RECEIVER_IP, RECEIVER_PORT))
                    print(f"Resent seq {seq} ({len(payload)} bytes)")

                total_packets_sent += 1
            last_send_time = time.time()

# ====== SEND END MARKER ======
# Try a few times in case of loss
for _ in range(3):
    sock.sendto(b"END", (RECEIVER_IP, RECEIVER_PORT))
    time.sleep(0.1)

end_time = time.time()
elapsed = end_time - start_time

# ====== STATS ======
print("\n--- GBN Sender ---")
print("Total packets (original chunks):", num_packets)
print("Total packets sent (incl. retransmissions):", total_packets_sent)
print("Simulated packet losses:", simulated_losses)
print(f"Total time: {elapsed:.3f} seconds")
print("Input file:", INPUT_FILE)
print("Input file size:", len(file_data), "bytes")

sock.close()

