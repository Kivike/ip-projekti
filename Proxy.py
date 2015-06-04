import socket
import struct
import sys

serverAddr = socket.gethostbyname("ii.virtues.fi")
serverPort = 10000


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

def closeconnections():
    print "Closing connections and sockets"
    UDPsocket.close()
    clientConn.close()

def forwardtoclient(data, clientUDPport):
    eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)
    UDPsocket.sendto(data, (clientAddr, clientUDPport))
    print "Forwarded packet to the client"
    return eom

def forwardtoserver(data, serverUDPport):
    eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)
    UDPsocket.sendto(data, (serverAddr, serverUDPport))
    print "Forwarded packet to the server."
    return eom

def initconnections(msg):
    # Send TCP message to server to request UDP port
    # Send own UDP bind port to the client
    global clientConn, serverConn, serverUDPport, serverPort, serverAddr

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

    return (clientport, serverport)

TCPsocket = socket.socket()
UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TCPbindPort, UDPbindPort = findavailableports()

TCPsocket.listen(1)

print "Waiting for connection"
clientConn, addrWithPort = TCPsocket.accept()

TCPsocket.close()

clientAddr = addrWithPort[0]
print "Client connected from", clientAddr

msgFromClient = clientConn.recv(1024)
print repr(msgFromClient)

clientUDPport, serverUDPport = initconnections(msgFromClient, UDPbindPort)

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

closeconnections()





