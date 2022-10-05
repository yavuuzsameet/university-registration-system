DELIMITER ///
CREATE TRIGGER check_quota 
BEFORE INSERT on Course FOR EACH ROW 
BEGIN 
	IF EXISTS (SELECT * FROM Course C INNER JOIN Classrooms Cl ON C.classroomID = Cl.classroomID WHERE c.classroomID = new.classroomID AND new.quota > cl.classroomcapacity)
	THEN SIGNAL SQLSTATE '45000'
	SET MESSAGE_TEXT = "A Course's quota cannot exceed its classroom's capacity";
	END IF;
END;
///