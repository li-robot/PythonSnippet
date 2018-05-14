from flask import *
from pymongo import *
from bson import ObjectId

app = Flask(__name__)

# http://localhost:8000/createCourse?name='创意美术'&startTime='2018-5-9 10:00'&endTime='2018-5-9 11:00'&teacher='李'

__STUDENT_DOC = 'student'
__COURSE_DOC = 'course'

#########################
# ***** course info *****
# 1. courseName
# 2. startTime
# 3. endTime
# 4. id
# 5. state
# 6. students
# 7. teacherName
#########################


#############################
# ****** student info *******
# 1. studentName
# 2. contacts
# 3. period
# 4. password
#############################


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


def isCourseComplete(obj):
    if obj['state'] == 1:
        return True
    return False

def generateCourse(obj):
    courseDict = dict()
    courseDict['id'] = str(obj['_id'])
    courseDict['courseName'] = obj['course_name']
    courseDict['startTime'] = obj['start_time']
    courseDict['endTime'] = obj['end_time']
    courseDict['teacherName'] = obj['teacher_name']
    courseDict['state'] = obj['state']
    courseDict['students'] = obj['students']
    return courseDict


def containsStudent(list, studentName):
    for student in list:
        if student['studentName'] == studentName:
            return True
    return False

def generateStudent(obj):
    studentDic = dict()
    studentDic['studentName'] = obj['studentName']
    studentDic['contacts'] = obj['contacts']
    studentDic['period'] = obj['period']
    studentDic['password'] = obj['password']
    return studentDic


def generateStudentWithoutPassword(obj):
    studentDic = dict()
    studentDic['studentName'] = obj['studentName']
    studentDic['contacts'] = obj['contacts']
    studentDic['period'] = obj['period']
    return studentDic


smDb = initDB(db_name='studentManager')


@app.route('/course/createCourse', methods=['POST', 'GET'])
def createCourse():
    if request.method == 'GET':
        try:
            course_name = request.args['courseName']
            course_startTime = request.args['startTime']
            course_endTime = request.args['endTime']
            teacher_name = request.args['teacher']
        except KeyError:
            return generateCallback(False, 'course name or time empty')

        course = create_course(course_name, course_startTime, course_endTime, teacher_name)
        courseDoc = getDocument(smDb, __COURSE_DOC)
        courseDoc.insert(course)

    return generateCallback(True, 'create course success')


@app.route('/course/getAllCourse', methods=['GET', 'POST'])
def getAllCourse():
    all_course = getDocument(smDb, __COURSE_DOC)
    courseList = []
    for course in all_course.find():
        courseList.append(generateCourse(course))
    return jsonify(courseList)


@app.route('/course/getNotCompleteCourse', methods=['GET', 'POST'])
def getNotCompleteCourse():
    all_course = getDocument(smDb, __COURSE_DOC)
    courseList = []
    for course in all_course.find():
        if not isCourseComplete(course):
            courseList.append(generateCourse(course))
    return jsonify(courseList)


@app.route('/course/setcomplte', methods=['GET', 'POST'])
def setComplete():
    if request.method == 'GET':
        try:
            course_id = request.args['courseId']
        except KeyError:
            return generateCallback(False, 'courseId is empty, set complete failed')
        courseDoc = getDocument(smDb, __COURSE_DOC)
        courseDoc.update({'_id': ObjectId(course_id)}, {'$set': {'state': 1}})
    return generateCallback(True, 'set complete true')


@app.route('/course/addStudentToCourse')
def addStudentToCourse():
    if request.method == 'GET':
        try:
            course_id = request.args['courseId']
            studentName = request.args['studentName']
        except KeyError:
            return generateCallback(False, 'courseId or studentName is empty, add failed')

        student = getDocument(smDb, __STUDENT_DOC).find_one({'studentName': studentName})
        course = getDocument(smDb, __COURSE_DOC).find_one({'_id': ObjectId(course_id)})
        courseDoc = getDocument(smDb, __COURSE_DOC)
        studentList = []
        if student and course:
            if course['students']:
                studentList = course['students']
            else:
                studentList = list()

            if not containsStudent(studentList, studentName):
                studentList.append(generateStudent(student))
            else:
                return generateCallback(False, 'already added, can not repeat add')
            courseDoc.update({'_id': ObjectId(course_id)}, {'$set': {'students': studentList}})
            return generateCallback(True, 'add student to course success')
        else:
            return generateCallback(False, 'courseId or studentName is invalidate')


@app.route('/signin', methods=['POST'])
def signin():
    if request.method == 'POST':
        try:
            studentName = request.form['studentName']
        except KeyError:
            return generateCallback(False, 'studentName is empty, add failed')
        studentDoc = getDocument(smDb, __STUDENT_DOC).find_one({"studentName": studentName})
        if studentDoc:
            curPeriod = studentDoc['period'] - 1
            getDocument(smDb, __STUDENT_DOC).update({"studentName": studentName}, {'$set':{'period': curPeriod}})
            return generateCallback(True, 'signin sucess')
        else:
            return generateCallback(False, 'student not exist')

# localhost:8000/student/addStudent?studentName=李治&contacts=15366123467&period=24

@app.route('/student/addStudent')
def addStudent():
    if request.method == 'GET':
        try:
            studentName = request.args['studentName']
            contacts = request.args['contacts']
            period = request.args['period']
        except KeyError:
            return generateCallback(False, 'studentName, contacts or period is empty, add failed')

        studentDoc = getDocument(smDb, __STUDENT_DOC).find_one({"studentName": studentName})
        if studentDoc:
            return generateCallback(False, 'the student has already added')
        else:
           getDocument(smDb, __STUDENT_DOC).insert({'studentName': studentName, 'contacts': contacts, 'period': int(period), 'password':'123456'})
        return generateCallback(True, 'add success')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        try:
            studentName = request.form['studentName']
            password = request.form['password']
        except KeyError:
            return generateCallback(False, 'studentName, or password is empty, add failed')
        student = getDocument(smDb, __STUDENT_DOC).find_one({'studentName': studentName})
        if student and student['password'] == password:
            return generateCallback(True, 'login success')
        else:
            return generateCallback(False, 'login failed')


@app.route('/resetPassword', methods=['POST'])
def resetPassword():
    if request.method == 'POST':
        try:
            studentName = request.form['studentName']
            oldPassword = request.form['oldPassword']
            newPassword = request.form['newPassword']
        except KeyError:
            return generateCallback(False, 'studentName, or password is empty, add failed')
        studentDoc = getDocument(smDb, __STUDENT_DOC).find_one({'studentName': studentName})
        if studentDoc and studentDoc['password'] == oldPassword:
            getDocument(smDb, __STUDENT_DOC).update({'studentName': studentName}, {'$set': {'password': newPassword}})
            return generateCallback(True, 'reset success')
        else:
            return generateCallback(False, 'reset failed')


@app.route('/modifyPeriod', methods=['POST'])
def modifyPeriod():
    if request.method == 'POST':
        try:
            studentName = request.form['studentName']
            period = request.form['period']
        except KeyError:
            return generateCallback(False, 'studentName, or period is empty, add failed')
        studentDoc = getDocument(smDb, __STUDENT_DOC).find_one({'studentName': studentName})
        if studentDoc:
            getDocument(smDb, __STUDENT_DOC).update({'studentName': studentName}, {'$set': {'period': period}})
            return generateCallback(True, 'modify success')
        else:
            return generateCallback(False, 'modify failed')


@app.route('/queryStudent')
def queryStudent():
    if request.method == 'GET':
        try:
            studentName = request.args['studentName']
        except KeyError:
            return generateCallback(False, 'studentName, or period is empty, add failed')
        student = getDocument(smDb, __STUDENT_DOC).find_one({'studentName': studentName})
        if student:
            return jsonify(generateStudentWithoutPassword(student))
        else:
            return generateCallback(False, 'student not exist')


#############################
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
#############################
