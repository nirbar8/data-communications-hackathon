import selectors
import sys
import os
import fcntl
import tty
import termios

server_socket = None
old_settings = None
stdin_fd = None
GO_ON = None

# set sys.stdin non-blocking
def set_input_nonblocking():
    orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

def from_server(sock, arg2):
    global old_settings
    global stdin_fd
    global GO_ON
    termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)
    data = sock.recv(1024)
    if not data:
        GO_ON = False
    else:
        print(data.decode("ascii"))
    tty.setraw(stdin_fd)


def from_keyboard(keyboard, arg2):
    global server_socket
    ch = sys.stdin.read(1)
    sys.stdin.flush()
    server_socket.send(ch.encode())

def setup(server_sock):
    global server_socket
    global old_settings
    global stdin_fd
    global GO_ON

    server_socket = server_sock
    GO_ON = True
    stdin_fd =sys.stdin.fileno()
    old_settings = termios.tcgetattr(stdin_fd)

    set_input_nonblocking()
    m_selector = selectors.DefaultSelector()
    tty.setraw(stdin_fd)
    m_selector.register(server_sock, selectors.EVENT_READ, from_server)
    m_selector.register(sys.stdin, selectors.EVENT_READ, from_keyboard)
    while GO_ON:
        for k, mask in m_selector.select():
            callback = k.data
            callback(k.fileobj, mask)
            
def restore_settings():
    termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)