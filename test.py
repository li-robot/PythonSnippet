import socket

class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((host, port))

    def write(self, data):
        self.sock.sendall(data.encode('utf-8'))
        pass

client = Client('127.0.0.1', 5000)
client.write('hello world')

        

