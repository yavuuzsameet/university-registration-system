DELIMITER ///
CREATE TRIGGER course_quota 
BEFORE INSERT on Takes FOR EACH ROW 
BEGIN 
	IF (SELECT COUNT(*) FROM Takes t WHERE t.courseid = new.courseid) = (SELECT quota FROM Course C WHERE C.CourseID = new.CourseID)
	THEN SIGNAL SQLSTATE '45000'
	SET MESSAGE_TEXT = "Students cannot add a course if the quota is full.";
	END IF;
END;
///