import socket
import struct
import sys
import questions


host = "ii.virtues.fi"
TCPsendPort = 10000
UDPbindPort = 9000
UDPsendPort = None
TCPsocket = socket.socket()
UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Check if command line args were given and do operations based on them
def checkarguments():
    global host, TCPsendPort, UDPbindPort

    for i in range(0, len(sys.argv)):
        if sys.argv[i] == "-h":
            host = sys.argv[i+1]

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

        if sys.argv[i] == "-info" or sys.argv[i] == "-help":
            print "Python client for Introduction to Internet 2015"
            print "Roope Rajala"
            print "Peetu Nuottajarvi"
            print "Samuel Savikoski"
            print "Arguments:"
            print "-h [host], Set host address"
            print "-tcp [port], Set TCP port to connect to"
            print "-udp [port], Set UDP port to bind to"
            print "-info or -help, Show this message"
            sys.exit()

# Request a TCP port from the host with UDP message
def requestUDPport(ownUDP, targetTCP):
    TCPsocket.connect((host, TCPsendPort))
    TCPsocket.settimeout(5)
    TCPsocket.send("HELO %d\r\n" % UDPbindPort)
    msg = TCPsocket.recv(1024)
    TCPsocket.close()
    return msg

# Send first message to the server
def sendinitialmessage(TCPmsg):
    global UDPsendPort
    UDPsendPort = int(filter(lambda x: x.isdigit(), TCPmsg))
    print "=> using UDP port", UDPsendPort, "to send datagrams."

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

if __name__ == "__main__":
    checkarguments()

    print 'Creating a TCP connection to %s:%d' % (host, TCPsendPort)
    TCPmsgfromserver = requestUDPport(UDPbindPort, TCPsendPort)
    print "HOST:", repr(TCPmsgfromserver)

    sendinitialmessage(TCPmsgfromserver)

    # Receive questions and answer them
    # Exits when message reads "Bye." or EOM is set to true
    while True:
            data, addr = UDPsocket.recvfrom(1024)

            print "HOST:", data
            eom, ack, length, remaining, msg = struct.unpack("!??HH64s", data)

            if "Bye." in msg or eom == 1:
                    print "Closing UDP socket"
                    UDPsocket.close()
                    break

            answer = questions.answer(msg)
            print "CLIENT:", answer
            sent = struct.pack('!??HH64s', eom, ack, length, remaining, answer)
            UDPsocket.sendto(sent, (host, UDPsendPort))
