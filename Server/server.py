from logging import error
from shutil import Error
import socket
import os
import threading
from setup import *
from time import sleep



class Server:

    def __init__(self):
        self.game_mode = None
        self.src_ip = get_src_ip()
        self.accept_sock, self.listen_port = set_accepting_socket(self.src_ip, MAX_CLIENTS)
        self.condition = threading.Condition()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("EXITING SERVER!!") #TODO: Debug, delete
        self.game_mode = GameMode.TERMINATE
        self.accept_sock.close()

    def broadcast_game_offer(self):
        '''
        This method should run as daemon thread single time.
        Method sends udp broadcasts with offers for game in the following format:
            SECRET_COOKIE(4) + MESSAGE TYPE(1) + CONNECTION PORT(2)
            For example - 0xabcddcba023030
        Method sleeps between offers (blocking).

        FOR DEVELOPERS: For higher frequency broadcasting, 
        you may change the architecture so the thread will not be daemon (called only if needed)
        '''
        assert threading.currentThread().isDaemon() 
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_sock.bind((self.src_ip, 0))
        packet = SECRET_COOKIE.to_bytes(4, byteorder='big') + \
                (0x02).to_bytes(1, byteorder='big') + \
                self.listen_port.to_bytes(2, byteorder='big') 


        while self.game_mode != GameMode.TERMINATE:
            if self.game_mode == GameMode.WAITING_FOR_CLIENTS:
                udp_sock.sendto(packet, (BROADCAST_IP, UDP_PORT))
                print("broadcast")                          # TODO: for debug, delete
            time.sleep(TIME_TO_SLEEP_BETWEEN_OFFERS)

        udp_sock.close()  

    def accept_clients(self):
        connections = []                                 # list of all clients sockets
        for i in range(MAX_CLIENTS):
            print("waiting for client..")               # TODO: for debug, delete
            conn, addr = self.accept_sock.accept()       # accept the i'th client
            connections.append(conn)                     # save the connection in list
            print("New client: ", conn, addr)               # TODO: for debug, delete

    def play_game(self, connections):
        self.game_mode = GameMode.IN_GAME
        
        #TODO: send clients welcome and quick math
        #TODO: game logic..


    def run(self):
        # daemon broadcasting offers as long as game in WAITING_FOR_CLIENTS mode:
        try:
            threading.Thread(target=self.broadcast_game_offer, daemon=True).start()
            print(f'Server started, listening on IP address {self.src_ip}')

            while True:
                self.game_mode = GameMode.WAITING_FOR_CLIENTS    # done every start of game
                connections = self.accept_clients()
                self.play_game(connections)

                # game over, restarting...
                print('Game over, sending out offer requests...')
        except Exception as err:
            print(err)





# TODO:
# 1. handle errors - communication exceptions, bad operations with OS (opening sockets)
# 2. add game logic, communication with listening threads





def main():
    with Server() as server:
        server.run()

if __name__ == "__main__":
    main()

