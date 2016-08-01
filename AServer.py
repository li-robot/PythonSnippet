import socket, threading, time, queue, json, traceback

msgQueue = queue.Queue()

class User:
    nickName = ''
    userId = ''
    
class Message:
    requestId = ''
    requestType = ''
    requestContent = ''
    forward = ''


class RequestClient(threading.Thread):

    runFlag = True
    user = None
    
    def __init__(self, addr, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.addr = addr

    def run(self):
        while self.runFlag:
            try:
                data = self.socket.recv(1024)
                dataJson = json.loads(data.decode('utf-8').strip())
                
                
                msg = Message()
                msg.requestId = dataJson['requestId']
                msg.requestType = dataJson['requestType']
                msgQueue.put(msg)

                print(data.decode('utf-8').strip())
                
            except:
                self.runFlag = False
                traceback.print_exc()

    def writeData(self, data):
            self.socket.sendall(data)



class PollThread(threading.Thread):

    runFlag = True

    def __init__(self, clientList):
        self.clientList = clientList
        threading.Thread.__init__(self)

    def run(self):
        while self.runFlag:
            for item in self.clientList:
                try:
                    item.writeData('response'.encode())
                except:
                    self.clientList.remove(item)
                
            time.sleep(3)
    

if __name__ == '__main__':
    
    clientList = []
   
    pt = PollThread(clientList)
    pt.start()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5000))
    server.listen(5)
    while True:
        try:
            client, addr = server.accept()
            c = RequestClient(addr, client)
            clientList.append(c)
            c.start()
        except:
            print('!!! io error !!!')
