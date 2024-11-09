import logging
from models.course_handler import CourseHandler
from models.general_education_handler import GeneralEducationHandler

logger = logging.getLogger(__name__)

class StudentDataHandler:
    def __init__(self, transcript_data, major_id, major_name):
        self.transcript_data = transcript_data
        self.major_id = major_id
        self.major_name = major_name

        # Initialize course handler based on major name
        if major_name == "Applied Psychology":
            self.course_handler = CourseHandler(major_name="Psychology", course_code_prefix="PSYC")
        elif major_name == "Sociology and Culture":
            self.course_handler = CourseHandler(major_name="Sociology", course_code_prefix="SOCL")
        else:
            self.course_handler = CourseHandler(major_name)

        # Initialize the GeneralEducationHandler with major information
        self.general_education_handler = GeneralEducationHandler(major_name=self.major_name, major_id=self.major_id)

    def fetch_required_courses(self):
        """Fetch required courses for the student."""
        core_courses = self.course_handler.query_core_courses()
        elective_courses = self.course_handler.query_elective_courses()
        supporting_courses = self.course_handler.query_supporting_courses()
        general_education_courses = self.general_education_handler.query_general_education_courses()

        logger.debug("Fetched required courses.")
        
        return {
            "core_courses": [{"course_code": course[0], "course_name": course[1], "credits": course[2]} for course in core_courses],
            "elective_courses": [{"course_code": course[0], "course_name": course[1], "credits": course[2]} for course in elective_courses],
            "supporting_courses": [{"course_code": course[0], "course_name": course[1], "credits": course[2]} for course in supporting_courses],
            "general_education_courses": [{"course_code": course[0], "course_name": course[1], "credits": course[2]} for course in general_education_courses],
        }

    def fetch_courses_passed(self):
        """Fetch courses with passing grades."""
        passing_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']
        
        passed_courses = [
            course for course in self.transcript_data['completed_courses']
            if course['grade'] in passing_grades  # Using the list of passing grades
        ]
        logger.info(f"Fetched passed courses: {passed_courses}")
        return passed_courses

    def fetch_courses_failed(self):
        """Fetch courses with failing grades."""
        failed_courses = [
            course for course in self.transcript_data['completed_courses']
            if course['grade'] == 'F'  # Identify failed courses
        ]
        logger.info(f"Fetched failed courses: {failed_courses}")
        return failed_courses

    def format_courses_by_semester(self):
        """Format the completed courses by semester."""
        formatted_courses = {}
        for course in self.transcript_data['completed_courses']:
            semester = course['semester']
            if semester not in formatted_courses:
                formatted_courses[semester] = []
            formatted_courses[semester].append(course)

        logger.debug(f"Formatted courses before filtering: {formatted_courses}")

        # Remove failed courses from formatted courses
        passing_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D']
        for semester, courses in formatted_courses.items():
            formatted_courses[semester] = [c for c in courses if c['grade'] in passing_grades]

        logger.debug(f"Formatted courses after filtering: {formatted_courses}")

        return formatted_courses

    def prepare_gpt_input(self, for_degree_audit=False):
        """Prepare data for GPT input.

        Args:
            for_degree_audit (bool): If True, prepare input for degree audit without failed courses.
        
        Returns:
            dict: Prepared input for GPT.
        """
        required_courses = self.fetch_required_courses()
        completed_courses = self.fetch_courses_passed() if not for_degree_audit else self.transcript_data['completed_courses']
        failed_courses = self.fetch_courses_failed() if not for_degree_audit else []  # No failed courses in degree audit
        formatted_courses = self.format_courses_by_semester()  # Format the courses

        gpt_input = {
            "completed_courses": completed_courses,
            "failed_courses": failed_courses,  # Will be an empty list if for_degree_audit is True
            "formatted_courses": formatted_courses,
            "required_courses": required_courses,
            "gpa": self.transcript_data.get('GPA', 0),  # Default to 0 if missing
            "cgpa": self.transcript_data.get('CGPA', 0),  # Default to 0 if missing
            "major_name": self.major_name
        }

        logger.debug(f"GPT input prepared: {gpt_input}")

        return gpt_input
