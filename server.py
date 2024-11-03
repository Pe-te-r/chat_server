import socket

class Server:
    def __init__(self,address,port,max_connections=10):
        self.server = None
        self.port=port
        self.address= address
        self.max_connections = max_connections
    
    def start(self):
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.bind((self.address,self.port))
        print(f'server is listening for {self.max_connections} connections on {self.address}:{self.port}')
        self.server.listen(self.max_connections)

    def wait_connections(self):
        while True:
            try:
                client_socket,client_address = self.server.accept()
                print(f'client connected: {client_address}')
                client_socket.close()
                print(f'client closed: {client_address}')
            except KeyboardInterrupt:
                server.close()
                client_socket.close()
                print('there was a connection error')

    def close(self):
        self.server.close()

server = Server('192.168.0.109',55125)
server.start()
server.wait_connections()
server.close()