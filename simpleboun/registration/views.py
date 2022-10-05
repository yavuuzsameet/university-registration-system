from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import *
from passlib.hash import sha256_crypt
import mysql.connector
import environ

env = environ.Env()
environ.Env.read_env()

connection = mysql.connector.connect(
  host=env("MYSQL_HOST"),
  user=env("MYSQL_USER"),
  password=env("MYSQL_PASSWORD"),
  database=env("MYSQL_NAME"),
  auth_plugin='mysql_native_password'
)

# allowed titles of the instructors
allowedtitles = ['Assistant Professor', 'Associate Professor', 'Professor']

# landing page
def redirect(req):
    if req.session: req.session.flush()
    
    isFailed = req.GET.get("fail",False)

    return render(req, 'redirect.html',{"action_fail":isFailed})

# renders manager login page
def index_manager(req):
    if req.session:
        req.session.flush()

    isFailed = req.GET.get("fail",False)

    loginForm = UserLoginForm()

    return render(req,'manager_login.html',{"login_form":loginForm, "action_fail":isFailed})

# renders instructor login page
def index_instructor(req):
    if req.session:
        req.session.flush()

    isFailed = req.GET.get("fail",False)

    loginForm = UserLoginForm()

    return render(req,'instructor_login.html',{"login_form":loginForm, "action_fail":isFailed})

# renders student login page
def index_student(req):
    if req.session:
        req.session.flush()

    isFailed = req.GET.get("fail",False)

    loginForm = UserLoginForm()

    return render(req,'student_login.html',{"login_form":loginForm, "action_fail":isFailed})

# manager login page handler
def manager_login(req):
    username = req.POST.get("username")
    password = req.POST.get("password")

    cursor = connection.cursor()
    cursor.execute(f"SELECT password FROM DatabaseManager WHERE username='{username}';")
    db_stored_password = cursor.fetchall()
    
    if(not db_stored_password): return HttpResponseRedirect('../registration?fail=true')

    db_stored_password = db_stored_password[0][0]

    decrypted = sha256_crypt.verify(password, db_stored_password)

    if decrypted: 
        req.session["username"] = username 
        return HttpResponseRedirect('../registration/manager')
    else:
        return HttpResponseRedirect('../registration?fail=true')

# student login page handler
def student_login(req):
    username = req.POST.get("username")
    password = req.POST.get("password")

    cursor = connection.cursor()
    cursor.execute(f"SELECT password FROM User_In WHERE username='{username}';")
    student_stored_password = cursor.fetchall()

    if(not student_stored_password): return HttpResponseRedirect('../registration?fail=true')
    
    student_stored_password = student_stored_password[0][0]

    decrypted = sha256_crypt.verify(password, student_stored_password)

    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM Student WHERE username='{username}';")
    isStudent = cursor.fetchall()

    if isStudent and decrypted: 
        req.session["username"] = username 
        return HttpResponseRedirect('../registration/student') 
    else:
        return HttpResponseRedirect('../registration?fail=true')

# instructor login page handler
def instructor_login(req):
    username = req.POST.get("username")
    password = req.POST.get("password")

    cursor = connection.cursor()
    cursor.execute(f"SELECT password FROM User_In WHERE username='{username}';")
    instructor_stored_password = cursor.fetchall()

    if(not instructor_stored_password): return HttpResponseRedirect('../registration?fail=true')
    
    instructor_stored_password = instructor_stored_password[0][0]

    decrypted = sha256_crypt.verify(password, instructor_stored_password)

    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM Instructor WHERE username='{username}';")
    isInstructor = cursor.fetchall()

    if isInstructor and decrypted: 
        req.session["username"] = username 
        return HttpResponseRedirect('../registration/instructor') 
    else:
        return HttpResponseRedirect('../registration?fail=true')

# renders manager home page
def db_manager_homepage(req):

    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    return render(req, 'managerHome.html',{'action_fail':isFailed, 'username':username})

# renders instructor home page
def instructor_homepage(req):
    
    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    return render(req, 'instructorHome.html',{'action_fail':isFailed, 'username':username})

# renders student home page
def student_homepage(req):
    
    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    return render(req, 'studentHome.html',{'action_fail':isFailed, 'username':username})

# handles student addition to the database
def add_student(req):

    username=req.POST["username"]
    password=req.POST["password"]
    name=req.POST["name"]
    surname=req.POST["surname"]
    email=req.POST["email"]
    departmentid=req.POST["departmentid"]

    studentid=int(req.POST["studentid"])

    encrypted = sha256_crypt.hash(password)

    try:
        sql_user = "INSERT INTO User_In (username, password, name, surname, email, departmentid) VALUES (%s, %s, %s, %s, %s, %s)"
        sql_student = "INSERT INTO Student (username, studentid, completedcredits, gpa) VALUES (%s, %s, %s, %s)"

        param_user = (username, encrypted, name, surname, email, departmentid)
        param_student = (username, studentid, 0, 0.0)

        cursor = connection.cursor()

        cursor.execute(sql_user,param_user)
        cursor.execute(sql_student,param_student)
        connection.commit()

        return HttpResponseRedirect("../registration/manager")
    
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../registration/manager?fail=true')

# handles instructor addition to the database
def add_instructor(req):

    username=req.POST["username"]
    password=req.POST["password"]
    name=req.POST["name"]
    surname=req.POST["surname"]
    email=req.POST["email"]
    departmentid=req.POST["departmentid"]

    title=req.POST["title"]

    encrypted = sha256_crypt.hash(password)

    if title not in allowedtitles: return HttpResponseRedirect('../registration/manager?fail=true')

    try:
        sql_user = "INSERT INTO User_In (username,password,name,surname,email,departmentid) VALUES (%s, %s, %s, %s, %s, %s)"
        sql_instructor = "INSERT INTO Instructor (username,title) VALUES (%s, %s)"
        sql_teachesfor = "INSERT INTO TeachesFor (username, DepartmentID) VALUES (%s, %s)"

        param_user = (username, encrypted, name, surname, email, departmentid)
        param_instructor = (username, title)
        param_teachesfor = (username, departmentid)

        cursor = connection.cursor()

        cursor.execute(sql_user,param_user)
        cursor.execute(sql_instructor,param_instructor)
        cursor.execute(sql_teachesfor,param_teachesfor)

        connection.commit()

        return HttpResponseRedirect("../registration/manager")
    
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../registration/manager?fail=true')

# handles student deletion from the database
def delete_student(req):
    
    studentid = req.POST["studentid"]

    #check if student exists
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM Student WHERE studentid = '{studentid}';")
    exist = cursor.fetchall()

    if not exist: return HttpResponseRedirect('../registration/manager?fail=true')

    try:
        delete_takes = "DELETE FROM Takes WHERE username IN (SELECT username FROM Student WHERE studentid = %s)"
        delete_hasgrades = "DELETE FROM Has_Grades WHERE studentid = %s"
        delete_studentt = "DELETE FROM Student WHERE studentid = %s"
        delete_user = "DELETE FROM User_In WHERE username IN (SELECT username FROM Student WHERE studentid = %s)"
        
        param = (studentid,)
        
        cursor = connection.cursor()
        cursor.execute(delete_user,param)
        cursor.execute(delete_takes,param)
        cursor.execute(delete_hasgrades,param)
        cursor.execute(delete_studentt,param)
        
        connection.commit()
        
        return HttpResponseRedirect("../registration/manager")
    
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../registration/manager?fail=true')

# handles title update of the instructor
def update_title(req):

    username = req.POST['username']
    title = req.POST['title']

    if title not in allowedtitles: return HttpResponseRedirect('../registration/manager?fail=true')

    try:
        update = "UPDATE Instructor SET title = %s WHERE username = %s"
        param = (title, username)
        cursor = connection.cursor()
        cursor.execute(update,param)
        connection.commit()
        return HttpResponseRedirect("../registration/manager")

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../registration/manager?fail=true')

# renders student list page
def view_students(req):
    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )
    cursor = connection.cursor()
    cursor.execute(f"select u.username, u.name, u.surname, u.email, u.departmentid, s.completedCredits, s.gpa from user_in u inner join student s on u.username = s.username order by s.completedcredits asc;")
    studentlist = cursor.fetchall()
    
    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    return render(req, 'studentlist.html',{'students':studentlist, 'action_fail':isFailed, 'username':username})

# renders instructor list page
def view_instructors(req):
    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )
    cursor = connection.cursor()
    cursor.execute(f"select u.username, name, surname, email, departmentid, title from user_in u inner join instructor i on u.username = i.username;")
    instructorlist= cursor.fetchall()             

    username = req.session['username']
    isFailed = req.GET.get('fail',False)
    
    return render(req, 'instructorlist.html',{'instructors':instructorlist, 'action_fail':isFailed, 'username':username})

# renders grade list page
def view_grades(req):
    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )

    studentid = req.POST["studentid"]

    cursor = connection.cursor()
    cursor.execute(f"select g.CourseID, name, grade from has_grades g inner join course c on c.CourseID = g.CourseID where g.StudentID = '{studentid}';")
    gradelist = cursor.fetchall()

    # studentid = req.POST["studentid"]
    # gradelist = run_statement(f"select g.CourseID, name, grade from has_grades g inner join course c on c.CourseID = g.CourseID where g.StudentID = '{studentid}';")
    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    return render(req, 'gradelist.html',{'grades':gradelist, 'action_fail':isFailed, 'username':username})

# renders course list page
def view_courses(req):
    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )

    instructor_username = req.POST["username"]

    cursor = connection.cursor()
    cursor.execute(f"SELECT c.CourseID, c.name, c.ClassroomID, r.campus, h.timeSlot FROM Course c, Classrooms r, HappensAt h WHERE c.ClassroomID = r.ClassroomID and c.CourseID = h.CourseID and c.InstructorUsername = '{instructor_username}';")
    courselist= cursor.fetchall()

    # instructor_username = req.POST["username"]
    # courselist = run_statement(f"SELECT c.CourseID, c.name, c.ClassroomID, r.campus, h.timeSlot FROM Course c, Classrooms r, HappensAt h WHERE c.ClassroomID = r.ClassroomID and c.CourseID = h.CourseID and c.InstructorUsername = '{instructor_username}';")

    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    return render(req, 'coursesOfAnInstructor.html',{'courses':courselist, 'action_fail':isFailed, 'username':username})

# renders average grade of a certain course page
def view_avg_grade(req):
    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )

    courseid = req.POST["courseid"]

    cursor = connection.cursor()
    cursor.execute(f"SELECT C.CourseID, name, avg(grade) FROM Has_Grades g, Course c WHERE g.CourseID = '{courseid}' AND g.CourseID=c.CourseID;")
    avg = cursor.fetchall()

    # courseid = req.POST["courseid"]
    # avg = run_statement(f"SELECT C.CourseID, name, avg(grade) FROM Has_Grades g, Course c WHERE g.CourseID = '{courseid}' AND g.CourseID=c.CourseID;")

    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    return render(req, 'averageGrade.html',{'course':avg, 'action_fail':isFailed, 'username':username})

# renders available classrooms list page
def view_available_classrooms(req):
    ###
    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )

    slot = req.POST["timeslot"]

    cursor = connection.cursor()
    cursor.execute(f"Select C.ClassroomID, C.campus, C.ClassroomCapacity FROM classrooms C WHERE C.ClassroomID NOT IN(SELECT C.ClassroomID  FROM classrooms C INNER JOIN takesplace T on T.ClassroomID=C.ClassroomID INNER JOIN happensAt H ON H.CourseID = T.CourseID WHERE timeSlot = '{slot}');")
    classrooms = cursor.fetchall()

    # slot = req.POST["timeslot"]
    # classrooms = run_statement(f"Select C.ClassroomID, C.campus, C.ClassroomCapacity FROM classrooms C WHERE C.ClassroomID NOT IN(SELECT C.ClassroomID  FROM classrooms C INNER JOIN takesplace T on T.ClassroomID=C.ClassroomID INNER JOIN happensAt H ON H.CourseID = T.CourseID WHERE timeSlot = '{slot}');")

    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    return render(req, 'availableClassrooms.html',{'classrooms':classrooms, 'action_fail':isFailed, 'username':username})

# handles course addition to the database
def add_course(req):

    username = req.session['username']

    courseid=req.POST["courseid"]
    name=req.POST["name"]
    credits=req.POST["credits"]
    classroomid=req.POST["classroomid"]
    timeslot=req.POST["timeslot"]
    quota=req.POST["quota"]
    
    try:
        course_query = "INSERT INTO Course (CourseID,name,credits,InstructorUsername,ClassroomID,quota) VALUES (%s, %s, %s, %s, %s, %s)"
        takesplace_query = "INSERT INTO TakesPlace (ClassroomID, CourseID) VALUES (%s,%s)"
        happensat_query = "INSERT INTO HappensAt (CourseID, timeSlot) VALUES (%s,%s)"
        teaches_query = "INSERT INTO Teaches (username, CourseID) VALUES (%s, %s)"

        course_param = (courseid, name, credits, username, classroomid, quota)
        takesplace_param = (classroomid, courseid)
        happensat_param = (courseid, timeslot)
        teaches_param = (username, courseid)
        
        cursor = connection.cursor()
        
        cursor.execute(course_query,course_param)
        cursor.execute(takesplace_query,takesplace_param)
        cursor.execute(happensat_query,happensat_param)
        cursor.execute(teaches_query, teaches_param)

        connection.commit()

        return HttpResponseRedirect("../registration/instructor")
    
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../registration/instructor?fail=true')

# handles prerequisite addition between courses to the database
def add_prerequisite(req):

    courseid = req.POST["courseid"]
    pre_courseid = req.POST["pre_courseid"]

    if(pre_courseid > courseid): return HttpResponseRedirect('../registration/instructor?fail=true')

    try:
        prerequisite_query = "INSERT INTO HasPrerequisition (CourseID1, CourseID2) VALUES (%s, %s)"
        prerequisite_param = (courseid, pre_courseid)

        cursor = connection.cursor()

        cursor.execute(prerequisite_query, prerequisite_param)

        connection.commit()

        return HttpResponseRedirect("../registration/instructor")
    
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../registration/instructor?fail=true')

# converts list to string
def list2str(list):
    s=''
    for tuple in list:
        s+=tuple[0]+', '
    return s[:-2]

# renders course page of a single instructor
def view_self_courses(req):
    
    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )
    cursor = connection.cursor()
    cursor.execute(f"SELECT C.CourseID, C.name, C.ClassroomID, H.timeSlot ,C.quota FROM Course C INNER JOIN HappensAt H ON H.CourseID=C.CourseID WHERE C.instructorUsername = '{username}' ORDER BY C.CourseID ASC;")
    courses = cursor.fetchall()

    i=0
    for course in courses:
        courseid = course[0]
        cursor_2 = connection.cursor()
        cursor_2.execute(f"SELECT CourseID2 FROM HasPrerequisition WHERE CourseID1 = '{courseid}';")
        prerequisites = cursor_2.fetchall()

        prereq = list2str(prerequisites)
        courses[i] += (prereq,)
        i += 1

    return render(req, 'selfCourses.html',{'courses':courses, 'action_fail':isFailed, 'username':username})

# renders student list page of a single course
def view_students_byCourseId(req):
    
    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )

    courseid = req.POST["courseid"]

    #check if the course is given by the instructor
    cursor_2 = connection.cursor()
    cursor_2.execute(f"SELECT '{courseid}' IN (SELECT CourseID FROM Teaches t WHERE t.username = '{username}');")
    check_instructor = cursor_2.fetchall()
    
    gives = check_instructor[0][0]
    if(not gives): return HttpResponseRedirect('../registration/instructor?fail=true')

    cursor = connection.cursor()
    cursor.execute(f"SELECT t.username, s.StudentID, u.email, u.name, u.surname FROM Takes t INNER JOIN Student s ON t.username = s.username INNER JOIN User_in u ON u.username = s.username WHERE t.CourseID = '{courseid}';")
    students = cursor.fetchall()
    
    return render(req, 'studentsInTheCourse.html',{'students':students, 'action_fail':isFailed, 'username':username})

# handles course name update 
def update_course(req):

    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    courseid = req.POST["courseid"]
    name = req.POST["name"]
    
    cursor_2 = connection.cursor()
    cursor_2.execute(f"SELECT '{courseid}' IN (SELECT CourseID FROM Teaches t WHERE t.username = '{username}');")
    check_instructor = cursor_2.fetchall()
    #check if the course is given by the instructor
    #check_instructor = run_statement(f"SELECT '{courseid}' IN (SELECT CourseID FROM Teaches t WHERE t.username = '{username}')")
    gives = check_instructor[0][0]
    if(not gives): return HttpResponseRedirect('../registration/instructor?fail=true')


    try:
        update_query = "UPDATE Course SET name = %s WHERE CourseID = %s;"
        update_param = (name, courseid)

        cursor = connection.cursor()

        cursor.execute(update_query, update_param)

        connection.commit()

        return HttpResponseRedirect("../registration/instructor")
    
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../registration/instructor?fail=true')

# handles grading of a student by the instructor
def give_grade(req):

    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    courseid = req.POST["courseid"]
    studentid = req.POST["studentid"]
    grade = req.POST["grade"]

    cursor_2 = connection.cursor()
    cursor_2.execute(f"SELECT '{courseid}' IN (SELECT CourseID FROM Teaches t WHERE t.username = '{username}');")
    check_instructor = cursor_2.fetchall()
    #check whether instructor gives the course
    #check_instructor = run_statement(f"SELECT '{courseid}' IN (SELECT CourseID FROM Teaches t WHERE t.username = '{username}')")
    gives = check_instructor[0][0]
    if(not gives): return HttpResponseRedirect('../registration/instructor?fail=true')
    

    cursor_3 = connection.cursor()
    cursor_3.execute(f"SELECT '{courseid}' IN (SELECT CourseID FROM Takes t, Student s WHERE s.StudentID = '{studentid}' and s.username = t.username);")
    check_student = cursor_3.fetchall()
    #check whether student takes the course
    #check_student = run_statement(f"SELECT '{courseid}' IN (SELECT CourseID FROM Takes t, Student s WHERE s.StudentID = '{studentid}' and s.username = t.username);")
    takes = check_student[0][0]
    if(not takes): return HttpResponseRedirect('../registration/instructor?fail=true')

    try:
        grade_query = "INSERT INTO Has_Grades (StudentID,CourseID,grade) VALUES (%s, %s, %s)"
        takes_query = "DELETE FROM Takes WHERE username IN (SELECT username FROM Student WHERE studentid = %s) and courseid = %s"
        
        param_grade = (studentid, courseid, grade)
        param_takes = (studentid, courseid)

        cursor = connection.cursor()

        cursor.execute(grade_query,param_grade)
        cursor.execute(takes_query,param_takes)
        
        connection.commit()
        return HttpResponseRedirect("../registration/instructor")
    
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../registration/instructor?fail=true')

# renders course list page
def view_all_courses(req):

    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )
    cursor = connection.cursor()
    cursor.execute(f"SELECT C.CourseID, C.name, U.surname, U.departmentid, C.credits, C.ClassroomID, H.timeSlot ,C.quota FROM Course C INNER JOIN HappensAt H ON H.CourseID=C.CourseID INNER JOIN User_In U ON U.username = C.InstructorUsername;")
    courses = cursor.fetchall()

    i=0
    for course in courses:
        courseid = course[0]

        cursor_2 = connection.cursor()
        cursor_2.execute(f"SELECT CourseID2 FROM HasPrerequisition WHERE CourseID1 = '{courseid}';")
        prerequisites = cursor_2.fetchall()

        prereq = list2str(prerequisites)
        courses[i] += (prereq,)
        i += 1

    return render(req, 'allCourses.html',{'courses':courses, 'action_fail':isFailed, 'username':username})

# handles course occupation by students
def take_course(req):

    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    courseid = req.POST["courseid"]

    #TRIGGERS

    try:
        takes_query = "INSERT INTO Takes (username, CourseID) VALUES (%s, %s)"
        takes_param = (username, courseid)

        cursor = connection.cursor()

        cursor.execute(takes_query, takes_param)

        connection.commit()
        return HttpResponseRedirect("../registration/student")
    
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../registration/student?fail=true')

# renders taken course list page
def view_taken_courses(req):

    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )

    cursor_2 = connection.cursor()
    cursor_2.execute(f"SELECT StudentID FROM Student WHERE username = '{username}';")
    studentid = cursor_2.fetchall()

    studentid = studentid[0][0]

    cursor = connection.cursor()
    cursor.execute(f"SELECT TEMP.Courseid, TEMP.name, grade FROM ((SELECT T.Courseid, C.name FROM Takes T INNER JOIN Student S ON s.username = t.username INNER JOIN Course C on C.CourseID = T.CourseID WHERE Studentid = '{studentid}') UNION (SELECT g.CourseID, c.name from has_grades g INNER JOIN Course c ON c.courseid = g.courseid where studentid = '{studentid}')) as TEMP LEFT JOIN has_Grades g ON g.courseid = TEMP.courseid and g.studentid = '{studentid}';")
    courses = cursor.fetchall()

    return render(req, 'takenCourses.html',{'courses':courses, 'action_fail':isFailed, 'username':username})

# renders a course list page specified with a certain keyword
def search(req):

    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    data = req.POST["data"]

    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )
    cursor = connection.cursor()
    cursor.execute(f"SELECT C.courseid, C.name, u.surname, u.departmentid , c.credits, c.ClassroomID, timeSlot, c.quota from course C INNER JOIN User_in U ON U.username = C.InstructorUsername INNER JOIN happensat ON happensat.courseid = c.CourseID WHERE c.name like '%{data}%';")
    courses = cursor.fetchall()

    i=0
    for course in courses:
        courseid = course[0]

        cursor_2 = connection.cursor()
        cursor_2.execute(f"SELECT CourseID2 FROM HasPrerequisition WHERE CourseID1 = '{courseid}';")
        prerequisites = cursor_2.fetchall()

        prereq = list2str(prerequisites)
        courses[i] += (prereq,)
        i += 1

    return render(req, 'search.html',{'courses':courses, 'action_fail':isFailed, 'username':username})

# renders course list page specified with filters
def filter_courses(req):
    username = req.session['username']
    isFailed = req.GET.get('fail',False)

    department = req.POST["department"]
    campus = req.POST["campus"]
    mincredits = req.POST["mincredits"]
    maxcredits = req.POST["maxcredits"]

    connection = mysql.connector.connect(
    host=env("MYSQL_HOST"),
    user=env("MYSQL_USER"),
    password=env("MYSQL_PASSWORD"),
    database=env("MYSQL_NAME"),
    auth_plugin='mysql_native_password'
    )
    cursor = connection.cursor()
    cursor.execute(f"CALL Filter_courses('{department}', '{campus}', '{mincredits}','{maxcredits}');")
    courses = cursor.fetchall()

    return render(req, 'filter.html',{'courses':courses, 'action_fail':isFailed, 'username':username})






