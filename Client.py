import socket
import time
import threading
from threading import Lock

# DEFINITIONS START #

# Define Constants
end_flag = -1
buf_size = 4096  # Receive buffer size.
window_size = 5
time_out = 0.13
max_packet = 15

# Define Variables
message = 0  # This is the message. We only use numbers in this program.
lock = Lock()  # With lock, the program will lock all threads until finish executing the block with lock
window = []  # packets that have been sent are stored in the window
packet_sent = 0  # Counter for largest number in the window
expected_ack = 0
server_address = ('localhost', 10000)
client_address = ("localhost", 0)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(client_address)


# Define class Packet
class Packet:
    def __init__(self, msg, timestamp):
        self._msg = msg
        self._time = timestamp

    def get_msg(self):
        return self._msg

    def get_time(self):
        return self._time

    def set_time(self, timestamp):
        self._time = timestamp


# Define Sub Thread - Receiving Loop logic
def receiving_listener():
    # State variables shared from main thread
    global buf_size
    global sock
    global expected_ack
    global window

    print("Receiving sub thread starting...")

    # Receiving Loop
    while True:
        data_in, ack_server_address = sock.recvfrom(buf_size)

        current_ack = int(data_in.decode())
        print("\tReceive ACK %d" % current_ack)

        # Lock to check for ACK
        with lock:

            if current_ack != expected_ack:  # If it is outdated late redundant ACK
                print("\tUnexpected ACK number, Packet loss, Expected ACK %d" % expected_ack)
                continue  # Then ignore this ack and continue receiving

            expected_ack += 1  # Update expected_ack to be the next one
            # Update window
            for each_packet in window:
                if each_packet.get_msg() <= expected_ack:
                    window.remove(each_packet)

            if expected_ack == max_packet:  # If all packets ack received
                break  # Then end loop and stop receiving thread



# Define Sub Thread - Sending Loop logic
def sending_listener():
    # State variables shared from main thread
    global sock
    global expected_ack
    global window
    global packet_sent

    print("Sending sub thread starting... \n")

    # Sending Loop
    while True:
        # Lock to watch for END
        with lock:
            if expected_ack == max_packet:  # If all packets ack received
                sock.sendto(str(end_flag).encode(), server_address)
                break  # Then end loop and stop receiving thread

        # Lock to watch for TIMEOUT
        with lock:
            # If the first packet in window timeout to receive ACK
            if len(window) > 0 and time.time() - window[0].get_time() >= time_out:
                print("\n\tTimeout is {1:0.2f}sec after Packet {0:d} loss"
                      .format(window[0].get_msg(), time.time() - window[0].get_time()))
                for tmp in window:  # Retransmit packets in window and update their timestamp
                    sock.sendto(str(tmp.get_msg()).encode(), server_address)  # Send old packet
                    tmp.set_time(time.time())  # Update the packet sent time
                    print("\tSend Packet %d [Re]" % tmp.get_msg())
                continue
            # If window is full
            if len(window) == window_size:
                continue

        # Window-Is-Not-Full Logic  # Add new packet to window and send it
        if packet_sent < max_packet:
            pkt = Packet(packet_sent, time.time())
            # Lock to add PACKET
            with lock:
                window.append(pkt)

            sock.sendto(str(pkt.get_msg()).encode(), server_address)  # Send new packet
            print("\tSend Packet %d" % pkt.get_msg())
            packet_sent += 1

    # Finishing
    sock.close()
    print("\n\t[Transmission Completed] \n\t Total %d packets" % max_packet)

# DEFINITIONS END #

# MAIN LOGIC START

# Create sub thread instants
thread_receive = threading.Thread(target=receiving_listener, args=())
thread_send = threading.Thread(target=sending_listener, args=())

thread_receive.start()
print("Receiving sub thread ready")
thread_send.start()
print("Sending sub thread ready")

# MAIN LOGIC END


