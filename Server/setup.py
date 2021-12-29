from scapy.all import *
from enum import Enum, auto
import queue
import random

class GameMode(Enum):
    WAITING_FOR_CLIENTS = auto()
    IN_GAME             = auto()
    TERMINATE           = auto()

class ProgramMode(Enum):
    DEBUG   = auto()
    RELEASE = auto()


'''
****************************************
*********                     **********
*********     FOR TESTERS     **********
*********                     **********
****************************************
'''
PROG_MODE = ProgramMode.DEBUG       # For Testing, switch to ProgramMode.RELEASE 


TIME_TO_SLEEP_BETWEEN_OFFERS = 1    # in seconds
TIME_FOR_ANSWER = 10                # in seconds
TIME_BEFORE_GAME = 10               # in seconds
MAX_CLIENTS = 2                     # server is scalable and can handle more users
UDP_PORT = 13117                    # for sending udp broadcasts
SECRET_COOKIE = 0xabcddcba          # opens "offer" message
BROADCAST_IP = "172.1.255.255"    # broadcast address TODO check
BUFFER_SIZE = 1 << 10               # buffer for receiving messages
TERMINATE_THREAD = object()         # flag for thread termination - used in message queue from main


def get_src_ip():
    if PROG_MODE == ProgramMode.DEBUG:
        network_name = 'eth1'
    elif PROG_MODE == ProgramMode.RELEASE:
        network_name = 'eth2'
    else:    
        raise RuntimeError("Bad config of setup.py: Program mode should be DEBUG or RELEASE")
    
    if network_name in get_if_list():
        return get_if_addr(network_name)
    else:
        raise RuntimeError(f"Network {network_name} not exist.")
        
def set_accepting_socket(src_ip, max_clients):
    '''
    Function sets TCP socket for accepting clients.
    Gets the maximal value of clients allowed to connect
    Returns the socket and the port the socket listens to.
    Non-Blocking and not accepting itself. 
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((src_ip, 0))  #TODO: os.uname()[1]
    _, src_port = sock.getsockname()
    # print("DEBUG: new connection - ", src_ip, src_port)
    sock.listen(max_clients)
    return sock, src_port 


def generate_quick_math():
    num1 = random.randint(0, 9)
    num2 = random.randint(0, 9 - num1)
    if random.randint(0, 1) == 0:       # plus
        return f'{num1}+{num2}', f'{num1+num2}'
    else:                               # minus
        maxNum, minNum = max(num1, num2), min(num1, num2)
        return f'{maxNum}-{minNum}', f'{maxNum-minNum}'


class Client():
    def __init__(self, client_sock):
        self.client_name = None
        self.client_sock : socket = client_sock
        self.messages_to_main = queue.Queue()
        self.messages_from_main = queue.Queue()
    