import socket, threading

class PyServer(threading.Thread):

    list = []

    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(5)

    def run(self):
        while True:
            s, addr = self.sock.accept()
            self.list.append(s)
            data = s.recv(1024)
            if not data:
                break
            else:
                print(data)
            print('total links : ' + str(len(self.list)))



if __name__ == '__main__':
    server = PyServer('127.0.0.1', 5000)
    server.start()
    
        
