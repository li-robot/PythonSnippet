from pymongo import *
from bson import ObjectId

mongoDb = MongoClient()
testdb = mongoDb['studentManager']

testDoc = testdb['course']

objId = '5af13ea3d373302d58bdd45e'

testDoc.update({'_id': ObjectId(objId)}, {'$set':{'state' : 1}})

print(str(testDoc.find_one({'_id': ObjectId(objId)})))
