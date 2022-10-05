DELIMITER ///
CREATE TRIGGER update_student
AFTER INSERT ON has_grades FOR EACH ROW 
BEGIN
	set @gpa = 0;
	set @totalcredits = (select sum(credits) from student s inner join course c inner join has_grades g on g.studentid = s.studentid and g.courseid = c.courseid where s.studentid = new.studentid);
	set @gpa = (select sum(grade*credits)/@totalcredits from student s inner join course c inner join has_grades g on g.studentid = s.studentid and g.courseid = c.courseid where s.studentid = new.studentid);
	UPDATE STUDENT s
	set gpa = @gpa, completedcredits = @totalcredits where s.studentid = new.studentid;
END;
///
