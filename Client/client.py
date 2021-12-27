import socket
from sshkeyboard import *
import random
import setup

bufferSize = 1024
udpPort = 13117

"""
Listen for udp broadcasts and return the required information for the TCP connections
"""

spamming_teams = ['172.18.0.102', '172.99.0.40', '172.18.0.3', '172.18.0.14', '172.1.0.132', '172.18.0.6'] # TODO: delete

def getIpAndPort():
    while True:
        print('1')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDPSocket:
            UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            UDPSocket.bind(('', udpPort))
            print("Client started, listening for offer requests...")
            
            msgFromServer = UDPSocket.recvfrom(bufferSize)
            # TODO: delete
            while (msgFromServer[1][0] != '172.1.0.66'):
                msgFromServer = UDPSocket.recvfrom(bufferSize)
            print(msgFromServer)
                
            serverIp = msgFromServer[1][0]
            msgFromServer = msgFromServer[0]
            if len(msgFromServer) >= 7:
                if int.from_bytes(msgFromServer[0:4], byteorder='big', signed=False) == 0xabcddcba:
                    if msgFromServer[4] == 2:
                        serverPort = int.from_bytes(msgFromServer[5:7], byteorder='big', signed=False)
                    return serverIp, serverPort

def connectByTCP(ipAndPort, TCPSocket):
    print("Received offer from " + (ipAndPort[0]) + ", attempting to connect...")
    print(ipAndPort)
    TCPSocket.connect(ipAndPort)
    TCPSocket.sendall((f'Team {random.randint(100,999)}\n').encode("ascii"))

def main():
    # Initiate tcp connection with server and set the global variable server_socket
    while True:
        ipAndPort = getIpAndPort()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPSocket:
            connectByTCP(ipAndPort, TCPSocket)
            # Attach the sendMsgs function to the keyboard listener
            setup.setup(TCPSocket)
        setup.restore_settings()
    # While waiting for the keyboard pressing event - receive messages from the server

if __name__ == "__main__":
    main()
