# Introduction to Internet 2015 course work
# Roope Rajala
# Peetu Nuottajaervi
# Samuel Savikoski

import socket
import struct
import sys
import questions

# Set default arguments
host = socket.gethostbyname("ii.virtues.fi")
TCPsendPort = 10000
UDPbindPort = 9000

# Check if command line args were given and do operations based on them
def checkarguments():
    global host, TCPsendPort, UDPbindPort

    if len(sys.argv) < 2:
        printhelp()
        sys.exit()

    for i in range(0, len(sys.argv)):
        if sys.argv[i] == "-host":
            try:
                host = socket.gethostbyname(sys.argv[i+1])
            except:
                sys.exit("Invalid host address")

        if sys.argv[i] == "-tcp":
            try:
                TCPsendPort = int(sys.argv[i+1])
            except:
                sys.exit("Invalid port")

        if sys.argv[i] == "-udp":
            try:
                UDPbindPort = int(sys.argv[i+1])
            except:
                sys.exit("Invalid port")

        if sys.argv[i] == "-info" or sys.argv[i] == "-help" or sys.argv[i] == "-h":
            printhelp()
            sys.exit()

        if sys.argv[i] == "-test":
            print "Testing with default arguments"


def printhelp():
    print "Python client for Introduction to Internet 2015"
    print "Roope Rajala"
    print "Peetu Nuottajaervi"
    print "Samuel Savikoski"
    print "Arguments:"
    print "-host [address], Set host address (default ii.virtues.fi)"
    print "-tcp [port], Set TCP port to connect to (default 10000)"
    print "-udp [port], Set UDP port to bind (default 9000)"
    print "-test, test with default arguments"
    print "-info or -help or -h, Show this message"

# Request a UDP port from the host with a TCP message
def requestUDPport(tcpsocket):
    global host, TCPsendPort

    print "Creating a TCP connection to %s:%d" % (host, TCPsendPort)

    tcpsocket.connect((host, TCPsendPort))
    tcpsocket.settimeout(5)
    tcpsocket.send("HELO %d\r\n" % UDPbindPort)
    msg = tcpsocket.recv(1024)
    tcpsocket.close()
    print "HOST: "+ repr(msg)

    return int(filter(lambda x: x.isdigit(), msg))


# Send first message to the server
def sendinitialmessage(UDPsendPort):
    print "=> using UDP port", UDPsendPort, "to send datagrams."

    UDPsocket.bind(("0.0.0.0", UDPbindPort))
    print "Listening UDP on port", UDPbindPort
    UDPsocket.settimeout(10)

    eom = False
    ack = True
    length = 64
    remaining = 0
    msg = "Bring out your dead!"
    print "CLIENT:", msg
    data = struct.pack('!??HH64s', eom, ack, length, remaining, msg)
    UDPsocket.sendto(data, (host, UDPsendPort));

    print "Sent initial message, waiting for a question"

if __name__ == "__main__":
    TCPsocket = socket.socket()
    UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    checkarguments()
    try:
        UDPsendPort = requestUDPport(TCPsocket)
    except:
        sys.exit("Failed to create a connection.")

    sendinitialmessage(UDPsendPort)

    # Receive questions and answer them
    # Exits when message reads "Bye." or when receiving message with EOM as true
    while True:
            data, addrWithPort = UDPsocket.recvfrom(1024)
            address = addrWithPort[0]
            if address == host:
                print "HOST:", data
                eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)

                if eom == True:
                        print "Closing UDP socket"
                        UDPsocket.close()
                        break

                answer = questions.answer(msg)
                print "CLIENT:", answer
                sent = struct.pack('!??HH64s', eom, ack, length, remaining, answer)
                UDPsocket.sendto(sent, (host, UDPsendPort))
