import socket

bufferSize = 1024
udpPort = 13117

"""
Listen for udp broadcasts and return the required information for the TCP connections
"""


def getIpAndPort():
    while True:
        UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        UDPSocket.bind(('', udpPort))
        print("Client started, listening for offer requests...")
        msgFromServer = UDPSocket.recvfrom(bufferSize)
        serverIp = msgFromServer[1]
        msgFromServer = msgFromServer[0]
        if len(msgFromServer) >= 7:
            if msgFromServer[0:5] == 0xabcddcba:
                if msgFromServer[5] == 2:
                    return serverIp, msgFromServer[6:8]
def connectByTCP(ipAndPort):
    TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Received offer from " + ipAndPort[0] + ", attempting to connect...")
    TCPSocket.connect(ipAndPort)
    TCPSocket.sendall(b'Team ')
def main():
    connectByTCP(getIpAndPort())


if __name__ == "__main__":
    main()
