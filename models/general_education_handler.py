import logging
from db import db
from sqlalchemy import text
from utils.normalization import normalize_course_code

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('general_education_handler.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class GeneralEducationHandler:
    """
    Handles general education requirements for a given major.
    """

    def __init__(self, major_id):
        self.major_id = major_id
        logger.info(f"Initialized GeneralEducationHandler for major ID: {major_id}")

    def get_general_education_requirements(self):
        """
        Retrieve general education requirements from the database.

        Returns:
            dict: General education courses grouped by category.
        """
        try:
            query = text(
                "SELECT category, course_code FROM bio_general_education WHERE major_id = :major_id"
            )
            with db.engine.connect() as connection:
                result = connection.execute(query, {"major_id": self.major_id}).fetchall()

            requirements = {}
            for row in result:
                category = row["category"]
                course_code = normalize_course_code(row["course_code"])
                if category not in requirements:
                    requirements[category] = []
                requirements[category].append(course_code)

            logger.info(f"General education requirements retrieved: {requirements}")
            return requirements

        except Exception as e:
            logger.error(f"Error retrieving general education requirements: {e}")
            return {}

    def get_remaining_requirements(self, completed_courses):
        """
        Calculate the remaining general education courses.

        Args:
            completed_courses (list): List of completed course codes.

        Returns:
            dict: Remaining general education courses by category.
        """
        try:
            all_requirements = self.get_general_education_requirements()
            remaining_requirements = {}

            # Normalize completed course codes
            normalized_completed = [normalize_course_code(c) for c in completed_courses]

            # Identify remaining courses by comparing with completed ones
            for category, courses in all_requirements.items():
                remaining = [course for course in courses if course not in normalized_completed]
                if remaining:
                    remaining_requirements[category] = remaining

            logger.info(f"Remaining general education requirements: {remaining_requirements}")
            return remaining_requirements

        except Exception as e:
            logger.error(f"Error calculating remaining general education requirements: {e}")
            return {}

    def is_general_education_course(self, course_code):
        """
        Check if the given course is a general education course.

        Args:
            course_code (str): Course code to validate.

        Returns:
            bool: True if it is a general education course, False otherwise.
        """
        try:
            all_requirements = self.get_general_education_requirements()
            all_courses = [course for category in all_requirements.values() for course in category]

            normalized_code = normalize_course_code(course_code)
            valid = normalized_code in all_courses

            logger.info(f"Course {course_code} is {'valid' if valid else 'not valid'} as a general education course.")
            return valid

        except Exception as e:
            logger.error(f"Error checking if course is general education: {e}")
            return False
