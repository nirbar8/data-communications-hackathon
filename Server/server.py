from scapy.all import *
from time import sleep
import socket
import os
import threading

TESTING_MODE = False                # For Testing, switch to True

TIME_TO_SLEEP_BETWEEN_OFFERS = 1    # in seconds
MAX_CLIENTS = 2
UDP_PORT = 13117
SECRET_COOKIE = 0xabcddcba
BROADCAST_IP = "255.255.255.255"


def get_src_ip():
    network_name = 'eth2' if TESTING_MODE else 'eth1'   
    if network_name in get_if_list():
        return get_if_addr(network_name)
    else:
        raise RuntimeError(f"Network {network_name} not exist.")
        


# def get_game_offer():
#     udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     udp_sock.bind(("127.0.0.1", UDP_PORT))
#     print(udp_sock.recvfrom(1024))
    


def send_game_offer(port):
    packet = SECRET_COOKIE.to_bytes(4, byteorder='big') + \
            (0x02).to_bytes(2, byteorder='big') + \
            port.to_bytes(2, byteorder='big') 
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.sendto(packet, (BROADCAST_IP, UDP_PORT))

def main():
    #while True:
        # tcp_connections = wait_for_clients()
        # play_game(tcp_connections)

    try:
        src_ip = get_src_ip()
        while True:
            print(f'Server started, listening on IP address {src_ip}')
            while True:
                serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                serversocket.bind((os.uname()[1], 0))
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

