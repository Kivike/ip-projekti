import re
import socket
import struct
import sys


TCPsocket = socket.socket()
UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TCPbindPort = None
UDPbindPort = None
clientUDPport = None
serverUDPport = None
serverConn = None
serverAddr = "ii.virtues.fi"
serverPort = "10000"

def findavailableports():
    print "Finding available ports"

    #Find a free tcp port
    for port in range(10000,10100):
        try:
            TCPsocket.bind(("0.0.0.0", port))
            TCPport = port
            print "Bind on tcpport " + str(port)
            break
        except:
            print str(port) + " didn't work"
            continue

    # Find a free udp port
    for port in range(10000,10100):
        try:
            UDPsocket.bind(("0.0.0.0", port))
            UDPport = port
            print "Bind on udpport " + str(port)
            break
        except:
            print str(port) + " didn't work"
            continue

    return (TCPport, UDPport)

def closeconnections():
    UDPsocket.close()
    TCPsocket.close()
    serverConn.close()
    clientConn.close()

def forwardtoclient(data):
    eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)
    UDPsocket.sendto(data, (clientAddr, clientUDPport))
    print "Forwarded packet to the client"
    if eom == 1:
        closeconnections()
        sys.exit("EOM received, exiting.")

def forwardtoserver(data):
    eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)
    UDPsocket.sendto(data, (serverAddr, serverUDPport))
    print "Forwarded packet to the server."
    if eom == 1:
        closeconnections()
        sys.exit("EOM received, exiting.")

def initconnections(msg):
    splitMsg = msg.split()

    if len(splitMsg) != 3:
        return False

    if splitMsg[0] != "HELO" or splitMsg[2] != "\r\n":
        return False

    try:
        clientUDPport = int(splitMsg[1])
    except:
        return False

    serverConn = TCPsocket.connect(serverAddr, serverPort)
    TCPsocket.settimeout(5)
    TCPsocket.send("HELO %d\r\n" % UDPbindPort)
    msgFromServer = TCPsocket.recv(1024)
    TCPsocket.close()

    serverUDPport = int(filter(lambda x: x.isdigit(), msgFromServer))
    clientConn.send("HELO %d\r\n" % UDPbindPort)


# Find a free tcp port

TCPbindPort, UDPbindPort = findavailableports()

TCPsocket.listen(1)

print "Waiting for connection"

clientConn = None
while(clientConn == None):
    clientConn, clientAddr = TCPsocket.accept()

print "Client connected"

msgFromClient = TCPsocket.recv(1024)

if initconnections(msgFromClient) == False:
    sys.exit("Failed to establish connections")

while(True):
    data, addr = UDPsocket.recvfrom(1024)
    if addr == serverAddr:
        print "Received packet from the server."
        forwardtoclient(data)
    elif addr == clientAddr:
        print "Received packet from the client."
        forwardtoserver(data)
    eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)

closeconnections()





