from flask import *
from pymongo import *

app = Flask(__name__)

# http://localhost:8000/createCourse?name='创意美术'&startTime='2018-5-9 10:00'&endTime='2018-5-9 11:00'&teacher='李耀华'

__STUDENT_DOC = 'student'
__COURSE_DOC = 'course'

def initDB(host='localhost', port=27017, db_name=None):
    client = MongoClient(host=host, port=port)
    return client[db_name]


def getDocument(db, doc_name):
    return db[doc_name]


def generateCallback(status, msg):
    ret = dict()
    ret['status'] = status
    ret['msg'] = msg
    return jsonify(ret)

# state 表示课程是否结束 0 没有 1 结束

def create_course(course_name, start_time, end_time, teacher_name):
    course = dict()
    course['course_name'] = course_name
    course['start_time'] = start_time
    course['end_time'] = end_time
    course['teacher_name'] = teacher_name
    course['state'] = 0
    course['students'] = []
    return course


smDb = initDB(db_name='studentManager')


@app.route('/createCourse', methods=['POST', 'GET'])
def createCourse():
    if request.method == 'GET':
        try:
            course_name = request.args['name']
            course_startTime = request.args['startTime']
            course_endTime = request.args['endTime']
            teacher_name = request.args['teacher']
        except KeyError:
            return generateCallback(False, 'course name or time empty')

        course = create_course(course_name, course_startTime, course_endTime, teacher_name)
        courseDoc = getDocument(smDb, __COURSE_DOC)
        courseDoc.insert(course)

    return generateCallback(True, 'create course success')


@app.route('/getCourse', methods=['GET', 'POST'])
def getCourse():
    all_course = getDocument(smDb, __COURSE_DOC)
    return str(list(all_course.find()))

#############################
app.debug = True
app.run(host='0.0.0.0', port=8000)
#############################

