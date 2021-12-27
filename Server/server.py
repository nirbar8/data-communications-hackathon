from contextlib import closing
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
        self.event_listener = threading.Event()

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

    def handle_client(self, client):
        while True:
            next_task = client.messages_from_main.get()
            if next_task == TERMINATE_THREAD:   
                break   
            else:
                next_task(client)


    def accept_client_name(self, client : Client):
        '''
        This method should run by the client handler thread
        '''
        while True:
            message : bytes = client.client_sock.recv(BUFFER_SIZE)
            message = message.decode()
            if message.endswith('\n'):
                print(message[:-1])
                def update_name():
                    client.client_name = message[:-1]
                client.messages_to_main.put(update_name)
                break


    def accept_clients(self):
        self.game_mode = GameMode.WAITING_FOR_CLIENTS    # done every start of game
        clients = []                                     # list of all clients sockets
        for i in range(MAX_CLIENTS):
            conn, addr = self.accept_sock.accept()   # accept the i'th client
            client = Client(conn)
            clients.append(client)             # save the connection in list
            threading.Thread(target=self.handle_client, args=(client,)).start()
            client.messages_from_main.put(self.accept_client_name) # TODO: make sure name sent and add to message_to_main

        for client in clients:
            client.messages_to_main.get()()

        return clients


    def play_game(self, connections):
        self.game_mode = GameMode.IN_GAME
        
        #TODO: send clients welcome and quick math
        #TODO: game logic..


    def run(self):
        try:
            # daemon broadcasting offers as long as game in WAITING_FOR_CLIENTS mode:
            threading.Thread(target=self.broadcast_game_offer, daemon=True).start()
            print(f'Server started, listening on IP address {self.src_ip}')

            while True:
                clients = self.accept_clients()
                time.sleep(1)
                print("senity check: the number of threads running", threading.active_count())
                print("killing threads")
                for client in clients:
                    client.messages_from_main.put(TERMINATE_THREAD)
                print("senity check: the number of threads running", threading.active_count())
                time.sleep(1)
                print("senity check: the number of threads running", threading.active_count())
                print("playing...")
                time.sleep(5)
                self.play_game(clients)
                print('Game over, sending out offer requests...')

        except Exception as err:
            print(err)





# TODO:
# 1. handle errors - communication exceptions, bad operations with OS (opening sockets)
#       check validity of socket? (that no client has disconnected)    
# 2. add game logic, communication with listening threads





def main():
    with Server() as server:
        server.run()

if __name__ == "__main__":
    main()

