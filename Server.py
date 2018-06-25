import socket
import random


# Define Constants
end_flag = -1
buf_size = 4096  # Receive buffer size.
packet_loss = 0.2  # Percent of packet loss probability


# Define Variables
total_count = 0
loss_count = 0
ack = 0
expected = 0  # Expect to receive at number
received_log = ''  # Log param.


# Create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)


# In this code, we are going to receive integers starting from 0 for each packet
print("\nReady ...")


while True:

    # Get Data
    data_in, address = sock.recvfrom(buf_size)
    message = int(data_in.decode())
    print("\n\t Receiving packet %d" % message)

    # End server when receiving complete
    if message == end_flag:
        sock.close()
        print("\t Get the packet -1 \n[Finish] \n\t Total Sent by Client {0:d} \n\t Loss {1:d}".format(total_count, loss_count))
        break

    total_count += 1  # count as a sent message from client

    # Possible data loss
    if random.random() < packet_loss:  # 20% of loss probability
        print("\t LOSS Packet %s" % message)
        loss_count += 1
        continue  # No ACK is sent

    # packet was received in order
    if message == expected:
        expected += 1
        received_log += str(message) + ' '  # Log all received numbers
        ack = message
    else:
        print("\t Unexpected Packet number, expected Packet %d" % expected)
        received_log = received_log + '(' + str(message) + ' '
        ack = expected - 1

    # Send ACK
    sock.sendto(str(ack).encode(), address)
    print("\t Get Packet %d" % message,"\n\t Send ACK %d" % ack)
    print("LOG %s \n " % received_log)
