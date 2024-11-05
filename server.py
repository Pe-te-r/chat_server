import socket
import threading
# import json
import queue
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


    def start(self):
        """
        Start the server, bind it to the address and port, and begin listening.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.address, self.port))
        self.server.listen(self.max_connections)
        print(f'Server is listening for {self.max_connections} connections on {self.address}:{self.port}')
        
        # Start the message processing thread
        threading.Thread(target=self.process_messages, daemon=True).start()

    def process_messages(self):
        while self.running:
            try:
                message = self.message_queue.get()
                if message:
                    # print(message.message)
                    print(message.serialize())
                    # self.broadcast(message)  # Send the message to all clients
                self.message_queue.task_done()
            except queue.Empty:
                continue

    def handle_client(self, client_socket, client_address):
        """
        Handle communication with a single client, continuously waiting for messages.
        """
        client = Client(client_address,client_socket)
        # Add the client to the clients dictionary
        with self.lock:
            self.clients[client_address] = client
            print(f'Client {client.client_address} connected. Total clients: {len(self.clients)}')

        client_socket.settimeout(10)

        handling = True

        try:
            # Continuous loop to listen for messages from the client
            while handling:
                try:
                    message = client_socket.recv(1024).decode('utf-8')
                    if message:
                        # Process the received message
                        msg= Message(client.client_address,message)
                        self.message_queue.put(msg)
                    else:
                        # If message is empty, the client has disconnected
                        continue
                        # break
                except socket.timeout:
                    print(f'Client {client_address} timed out.')
                finally:
                    handling = False
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        
        finally:
            # Remove the client from the clients dictionary on disconnect
            client =  self.clients[client_address]
            client.close()
            del self.clients[client_address]
            print(f'Client {client_address} disconnected. Total clients: {len(self.clients)}')

    def broadcast(self, message, exclude_client=None):
        """
        Send a message to all connected clients, optionally excluding one client.
        """
        for client_address, client_socket in self.clients.items():
            if client_address != exclude_client:  # Optional exclusion of the sender
                try:
                    client_socket.sendall(message.encode('utf-8'))
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
                
                # Start a new thread to handle the client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
                
            except KeyboardInterrupt:
                print('Server shutting down.')
            except Exception as e:
                print(f"There was a connection error: {e}")
            finally:
                self.running = False

    def close(self):
        """
        Close the server socket and disconnect all clients.
        """
        with self.lock:
            if  self.clients:
                for client_address, client_socket in self.clients.items():
                    client_socket.close()
                    print(f"Client {client_address} forcibly disconnected.")
        
        if self.server:
            self.server.close()
            print("Server closed.")

# Usage example
if __name__ == "__main__":
    server = Server('192.168.0.109', 65118)
    server.start()
    server.wait_connections()
    # server.close()
