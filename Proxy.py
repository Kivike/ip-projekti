# Introduction to Internet 2015
# Roope Rajala
# Peetu Nuottajärvi
# Samuel Savikoski
############################################################
# This proxy is a stand-alone program                      #
# If you want to change the server, use ip:port as argument#
# Accepts ONE client connection and forwards all messages  #
# between server and client.                               #
############################################################

import socket
import struct
import sys

serverAddr = socket.gethostbyname("ii.virtues.fi")
serverPort = 10000

def checkarguments():
    global serverAddr
    try:
        serverAddr, serverPort = sys.argv[1].split(":")
        serverAddr = socket.gethostbyname(serverAddr)
    except:
        sys.exit("Invalid server address")


# Select which ports to bind
# Tries all ports in range 10000-10099
def findavailableports():
    print "Finding available ports"

    #Find a free tcp port
    for port in range(10000,10100):
        try:
            TCPsocket.bind(("0.0.0.0", port))
            TCPport = port
            print "Bind on TCP port ", port
            break
        except:
            print str(port) + " didn't work"
            continue

    # Find a free udp port
    for port in range(10000,10100):
        try:
            UDPsocket.bind(("0.0.0.0", port))
            UDPport = port
            print "Bind on UDP port ", port
            break
        except:
            print str(port) + " didn't work"
            continue

    return (TCPport, UDPport)

# Forward message from server to client
# Returns End Of Message flag
def forwardtoclient(data, clientUDPport):
    eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)
    UDPsocket.sendto(data, (clientAddr, clientUDPport))
    print "Forwarded packet to the client"
    return eom

# Forward message from client to server
# Returns End Of Message flag
def forwardtoserver(data, serverUDPport):
    eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)
    UDPsocket.sendto(data, (serverAddr, serverUDPport))
    print "Forwarded packet to the server."
    return eom

# Send TCP message to server to request an UDP port
# Send own UDP bind port to the client
def initconnections(msg, UDPbindPort, clientconn):
    global serverPort, serverAddr

    splitMsg = msg.split()

    if len(splitMsg) != 2 or splitMsg[0] != "HELO":
        return None

    try:
        clientport = int(splitMsg[1].replace("\r\n", ""))
    except:
        return None

    TCPsocket = socket.socket()
    TCPsocket.connect((serverAddr, serverPort))
    TCPsocket.settimeout(5)
    TCPsocket.send("HELO %d\r\n" % UDPbindPort)
    msgFromServer = TCPsocket.recv(1024)
    TCPsocket.close()

    serverport = int(filter(lambda x: x.isdigit(), msgFromServer))
    clientConn.send("HELO %d\r\n" % UDPbindPort)
    clientConn.close()

    return (clientport, serverport)

if "__name__" == "__main__":
    checkarguments()

    TCPsocket = socket.socket()
    UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    TCPbindPort, UDPbindPort = findavailableports()

    # Listen TCP socket for client
    TCPsocket.listen(1)
    print "Waiting for connection"
    clientConn, addrWithPort = TCPsocket.accept()
    TCPsocket.close()

    clientAddr = addrWithPort[0]
    print "Client connected from", clientAddr

    msgFromClient = clientConn.recv(1024)
    print repr(msgFromClient)
    clientUDPport, serverUDPport = initconnections(msgFromClient, UDPbindPort, clientConn)

    if clientUDPport == None:
        sys.exit("Wrong message format from client. Needs to be 'HELO portnumber\r\n'")

    forwarding = True
    while(forwarding):
        data, addrWithPort = UDPsocket.recvfrom(1024)
        print "Received UDP packet from", addrWithPort[0]

        if addrWithPort[0] == clientAddr:
            print "Received packet from the client."
            if forwardtoserver(data, serverUDPport) == True:
                forwarding = False
        elif addrWithPort[0] == serverAddr:
            print "Received packet from the server."
            if forwardtoclient(data, clientUDPport) == True:
                forwarding = False

    UDPsocket.close()