DELIMITER ///
CREATE TRIGGER prerequisite 
BEFORE INSERT on Takes FOR EACH ROW 
BEGIN
	IF (EXISTS (SELECT CourseID2 FROM hasprerequisition p WHERE p.CourseID1 = new.courseid) AND (SELECT CourseID2 FROM hasprerequisition p WHERE p.CourseID1 = new.courseid) NOT IN (SELECT CourseID FROM has_grades g INNER JOIN student s ON s.studentid = g.studentid WHERE s.username = new.username))
	THEN SIGNAL SQLSTATE '45000'
	SET MESSAGE_TEXT = "To take the course, student must have a grade from all of its prerequisites.";
	END IF;
END;
///