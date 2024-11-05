class Client:
    def __init__(self, client_address, client_socket):
        self.client_socket = client_socket
        self.client_address = client_address
        self.username = None
    
    def send_message(self,message):
        self.client_socket.sendall(message.encode())
    
    def close(self):
        self.client_socket.close()