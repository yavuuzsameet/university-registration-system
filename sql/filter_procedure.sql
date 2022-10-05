DELIMITER ///
Create Procedure Filter_courses (IN departmentid CHAR(10) , IN campus CHAR(20), IN minCredits int, IN maxCredits int)
BEGIN
 	SELECT C.CourseID FROM Course C INNER JOIN Teachesfor t ON t.Username = C.InstructorUsername AND t.departmentid = departmentid
 	INNER JOIN classrooms ON classrooms.ClassroomID = c.classroomID AND classrooms.campus = campus
 	WHERE minCredits <= C.credits AND maxCredits >= C.credits;
END ///
DELIMITER ;