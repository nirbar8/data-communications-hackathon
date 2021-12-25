from scapy.all import *
from enum import Enum, auto


class GameMode(Enum):
    WAITING_FOR_CLIENTS = auto()
    IN_GAME             = auto()

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
MAX_CLIENTS = 2                     # server is scalable and can handle more users
UDP_PORT = 13117                    # for sending udp broadcasts
SECRET_COOKIE = 0xabcddcba          # opens "offer" message
BROADCAST_IP = "255.255.255.255"    


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
        
def set_accepting_socket(max_clients):
    '''
    Function sets TCP socket for accepting clients.
    Gets the maximal value of clients allowed to connect
    Returns the socket and the port the socket listens to.
    Non-Blocking and not accepting itself. 
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((os.uname()[1], 0))
    _, src_port = sock.getsockname()
    sock.listen(max_clients)
    return sock, src_port 