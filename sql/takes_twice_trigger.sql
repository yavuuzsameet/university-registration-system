DELIMITER ///
CREATE TRIGGER takes_twice 
BEFORE INSERT on Takes FOR EACH ROW 
BEGIN 
	IF EXISTS (SELECT * FROM Has_Grades g INNER JOIN Student s ON s.username = new.username WHERE g.studentid = s.studentid AND g.courseid = new.courseid)
	THEN SIGNAL SQLSTATE '45000'
	SET MESSAGE_TEXT = "Students cannot take a course twice.";
	END IF;
END;
///