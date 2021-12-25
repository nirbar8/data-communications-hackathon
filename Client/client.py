import socket
from sshkeyboard import listen_keyboard

bufferSize = 1024
udpPort = 13117

"""
Listen for udp broadcasts and return the required information for the TCP connections
"""

server_socket = None

def getIpAndPort():
    while True:
        UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        UDPSocket.bind(('', udpPort))
        print("Client started, listening for offer requests...")
        msgFromServer = UDPSocket.recvfrom(bufferSize)
        serverIp = msgFromServer[1]
        msgFromServer = msgFromServer[0]
        if len(msgFromServer) >= 7:
            if msgFromServer[0:4] == 0xabcddcba:
                if msgFromServer[4] == 2:
                    return serverIp, msgFromServer[5:7]

def connectByTCP(ipAndPort):
    TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Received offer from " + ipAndPort[0] + ", attempting to connect...")
    TCPSocket.connect(ipAndPort)
    TCPSocket.sendall(b'Team \n')
    global server_socket
    server_socket = TCPSocket

# Reads a message from the server and prints it to the screen
def receiveMsgs():
    while True:
        msg = server_socket.recv(bufferSize)
        if not msg: break
        print(msg.decode())

# Gets a char from the keyboard and sends it to the server
def sendMsgs(msg):
    global server_socket
    server_socket.send(msg)

def main():
    # Initiate tcp connection with server and set the global variable server_socket
    connectByTCP(getIpAndPort())
    # Attach the sendMsgs function to the keyboard listener
    listen_keyboard(on_press= sendMsgs, sequential=True)
    # While waiting for the keyboard pressing event - receive messages from the server
    receiveMsgs()
    

def connectByTCP(ipAndPort):
    TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Received offer from " + ipAndPort[0] + ", attempting to connect...")
    TCPSocket.connect(ipAndPort)
    TCPSocket.sendall(b'Team \n')
    global server_socket
    server_socket = TCPSocket

# Reads a message from the server and prints it to the screen
def receiveMsgs():
    while True:
        msg = server_socket.recv(bufferSize)
        if not msg: break
        print(msg.decode())

# Gets a char from the keyboard and sends it to the server
def sendMsgs(msg):
    global server_socket
    server_socket.send(msg)

def main():
    # Initiate tcp connection with server and set the global variable server_socket
    connectByTCP(getIpAndPort())
    # Attach the sendMsgs function to the keyboard listener
    listen_keyboard(on_press= sendMsgs, sequential=True)
    # While waiting for the keyboard pressing event - receive messages from the server
    receiveMsgs()

if __name__ == "__main__":
    main()
