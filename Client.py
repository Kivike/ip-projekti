import socket
import struct

TCPsocket = socket.socket()
host = "ii.virtues.fi"
port = 10000

TCPsocket.connect((host, port))
TCPsocket.settimeout(5)
TCPsocket.send("HELO 10000\r\n")
print TCPsocket.recv(1024)


UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPsocket.settimeout(5) #sulkee sukatin jos ei saa pakettia

endOfMessage = True
acknowledgeReceipt = True
length = 64
message = "Bring out your dead!"

#struct.pack("!??Ha", endOfMessage, acknowledgeReceipt, length)


UDPsocket.sendto(message, (host, port));
print UDPsocket.recv(1024)
UDPsocket.close()
TCPsocket.close()