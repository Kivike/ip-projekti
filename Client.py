import socket
import struct
import sys
import questions

TCPsocket = socket.socket()
host = "ii.virtues.fi"
TCPport = 10000
UDPbindPort = 9000
UDPsendPort = None
if (len(sys.argv) >= 2):
	host = sys.argv[1]
if (len(sys.argv) >= 3):
	TCPport = int(sys.argv[2])
if (len(sys.argv) == 4):
	UDPbindPort = int(sys.argv[3])

print 'Creating a TCP connection to %s:%d' % (host, TCPport)
TCPsocket.connect((host, TCPport))
TCPsocket.settimeout(5)
TCPsocket.send("HELO %d\r\n" % UDPbindPort)
TCPmsg = TCPsocket.recv(1024)
TCPsocket.close()
print "HOST:", repr(TCPmsg)

UDPsendPort = int(filter(lambda x: x.isdigit(), TCPmsg))
print "=> using UDP port", UDPsendPort, "to send datagrams."
UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPsocket.bind(("0.0.0.0", UDPbindPort))
print "Listening UDP on port", UDPbindPort
UDPsocket.settimeout(10) #sulkee sukatin jos ei saa pakettia

eom = True
ack = True
length = 64
remaining = 0
msg = "Bring out your dead!"
data = struct.pack('!??HH64s', eom, ack, length, remaining, msg)
UDPsocket.sendto(data, (host, UDPsendPort));
print "Sent initial message, waiting for a question"
while True:
	data, addr = UDPsocket.recvfrom(1024)
	print "HOST:", data
	eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)
	answer = questions.answer(msg)
	print "CLIENT:", answer
	sent = struct.pack('!??HH64s', eom, ack, length, remaining, answer)
	UDPsocket.sendto(sent, (host, UDPsendPort));
