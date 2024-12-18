import socket
import threading
import queue
from time import sleep
import json
from message_client import Message
from client_server import Client

class Server:
    def __init__(self, address, port, max_connections=10):
        self.server = None
        self.port = port
        self.address = address
        self.max_connections = max_connections
        self.clients = {}
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()
        self.running = True 
        self.server_udp=None
        self.udp_port = 60123


    def start(self):
        """
        Start the server, bind it to the address and port, and begin listening.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.address, self.port))
        self.server.listen(self.max_connections)
        if self.server_udp is None:
            self.server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # self.server_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_udp.bind((self.address, self.udp_port))   
            print(f'UDP Server listening on {self.server_udp}:{self.udp_port}')

        print(f'Server is listening for {self.max_connections} connections on {self.address}:{self.port}')
        
        # Start the message processing thread
        threading.Thread(target=self.process_messages, daemon=True).start()
        threading.Thread(target=self.ping,daemon=True).start()
    
    def ping(self):
        while self.running:
            try:
                if self.server_udp is not None:
                    message, client_address = self.server_udp.recvfrom(1024)
                    message = message.decode('utf-8')
                    message = json.loads(message)
                    user=message['username']
                    print('below here')
                    # print(message)
                    print(self.clients)
                    # print(self.clients[user])

                    # print('here')
                    # # if message.decode('utf-8') == 'ping':
            except Exception as e:
                print(e)


    def process_messages(self):
        while self.running:
            try:
                message = self.message_queue.get()
                print(f'processing: {message}')
                if message.message['username']:
                    client = self.clients[message.username]
                    client.username = message.message['username']
                if message:
                    print(message.serialize())
                    # self.broadcast(message)  # Send the message to all clients
                self.message_queue.task_done()
            except queue.Empty:
                continue


    def add(self,client,username):
                client.username=username
                print(client)
            # with self.lock:
                print('client above')
                print('username: ' + client)
                self.clients[client.username] = client
                print(f'Client {client.client_address} connected. Total clients: {len(self.clients)}')
    def handle_client(self, client_socket, client_address):
        """
        Handle communication with a single client, continuously waiting for messages.
        """
        client = Client(client_address,client_socket)

        list_add=False

        
                # list_add=True

        # client_socket.settimeout(10)


        try:
            handling = True

            while handling:
                try:
                    message = client_socket.recv(1024).decode('utf-8')
                    message = json.loads(message)
                    print(message['username'])
                    if message['username'] and not list_add:
                        print('adding')
                        self.add(client, message['username'])
                        list_add=True
                    print(f'message received: {message}')
                    

                    if message:
                        msg= Message(client.client_address,message,client.username)
                        self.message_queue.put(msg)
                    else:
                        # print(client)
                        continue
                except socket.timeout:
                    print(f'Client {client_address} timed out.')
                    handling=False
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        
        finally:
            client =  self.clients[client.username]
            client.close()
            del self.clients[client.username]
            print(f'Client {client_address} disconnected. Total clients: {len(self.clients)}')

    def broadcast(self, message, exclude_client=None):
        """
        Send a message to all connected clients, optionally excluding one client.
        """
        for client_address, client_socket in self.clients.items():
            if client_address != exclude_client:  # Optional exclusion of the sender
                try:
                    client_socket.sendall(message)
                except Exception as e:
                    print(f"Error sending message to {client_address}: {e}")

    def wait_connections(self):
        """
        Accept incoming connections and spawn a new thread for each client.
        """
        while self.running:
            try:
                client_socket, client_address = self.server.accept()
                print(f'Client connected: {client_address}')
                
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
                
            except KeyboardInterrupt:
                self.running = False
                print('Server shutting down.')
            except Exception as e:
                print(f"There was a connection error: {e}")
            finally:
                pass

    def close(self):
        """
        Close the server socket and disconnect all clients.
        """
        with self.lock:
            if  self.clients:
                for client_address, client_socket in self.clients.items():
                    client_socket.close()
                    print(f"Client {client_address} forcibly disconnected.")
            else:
                print('no client now')
        if self.server:
            self.server.close()
            print("Server closed.")

# Usage example
if __name__ == "__main__":
    server = Server('localhost', 65120)
    server.start()
    server.wait_connections()
    while server.wait_connections():
        sleep(1)
    server.close()
