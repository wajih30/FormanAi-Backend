import logging
from db import db
from config import GENERAL_ED_REQUIREMENTS, MAJOR_TABLE_MAPPING
from utils.normalization import normalize_course_code, normalize_course_name

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('general_education_handler.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class GeneralEducationHandler:
    """Handles the general education courses and their completion status for each major."""

    def __init__(self, major_id):
        """
        Initialize GeneralEducationHandler with the provided major ID.
        
        Args:
        - major_id (int): The ID of the student's major.
        """
        self.major_id = major_id
        self.requirements = GENERAL_ED_REQUIREMENTS.get(major_id, {})
        self.general_table = MAJOR_TABLE_MAPPING.get("general", {}).get("table", None)  # Reference to the general education table

        logger.info(f"Initialized GeneralEducationHandler for major ID: {major_id}")

    def _fetch_courses(self, column_name, values):
        """
        Helper function to retrieve courses based on course code prefixes or specific columns.
        
        Args:
        - column_name (str): The column name to filter courses (e.g., `course_code`).
        - values (list): List of values to match against the specified column.

        Returns:
        - list: List of course dictionaries that match the criteria.
        """
        if not values or not self.general_table:
            logger.warning(f"No values provided or general table not found for major ID: {self.major_id}")
            return []

        try:
            query = f"SELECT course_code, course_name, credits FROM {self.general_table} WHERE {column_name} IN :values"
            # Using a connection to execute the query
            with db.engine.connect() as connection:
                result = connection.execute(query, {'values': tuple(values)}).fetchall()

            logger.info(f"Fetched general education courses for {column_name} with values: {values}")
            return [
                {
                    "course_code": normalize_course_code(row['course_code']),
                    "course_name": normalize_course_name(row['course_name']),
                    "credits": row['credits']
                }
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error fetching courses from {self.general_table} for {column_name}: {str(e)}")
            return []

    def get_compulsory_courses(self):
        """Retrieve compulsory general education courses required for the major."""
        compulsory_codes = self.requirements.get("compulsory", [])
        logger.info(f"Fetching compulsory courses for major ID: {self.major_id}")
        return self._fetch_courses("course_code", compulsory_codes)

    def get_religious_courses(self):
        """Retrieve religious study courses based on the major's requirements."""
        religious_codes = self.requirements.get("religious", [])
        logger.info(f"Fetching religious courses for major ID: {self.major_id}")
        return self._fetch_courses("course_code", religious_codes)

    def get_humanities_courses(self):
        """Retrieve humanities courses as per the major's requirements."""
        humanities_options = self.requirements.get("humanities_options", [])
        logger.info(f"Fetching humanities courses for major ID: {self.major_id}")
        return self._fetch_courses("course_code", humanities_options)

    def get_social_science_courses(self):
        """Retrieve social science courses for the general education requirement."""
        social_options = self.requirements.get("social_sciences_options", [])
        logger.info(f"Fetching social science courses for major ID: {self.major_id}")
        return self._fetch_courses("course_code", social_options)

    def get_science_lab_courses(self):
        """Retrieve science lab courses for the general education requirement."""
        science_options = self.requirements.get("science_lab_options", [])
        logger.info(f"Fetching science lab courses for major ID: {self.major_id}")
        return self._fetch_courses("course_code", science_options)

    def get_math_courses(self):
        """Retrieve mathematics courses for the general education requirement."""
        math_options = self.requirements.get("math_options", [])
        logger.info(f"Fetching math courses for major ID: {self.major_id}")
        return self._fetch_courses("course_code", math_options)

    def get_computer_science_courses(self):
        """Retrieve computer science courses for the general education requirement."""
        cs_options = self.requirements.get("computer_science", [])
        logger.info(f"Fetching computer science courses for major ID: {self.major_id}")
        return self._fetch_courses("course_code", cs_options)

    def get_additional_courses(self):
        """Retrieve any additional general education courses required for the major."""
        additional_options = self.requirements.get("additional_courses", [])
        logger.info(f"Fetching additional general education courses for major ID: {self.major_id}")
        return self._fetch_courses("course_code", additional_options)

    def get_all_gen_ed_courses(self):
        """Retrieve all general education courses, categorized by type."""
        logger.info(f"Fetching all general education courses for major ID: {self.major_id}")
        return {
            "compulsory_courses": self.get_compulsory_courses(),
            "religious_courses": self.get_religious_courses(),
            "humanities_courses": self.get_humanities_courses(),
            "social_science_courses": self.get_social_science_courses(),
            "science_lab_courses": self.get_science_lab_courses(),
            "math_courses": self.get_math_courses(),
            "computer_science_courses": self.get_computer_science_courses(),
            "additional_courses": self.get_additional_courses()
        }

    def get_remaining_requirements(self, completed_courses):
        """
        Calculate the remaining general education requirements based on completed courses.
        
        Args:
        - completed_courses (list): List of completed course codes.

        Returns:
        - dict: Dictionary of unmet general education requirements.
        """
        unmet_requirements = {}
        all_gen_ed_courses = self.get_all_gen_ed_courses()

        for category, courses in all_gen_ed_courses.items():
            unmet = [course for course in courses if course['course_code'] not in completed_courses]
            if unmet:
                unmet_requirements[category] = unmet

        logger.info(f"Generated remaining general education requirements for major ID: {self.major_id}")
        return unmet_requirements
