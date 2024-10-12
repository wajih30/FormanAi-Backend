import logging
from db import db
from config import MAJOR_TABLE_MAPPING, MAJOR_REQUIREMENTS
from utils.normalization import normalize_course_code, normalize_course_name
from sqlalchemy import text

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('course_handler.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class CourseHandler:
    def __init__(self, major_id, sub_major=None):
        """
        Initialize the CourseHandler for the given major and sub-major.
        """
        self.major_id = major_id
        self.sub_major = sub_major
        self.major_tables = self._get_major_table_mapping()
        self.requirements = MAJOR_REQUIREMENTS.get(major_id, {})
        self.elective_courses_needed = self.requirements.get("elective_courses_needed", 0)
        logger.info(f"Initialized CourseHandler for major ID: {major_id}, sub-major: {sub_major}")

    def get_courses(self, course_type):
        """
        Retrieve the courses for a specific type (core, elective, or supporting).
        """
        table_name = self.major_tables.get(course_type)
        if not table_name:
            logger.error(f"{course_type.capitalize()} courses table not found for major ID: {self.major_id}")
            return []

        try:
            with db.engine.connect() as connection:
                query = text(f"SELECT course_code, course_name, credits FROM {table_name}")
                result = connection.execute(query).fetchall()
        except Exception as e:
            logger.error(f"Error fetching courses from {table_name}: {str(e)}")
            return []

        return [
            {
                "course_code": normalize_course_code(row[0]),
                "course_name": normalize_course_name(row[1]),
                "credits": row[2]
            }
            for row in result
        ]

    def get_completed_courses(self):
        """
        Retrieve a list of completed courses for the student from the database or input.
        """
        try:
            with db.engine.connect() as connection:
                query = text("SELECT course_code FROM completed_courses")
                result = connection.execute(query).fetchall()
        except Exception as e:
            logger.error(f"Error fetching completed courses: {str(e)}")
            return []

        return [normalize_course_code(row[0]) for row in result]

    def get_core_courses(self):
        """
        Retrieve core courses for the major.
        """
        return self.get_courses("core")

    def get_supporting_courses(self):
        """
        Retrieve supporting courses for the major.
        """
        return self.get_courses("supporting")

    def get_elective_courses(self):
        """
        Retrieve elective courses for the major.
        """
        return self.get_courses("elective")

    def get_missing_core_courses(self, completed_courses):
        """
        Get the missing core courses based on completed courses.
        """
        all_core_courses = self.get_core_courses()
        return [
            course for course in all_core_courses if course['course_code'] not in completed_courses
        ]

    def get_missing_supporting_courses(self, completed_courses):
        """
        Get the missing supporting courses based on completed courses.
        """
        supporting_courses = self.get_supporting_courses()
        return [
            course for course in supporting_courses if course['course_code'] not in completed_courses
        ]

    def get_missing_elective_courses(self, completed_courses):
        """
        Calculate the number of missing elective courses based on requirements.
        """
        elective_courses = self.get_elective_courses()
        completed_electives = [course for course in elective_courses if course['course_code'] in completed_courses]
        return max(0, self.elective_courses_needed - len(completed_electives))

    def format_course_list(self, courses):
        """
        Format the list of courses into a readable string.
        """
        if not courses:
            return "No courses available."
        return "\n".join([f"{course['course_code']} - {course['course_name']} ({course['credits']} credits)" for course in courses])

    def get_general_education_status(self, completed_courses):
        """
        Analyze and return the student's general education status.
        """
        gen_ed_table = self.major_tables.get("general")
        if not gen_ed_table:
            logger.warning(f"General education table not found for major ID: {self.major_id}")
            return {}

        try:
            with db.engine.connect() as connection:
                query = text(f"SELECT course_code, course_type, course_name FROM {gen_ed_table}")
                result = connection.execute(query).fetchall()
        except Exception as e:
            logger.error(f"Error fetching general education courses from {gen_ed_table}: {str(e)}")
            return {}

        gen_ed_status = {}
        for row in result:
            course_code = normalize_course_code(row[0])
            course_type = row[1]
            course_name = normalize_course_name(row[2])
            status = "completed" if course_code in completed_courses else "unmet"

            if course_type not in gen_ed_status:
                gen_ed_status[course_type] = []
            gen_ed_status[course_type].append({
                "course_code": course_code,
                "course_name": course_name,
                "status": status
            })

        return gen_ed_status

    def validate_major_requirements(self, completed_courses):
        """
        Validate completed courses against core, elective, and general education requirements.
        """
        core_courses = self.get_core_courses()
        elective_courses = self.get_elective_courses()
        supporting_courses = self.get_supporting_courses()
        gen_ed_status = self.get_general_education_status(completed_courses)

        return {
            "core_courses": {
                "completed": [course for course in core_courses if course["course_code"] in completed_courses],
                "missing": self.get_missing_core_courses(completed_courses)
            },
            "elective_courses": {
                "completed": [course for course in elective_courses if course["course_code"] in completed_courses],
                "missing": self.get_missing_elective_courses(completed_courses)
            },
            "supporting_courses": {
                "completed": [course for course in supporting_courses if course["course_code"] in completed_courses],
                "missing": self.get_missing_supporting_courses(completed_courses)
            },
            "general_education": gen_ed_status
        }

    def _determine_elective_table(self):
        """
        Determine the elective table based on the major and sub-major.
        """
        if self.major_id == 17:  # Psychology
            return self.major_tables.get("applied_elective") if self.sub_major == "Applied" else self.major_tables.get("elective")
        if self.major_id == 19:  # Sociology
            return self.major_tables.get("cult_elective") if self.sub_major == "Sociology and Cult" else self.major_tables.get("elective")
        return self.major_tables.get("elective")

    def _get_major_table_mapping(self):
        """
        Retrieve the table mapping for the major and sub-major.
        """
        if self.sub_major and self.major_id in [17, 19]:  # Psychology or Sociology
            return MAJOR_TABLE_MAPPING.get(self.major_id, {}).get("sub_categories", {}).get(self.sub_major, {})
        return MAJOR_TABLE_MAPPING.get(self.major_id, {})
