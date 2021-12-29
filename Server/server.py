from contextlib import closing
import enum
import socket
import os
import sys
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
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udp_sock:
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_sock.bind((self.src_ip, 0))
            packet = SECRET_COOKIE.to_bytes(4, byteorder='little') + \
                    (0x02).to_bytes(1, byteorder='big') + \
                    self.listen_port.to_bytes(2, byteorder='little') 

            while True:
                if self.game_mode == GameMode.WAITING_FOR_CLIENTS:
                    udp_sock.sendto(packet, (BROADCAST_IP, UDP_PORT))
                    # print("DEBUG: broadcast offer sent")                          # TODO: for debug, delete

                for i in range(2):
                    # print(f"DEBUG: active threads {threading.active_count()}")
                    time.sleep(1)
                time.sleep(TIME_TO_SLEEP_BETWEEN_OFFERS)


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

    def accept_answer(self, client : Client):
        '''
        This method should run by the client handler thread
        '''
        try: 
            client.client_sock.settimeout(TIME_FOR_ANSWER) 
            # print(f'DEBUG: set timeout for client {client.client_name} and wait for answer')
            message : bytes = client.client_sock.recv(BUFFER_SIZE)
            if not message:
                pass
            message = message.decode()
            if len(message) == 1:
                # print(f'DEBUG: client {client.cslient_name} answered {message}')
                client.messages_to_main.put(message)
                self.event_listener.set()               # waking the main thread up
        except socket.error:
            pass
        except OSError:
            #print(f"DEBUG: OSError from thread {threading.current_thread().name}. Bye...")
            pass



    def accept_clients(self):
        self.game_mode = GameMode.WAITING_FOR_CLIENTS    # done every start of game
        clients = []                                     # list of all clients sockets
        for _ in range(MAX_CLIENTS):
            conn, addr = self.accept_sock.accept()   # accept the i'th client
            client = Client(conn)
            clients.append(client)             # save the connection in list
            threading.Thread(target=self.handle_client, args=(client,)).start()
            client.messages_from_main.put(self.accept_client_name)

        for client in clients:
            client.messages_to_main.get()()

        return clients


    def generate_quick_math_message(self, clients):
        question, answer = generate_quick_math()
        message = f'Welcome to Quick Maths.\n'
        for index, client in enumerate(clients):
            message += f'Player {index}: {client.client_name}\n'
        message += '==\n'
        message += 'Please answer the following question as fast as you can:\n'
        message += f'How much is {question}?\n'
        return message, answer

    def broadcast_str_to_client(self, clients, msg):
        #print("DEBUG: broadcasting to clients") #TODO: delete
        print(msg)
        for client in clients:
            client.client_sock.sendall(msg.encode("ascii"))


    def broadcast_draw(self, clients, game_over_msg):
        game_over_msg += "No one won this game...\n\n"
        self.broadcast_str_to_client(clients, game_over_msg)
    def broadcast_win(self, clients, game_over_msg, client):
        game_over_msg += f"Congratulations to the winner: {client.client_name}\n\n"
        self.broadcast_str_to_client(clients, game_over_msg)
    def broadcast_lose(self, clients, game_over_msg, client):
        game_over_msg += f"The player: {client.client_name} has lost this game...\n\n"
        self.broadcast_str_to_client(clients, game_over_msg)

    def get_game_results(self, clients):
        first_client = None
        client_answer = None
        for client in clients:
            try:
                client_answer = client.messages_to_main.get(False)      # non-blocking get - returns answer when this is the thread sent the notification
                first_client = client
                break
            except queue.Empty:                                         # not the client that notify the main thread because of answer
                pass
        return first_client, client_answer

    def play_game(self, clients):
        self.game_mode = GameMode.IN_GAME
        time.sleep(TIME_BEFORE_GAME)
        message, correct_answer = self.generate_quick_math_message(clients)
        self.broadcast_str_to_client(clients, message)
        for client in clients:
            client.messages_from_main.put(self.accept_answer)
        self.event_listener.wait(timeout=TIME_FOR_ANSWER)       # waiting for the client threads to noitify that answer recieved
        
        first_client, client_answer = self.get_game_results(clients)
        game_over_msg = f'Game over!\nThe correct answer was {correct_answer}!\n\n'
        if first_client == None:                # a draw
            self.broadcast_draw(clients, game_over_msg)
        elif client_answer == correct_answer:   # first client won
            self.broadcast_win(clients, game_over_msg, first_client)
        else:                                   # first client lost
            self.broadcast_lose(clients, game_over_msg, first_client)
        
        for client in clients:
            client.messages_from_main.put(TERMINATE_THREAD)
            client.client_sock.close()


    def run(self):
        # try:
            # daemon broadcasting offers as long as game in WAITING_FOR_CLIENTS mode:
            threading.Thread(target=self.broadcast_game_offer, daemon=True).start()
            print(f'Server started, listening on IP address {self.src_ip}')

            while True:
                clients = self.accept_clients()
                # print('starting game...')           # TODO: debug
                self.play_game(clients)
                print('Game over, sending out offer requests...')
                self.event_listener = threading.Event()

        # except Exception as err:
        #     print(err)

def main():
    with Server() as server:
        try:
            server.run()
        except KeyboardInterrupt:
            print("\nExiting server...")
            os._exit(0)


if __name__ == "__main__":
    main()

