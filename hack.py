# use python 3

import urllib.request
import threading
import re
import os
import hash

class WorkTask(threading.Thread):

    path = ''
    
    def __init__(self, url, callback):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        list = self.getAllLinks(str(self.getData(self.url)))
        for link in list:
            print(link)
        callback()
       

    def getAllLinks(self, data):
        list = re.findall('http://[\\w|\\d|\\.|/]{0,}', data)
        return list
    
    def getData(self, url):
        file = urllib.request.urlopen(url)
        return file.read()

def callback():
    print('task down!')


task = WorkTask('http://www.apicloud.com', callback)
task.start()

   
