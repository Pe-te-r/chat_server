class Client:
    def __init__(self, client_address, client_socket,username=None):
        self.client_socket = client_socket
        self.udp_socket = None
        self.client_address = client_address
        self.username = username
    
    def __repr__(self):
        return f'Client(Address: {self.client_address}, Username: {self.username})'
    
    # def setUdpSocket(self,socket):
    #     self.udp_socket=socket

    def send_message(self,message):
        self.client_socket.sendall(message.encode())
    
    def close(self):
        self.client_socket.close()
    
    def sendall(self,message):
        self.client_socket.sendall(message.encode('utf-8'))
