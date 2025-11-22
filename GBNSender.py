import socket
import sys
import time

# super basic settings
WINDOW_SIZE = 4        # GBN window size
TIMEOUT = 2.0          # seconds
RECV_BUF = 1024

# make a very simple "packet": "seq|data"
def make_packet(seq_num, data):
    return f"{seq_num}|{data}".encode()

def parse_ack(ack_bytes):
    try:
        s = ack_bytes.decode().strip()
        # expect "ACK <num>"
        if s.startswith("ACK"):
            parts = s.split()
            if len(parts) == 2:
                return int(parts[1])
    except:
        pass
    return None

def main():
    if len(sys.argv) != 3:
        print("usage: python gbn_sender.py <receiver_ip> <receiver_port>")
        sys.exit(1)

    receiver_ip = sys.argv[1]
    receiver_port = int(sys.argv[2])
    addr = (receiver_ip, receiver_port)

    # data we want to send (each entry is one packet)
    data_list = [
        "packet 0 data",
        "packet 1 data",
        "packet 2 data",
        "packet 3 data",
        "packet 4 data",
        "packet 5 data"
    ]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)  # short recv timeout so we can check our timer

    base = 0              # first unACKed packet
    next_seq = 0          # next seq number to send
    n_packets = len(data_list)
    timer_start = None

    while base < n_packets:
        # send new packets while window not full
        while next_seq < base + WINDOW_SIZE and next_seq < n_packets:
            pkt = make_packet(next_seq, data_list[next_seq])
            sock.sendto(pkt, addr)
            print("sent packet", next_seq)
            if base == next_seq:
                timer_start = time.time()
            next_seq += 1

        # wait for ACK or timeout
        try:
            ack_bytes, _ = sock.recvfrom(RECV_BUF)
            ack_num = parse_ack(ack_bytes)
            if ack_num is not None:
                print("received ACK for next expected =", ack_num)
                # ack_num is "next expected", so base moves up to ack_num
                if ack_num > base:
                    base = ack_num
                    # if all outstanding packets are ACKed, stop timer
                    if base == next_seq:
                        timer_start = None
                    else:
                        timer_start = time.time()
        except socket.timeout:
            # check for timeout of oldest unACKed
            if timer_start is not None and (time.time() - timer_start) >= TIMEOUT:
                print("timeout, resending window from", base, "to", next_seq - 1)
                for seq in range(base, next_seq):
                    pkt = make_packet(seq, data_list[seq])
                    sock.sendto(pkt, addr)
                    print("re-sent packet", seq)
                timer_start = time.time()

    # optional: tell receiver we are done
    sock.sendto(b"END", addr)
    print("all packets sent and ACKed, closing sender")
    sock.close()

if __name__ == "__main__":
    main()


