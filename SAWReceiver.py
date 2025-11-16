# saw_receiver.py
import socket
import random
import time
import os

LOCAL_PORT = 12345          
MAX_PAYLOAD = 1024          
OUTPUT_FILE = "COSC635_P2_DataRecieved.txt"
SENT_FILE = "COSC635_P2_DataSent.txt"  

loss_rate = int(input("Enter packet loss rate (0-99): "))
print(f"Simulating {loss_rate}% packet loss...")

random.seed(time.time())

# UDP socket and bind
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', LOCAL_PORT))
print(f"Receiver listening on port {LOCAL_PORT}...")

# Stats tracking
start_time = time.time()
packets_received = 0
packets_lost_simulated = 0
data_bytes_received = 0

# Open output file
with open(OUTPUT_FILE, 'wb') as f:
    expected_seq = 0 

    while True:
        try:
            # Receive packet
            packet, sender_addr = sock.recvfrom(MAX_PAYLOAD + 100)

        
            if random.randint(0, 99) < loss_rate:
                packets_lost_simulated += 1
                print(f"[SIMULATED LOSS] Dropped packet from {sender_addr}")
                continue  

            if packet == b"END":
                print("Received END signal. Closing connection.")
                break

            f.write(packet)
            data_bytes_received += len(packet)
            packets_received += 1
            print(f"Received packet #{packets_received} ({len(packet)} bytes)")

            # Send ACK
            sock.sendto(b"ACK", sender_addr)
            print("Sent ACK")

        except socket.timeout:
            
            continue
        except Exception as e:
            print(f"Error: {e}")
            break

# Close socket
sock.close()

# Final Statistics
end_time = time.time()
elapsed = end_time - start_time

print("\n" + "="*50)
print("TRANSMISSION COMPLETE")
print("="*50)
print(f"Time taken: {elapsed:.2f} seconds")
print(f"Packets received: {packets_received}")
print(f"Simulated losses: {packets_lost_simulated}")
print(f"Data bytes received: {data_bytes_received}")
print(f"Output file: {OUTPUT_FILE}")

# Verify file integrity
if os.path.exists(SENT_FILE):
    sent_size = os.path.getsize(SENT_FILE)
    recv_size = os.path.getsize(OUTPUT_FILE)
    if sent_size == recv_size:
        print(f"FILE INTEGRITY: PASS ({sent_size} bytes)")
    else:
        print(f"FILE INTEGRITY: FAIL (Sent: {sent_size}, Recv: {recv_size})")
else:
    print("Warning: Original file not found for comparison.")
