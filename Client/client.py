import socket

bufferSize = 1024
udpPort = 13117

"""
Listen for udp broadcasts and return the required information for the TCP connections
"""


def getIpAndPort():
    while True:
        UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPSocket.bind(('', udpPort))
        msgFromServer = UDPSocket.recvfrom(bufferSize)
        serverIp = msgFromServer[1]
        msgFromServer = msgFromServer[0]
        if len(msgFromServer) >= 7:
            if msgFromServer[0:5] == 0xabcddcba:
                if msgFromServer[5] == 2:
                    return serverIp, msgFromServer[6:8]


def main():
    getIpAndPort()


if __name__ == "__main__":
    main()
