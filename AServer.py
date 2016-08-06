import socket, threading, time, queue, json, traceback

msgQueue = queue.Queue()
DEBUG_MODE = False

class User:

    def __init__(self, name, password):
        self.name = name;
        self.password = password
        
    name = ''
    password = ''
    isOnLine = False
    messageBox = []
    conn = None


class Message:
    requestId = ''
    requestType = ''
    requestContent = ''
    forward = ''


class ErrorCode:
    REQUEST_SUCCESS = 0
    REQUEST_FORMAT_BAD = 1
    REQUEST_FAILED = 2
    LOGIN_FAILED = 3
    HAS_LOGINED = 4
    USER_INEXISTENCE = 5
    
## user management
   
localUserList = []
onLineUserList = []

user1 = User('robot', '123')
user2 = User('ligo', '234')
user3 = User('haha', '123')

localUserList.append(user1)
localUserList.append(user2)
localUserList.append(user3)


class Response:
    
    def response(requestType, requestId, errorCode):
        ret = json.loads('{}')
        ret['requestId'] = requestId
        ret['errorCode'] = errorCode
        ret['requestType'] = requestType
        return json.dumps(ret) + '\n'
        

class Connection(threading.Thread):

    runFlag = True
    isConnect = False
    
    def __init__(self, addr, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.addr = addr

    def run(self):
        while self.runFlag:
            try:
                data = self.socket.recv(1024)
                dataJson = json.loads(data.decode('utf-8').strip())

                if 'message' == dataJson['requestType'] and self.isConnect:
                    msg = self.parseMessage(dataJson)
                    msgQueue.put(msg)
                    resp = Response.response('message', dataJson['requestId'], ErrorCode.REQUEST_SUCCESS)
                    self.writeData(resp)

                if 'login' == dataJson['requestType']:
                    if self.handleLogin(dataJson):
                        resp = Response.response('login', dataJson['requestId'], ErrorCode.REQUEST_SUCCESS)
                        self.writeData(resp)
                        ## build session ##
                        user = User(dataJson['userName'], dataJson['password'])
                        user.isOnLine = True
                        user.conn = self
                        onLineUserList.append(user)
                        self.isConnect = True
                        ##
                    else:
                        resp = Response.response('login', dataJson['requestId'], ErrorCode.LOGIN_FAILED)
                        self.writeData(resp)
                        self.runFlag = False
                        self.socket.close()

                
            except:
                self.runFlag = False
                resp = Response.response('','', ErrorCode.REQUEST_FORMAT_BAD)
                self.writeData(resp)
                self.socket.close()
                if DEBUG_MODE:
                    traceback.print_exc()

    def writeData(self, data):
        if self.socket:
            self.socket.sendall(data.encode('utf-8'))

    def parseMessage(self, dataJson):
        msg = Message()
        msg.requestId = dataJson['requestId']
        msg.requestType = dataJson['requestType']
        msg.requestContent = dataJson['requestContent']
        msg.forward = dataJson['forward']
        return msg

    def handleLogin(self, dataJson):
        for user in localUserList:
            if user.name == dataJson['userName'] and user.password == dataJson['password']:
                return True
            else:
                return False




class MessageHandleThread(threading.Thread):

    runFlag = True

    def __init__(self, clientList):
        self.clientList = clientList
        threading.Thread.__init__(self)

    def run(self):
        while self.runFlag:
           msg = msgQueue.get()
           print(" == get a message == ")
           print(" == message id == " + msg.requestId)
           handleMessage(msg)

    def handleMessage(self, msg):
       for onLine in onLineUserList:
           if msg.forward == onLine.name:
               onLine.writeData(msg.requestContent)
                


if __name__ == '__main__':
    
    clientList = []
   
    pt = MessageHandleThread(clientList)
    pt.start()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5000))
    server.listen(5)
    while True:
        try:
            client, addr = server.accept()
            c = Connection(addr, client)
            c.start()
        except:
            print('!!! io error !!!')
