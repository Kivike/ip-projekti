import socket

socket = socket.socket()
host = "ii.virtues.fi"
port = 10000

socket.connect((host, port))
print socket.recv(1024)
socket.close