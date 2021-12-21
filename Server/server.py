from scapy.all import *
from time import sleep

TESTING_MODE = False                # For Testing, switch to True

TIME_TO_SLEEP_BETWEEN_OFFERS = 1    # in seconds
MAX_CLIENTS = 2
UDP_PORT = 13117

def get_src_ip():
    network_name = 'eth2' if TESTING_MODE else 'eth2'   
    if network_name in get_if_list():
        return 'blablabla' # get_if_addr(network_name)        #TODO: remove comment when testing
    else:
        raise RuntimeError(f"Network {network_name} not exist.")
        


def send_game_offer(port):
    packet = "\xab\xcd\xdc\xba" + "\x02" + port 
    send(IP(dst="255.255.255.255")/UDP(dport=UDP_PORT)/Raw(load=packet))


def main():
    try:
        src_ip = get_src_ip()
        while True:
            print(f'Server started, listening on IP address {src_ip}')
            while True:
                serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                serversocket.bind((serversocket.gethostname(), 0))
                _, src_port = serversocket.getsockname()
                serversocket.listen(MAX_CLIENTS)
                send_game_offer(src_port)
                print("test")
                sleep(TIME_TO_SLEEP_BETWEEN_OFFERS)
            
            break  

    except RuntimeError as err:
        print(err)


if __name__ == "__main__":
    main()

