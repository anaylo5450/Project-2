#sender for Stop and Wait procedure
import socket, time

receiver_ip = input("Enter receiver IP: ")  
receiver_port = input("ender receiver port: ")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)  # 1 second timeout

message = input("Enter message to send: ")
data = message.encode()

while True:
    sock.sendto(data, (receiver_ip, receiver_port))
    print("Sent:", message)
    try:
        ack, _ = sock.recvfrom(1024)
        if ack == b"ACK":
            print("ACK received! Transmission complete.")
            break
    except socket.timeout:
        print("Timeout, resending...")

sock.sendto(b"END", (receiver_ip, receiver_port))
