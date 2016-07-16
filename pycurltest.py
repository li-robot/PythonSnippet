import urllib.request
import threading
import time

def getImage(url):
    file = urllib.request.urlopen(url)
    saveFile = open('c:/log/icon.jpg', 'wb')
    saveFile.write(file.read())

class DownLoadImage(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        getImage('http://img1.3lian.com/2015/w7/98/d/22.jpg')
        print('download success')

if __name__ == '__main__':

    task = DownLoadImage()
    task.start();

    while True:
       time.sleep(1)
       print('main loop')
        
        


