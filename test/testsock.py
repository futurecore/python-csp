import socket

HOST = socket.gethostbyname(socket.gethostname())

PORT = 8887
data = 'flibble'

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # Connect to server and send data
# sock.connect((HOST, PORT))
# sock.send(data + "\n")

# # Receive data from the server and shut down
# received = sock.recv(1024)
# sock.close()



# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(data + "\n", (HOST, PORT))
received = sock.recv(1024)

print("Sent:     {0}".format(data))
print("Received: {0}".format(received))
