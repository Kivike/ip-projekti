import re
import socket
import struct
import sys

TCPbindPort = None
UDPbindPort = None
serverUDPport = None
serverConn = None
serverAddr = "ii.virtues.fi"
serverPort = 10000

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
    clientConn.close()

def forwardtoclient(data, clientUDPport):
    eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)
    UDPsocket.sendto(data, (clientAddr[0], clientUDPport))
    print "Forwarded packet to the client"
    if eom == True:
        closeconnections()
        sys.exit("EOM received, exiting.")

def forwardtoserver(data):
    eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)
    UDPsocket.sendto(data, (serverAddr, serverUDPport))
    print "Forwarded packet to the server."
    if eom == True:
        closeconnections()
        sys.exit("EOM received, exiting.")

def initconnections(msg):
    global clientConn, serverConn, serverUDPport, UDPbindPort, serverPort, serverAddr

    splitMsg = msg.split()

    if len(splitMsg) != 2:
        print "123"
        return None

    if splitMsg[0] != "HELO":
        print "456"
        return None

    clientUDPport = None
    try:
        clientUDPport = int(splitMsg[1].replace("\r\n", ""))
    except:
        print "789"


    TCPsocket = socket.socket()
    TCPsocket.connect((serverAddr, serverPort))
    TCPsocket.settimeout(5)
    TCPsocket.send("HELO %d\r\n" % UDPbindPort)
    msgFromServer = TCPsocket.recv(1024)
    TCPsocket.close()

    serverUDPport = int(filter(lambda x: x.isdigit(), msgFromServer))
    clientConn.send("HELO %d\r\n" % UDPbindPort)

    return clientUDPport

# Find a free tcp port
TCPsocket = socket.socket()
UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TCPbindPort, UDPbindPort = findavailableports()


TCPsocket.listen(1)

print "Waiting for connection"

clientConn = None
while(clientConn == None):
    clientConn, clientAddr = TCPsocket.accept()

TCPsocket.close()

print "Client connected from " + str(clientAddr)

msgFromClient = clientConn.recv(1024)
print repr(msgFromClient)

clientUDPport = initconnections(msgFromClient)
if clientUDPport == None:
    sys.exit("Failed to establish connections")

while(True):
    data, addr = UDPsocket.recvfrom(1024)
    print "Received UDP packet"
    print addr

    if addr[0] == clientAddr[0]:
        print "Received packet from the client."
        forwardtoserver(data)
    else:
        print "Received packet from the server."
        forwardtoclient(data, clientUDPport)
    eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)

closeconnections()





