import socket, threading, time, queue, json, traceback

msgQueue = queue.Queue()
DEBUG_MODE = True


class User:
    nickName = ''
    userId = ''


class Message:
    requestId = ''
    requestType = ''
    requestContent = ''
    forward = ''


class ErrorCode:
    REQUEST_SUCCESS = 0
    REQUEST_FORMAT_BAD = 1
    REQUEST_FAILED = 2



class Response:
    
    def response(requestId, errorCode):
        ret = json.loads('{}')
        ret['requestId'] = requestId
        ret['errorCode'] = errorCode
        return json.dumps(ret) + '\n'
        

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
                
                print(data.decode('utf-8').strip())
                dataJson = json.loads(data.decode('utf-8').strip())

                if 'message' == dataJson['requestType']:
                    msg = parseMessage(dataJson)
                    msgQueue.put(msg)
                    resp = Response.response(self.requestId, ErrorCode.REQUEST_SUCCESS)
                    self.writeData(resp)

                if 'login' == dataJson['requestType']:
                    pass
                
            except:
                self.runFlag = False
                resp = Response.response(self.requestId, ErrorCode.REQUEST_FORMAT_BAD)
                self.writeData(resp)
                if DEBUG_MODE:
                    traceback.print_exc()

    def writeData(self, data):
        if self.socket:
            self.socket.sendall(data.encode('utf-8'))

    def parseMessage(dataJson):
        msg = Message()
        msg.requestId = dataJson['requestId']
        msg.requestType = dataJson['requestType']
        msg.requestContent = dataJson['requestContent']
        msg.forward = dataJson['forward']
        return msg

    def handleLogin(dataJson):
        pass

    def verifyUser(dataJson):
        pass



class PollThread(threading.Thread):

    runFlag = True

    def __init__(self, clientList):
        self.clientList = clientList
        threading.Thread.__init__(self)

    def run(self):
        while self.runFlag:
           msg = msgQueue.get()
           print(" == get a message == ")
           print(" == message id == " + msg.requestId)

    def handleMessage(self, message):
        if message.requestType == 'message':
            pass

    def getClientByUserId(self, userId):
        for client in self.clientList:
            if client.user.userId == userId:
                return client
        return None


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
