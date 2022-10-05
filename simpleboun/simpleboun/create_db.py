import mysql.connector
import environ
from passlib.hash import sha256_crypt

env = environ.Env()
environ.Env.read_env()

connection = mysql.connector.connect(
  host=env("MYSQL_HOST"),
  user=env("MYSQL_USER"),
  password=env("MYSQL_PASSWORD"),
  database=env("MYSQL_NAME"),
  auth_plugin='mysql_native_password'
)

cursor = connection.cursor()

# create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS DatabaseManager(
username varchar(30),
password varchar(300),
PRIMARY KEY(username)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Department(
name varchar(30),
DepartmentID varchar(10),
PRIMARY KEY(DepartmentID),
UNIQUE(name)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Course(
  CourseID varchar(10),
  name varchar(30),
  credits int,
  InstructorUsername varchar(30),
  ClassroomID varchar(20),
  quota int,
  PRIMARY KEY(CourseID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Times(
  timeSlot int,
  PRIMARY KEY(timeSlot),
  CHECK(timeSlot <11 AND timeSlot > 0)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Classrooms(
  ClassroomID varchar(20),
  campus varchar(20),
  ClassroomCapacity int,
  PRIMARY KEY(ClassroomID)
);
""")

# commit tables
connection.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS User_In(
  username varchar(30),
  password varchar(300),
  name varchar(20),
  surname varchar(20),
  email varchar(35),
  DepartmentID varchar(10) NOT NULL,
  PRIMARY KEY(username),
  FOREIGN KEY(DepartmentID) references Department(DepartmentID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS TakesPlace(
  ClassroomID varchar(20),
  CourseID varchar(10),
  PRIMARY KEY(CourseID),
  FOREIGN KEY(CourseID) references Course(CourseID),
  FOREIGN KEY(ClassroomID) references Classrooms(ClassroomID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS HasPrerequisition(
  CourseID1 varchar(10),
  CourseID2 varchar(10),
  PRIMARY KEY(CourseID1, CourseID2),
  FOREIGN KEY(CourseID1) references Course(CourseID),
  FOREIGN KEY(CourseID2) references Course(CourseID),
  CHECK(CourseID1 > CourseID2)
);
""")

# commit tables
connection.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Student (
  username varchar(30),
  StudentID int,
  completedCredits int,
  GPA real,
  PRIMARY KEY(username),
  UNIQUE(StudentID),
  FOREIGN KEY(username) references User_In(username) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Instructor(
  username varchar(30),
  title varchar(20),
  PRIMARY KEY(username),
  FOREIGN KEY(username) references User_In(username) ON DELETE CASCADE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS HappensAt(
  CourseID varchar(10),
  timeSlot int,
  PRIMARY KEY(CourseID),
  FOREIGN KEY(timeSlot) references Times(timeSlot),
  FOREIGN KEY(CourseID) references TakesPlace(CourseID)
);
""")

# commit tables
connection.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS TeachesFor(
  username varchar(30),
  DepartmentID varchar(10) NOT NULL,
  PRIMARY KEY(username),
  FOREIGN KEY(DepartmentID) references Department(DepartmentID),
  FOREIGN KEY(username) references Instructor(username)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Takes(
  username varchar(30),
  CourseID varchar(10) NOT NULL,
  PRIMARY KEY(username, CourseID),
  FOREIGN KEY(username) references Student(username),
  FOREIGN KEY(CourseID) references Course(CourseID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Has_Grades(
  StudentID int NOT NULL,
  CourseID varchar(10),
  grade real,
  PRIMARY KEY(StudentID, CourseID),
  FOREIGN KEY(StudentID) references Student(StudentID) ON DELETE CASCADE
);
""")

# commit tables
connection.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Teaches(
  username varchar(30),
  CourseID varchar(10),
  PRIMARY KEY(username, CourseID),
  FOREIGN KEY(username) references TeachesFor(username),
  FOREIGN KEY(CourseID) references Course(CourseID)
);
""")


#commit procedures
connection.commit()

# cursor.execute("""
# DELIMITER ///
# CREATE TRIGGER update_student
# AFTER INSERT ON has_grades FOR EACH ROW 
# BEGIN
# 	set @gpa = 0;
# 	set @totalcredits = (select sum(credits) from student s inner join course c inner join has_grades g on g.studentid = s.studentid and g.courseid = c.courseid where s.studentid = new.studentid);
# 	set @gpa = (select sum(grade*credits)/@totalcredits from student s inner join course c inner join has_grades g on g.studentid = s.studentid and g.courseid = c.courseid where s.studentid = new.studentid);
# 	UPDATE STUDENT s
# 	set gpa = @gpa, completedcredits = @totalcredits where s.studentid = new.studentid;
# END;
# ///
# """)

# cursor.execute("""
# DELIMITER ///
# CREATE TRIGGER check_quota 
# BEFORE INSERT on Course FOR EACH ROW 
# BEGIN 
# 	IF EXISTS (SELECT * FROM Course C INNER JOIN Classrooms Cl ON C.classroomID = Cl.classroomID WHERE c.classroomID = new.classroomID AND new.quota > cl.classroomcapacity)
# 	THEN SIGNAL SQLSTATE '45000'
# 	SET MESSAGE_TEXT = "A Course's quota cannot exceed its classroom's capacity";
# 	END IF;
# END;
# ///
# """)

# cursor.execute("""
# DELIMITER ///
# CREATE TRIGGER takes_twice 
# BEFORE INSERT on Takes FOR EACH ROW 
# BEGIN 
# 	IF EXISTS (SELECT * FROM Has_Grades g INNER JOIN Student s ON s.username = new.username WHERE g.studentid = s.studentid AND g.courseid = new.courseid)
# 	THEN SIGNAL SQLSTATE '45000'
# 	SET MESSAGE_TEXT = "Students cannot take a course twice.";
# 	END IF;
# END;
# ///
# """)

# cursor.execute("""
# DELIMITER ///
# CREATE TRIGGER course_quota 
# BEFORE INSERT on Takes FOR EACH ROW 
# BEGIN 
# 	IF (SELECT COUNT(*) FROM Takes t WHERE t.courseid = new.courseid) = (SELECT quota FROM Course C WHERE C.CourseID = new.CourseID)
# 	THEN SIGNAL SQLSTATE '45000'
# 	SET MESSAGE_TEXT = "Students cannot add a course if the quota is full.";
# 	END IF;
# END;
# ///
# """)

# cursor.execute("""
# DELIMITER ///
# CREATE TRIGGER prerequisite 
# BEFORE INSERT on Takes FOR EACH ROW 
# BEGIN
# 	IF (EXISTS (SELECT CourseID2 FROM hasprerequisition p WHERE p.CourseID1 = new.courseid) AND (SELECT CourseID2 FROM hasprerequisition p WHERE p.CourseID1 = new.courseid) NOT IN (SELECT CourseID FROM has_grades g INNER JOIN student s ON s.studentid = g.studentid WHERE s.username = new.username))
# 	THEN SIGNAL SQLSTATE '45000'
# 	SET MESSAGE_TEXT = "To take the course, student must have a grade from all of its prerequisites.";
# 	END IF;
# END;
# ///
# """)

# cursor.execute("""
# DELIMITER ///
# Create Procedure Filter_courses (IN departmentid VARCHAR(10) , IN campus VARCHAR(20), IN minCredits int, IN maxCredits int)
# BEGIN
# 	SELECT C.CourseID FROM Course C INNER JOIN Teachesfor t ON t.Username = C.InstructorUsername AND t.departmentid = departmentid
# 	INNER JOIN classrooms ON classrooms.ClassroomID = c.classroomID AND classrooms.campus = campus
# 	WHERE minCredits <= C.credits AND maxCredits >= C.credits;
# END ///
# DELIMITER ;
# """)

# # fill tables
tollen = sha256_crypt.hash("tollen")
huebsch = sha256_crypt.hash("huebsch")
cursor.execute(f"INSERT IGNORE INTO DatabaseManager VALUES ('manager1','{tollen}');")
cursor.execute(f"INSERT IGNORE INTO DatabaseManager VALUES ('manager2','{huebsch}');")

cursor.execute('INSERT IGNORE INTO Department VALUES ("Computer Engineering","CMPE");')
cursor.execute('INSERT IGNORE INTO Department VALUES ("Physics","PHYS");')
cursor.execute('INSERT IGNORE INTO Department VALUES ("Mathematics","MATH");')

password_suyunu = sha256_crypt.hash("burak")
cursor.execute(f'INSERT IGNORE INTO User_In VALUES ("buraksuyunu","{password_suyunu}","burak","suyunu","burak.suyunu@boun","CMPE");')
cursor.execute('INSERT IGNORE INTO Instructor VALUES ("buraksuyunu","Professor");')
cursor.execute('INSERT IGNORE INTO TeachesFor VALUES ("buraksuyunu", "CMPE");')

password_topcuoglu = sha256_crypt.hash("samet")
cursor.execute(f'INSERT IGNORE INTO User_In VALUES ("yavuuzsameet","{password_topcuoglu}","yavuz","topcuoglu","yavuz@boun","CMPE");')
cursor.execute('INSERT IGNORE INTO Student VALUES ("yavuuzsameet","285","0","0.0");')

cursor.execute("INSERT IGNORE INTO Times VALUES (1);")
cursor.execute("INSERT IGNORE INTO Times VALUES (2);")
cursor.execute("INSERT IGNORE INTO Times VALUES (3);")
cursor.execute("INSERT IGNORE INTO Times VALUES (4);")
cursor.execute("INSERT IGNORE INTO Times VALUES (5);")
cursor.execute("INSERT IGNORE INTO Times VALUES (6);")
cursor.execute("INSERT IGNORE INTO Times VALUES (7);")
cursor.execute("INSERT IGNORE INTO Times VALUES (8);")
cursor.execute("INSERT IGNORE INTO Times VALUES (9);")
cursor.execute("INSERT IGNORE INTO Times VALUES (10);")

cursor.execute('INSERT IGNORE INTO Classrooms VALUES ("BMA4","Kuzey","40");')
cursor.execute('INSERT IGNORE INTO Classrooms VALUES ("BMA5","Kuzey","20");')
cursor.execute('INSERT IGNORE INTO Classrooms VALUES ("NH101","Kuzey","100");')
cursor.execute('INSERT IGNORE INTO Classrooms VALUES ("Albert Long","Guney","120");')
cursor.execute('INSERT IGNORE INTO Classrooms VALUES ("Ayhan Sahenk","Ucaksavar","200");')

# commit fill-ins
connection.commit()


