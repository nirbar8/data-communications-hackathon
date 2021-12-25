import socket
import os
import threading
from setup import *
from time import sleep



class Server:

    def __init__(self):
        self.game_mode = None
        self.src_ip = get_src_ip()
        self.accept_sock, self.listen_port = set_accepting_socket(MAX_CLIENTS)


    def broadcast_game_offer(self, port):
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
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        packet = SECRET_COOKIE.to_bytes(4, byteorder='big') + \
                (0x02).to_bytes(2, byteorder='big') + \
                port.to_bytes(2, byteorder='big') 

        while True:
            if self.game_mode == GameMode.WAITING_FOR_CLIENTS:
                udp_sock.sendto(packet, (BROADCAST_IP, UDP_PORT))
            time.sleep(TIME_TO_SLEEP_BETWEEN_OFFERS)


    def run(self):
        #while True:
            # tcp_connections = wait_for_clients()
            # play_game(tcp_connections)

            # daemon broadcasting offers as long as game in WAITING_FOR_CLIENTS mode:
            threading.Thread(target=self.broadcast_game_offer, args=(self.listen_port, ), daemon=True).start()   
            print(f'Server started, listening on IP address {self.src_ip}')

            while True:
                game_mode = GameMode.WAITING_FOR_CLIENTS    # done every start of game
                connections = []                    # list of all clients sockets
                for i in range(MAX_CLIENTS):
                    conn, addr = self.accept_sock.accept()
                    connections.append(conn)
                    print(conn, addr)               # TODO: for debug, delete

                # done accepting clients - starting game
                game_mode = GameMode.IN_GAME
                
                #TODO: send clients welcome and quick math
                #TODO: game logic..

                # game over, restarting...
                print('Game over, sending out offer requests...')





# TODO:
# 1. handle errors - communication exceptions, bad operations with OS (opening sockets)
# 2. add game logic, communication with listening threads





def main():
    server = Server()
    server.run()

if __name__ == "__main__":
    main()

