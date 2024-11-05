import socket
import threading
import time

class Client:
    def __init__(self, address, port, udp_port):
        self.server_address = address
        self.server_port = port
        self.udp_port = udp_port
        self.running = True

        # TCP socket for messaging
        self.server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # UDP socket for pinging
        self.server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        # Start the TCP connection
        self.server_tcp.connect((self.server_address, self.server_port))
        print("Connected to server via TCP.")
        
        # Start threads
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
        threading.Thread(target=self.ping_server, daemon=True).start()
        
        # Send messages from user input
        self.send_messages()

    def ping_server(self):
        """ Periodically sends UDP pings to the server every 7 seconds. """
        while self.running:
            try:
                ping_message = "ping"
                self.server_udp.sendto(ping_message.encode('utf-8'), (self.server_address, self.udp_port))
                print("Ping sent via UDP")
            except Exception as e:
                print(f"Error sending UDP ping: {e}")
            time.sleep(3)

    def listen_for_messages(self):
        """ Continuously listens for messages from the server via TCP. """
        while self.running:
            try:
                message = self.server_tcp.recv(1024).decode('utf-8')
                if message:
                    print(f"Server: {message}")
                else:
                    print("Server disconnected.")
                    self.running = False
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.running = False

    def send_messages(self):
        """ Sends user-input messages to the server via TCP. """
        while self.running:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                self.running = False
                self.server_tcp.close()
                self.server_udp.close()
                print("Disconnected from server.")
                break
            try:
                self.server_tcp.sendall(user_input.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")
                self.running = False
                break

# Usage example
if __name__ == "__main__":
    client = Client('localhost', 65120, 60123)
    client.start()
