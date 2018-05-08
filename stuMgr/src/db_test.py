from pymongo import *

mongoDb = MongoClient()
testdb = mongoDb['test']

testDoc = testdb['testDoc']

testDoc1 = testdb['testDoc1']

testDoc1.insert({"name":'haha'})