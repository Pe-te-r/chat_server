import socket
import threading
# import json
import queue

class Server:
    def __init__(self, address, port, max_connections=10):
        self.server = None
        self.port = port
        self.address = address
        self.max_connections = max_connections
        self.clients = {}
        self.message_queue = queue.Queue()
        self.lock = threading.Lock()

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
        while True:
            message = self.message_queue.get()
            if message is None:  # Exit the loop if None is received
                break
                # pass
            print(message)
            # self.broadcast(message)  # Send the message to all clients
            self.message_queue.task_done()

    def handle_client(self, client_socket, client_address):
        """
        Handle communication with a single client, continuously waiting for messages.
        """
        # Add the client to the clients dictionary
        with self.lock:
            self.clients[client_address] = client_socket
            print(f'Client {client_address} connected. Total clients: {len(self.clients)}')

        client_socket.settimeout(10)

        try:
            # Continuous loop to listen for messages from the client
            while True:
                try:
                    message = client_socket.recv(1024).decode('utf-8')
                    if message:
                        # Process the received message
                        self.message_queue.put(f'{client_address}: {message}')
                    else:
                        # If message is empty, the client has disconnected
                        break
                        # pass
                except socket.timeout:
                    print(f'Client {client_address} timed out.')
                    break
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        
        finally:
            # Remove the client from the clients dictionary on disconnect
            del self.clients[client_address]
            client_socket.close()
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
        while True:
            try:
                client_socket, client_address = self.server.accept()
                print(f'Client connected: {client_address}')
                
                # Start a new thread to handle the client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
                
            except KeyboardInterrupt:
                print('Server shutting down.')
                self.close()
                break
            except Exception as e:
                self.close()
                print(f"There was a connection error: {e}")

    def close(self):
        """
        Close the server socket and disconnect all clients.
        """
        # Close all active client connections
        with self.lock:
            if not self.clients:
                return
            for client_address, client_socket in self.clients.items():
                client_socket.close()
                print(f"Client {client_address} forcibly disconnected.")
        
        if self.server:
            self.server.close()
            print("Server closed.")

# Usage example
if __name__ == "__main__":
    server = Server('192.168.0.109', 65124)
    server.start()
    server.wait_connections()
    server.close()
