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

    def get_core_courses(self):
        """
        Retrieve core courses for the major.
        """
        return self.get_courses("core")

    def get_courses(self, course_type):
        """
        Retrieve the courses for a specific type (e.g., 'core', 'elective').
        """
        table_name = self.major_tables.get(course_type)
        if not table_name:
            logger.error(f"{course_type.capitalize()} courses table not found for major ID: {self.major_id}")
            return []

        with db.engine.connect() as connection:
            query = text(f"SELECT course_code, course_name, credits FROM {table_name}")
            result = connection.execute(query).fetchall()

        logger.info(f"Fetched {course_type} courses: {result}")
        return [
            {
                "course_code": normalize_course_code(row[0]),
                "course_name": normalize_course_name(row[1]),
                "credits": row[2]
            }
            for row in result
        ]

    def get_missing_core_courses(self, completed_courses):
        """
        Get the missing core courses based on the completed courses.
        """
        all_core_courses = self.get_courses('core')
        missing_courses = [
            course for course in all_core_courses if course['course_code'] not in completed_courses
        ]
        logger.info(f"Missing core courses: {missing_courses}")
        return missing_courses

    def get_elective_courses(self):
        """
        Retrieve elective courses based on the specific requirements for each major and sub-major.
        """
        elective_table = self._determine_elective_table()
        if elective_table:
            with db.engine.connect() as connection:
                query = text(f"SELECT course_code, course_name FROM {elective_table}")
                result = connection.execute(query).fetchall()

            logger.info(f"Fetched elective courses for major ID: {self.major_id}")
            return [
                {
                    "course_code": normalize_course_code(row[0]),
                    "course_name": normalize_course_name(row[1])
                }
                for row in result
            ]
        else:
            logger.warning(f"Elective courses table not found for major ID: {self.major_id}")
            return []

    def get_missing_elective_courses(self, completed_courses):
        """
        Calculate the number of missing elective courses based on requirements.
        """
        elective_courses = self.get_elective_courses()
        elective_completed = [
            course for course in elective_courses if course['course_code'] in completed_courses
        ]
        missing_count = max(0, self.elective_courses_needed - len(elective_completed))
        logger.info(f"Missing elective courses count: {missing_count}")
        return missing_count

    def get_general_education_status(self, completed_courses):
        """
        Analyze and return the student's general education status.
        """
        gen_ed_table = self.major_tables.get("general")
        gen_ed_status = {}

        if not gen_ed_table:
            logger.warning(f"General education table not found for major ID: {self.major_id}")
            return gen_ed_status

        with db.engine.connect() as connection:
            query = text(f"SELECT course_code, course_type, course_name FROM {gen_ed_table}")
            result = connection.execute(query).fetchall()

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

        logger.info(f"Generated general education status for major ID: {self.major_id}")
        return gen_ed_status

    def validate_major_requirements(self, completed_courses):
        """
        Validate the student's completed courses against major-specific core, elective, and general education requirements.
        """
        core_courses = self.get_courses("core")
        elective_courses = self.get_elective_courses()
        gen_ed_status = self.get_general_education_status(completed_courses)

        core_completed = [course for course in core_courses if course["course_code"] in completed_courses]
        elective_completed = [course for course in elective_courses if course["course_code"] in completed_courses]

        return {
            "core_courses": {
                "completed": core_completed,
                "missing": self.get_missing_core_courses(completed_courses)
            },
            "elective_courses": {
                "completed": elective_completed,
                "missing": self.get_missing_elective_courses(completed_courses)
            },
            "general_education": gen_ed_status
        }

    def _determine_elective_table(self):
        """
        Determine the appropriate elective table based on the major and sub-major.
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
