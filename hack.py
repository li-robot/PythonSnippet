# use python 3

import urllib.request
import threading
import re
import os

class WorkTask(threading.Thread):

    path = ''
    
    def __init__(self, url, path=''):
        threading.Thread.__init__(self)
        self.url = url
        self.path = path

    def run(self):
        list = self.getAllLinks(str(self.getData(self.url)))
        for link in list:
            print(link)
        if not self.path and os.path.exist(self.path):
            self.writeToFile(list, self.path, 'a')
        else:
            self.writeToFile(list, self.path, 'w')

    def getAllLinks(self, data):
        list = re.findall('http://[\\w|\\d|\\.|/]{0,}', data)
        return list
    
    def getData(self, url):
        file = urllib.request.urlopen(url)
        return file.read()

    def writeToFile(self, result, path, mode):
        file = open(path, mode)
        file.writelines(result)



if __name__ == '__main__':
    task = WorkTask('http://www.apicloud.com', 'c:/log/result.txt')
    task.start()
   
